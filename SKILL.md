---
name: browser-harness-mcp
description: Direct browser control via MCP (Model Context Protocol). Use when the user wants to automate, scrape, test, or interact with web pages. Connects to the user's already-running Chrome.
---

# browser-harness-mcp

Direct browser control via MCP. Read `mcp_server.py` and `helpers.py` — that's where the functions live. For setup, install, or connection problems, read `install.md`.

## Usage

This harness now operates exclusively via **MCP native tools** with a fully autonomous connection flow. 
- You DO NOT need to write temporary python files. 
- You DO NOT need to use terminal commands to run scripts.
- You DO NOT need to launch Chrome manually. The MCP will detect if Chrome is running and automatically launch it with the required debugging flags if necessary.

Instead, invoke the provided MCP tools directly:
- `browser_navigate(url)`
- `browser_execute_js(script)`
- `browser_type_text(text, selector=None)`
- `browser_click(selector)`
- `browser_click_at_xy(x, y, button, clicks)`
- `browser_upload_file(selector, path)`
- `browser_wait(seconds)`
- `browser_wait_for_load(timeout)`
- `browser_take_screenshot(filename)`
- `browser_page_info()`
- `browser_list_tabs(include_chrome=True)`
- `browser_switch_tab(target_id)`
- `browser_new_tab(url)`
- `browser_close_tab(target_id)`
- `browser_scroll(x, y, dy, dx)`
- `browser_scroll_to_bottom()`
- `browser_scroll_to_top()`
- `browser_press_key(key, modifiers)`
- `browser_dispatch_key(selector, key, event)`
- `browser_iframe_target(url_substr)`
- `browser_handle_dialog(accept, prompt_text)`
- `browser_get_text(selector)`
- `browser_get_html(selector)`
- `browser_select_option(selector, value)`
- `browser_go_back()`
- `browser_go_forward()`

Example workflow:
1. `browser_navigate("https://x.com")` — automatically waits for `document.readyState == 'complete'`
2. `browser_take_screenshot("check_state.png")`
3. Inspect the image.
4. `browser_click('[data-testid="postButton"]')`

Available interaction skills:
- `interaction-skills/connection.md` — startup sequence, tab visibility, omnibox popup fix

Available domain skills:
- `domain-skills/x-twitter/community-manager.md`
- `domain-skills/tiktok/upload.md`

## Search first

Search `domain-skills/` first for the domain you are working on before inventing a new approach.

Only if you start struggling with a specific mechanic while navigating, look in `interaction-skills/` for helpers.

## Always contribute back

If you learned anything non-obvious about how a site works, open a PR to `domain-skills/<site>/` before you finish. Default to contributing. The harness gets better only because agents file what they learn.

Examples of what's worth documenting:
- A private API the page calls (XHR/fetch endpoint, request shape, auth)
- A stable selector (`data-testid`) that beats the obvious one.
- A framework quirk (React synthetic events issues, Vue list rendering).
- A trap — stale drafts, legacy IDs that now return null, beforeunload dialogs.

## Design constraints

- **Stealth and Security:** We use CDP to attach to the user's real browser profile. Do not attempt to run Playwright/Selenium which have highly detectable signatures.
- **MCP Native:** Expose everything through `mcp_server.py`.
- **Human in the Loop:** Always wait for user confirmation before executing destructive actions (Posting, Buying, Deleting) when outlined in the `domain-skills`.

## Clicking strategy

| Situation | Preferred tool |
|-----------|----------------|
| Standard HTML element (button, a, input, label) | `browser_click(selector)` — uses JS `.click()`, fast and reliable |
| Unknown position / floating menu / toast button | `browser_click_at_xy(x, y)` — use screenshot + pixel coords |
| SVG, Canvas, or element behind an overlay | `browser_click_at_xy(x, y)` — JS `.click()` ignores overlays |
| Element inside Shadow DOM | `browser_execute_js` with `shadowRoot.querySelector` |

When `browser_click` raises `ValueError: Element not found`, first verify the selector with `browser_get_html('body')` or check if the element is inside a shadow root.

## Gotchas (field-tested)

- After every meaningful action, re-screenshot (`browser_take_screenshot`) before assuming it worked. Use the image to verify changed state, open menus, navigation, visible errors, and whether the page is in the state you expected.
- `browser_navigate` now waits for page load automatically — no need to call `browser_wait(2)` after it unless you need to wait for dynamic content to render after load.
- If you need framework-specific DOM tricks, check `interaction-skills/` first. That is where dropdown, dialog, iframe, shadow DOM, and form-specific guidance belongs.

## Interaction notes

- `interaction-skills/` holds reusable UI mechanics such as dialogs, tabs, dropdowns, iframes, and uploads.
- `domain-skills/` holds site-specific workflows and should be updated when you discover reusable patterns for a website.
