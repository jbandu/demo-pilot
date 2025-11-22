"""
Browser Controller - Playwright wrapper for demo automation with human-like behavior
Handles browser navigation, screenshots, and interaction recording
"""
import asyncio
import base64
import random
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import logging

logger = logging.getLogger(__name__)


class BrowserController:
    """
    Manages browser automation for demos using Playwright with human-like behavior
    """

    def __init__(
        self,
        headless: bool = False,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        record_video: bool = True,
        video_dir: str = "./recordings",
        slow_mo: int = 100  # Milliseconds to slow down operations
    ):
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.record_video = record_video
        self.video_dir = video_dir
        self.slow_mo = slow_mo

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
        """Initialize browser and create context with human-like settings"""
        logger.info("Starting browser...")

        self.playwright = await async_playwright().start()

        # Launch browser with human-like settings
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,  # Slow down operations for visibility
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',  # Hide automation
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',  # For demo purposes
            ]
        )

        # Create context with video recording and realistic settings
        context_options = {
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "locale": "en-US",
            "timezone_id": "America/Los_Angeles",
            "geolocation": {"longitude": -122.4194, "latitude": 37.7749},  # San Francisco
            "permissions": ["geolocation"],
            "color_scheme": "light",
            "has_touch": False,
            "is_mobile": False,
            "java_script_enabled": True,
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

        # Inject human-like behavior scripts
        await self._inject_human_behavior()

        logger.info("Browser started successfully")

    async def _inject_human_behavior(self):
        """Inject scripts to make browser appear more human-like"""
        # Hide webdriver property
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Override plugins to appear more realistic
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        # Override languages
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        logger.debug("Human behavior scripts injected")

    async def stop(self):
        """Close browser and cleanup"""
        logger.info("Stopping browser...")

        video_path = None
        if self.page and self.page.video:
            try:
                video_path = await self.page.video.path()
                logger.info(f"Video saved to: {video_path}")
            except Exception as e:
                logger.warning(f"Could not get video path: {e}")

        if self.page:
            await self.page.close()

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

        logger.info("Browser stopped")
        return video_path

    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """Navigate to URL and wait for page load"""
        logger.info(f"Navigating to: {url}")

        try:
            await self.page.goto(url, wait_until=wait_until, timeout=30000)
            await asyncio.sleep(self._random_delay(0.5, 1.5))  # Natural pause
            await self._log_action("navigate", {"url": url})
            await self._capture_screenshot(f"navigate_{datetime.now().timestamp()}")
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            raise

    async def click(self, selector: str, description: str = ""):
        """Click element with human-like behavior"""
        logger.info(f"Clicking: {selector} ({description})")

        try:
            # Wait for element to be visible and clickable (increased timeout)
            await self.page.wait_for_selector(selector, state="visible", timeout=60000)

            # Scroll element into view first
            await self.smooth_scroll_to(selector)
            await asyncio.sleep(self._random_delay(0.3, 0.7))

            # Highlight element before clicking
            await self.highlight_element(selector, duration_ms=500, color="#4CAF50")
            await asyncio.sleep(self._random_delay(0.2, 0.5))

            # Move mouse to element with natural movement
            element = await self.page.query_selector(selector)
            if element:
                box = await element.bounding_box()
                if box:
                    # Add random offset to click point (more human-like)
                    x = box['x'] + box['width'] / 2 + random.randint(-5, 5)
                    y = box['y'] + box['height'] / 2 + random.randint(-5, 5)
                    await self.page.mouse.move(x, y, steps=random.randint(5, 15))
                    await asyncio.sleep(self._random_delay(0.1, 0.3))

            # Click with random delay and increased timeout
            await self.page.click(selector, delay=random.randint(50, 150), timeout=60000)
            await asyncio.sleep(self._random_delay(0.3, 0.8))

            await self._log_action("click", {
                "selector": selector,
                "description": description
            })
            await self._capture_screenshot(f"click_{datetime.now().timestamp()}")

        except Exception as e:
            logger.error(f"Click failed on {selector}: {e}")
            raise

    async def type_text(self, selector: str, text: str, delay: int = 100):
        """Type text with human-like speed and variation"""
        logger.info(f"Typing into: {selector}")

        try:
            # Click the field first
            await self.click(selector, "input field")
            await asyncio.sleep(self._random_delay(0.2, 0.4))

            # Clear existing content
            await self.page.fill(selector, '')
            await asyncio.sleep(self._random_delay(0.1, 0.2))

            # Type with variable delay (humans don't type at constant speed)
            for char in text:
                char_delay = delay + random.randint(-30, 50)
                await self.page.type(selector, char, delay=char_delay)

                # Occasionally pause longer (like thinking)
                if random.random() < 0.05:  # 5% chance
                    await asyncio.sleep(self._random_delay(0.3, 0.6))

            await asyncio.sleep(self._random_delay(0.3, 0.6))

            await self._log_action("type", {
                "selector": selector,
                "text": text
            })
            await self._capture_screenshot(f"type_{datetime.now().timestamp()}")

        except Exception as e:
            logger.error(f"Type failed on {selector}: {e}")
            raise

    async def upload_file(self, selector: str, file_path: str):
        """Upload file to input field"""
        logger.info(f"Uploading file: {file_path}")

        try:
            # Verify file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            await self.page.set_input_files(selector, file_path)
            await asyncio.sleep(self._random_delay(0.5, 1.0))

            await self._log_action("upload", {
                "selector": selector,
                "file_path": file_path
            })
            await self._capture_screenshot(f"upload_{datetime.now().timestamp()}")

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise

    async def hover(self, selector: str):
        """Hover over element with natural movement"""
        logger.info(f"Hovering: {selector}")

        try:
            await self.page.hover(selector)
            await asyncio.sleep(self._random_delay(0.3, 0.6))
            await self._log_action("hover", {"selector": selector})
        except Exception as e:
            logger.error(f"Hover failed on {selector}: {e}")
            raise

    async def scroll(self, direction: str = "down", pixels: int = 500):
        """Scroll page with smooth behavior"""
        logger.info(f"Scrolling {direction} by {pixels}px")

        try:
            if direction == "down":
                await self.page.evaluate(f"""
                    window.scrollBy({{
                        top: {pixels},
                        left: 0,
                        behavior: 'smooth'
                    }});
                """)
            elif direction == "up":
                await self.page.evaluate(f"""
                    window.scrollBy({{
                        top: -{pixels},
                        left: 0,
                        behavior: 'smooth'
                    }});
                """)

            await asyncio.sleep(self._random_delay(0.8, 1.5))
            await self._log_action("scroll", {"direction": direction, "pixels": pixels})

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            raise

    async def wait_for_selector(self, selector: str, timeout: int = 10000):
        """Wait for element to appear"""
        logger.info(f"Waiting for: {selector}")

        try:
            await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
        except Exception as e:
            logger.error(f"Wait for selector failed: {selector}")
            raise

    async def wait_for_navigation(self, timeout: int = 10000):
        """Wait for navigation to complete"""
        logger.info("Waiting for navigation...")

        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            logger.error(f"Wait for navigation failed: {e}")
            raise

    async def get_text(self, selector: str) -> str:
        """Get text content of element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.text_content()
            return ""
        except Exception as e:
            logger.error(f"Get text failed on {selector}: {e}")
            return ""

    async def screenshot(self, full_page: bool = False) -> bytes:
        """Take screenshot and return bytes"""
        try:
            return await self.page.screenshot(full_page=full_page)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return b""

    async def screenshot_element(self, selector: str) -> bytes:
        """Screenshot specific element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.screenshot()
            return b""
        except Exception as e:
            logger.error(f"Element screenshot failed: {e}")
            return b""

    async def get_video_frame(self) -> Optional[str]:
        """Get current video frame as base64"""
        try:
            screenshot = await self.screenshot()
            if screenshot:
                return base64.b64encode(screenshot).decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"Error capturing video frame: {e}")
            return None

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
            logger.error(f"Screenshot capture failed: {e}")

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
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return None

    async def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url

    async def get_page_title(self) -> str:
        """Get current page title"""
        try:
            return await self.page.title()
        except Exception as e:
            logger.error(f"Get title failed: {e}")
            return ""

    def get_actions_log(self) -> List[Dict[str, Any]]:
        """Get all logged actions"""
        return self.actions_log

    def clear_actions_log(self):
        """Clear actions log"""
        self.actions_log = []

    async def highlight_element(self, selector: str, duration_ms: int = 1000, color: str = "#4CAF50"):
        """Visually highlight element with colored outline"""
        try:
            await self.page.evaluate(f"""
                (selector, duration, color) => {{
                    const element = document.querySelector(selector);
                    if (element) {{
                        const originalOutline = element.style.outline;
                        const originalOutlineOffset = element.style.outlineOffset;
                        element.style.outline = `3px solid ${{color}}`;
                        element.style.outlineOffset = '2px';
                        setTimeout(() => {{
                            element.style.outline = originalOutline;
                            element.style.outlineOffset = originalOutlineOffset;
                        }}, duration);
                    }}
                }}
            """, selector, duration_ms, color)
        except Exception as e:
            logger.warning(f"Highlight failed: {e}")

    async def smooth_scroll_to(self, selector: str):
        """Smooth scroll to element"""
        try:
            await self.page.evaluate(f"""
                (selector) => {{
                    const element = document.querySelector(selector);
                    if (element) {{
                        element.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'center',
                            inline: 'center'
                        }});
                    }}
                }}
            """, selector)
            await asyncio.sleep(self._random_delay(0.8, 1.2))
        except Exception as e:
            logger.warning(f"Smooth scroll failed: {e}")

    async def wait(self, seconds: float):
        """Simple wait/pause"""
        await asyncio.sleep(seconds)

    def _random_delay(self, min_seconds: float, max_seconds: float) -> float:
        """Generate random delay for human-like behavior"""
        return random.uniform(min_seconds, max_seconds)

    async def press_key(self, key: str):
        """Press a keyboard key"""
        logger.info(f"Pressing key: {key}")
        try:
            await self.page.keyboard.press(key)
            await asyncio.sleep(self._random_delay(0.1, 0.3))
            await self._log_action("key_press", {"key": key})
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            raise

    async def select_option(self, selector: str, value: str):
        """Select option from dropdown"""
        logger.info(f"Selecting option {value} from {selector}")
        try:
            await self.click(selector)
            await asyncio.sleep(self._random_delay(0.2, 0.4))
            await self.page.select_option(selector, value)
            await asyncio.sleep(self._random_delay(0.2, 0.4))
            await self._log_action("select", {"selector": selector, "value": value})
        except Exception as e:
            logger.error(f"Select failed: {e}")
            raise

    async def check_checkbox(self, selector: str, checked: bool = True):
        """Check or uncheck a checkbox"""
        logger.info(f"Setting checkbox {selector} to {checked}")
        try:
            await self.page.set_checked(selector, checked)
            await asyncio.sleep(self._random_delay(0.2, 0.4))
            await self._log_action("checkbox", {"selector": selector, "checked": checked})
        except Exception as e:
            logger.error(f"Checkbox operation failed: {e}")
            raise

    async def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute value of element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.get_attribute(attribute)
            return None
        except Exception as e:
            logger.error(f"Get attribute failed: {e}")
            return None

    async def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.is_visible()
            return False
        except Exception as e:
            logger.error(f"Is visible check failed: {e}")
            return False


# Example usage
async def demo_example():
    """Example of browser controller usage"""
    controller = BrowserController(headless=False, slow_mo=200)

    try:
        await controller.start()
        await controller.navigate("https://example.com")
        await controller.wait(2)
        await controller.screenshot()
        print("Browser test successful!")

    finally:
        video_path = await controller.stop()
        print(f"Demo completed. Video saved at: {video_path}")


if __name__ == "__main__":
    asyncio.run(demo_example())
