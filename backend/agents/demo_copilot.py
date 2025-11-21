"""
Demo Copilot - Main orchestrator for autonomous product demonstrations
Coordinates browser automation, voice narration, and question handling
"""
import asyncio
import uuid
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum
import logging

from .browser_controller import BrowserController
from .voice_engine import VoiceEngine, DemoNarrator
from .question_handler import QuestionHandler, INSIGN_PRODUCT_CONTEXT
from .demo_scripts.insign_demo import InSignDemoScript

logger = logging.getLogger(__name__)


class DemoState(str, Enum):
    """Current state of the demo"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ANSWERING_QUESTION = "answering_question"
    COMPLETED = "completed"
    FAILED = "failed"


class DemoCopilot:
    """
    Main autonomous demo agent that orchestrates product demonstrations
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        headless: bool = False,
        voice_id: str = "Rachel"
    ):
        self.session_id = session_id or str(uuid.uuid4())

        # Initialize components
        self.browser = BrowserController(
            headless=headless,
            record_video=True,
            video_dir=f"./recordings/{self.session_id}"
        )

        self.voice = VoiceEngine(voice_id=voice_id)
        self.narrator = DemoNarrator(self.voice)
        self.question_handler = QuestionHandler()

        # Demo script (can be swapped)
        self.demo_script: Optional[InSignDemoScript] = None

        # State management
        self.state = DemoState.IDLE
        self.started_at: Optional[datetime] = None
        self.paused_at: Optional[datetime] = None
        self.pause_duration: float = 0.0

        # Customer info
        self.customer_name: Optional[str] = None
        self.customer_email: Optional[str] = None

        # Metrics
        self.questions_asked = 0
        self.pauses_count = 0

        # Callbacks for real-time updates
        self.on_state_change: Optional[Callable] = None
        self.on_progress_update: Optional[Callable] = None
        self.on_screenshot: Optional[Callable] = None
        self.on_audio: Optional[Callable] = None

        # Set up browser callbacks
        self.browser.on_screenshot = self._handle_screenshot
        self.browser.on_action = self._handle_browser_action

        # Set up voice callbacks
        self.voice.on_audio_chunk = self._handle_audio_chunk
        self.voice.on_speech_start = self._handle_speech_start
        self.voice.on_speech_end = self._handle_speech_end

    async def initialize(self, product: str = "insign", customer_name: Optional[str] = None):
        """
        Initialize demo for a specific product

        Args:
            product: Product to demo ("insign", "crew", etc.)
            customer_name: Optional customer name for personalization
        """
        logger.info(f"Initializing demo for product: {product}")

        self.customer_name = customer_name
        self.state = DemoState.STARTING

        # Start browser
        await self.browser.start()

        # Load demo script
        if product.lower() == "insign":
            self.demo_script = InSignDemoScript(self.browser, self.voice)
            self.question_handler.set_product_context(INSIGN_PRODUCT_CONTEXT)
        else:
            raise ValueError(f"Unknown product: {product}")

        logger.info("Demo initialized successfully")

    async def start_demo(self):
        """
        Start the full demo presentation

        Returns:
            Demo session info
        """
        if not self.demo_script:
            raise ValueError("Demo not initialized. Call initialize() first.")

        logger.info(f"Starting demo session: {self.session_id}")

        self.state = DemoState.RUNNING
        self.started_at = datetime.now()

        await self._emit_state_change()

        try:
            # Run the full demo script
            await self.demo_script.run_full_demo(customer_name=self.customer_name)

            self.state = DemoState.COMPLETED
            await self._emit_state_change()

            logger.info("Demo completed successfully")

            return {
                "session_id": self.session_id,
                "status": "completed",
                "duration_seconds": self._get_duration(),
                "questions_asked": self.questions_asked,
                "pauses_count": self.pauses_count
            }

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            self.state = DemoState.FAILED
            await self._emit_state_change()
            raise

    async def pause_demo(self):
        """Pause the demo"""
        if self.state != DemoState.RUNNING:
            logger.warning("Cannot pause - demo not running")
            return

        logger.info("Pausing demo")

        self.state = DemoState.PAUSED
        self.paused_at = datetime.now()
        self.pauses_count += 1

        await self._emit_state_change()

        await self.narrator.pause_for_question()

    async def resume_demo(self):
        """Resume the demo from pause"""
        if self.state != DemoState.PAUSED:
            logger.warning("Cannot resume - demo not paused")
            return

        logger.info("Resuming demo")

        # Track pause duration
        if self.paused_at:
            self.pause_duration += (datetime.now() - self.paused_at).total_seconds()

        self.state = DemoState.RUNNING
        self.paused_at = None

        await self._emit_state_change()

        await self.voice.speak("Let's continue with the demonstration.", stream=False)

    async def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Ask a question during the demo

        Args:
            question: Customer's question

        Returns:
            Answer and metadata
        """
        logger.info(f"Customer question: {question}")

        previous_state = self.state
        self.state = DemoState.ANSWERING_QUESTION
        self.questions_asked += 1

        await self._emit_state_change()

        # Update question handler with current demo context
        if self.demo_script:
            self.question_handler.set_demo_context(
                self.demo_script.get_current_progress()
            )

        # Get answer from Claude
        result = await self.question_handler.answer_question(question)

        # Speak the answer
        await self.narrator.answer_question(result["answer"])

        # Resume previous state
        self.state = previous_state
        await self._emit_state_change()

        return result

    async def skip_to_section(self, section_name: str):
        """Skip to a specific demo section"""
        if not self.demo_script:
            raise ValueError("Demo not initialized")

        logger.info(f"Skipping to section: {section_name}")

        await self.demo_script.skip_to_section(section_name)

        await self._emit_progress_update()

    async def stop_demo(self):
        """Stop and cleanup demo"""
        logger.info("Stopping demo")

        self.state = DemoState.IDLE

        # Cleanup
        await self.browser.stop()

        logger.info("Demo stopped and cleaned up")

    def get_status(self) -> Dict[str, Any]:
        """Get current demo status"""
        status = {
            "session_id": self.session_id,
            "state": self.state,
            "duration_seconds": self._get_duration(),
            "questions_asked": self.questions_asked,
            "pauses_count": self.pauses_count,
            "customer_name": self.customer_name
        }

        if self.demo_script:
            status["progress"] = self.demo_script.get_current_progress()

        return status

    def _get_duration(self) -> int:
        """Get demo duration in seconds"""
        if not self.started_at:
            return 0

        end_time = datetime.now()
        total_seconds = (end_time - self.started_at).total_seconds()

        # Subtract pause duration
        return int(total_seconds - self.pause_duration)

    async def _handle_screenshot(self, screenshot_b64: str):
        """Handle screenshot from browser"""
        if self.on_screenshot:
            await self.on_screenshot(screenshot_b64)

    async def _handle_browser_action(self, action: Dict[str, Any]):
        """Handle browser action"""
        logger.debug(f"Browser action: {action['type']}")
        await self._emit_progress_update()

    async def _handle_audio_chunk(self, audio_chunk: bytes):
        """Handle audio chunk from voice engine"""
        if self.on_audio:
            await self.on_audio(audio_chunk)

    async def _handle_speech_start(self, text: str):
        """Handle speech start"""
        logger.debug(f"Speaking: {text[:50]}...")

    async def _handle_speech_end(self, text: str):
        """Handle speech end"""
        logger.debug("Speech completed")

    async def _emit_state_change(self):
        """Emit state change event"""
        if self.on_state_change:
            await self.on_state_change(self.state)

    async def _emit_progress_update(self):
        """Emit progress update event"""
        if self.on_progress_update:
            status = self.get_status()
            await self.on_progress_update(status)


# Example usage
async def demo_example():
    """Example of running a complete demo"""
    copilot = DemoCopilot(
        headless=False,
        voice_id="Rachel"
    )

    # Set up callbacks
    async def on_state_change(state):
        print(f"State changed: {state}")

    async def on_progress(status):
        progress = status.get("progress", {})
        print(f"Progress: {progress.get('progress_percentage', 0):.0f}%")

    copilot.on_state_change = on_state_change
    copilot.on_progress_update = on_progress

    try:
        # Initialize for InSign demo
        await copilot.initialize(product="insign", customer_name="Sarah")

        # Start the demo
        result = await copilot.start_demo()

        print(f"\nDemo completed!")
        print(f"Duration: {result['duration_seconds']}s")
        print(f"Questions: {result['questions_asked']}")

    except Exception as e:
        print(f"Demo failed: {e}")

    finally:
        await copilot.stop_demo()


if __name__ == "__main__":
    asyncio.run(demo_example())
