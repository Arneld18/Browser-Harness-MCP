<img src="https://r2.browser-use.com/github/ajsdlasnnalsgasld.png" alt="Browser Harness MCP" width="100%" />

# Browser Harness MCP ♞

The simplest, thinnest, **self-healing** harness that gives LLM **complete freedom** to complete any browser task. Built directly on CDP and modernized via the **Model Context Protocol (MCP)**.

Instead of requiring the agent to write temporary Python scripts to interact with your browser, this version exposes native AI tools (e.g., `browser_navigate`, `browser_click`) via an MCP server. This results in **extreme speed, zero footprint, and natural interactions**.

```
  ● agent: wants to upload a file
  │
  ● Calls MCP Tool: browser_upload_file(selector, path)
  │
  ✓ file uploaded instantly (no intermediate scripts)
```

**You will never use the browser again.**

## Setup & Configuration

This project is designed to be added as an MCP server to your AI coding agent (like Antigravity, Claude Desktop, or Cline).

### 1. Installation

**Windows (PowerShell) — run from any directory:**
```powershell
irm https://raw.githubusercontent.com/Arneld18/Browser-Harness-MCP/main/install.ps1 | iex
```

**macOS / Linux — run from any directory:**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Arneld18/Browser-Harness-MCP/main/install.sh)
```

The script will:
- Clone the repo to `~/browser-harness-mcp` (Windows: `%USERPROFILE%\browser-harness-mcp`)
- Install all dependencies (`uv sync` or pip fallback)
- Print the exact `mcp.json` block with the correct paths for your machine

> **Prerequisites:** `git` must be installed. `uv` is recommended but the script falls back to `pip` automatically.

### 2. Connect to your Agent

Add the following to your MCP client configuration (e.g., `mcp.json`):

```json
{
  "mcpServers": {
    "browser-harness": {
      "command": "uv",
      "args": [
        "run",
        "/absolute/path/to/browser-harness-mcp/mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

Restart your agent, and it will immediately gain the ability to natively control your real Chrome browser!

## How simple is it?

- `mcp_server.py` — The FastMCP wrapper exposing the tools.
- `helpers.py` — The core CDP logic and DOM interaction primitives.
- `daemon.py` + `admin.py` — The socket bridge to your actual running Chrome instance.

## Contributing

PRs and improvements welcome. The best way to help: **contribute a new domain skill** under `domain-skills/` by documenting best practices and robust selectors for specific sites (like X/Twitter, LinkedIn, etc).

---

[The Bitter Lesson of Agent Harnesses](https://browser-use.com/posts/bitter-lesson-agent-harnesses) · [Web Agents That Actually Learn](https://browser-use.com/posts/web-agents-that-actually-learn)
