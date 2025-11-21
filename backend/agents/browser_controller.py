"""
Browser Controller - Playwright wrapper for demo automation
Handles browser navigation, screenshots, and interaction recording
"""
import asyncio
import base64
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import logging

logger = logging.getLogger(__name__)


class BrowserController:
    """
    Manages browser automation for demos using Playwright
    """

    def __init__(
        self,
        headless: bool = False,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        record_video: bool = True,
        video_dir: str = "./recordings"
    ):
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.record_video = record_video
        self.video_dir = video_dir

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Tracking
        self.actions_log: List[Dict[str, Any]] = []
        self.screenshots: List[str] = []

        # Callbacks for streaming
        self.on_screenshot: Optional[Callable] = None
        self.on_action: Optional[Callable] = None

    async def start(self):
        """Initialize browser and create context"""
        logger.info("Starting browser...")

        self.playwright = await async_playwright().start()

        # Launch browser
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )

        # Create context with video recording
        context_options = {
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "locale": "en-US",
            "timezone_id": "America/New_York"
        }

        if self.record_video:
            Path(self.video_dir).mkdir(parents=True, exist_ok=True)
            context_options["record_video_dir"] = self.video_dir
            context_options["record_video_size"] = {
                "width": self.viewport_width,
                "height": self.viewport_height
            }

        self.context = await self.browser.new_context(**context_options)

        # Create page
        self.page = await self.context.new_page()

        logger.info("Browser started successfully")

    async def stop(self):
        """Close browser and cleanup"""
        logger.info("Stopping browser...")

        if self.page:
            await self.page.close()

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

        logger.info("Browser stopped")

    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """Navigate to URL and wait for page load"""
        logger.info(f"Navigating to: {url}")

        await self.page.goto(url, wait_until=wait_until)
        await self._log_action("navigate", {"url": url})
        await self._capture_screenshot(f"navigate_{datetime.now().timestamp()}")

    async def click(self, selector: str, description: str = ""):
        """Click element by selector"""
        logger.info(f"Clicking: {selector} ({description})")

        await self.page.click(selector)
        await asyncio.sleep(0.5)  # Brief pause for UI updates

        await self._log_action("click", {
            "selector": selector,
            "description": description
        })
        await self._capture_screenshot(f"click_{datetime.now().timestamp()}")

    async def type_text(self, selector: str, text: str, delay: int = 50):
        """Type text into element"""
        logger.info(f"Typing into: {selector}")

        await self.page.fill(selector, text)
        await asyncio.sleep(0.3)

        await self._log_action("type", {
            "selector": selector,
            "text": text
        })
        await self._capture_screenshot(f"type_{datetime.now().timestamp()}")

    async def hover(self, selector: str):
        """Hover over element"""
        logger.info(f"Hovering: {selector}")

        await self.page.hover(selector)
        await asyncio.sleep(0.3)

        await self._log_action("hover", {"selector": selector})

    async def scroll(self, direction: str = "down", pixels: int = 500):
        """Scroll page"""
        logger.info(f"Scrolling {direction} by {pixels}px")

        if direction == "down":
            await self.page.evaluate(f"window.scrollBy(0, {pixels})")
        elif direction == "up":
            await self.page.evaluate(f"window.scrollBy(0, -{pixels})")

        await asyncio.sleep(0.5)
        await self._log_action("scroll", {"direction": direction, "pixels": pixels})

    async def wait_for_selector(self, selector: str, timeout: int = 10000):
        """Wait for element to appear"""
        logger.info(f"Waiting for: {selector}")

        await self.page.wait_for_selector(selector, timeout=timeout)

    async def wait_for_navigation(self, timeout: int = 10000):
        """Wait for navigation to complete"""
        logger.info("Waiting for navigation...")

        await self.page.wait_for_load_state("networkidle", timeout=timeout)

    async def get_text(self, selector: str) -> str:
        """Get text content of element"""
        element = await self.page.query_selector(selector)
        if element:
            return await element.text_content()
        return ""

    async def screenshot(self, full_page: bool = False) -> bytes:
        """Take screenshot and return bytes"""
        return await self.page.screenshot(full_page=full_page)

    async def screenshot_element(self, selector: str) -> bytes:
        """Screenshot specific element"""
        element = await self.page.query_selector(selector)
        if element:
            return await element.screenshot()
        return b""

    async def _capture_screenshot(self, name: str):
        """Capture screenshot and trigger callback"""
        try:
            screenshot_bytes = await self.screenshot()
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()

            self.screenshots.append({
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "data": screenshot_b64
            })

            if self.on_screenshot:
                await self.on_screenshot(screenshot_b64)

        except Exception as e:
            logger.error(f"Screenshot failed: {e}")

    async def _log_action(self, action_type: str, details: Dict[str, Any]):
        """Log action and trigger callback"""
        action = {
            "type": action_type,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }

        self.actions_log.append(action)

        if self.on_action:
            await self.on_action(action)

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on page"""
        return await self.page.evaluate(script)

    async def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url

    async def get_page_title(self) -> str:
        """Get current page title"""
        return await self.page.title()

    def get_actions_log(self) -> List[Dict[str, Any]]:
        """Get all logged actions"""
        return self.actions_log

    def clear_actions_log(self):
        """Clear actions log"""
        self.actions_log = []

    async def highlight_element(self, selector: str, duration_ms: int = 1000):
        """Visually highlight element (useful for demos)"""
        await self.page.evaluate(f"""
            const element = document.querySelector('{selector}');
            if (element) {{
                const originalOutline = element.style.outline;
                element.style.outline = '3px solid #FF6B6B';
                setTimeout(() => {{
                    element.style.outline = originalOutline;
                }}, {duration_ms});
            }}
        """)

    async def smooth_scroll_to(self, selector: str):
        """Smooth scroll to element"""
        await self.page.evaluate(f"""
            const element = document.querySelector('{selector}');
            if (element) {{
                element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
        """)
        await asyncio.sleep(1)

    async def wait(self, seconds: float):
        """Simple wait/pause"""
        await asyncio.sleep(seconds)


# Example usage
async def demo_example():
    """Example of browser controller usage"""
    controller = BrowserController(headless=False)

    try:
        await controller.start()
        await controller.navigate("https://example.com")
        await controller.wait(2)
        await controller.screenshot()

    finally:
        await controller.stop()


if __name__ == "__main__":
    asyncio.run(demo_example())
