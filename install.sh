#!/usr/bin/env bash
# ============================================================
#  Browser Harness MCP — macOS / Linux Installer
#  Usage:
#    bash install.sh
#    bash install.sh --install-dir "$HOME/my-tools/browser-harness-mcp"
# ============================================================

set -e

REPO_URL="https://github.com/Arneld18/Browser-Harness-MCP"
INSTALL_DIR="$HOME/browser-harness-mcp"

# ── Parse arguments ─────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --install-dir=*)
            INSTALL_DIR="${1#*=}"
            shift
            ;;
        -h|--help)
            echo "Usage: bash install.sh [--install-dir PATH]"
            echo "  --install-dir PATH   Where to install (default: ~/browser-harness-mcp)"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

MCP_ENTRY="$INSTALL_DIR/mcp_server.py"

# ── Helpers ─────────────────────────────────────────────────

CYAN="\033[1;36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
GRAY="\033[0;37m"
RESET="\033[0m"

step()    { echo -e "\n${CYAN}==> $1${RESET}"; }
success() { echo -e "  ${GREEN}✓ $1${RESET}"; }
warn()    { echo -e "  ${YELLOW}⚠ $1${RESET}"; }
error()   { echo -e "\n${RED}ERROR: $1${RESET}" >&2; exit 1; }

require() {
    command -v "$1" >/dev/null 2>&1 || \
        error "'$1' is not installed or not in PATH. Please install it and rerun."
}

# ── 1. Check prerequisites ───────────────────────────────────

step "Checking prerequisites..."
require git

HAS_UV=false
HAS_PYTHON=false

command -v uv     >/dev/null 2>&1 && HAS_UV=true
command -v python3 >/dev/null 2>&1 && HAS_PYTHON=true
command -v python  >/dev/null 2>&1 && HAS_PYTHON=true

if ! $HAS_UV && ! $HAS_PYTHON; then
    error "Neither 'uv' nor 'python3' found in PATH.\n  Install uv (recommended): https://docs.astral.sh/uv/getting-started/installation/\n  Or install Python 3.11+:  https://www.python.org/downloads/"
fi

success "git found"
if $HAS_UV; then
    success "uv found (will be used for dependency install)"
else
    warn "uv not found — falling back to pip"
fi

# ── 2. Clone repository ──────────────────────────────────────

step "Cloning repository..."

if [ -d "$INSTALL_DIR" ]; then
    warn "Directory already exists: $INSTALL_DIR"
    warn "Pulling latest changes instead of cloning..."
    git -C "$INSTALL_DIR" pull --ff-only || error "git pull failed. Please resolve manually."
else
    git clone "$REPO_URL" "$INSTALL_DIR" || error "git clone failed."
fi

success "Repository ready at: $INSTALL_DIR"

# ── 3. Install dependencies ──────────────────────────────────

step "Installing dependencies..."

if $HAS_UV; then
    (cd "$INSTALL_DIR" && uv sync) || error "uv sync failed."
    PYTHON="$INSTALL_DIR/.venv/bin/python"
else
    # Detect python binary
    PYTHON_BIN=$(command -v python3 || command -v python)
    "$PYTHON_BIN" -m venv "$INSTALL_DIR/.venv"
    PYTHON="$INSTALL_DIR/.venv/bin/python"
    "$PYTHON" -m pip install --quiet -e "$INSTALL_DIR" || error "pip install failed."
fi

success "Dependencies installed"

# ── 4. Detect Claude Desktop config location ─────────────────

CLAUDE_CONFIG=""
OS_TYPE="$(uname -s)"

if [ "$OS_TYPE" = "Darwin" ]; then
    CANDIDATE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    [ -f "$CANDIDATE" ] && CLAUDE_CONFIG="$CANDIDATE"
fi

# ── 5. Build mcp.json block ──────────────────────────────────

MCP_BLOCK=$(cat <<EOF
{
  "mcpServers": {
    "browser-harness": {
      "command": "$PYTHON",
      "args": [
        "$MCP_ENTRY"
      ],
      "env": {}
    }
  }
}
EOF
)

# ── 6. Print result ──────────────────────────────────────────

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}  ✅  Browser Harness MCP installed successfully!${RESET}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  Install path : $INSTALL_DIR"
echo -e "  Python       : $PYTHON"
echo ""
echo -e "─────────────────────────────────────────────────────────"
echo -e "${YELLOW}  STEP 1 — Add this block to your mcp.json${RESET}"
echo -e "─────────────────────────────────────────────────────────"
echo ""
echo "$MCP_BLOCK"
echo ""
echo -e "─────────────────────────────────────────────────────────"
echo -e "${YELLOW}  STEP 2 — Common mcp.json locations${RESET}"
echo -e "─────────────────────────────────────────────────────────"
echo ""
echo -e "  Antigravity  : Check your Antigravity MCP settings panel"

if [ "$OS_TYPE" = "Darwin" ]; then
    echo -e "  Claude Desktop (macOS):"
    echo -e "    ${GRAY}~/Library/Application Support/Claude/claude_desktop_config.json${RESET}"
    if [ -n "$CLAUDE_CONFIG" ]; then
        echo -e "  ${GREEN}↳ Config file detected at the above path${RESET}"
    fi
else
    echo -e "  Claude Desktop: check ~/.config or your agent's documentation"
fi

echo ""
echo -e "─────────────────────────────────────────────────────────"
echo -e "${YELLOW}  STEP 3 — Restart your AI agent${RESET}"
echo -e "─────────────────────────────────────────────────────────"
echo ""
echo -e "  Restart Antigravity / Claude Desktop after saving mcp.json."
echo -e "  Chrome will launch automatically on first browser tool call."
echo ""
echo -e "  ${GRAY}Need help? Read: $INSTALL_DIR/install.md${RESET}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
