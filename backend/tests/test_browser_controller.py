import pytest
from agents.browser_controller import BrowserController


@pytest.mark.asyncio
async def test_browser_initialization():
    """Test browser can initialize"""
    controller = BrowserController(headless=True)

    try:
        await controller.initialize()
        assert controller.browser is not None
        assert controller.page is not None
    finally:
        await controller.close()


@pytest.mark.asyncio
async def test_browser_navigation():
    """Test browser navigation"""
    controller = BrowserController(headless=True, slow_mo=0)

    try:
        await controller.initialize()
        await controller.navigate("https://example.com")

        # Check we're on the right page
        title = await controller.page.title()
        assert "Example" in title
    finally:
        await controller.close()


@pytest.mark.asyncio
async def test_browser_click():
    """Test clicking elements"""
    controller = BrowserController(headless=True, slow_mo=0)

    try:
        await controller.initialize()
        await controller.navigate("https://example.com")

        # Find and click a link (example.com has a "More information..." link)
        await controller.click("a")

        # Should navigate to IANA page
        await controller.page.wait_for_load_state("networkidle")
        url = controller.page.url
        assert "iana.org" in url
    finally:
        await controller.close()


@pytest.mark.asyncio
async def test_browser_type():
    """Test typing text"""
    controller = BrowserController(headless=True, slow_mo=0)

    try:
        await controller.initialize()
        await controller.navigate("https://www.google.com")

        # Type in search box
        await controller.type_text("textarea[name='q']", "test query", delay=10)

        # Verify text was typed
        value = await controller.page.input_value("textarea[name='q']")
        assert value == "test query"
    finally:
        await controller.close()


@pytest.mark.asyncio
async def test_browser_screenshot():
    """Test taking screenshots"""
    controller = BrowserController(headless=True, slow_mo=0)

    try:
        await controller.initialize()
        await controller.navigate("https://example.com")

        screenshot = await controller.screenshot()
        assert screenshot is not None
        assert len(screenshot) > 0
    finally:
        await controller.close()
