"""Integration tests for browser connection and basic MCP tool functionality.

These tests require a live Chrome instance with remote debugging enabled on port 9222.
Run them explicitly with:  uv run pytest tests/test_connect.py -m integration
They are skipped in normal CI runs to avoid requiring a browser.
"""
import time
import pytest
from mcp_server import (
    browser_navigate,
    browser_execute_js,
    browser_page_info,
    browser_wait
)


@pytest.mark.integration
def test_browser_connection_and_navigation():
    """Test that we can navigate to a simple page and retrieve its info."""
    # 1. Navigate to a simple, reliable page
    browser_navigate(url="https://example.com")

    # Allow a moment for navigation
    browser_wait(seconds=2)

    # 2. Verify page info
    info = str(browser_page_info())
    assert "Example Domain" in info, f"Unexpected title in: {info}"
    assert "example.com" in info.lower(), f"Unexpected URL in: {info}"

    # 3. Test JS execution
    result = browser_execute_js("return document.title;")
    assert "Example Domain" in result, f"Unexpected JS result: {result}"
