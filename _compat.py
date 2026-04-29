"""Windows compatibility shim for browser-harness.

On Linux/macOS, browser-harness uses AF_UNIX sockets at /tmp/bu-<NAME>.sock.
On Windows (where AF_UNIX is often unavailable), we fall back to localhost TCP
on a deterministic port derived from the BU_NAME. Temp files (logs, pid) also
use the OS temp directory instead of /tmp.

Every module that needs socket paths or connections imports from here.
"""

import hashlib
import os
import socket
import sys
import tempfile
from pathlib import Path

def load_env():
    p = Path(__file__).parent / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()

IS_WINDOWS = sys.platform == "win32"
HAS_AF_UNIX = hasattr(socket, "AF_UNIX")
USE_TCP = IS_WINDOWS and not HAS_AF_UNIX

# --- temp directory ---
# On Unix: /tmp.  On Windows: %TEMP%.
TMPDIR = Path(tempfile.gettempdir()) if IS_WINDOWS else Path("/tmp")


def _tcp_port_for_name(name: str) -> int:
    """Deterministic port in the 49152–65535 ephemeral range from BU_NAME."""
    h = int(hashlib.sha256(f"bu-{name}".encode()).hexdigest()[:8], 16)
    return 49152 + (h % (65535 - 49152))


def paths(name: str):
    """Return (sock_or_port, log_path, pid_path) for a given BU_NAME."""
    log = str(TMPDIR / f"bu-{name}.log")
    pid = str(TMPDIR / f"bu-{name}.pid")
    if USE_TCP:
        # Store the port number in a file so other processes can read it.
        port_file = str(TMPDIR / f"bu-{name}.port")
        return port_file, log, pid
    else:
        sock = str(TMPDIR / f"bu-{name}.sock")
        return sock, log, pid


def get_port(name: str) -> int:
    """Get the TCP port for a given name. Read from port file if it exists,
    otherwise compute deterministically."""
    port_file = str(TMPDIR / f"bu-{name}.port")
    try:
        return int(Path(port_file).read_text().strip())
    except (FileNotFoundError, ValueError):
        return _tcp_port_for_name(name)


def write_port(name: str, port: int):
    """Write the actual listening port to the port file."""
    port_file = str(TMPDIR / f"bu-{name}.port")
    Path(port_file).write_text(str(port))


def connect_to_daemon(name: str, timeout: float = 1.0) -> socket.socket:
    """Create a connected socket to the daemon for the given BU_NAME."""
    if USE_TCP:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        port = get_port(name)
        s.connect(("127.0.0.1", port))
        return s
    else:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        sock_path = str(TMPDIR / f"bu-{name}.sock")
        s.connect(sock_path)
        return s


def daemon_check_alive(name: str) -> bool:
    """Check if the daemon is alive by attempting a TCP/Unix connection."""
    try:
        s = connect_to_daemon(name, timeout=1.0)
        s.close()
        return True
    except (FileNotFoundError, ConnectionRefusedError, socket.timeout, OSError):
        return False


def cleanup_files(name: str):
    """Remove socket/port and pid files."""
    _, log, pid = paths(name)
    port_file = str(TMPDIR / f"bu-{name}.port")
    sock_file = str(TMPDIR / f"bu-{name}.sock")
    for f in (sock_file, port_file, pid):
        try:
            os.unlink(f)
        except FileNotFoundError:
            pass
