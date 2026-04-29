---
name: browser-harness-mcp-install
description: Install and bootstrap browser-harness-mcp into your MCP-compatible agent.
---

# Browser-Harness MCP Install

This project has been updated to function exclusively as an **MCP (Model Context Protocol) Server**. It no longer requires the dynamic generation of Python scripts (`run.py`), nor registering `SKILL.md` as a global instruction in the old way.

## 1. Quick Install (recommended)

Run the installer script for your OS. It clones the repo to a standard location, installs dependencies, and prints the exact `mcp.json` block you need to copy.

### Windows (PowerShell)

```powershell
# Run from any directory — no need to clone first
irm https://raw.githubusercontent.com/Arneld18/Browser-Harness-MCP/main/install.ps1 | iex
```

Or if you already have the repo locally:
```powershell
.\install.ps1
# Custom install directory:
.\install.ps1 -InstallDir "D:\my-tools\browser-harness-mcp"
```

### macOS / Linux (Bash)

```bash
# Run from any directory — no need to clone first
bash <(curl -fsSL https://raw.githubusercontent.com/Arneld18/Browser-Harness-MCP/main/install.sh)
```

Or if you already have the repo locally:
```bash
bash install.sh
# Custom install directory:
bash install.sh --install-dir "$HOME/my-tools/browser-harness-mcp"
```

The script will:
1. Clone the repo to `~/browser-harness-mcp` (Windows: `%USERPROFILE%\browser-harness-mcp`)
2. Install all dependencies via `uv sync` (or pip as fallback)
3. Print the exact `mcp.json` block with correct paths for your machine
4. Show you where to paste it and what to do next

> **Prerequisites:** `git` must be installed. `uv` is recommended but falls back to `pip` automatically.

---

## 1b. Manual Setup (alternative)

If you prefer to install manually:

```bash
git clone https://github.com/Arneld18/Browser-Harness-MCP
cd browser-harness-mcp
uv sync
# Or: python -m pip install -e .
```

Make sure all dependencies install correctly, otherwise the background daemon will silently fail to start.

## 2. Configure the MCP Client

After running the installer script, it will print a ready-to-use `mcp.json` block like this (with your actual paths filled in):

**Windows example:**
```json
{
  "mcpServers": {
    "browser-harness": {
      "command": "C:\\Users\\YourUser\\browser-harness-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\YourUser\\browser-harness-mcp\\mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

**macOS / Linux example:**
```json
{
  "mcpServers": {
    "browser-harness": {
      "command": "/home/youruser/browser-harness-mcp/.venv/bin/python",
      "args": [
        "/home/youruser/browser-harness-mcp/mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

Copy the block the installer printed (it contains your real paths), paste it into your agent's `mcp.json`, and restart the agent.

**Common `mcp.json` locations:**
| Agent | Location |
|-------|----------|
| Antigravity | MCP settings panel in the UI |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |


## 3. Functionality Check

Once configured, restart your agent. If the connection was successful, your agent will have automatic access to the following 26 native tools:

**Navigation & Page**
- `browser_navigate(url)` — navigate and auto-wait for page load
- `browser_page_info()` — returns title, URL, viewport as JSON
- `browser_wait_for_load(timeout)` — wait until `readyState == complete`
- `browser_wait(seconds)` — explicit pause
- `browser_go_back()` / `browser_go_forward()` — history navigation

**Interaction**
- `browser_click(selector)` — JS click on CSS selector
- `browser_click_at_xy(x, y, button, clicks)` — native mouse click at pixel coords
- `browser_type_text(text, selector)` — keyboard input, optional focus
- `browser_press_key(key, modifiers)` — single key with modifier bitfield
- `browser_dispatch_key(selector, key, event)` — DOM KeyboardEvent to element
- `browser_select_option(selector, value)` — select `<select>` dropdown option
- `browser_handle_dialog(accept, prompt_text)` — dismiss alert/confirm/prompt

**DOM Inspection**
- `browser_get_text(selector)` — innerText of matched element
- `browser_get_html(selector)` — outerHTML of matched element
- `browser_execute_js(script)` — arbitrary JavaScript, returns result

**Tabs & Windows**
- `browser_list_tabs(include_chrome)` — lists all tabs as JSON
- `browser_switch_tab(target_id)` — focus a tab by ID
- `browser_new_tab(url)` — open new tab, returns its ID
- `browser_close_tab(target_id)` — close a tab
- `browser_iframe_target(url_substr)` — find iframe targetId by URL fragment

**Scrolling**
- `browser_scroll(x, y, dy, dx)` — wheel event at coordinates
- `browser_scroll_to_bottom()` — jump to bottom of page
- `browser_scroll_to_top()` — jump to top of page

**Files & Media**
- `browser_take_screenshot(filename)` — PNG screenshot, saved to temp dir
- `browser_upload_file(selector, file_path)` — file input via CDP (bypasses bot detection)

Your agent can invoke these functions directly and invisibly.

## 4. Browser Connection (Chrome DevTools Protocol)

The browser-harness MCP server features a **fully autonomous connection flow**. 

**You DO NOT need to manually launch Chrome.**

If Chrome is not running, the MCP server will automatically detect this and launch it for you with the required debugging flags (`--remote-debugging-port=9222` and `--remote-allow-origins=*`).

The system will attempt to find your default Chrome installation automatically on Windows, macOS, and Linux.

If you prefer to start Chrome manually (for example, to use a specific profile), you must start it with those exact flags:

### Windows (Manual Launch Option)
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=*
```

### macOS (Manual Launch Option)
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --remote-allow-origins=*
```

### Linux (Manual Launch Option)
```bash
google-chrome --remote-debugging-port=9222 --remote-allow-origins=*
```

---
**Final Workflow:**
1. Configure your agent to point to the `mcp_server.py`.
2. Start your agent.
3. Your AI agent automatically connects via the MCP Server invisibly and natively. If Chrome is not running, it will launch it.
4. Zero scripts and zero configuration screens!

## 5. Optional Environment Variables

These variables can be set in a `.env` file in the project root or directly in the `env` block of your `mcp.json`:

| Variable | Purpose |
|----------|---------|
| `BU_CDP_WS` | Connect to a remote Chrome via WebSocket URL instead of the local browser (e.g. `ws://192.168.1.10:9222/devtools/browser/...`) |
| `BU_CDP_URL` | HTTP DevTools endpoint for a remote Chrome (e.g. `http://127.0.0.1:9333`). The harness resolves this to a WS URL automatically. |
| `BU_NAME` | Daemon instance name. Useful when running multiple harness instances in parallel. Default: `default` |
| `BROWSER_USE_API_KEY` | Needed only for Browser Use cloud browsers and profile sync. Not required for local Chrome. |

Example `.env`:
```dotenv
# Only needed for remote/cloud usage
BU_CDP_WS=ws://127.0.0.1:9222/devtools/browser/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
BROWSER_USE_API_KEY=your_key_here
```
