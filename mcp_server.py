import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import helpers
from _compat import TMPDIR

mcp = FastMCP("BrowserHarness")

@mcp.tool()
def browser_navigate(url: str) -> str:
    """Navigates to a specific URL in the active browser tab and waits for the page to load."""
    helpers.goto_url(url)
    helpers.wait_for_load(timeout=15.0)
    return f"Navigated to {url}"

@mcp.tool()
def browser_execute_js(script: str) -> str:
    """Executes JavaScript code in the context of the current page and returns the result."""
    result = helpers.js(script)
    return str(result)

@mcp.tool()
def browser_type_text(text: str, selector: str = None) -> str:
    """
    Types text into the browser.
    If a CSS selector is provided, it attempts to focus that element first using JS.
    """
    if selector:
        # Escape single quotes
        safe_selector = selector.replace("'", "\\'")
        helpers.js(f"var el = document.querySelector('{safe_selector}'); if(el) el.focus();")
        helpers.wait(0.5)
    
    helpers.type_text(text)
    return f"Typed text successfully"

@mcp.tool()
def browser_click(selector: str) -> str:
    """
    Clicks on the element specified by the CSS selector using JavaScript.
    This is generally more reliable for silent automation.
    """
    safe_selector = selector.replace("'", "\\'")
    result = helpers.js(f"var el = document.querySelector('{safe_selector}'); if(el){{ el.click(); 'clicked'; }} else {{ 'not found'; }}")
    if result == 'not found':
        raise ValueError(f"Element not found: {selector}")
    return f"Clicked element: {selector}"

@mcp.tool()
def browser_wait(seconds: float) -> str:
    """Waits for a specific amount of seconds (ideal for human-mimicry)."""
    helpers.wait(seconds)
    return f"Waited for {seconds} seconds"

@mcp.tool()
def browser_take_screenshot(filename: str = "mcp_screenshot.png"):
    """
    Takes a screenshot of the current browser viewport and saves it to disk.
    Returns an Image object natively supported by FastMCP.
    If filename is a relative path, it is resolved inside the OS temp directory
    so the file always ends up in a predictable, writable location.
    """
    # Resolve relative filenames to TMPDIR so files don't land in unknown CWD.
    resolved = filename if Path(filename).is_absolute() else str(TMPDIR / filename)
    path = helpers.capture_screenshot(resolved)
    try:
        from mcp.server.fastmcp import Image
        with open(path, "rb") as f:
            data = f.read()
        return Image(data=data, format="png")
    except ImportError:
        return f"Screenshot saved to {path}"

@mcp.tool()
def browser_page_info() -> str:
    """Returns a summary of the current page including title, URL, and viewport info."""
    info = helpers.page_info()
    return json.dumps(info)

@mcp.tool()
def browser_upload_file(selector: str, file_path: str) -> str:
    """
    Uploads a file to an <input type="file"> element using its CSS selector.
    Uses the native CDP DOM.setFileInputFiles method, bypassing bot detection.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"Error: File does not exist at path {file_path}")
    
    helpers.upload_file(selector, file_path)
    return f"File {file_path} uploaded to {selector}"

@mcp.tool()
def browser_list_tabs(include_chrome: bool = True) -> str:
    """
    Lists all available browser tabs.
    Set include_chrome to False to hide internal chrome:// tabs.
    Returns a list of dictionaries with targetId, title, and url.
    """
    tabs = helpers.list_tabs(include_chrome)
    return json.dumps(tabs)

@mcp.tool()
def browser_switch_tab(target_id: str) -> str:
    """
    Switches to the browser tab specified by the given targetId.
    You can get targetIds from browser_list_tabs.
    """
    helpers.switch_tab(target_id)
    return f"Switched to tab {target_id}"

@mcp.tool()
def browser_new_tab(url: str = "about:blank") -> str:
    """
    Opens a new browser tab and optionally navigates to a URL.
    Returns the targetId of the new tab.
    """
    target_id = helpers.new_tab(url)
    return f"New tab created with targetId: {target_id}"

@mcp.tool()
def browser_close_tab(target_id: str) -> str:
    """
    Closes the browser tab specified by the given targetId.
    You can get targetIds from browser_list_tabs or browser_new_tab.
    """
    helpers.cdp("Target.closeTarget", targetId=target_id)
    return f"Closed tab {target_id}"

@mcp.tool()
def browser_scroll(x: int, y: int, dy: int = -300, dx: int = 0) -> str:
    """
    Dispatches a mouse wheel scroll event at the specified (x, y) coordinates.
    dy is the vertical scroll delta (negative means scroll down, positive means scroll up).
    dx is the horizontal scroll delta.
    """
    helpers.scroll(x, y, dy, dx)
    return f"Scrolled at ({x}, {y}) by dy={dy}, dx={dx}"

@mcp.tool()
def browser_scroll_to_bottom() -> str:
    """Scrolls to the absolute bottom of the current page."""
    helpers.js("window.scrollTo(0, document.body.scrollHeight);")
    return "Scrolled to bottom"

@mcp.tool()
def browser_scroll_to_top() -> str:
    """Scrolls to the absolute top of the current page."""
    helpers.js("window.scrollTo(0, 0);")
    return "Scrolled to top"

@mcp.tool()
def browser_press_key(key: str, modifiers: int = 0) -> str:
    """
    Presses a specific keyboard key (e.g., 'Enter', 'Tab', 'Escape', 'a', 'B').
    modifiers is a bitfield: 1=Alt, 2=Ctrl, 4=Meta(Cmd), 8=Shift.
    """
    helpers.press_key(key, modifiers)
    return f"Pressed key {key} with modifiers {modifiers}"

@mcp.tool()
def browser_click_at_xy(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    """
    Dispatches a native mouse click at the given viewport coordinates (x, y).
    Button can be 'left', 'middle', or 'right'.
    """
    helpers.click_at_xy(x, y, button, clicks)
    return f"Clicked {button} button at ({x}, {y}) {clicks} time(s)"

@mcp.tool()
def browser_wait_for_load(timeout: float = 15.0) -> str:
    """
    Waits until document.readyState == 'complete' or the timeout is reached.
    """
    success = helpers.wait_for_load(timeout)
    if success:
        return "Page loaded successfully"
    return "Timeout waiting for page to load"

@mcp.tool()
def browser_dispatch_key(selector: str, key: str = "Enter", event: str = "keypress") -> str:
    """
    Dispatches a DOM KeyboardEvent directly to the matched element.
    Use this when synthetic DOM events work more reliably than native CDP input.
    """
    helpers.dispatch_key(selector, key, event)
    return f"Dispatched {event} for key {key} to {selector}"

@mcp.tool()
def browser_iframe_target(url_substr: str) -> str:
    """
    Finds the targetId of the first iframe whose URL contains url_substr.
    This targetId can be used with js(..., target_id=...) internally, or returned for reference.
    """
    target_id = helpers.iframe_target(url_substr)
    if target_id:
        return f"Found iframe targetId: {target_id}"
    return f"No iframe found matching {url_substr}"

@mcp.tool()
def browser_handle_dialog(accept: bool = True, prompt_text: str = None) -> str:
    """
    Handles an open JavaScript dialog (alert, confirm, prompt, beforeunload).
    Set accept=True to click OK/Yes, and accept=False to click Cancel/No.
    If it's a prompt, you can provide prompt_text to fill the input field.
    """
    params = {"accept": accept}
    if prompt_text is not None:
        params["promptText"] = prompt_text
    helpers.cdp("Page.handleJavaScriptDialog", **params)
    return f"Dialog handled (accept={accept}, text={prompt_text})"

@mcp.tool()
def browser_get_text(selector: str) -> str:
    """
    Retrieves the innerText of the element matched by the CSS selector.
    """
    safe_selector = selector.replace("'", "\\'")
    result = helpers.js(f"var el = document.querySelector('{safe_selector}'); if(el){{ return el.innerText; }} else {{ return null; }}")
    if result is None:
        raise ValueError(f"Element not found: {selector}")
    return str(result)

@mcp.tool()
def browser_get_html(selector: str) -> str:
    """
    Retrieves the outerHTML of the element matched by the CSS selector.
    Useful for inspecting DOM structure when innerText is insufficient.
    """
    safe_selector = selector.replace("'", "\\'")
    result = helpers.js(f"var el = document.querySelector('{safe_selector}'); if(el){{ return el.outerHTML; }} else {{ return null; }}")
    if result is None:
        raise ValueError(f"Element not found: {selector}")
    return str(result)

@mcp.tool()
def browser_select_option(selector: str, value: str) -> str:
    """
    Selects an option in a <select> dropdown by its value attribute.
    """
    safe_selector = selector.replace("'", "\\'")
    safe_value = value.replace("'", "\\'")
    result = helpers.js(f"var el = document.querySelector('{safe_selector}'); if(el && el.tagName === 'SELECT'){{ el.value = '{safe_value}'; el.dispatchEvent(new Event('change', {{ bubbles: true }})); return 'selected'; }} else {{ return 'not found'; }}")
    if result == 'not found':
        raise ValueError(f"Select element not found or invalid: {selector}")
    return f"Selected '{value}' in {selector}"

@mcp.tool()
def browser_go_back() -> str:
    """Navigates to the previous page in history."""
    helpers.js("window.history.back();")
    return "Navigated back"

@mcp.tool()
def browser_go_forward() -> str:
    """Navigates to the next page in history."""
    helpers.js("window.history.forward();")
    return "Navigated forward"

if __name__ == "__main__":
    # Start the server using standard IO (stdio), standard for MCP
    mcp.run()
