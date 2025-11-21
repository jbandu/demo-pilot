import asyncio
import os
from typing import Optional, Dict, Any
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from openai import AsyncOpenAI
import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VoiceEngine:
    """
    Handles all voice operations for Demo Copilot:
    - Text-to-speech (TTS) using ElevenLabs
    - Speech-to-text (STT) using OpenAI Whisper
    - Voice streaming for real-time narration
    """

    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize ElevenLabs client
        self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)

        # Voice configuration
        self.voice_id = "EXAVITQu4vr4xnSDxMaL"  # Rachel (professional female)
        # Alternative voices:
        # "pNInz6obpgDQGcFmaJgB" - Adam (professional male)
        # "21m00Tcm4TlvDq8ikWAM" - Antoni (calm, narration)

        self.voice_settings = VoiceSettings(
            stability=0.5,  # 0-1: Lower = more expressive, Higher = more stable
            similarity_boost=0.75,  # 0-1: How closely to match the voice
            style=0.5,  # 0-1: Exaggeration of the style
            use_speaker_boost=True
        )

        # Audio cache
        self.audio_cache: Dict[str, bytes] = {}

    async def text_to_speech(
        self,
        text: str,
        save_path: Optional[str] = None
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs.

        Args:
            text: Text to convert to speech
            save_path: Optional path to save audio file

        Returns:
            Audio bytes
        """
        logger.info(f"Generating speech for: {text[:50]}...")

        try:
            # Check cache first
            cache_key = f"{self.voice_id}:{text}"
            if cache_key in self.audio_cache:
                logger.info("Using cached audio")
                return self.audio_cache[cache_key]

            # Generate full audio (better quality) using new client API
            audio_generator = self.elevenlabs_client.generate(
                text=text,
                voice=self.voice_id,
                model="eleven_multilingual_v2",  # Best quality
                voice_settings=self.voice_settings
            )

            # Collect all audio chunks into bytes
            audio_bytes = b"".join(audio_generator)

            # Cache the audio
            self.audio_cache[cache_key] = audio_bytes

            # Save to file if requested
            if save_path:
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(audio_bytes)
                logger.info(f"Audio saved to: {save_path}")

            return audio_bytes

        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise

    async def text_to_speech_stream(self, text: str):
        """
        Stream text-to-speech audio in real-time for lower latency.

        Args:
            text: Text to convert to speech

        Yields:
            Audio chunks as they are generated
        """
        logger.info(f"Streaming speech for: {text[:50]}...")

        try:
            # Stream audio in real-time (lower latency) using new client API
            audio_stream = self.elevenlabs_client.generate(
                text=text,
                voice=self.voice_id,
                model="eleven_turbo_v2",  # Fastest model
                stream=True,
                voice_settings=self.voice_settings
            )

            # Stream chunks to websocket or audio player
            for chunk in audio_stream:
                yield chunk

        except Exception as e:
            logger.error(f"Error streaming speech: {e}")
            raise

    async def speech_to_text(
        self,
        audio_file_path: Optional[str] = None,
        audio_bytes: Optional[bytes] = None
    ) -> str:
        """
        Convert speech to text using OpenAI Whisper.

        Args:
            audio_file_path: Path to audio file
            audio_bytes: Raw audio bytes

        Returns:
            Transcribed text
        """
        logger.info("Transcribing audio...")

        try:
            if audio_file_path:
                with open(audio_file_path, 'rb') as audio_file:
                    transcript = await self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"
                    )
            elif audio_bytes:
                # Create file-like object from bytes
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "audio.wav"

                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            else:
                raise ValueError("Must provide either audio_file_path or audio_bytes")

            text = transcript.text
            logger.info(f"Transcribed: {text}")
            return text

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    async def narrate_and_wait(self, text: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate speech and return audio info (duration, file path, etc).
        Used for synchronizing narration with browser actions.

        Returns:
            Dict with audio_bytes, duration_ms, file_path
        """
        audio_bytes = await self.text_to_speech(text, save_path=save_path)

        # Calculate duration (approximate)
        # Average speaking rate: ~150 words per minute
        word_count = len(text.split())
        duration_ms = int((word_count / 150) * 60 * 1000)

        return {
            "audio_bytes": audio_bytes,
            "duration_ms": duration_ms,
            "file_path": save_path,
            "text": text
        }

    def get_available_voices(self) -> list:
        """Get list of available ElevenLabs voices"""
        try:
            # Use new client API to get voices
            available_voices = self.elevenlabs_client.voices.get_all()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', ''),
                    "description": getattr(voice, 'description', '')
                }
                for voice in available_voices.voices
            ]
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return []

    def set_voice(self, voice_id: str) -> None:
        """Change the voice for narration"""
        self.voice_id = voice_id
        logger.info(f"Voice changed to: {voice_id}")

    def clear_cache(self) -> None:
        """Clear audio cache"""
        self.audio_cache.clear()
        logger.info("Audio cache cleared")


class AudioSynchronizer:
    """
    Synchronizes audio narration with browser actions.
    Ensures voice and screen stay perfectly in sync.
    """

    def __init__(self, voice_engine: VoiceEngine):
        self.voice_engine = voice_engine
        self.current_audio_task: Optional[asyncio.Task] = None

    async def sync_narrate_and_act(
        self,
        narration: str,
        browser_actions: list,
        browser_controller
    ) -> None:
        """
        Run narration and browser actions in parallel, synchronized.

        Args:
            narration: Text to narrate
            browser_actions: List of browser actions to perform
            browser_controller: BrowserController instance
        """
        # Start narration
        audio_task = asyncio.create_task(
            self.voice_engine.narrate_and_wait(narration)
        )

        # Start browser actions after brief delay (let narration start first)
        await asyncio.sleep(0.5)

        action_task = asyncio.create_task(
            self._execute_browser_actions(browser_actions, browser_controller)
        )

        # Wait for both to complete
        audio_result, _ = await asyncio.gather(audio_task, action_task)

        return audio_result

    async def _execute_browser_actions(self, actions: list, browser_controller) -> None:
        """Execute list of browser actions sequentially"""
        for action in actions:
            action_type = action.get('type')

            if action_type == 'click':
                await browser_controller.click(action['selector'])
            elif action_type == 'type':
                await browser_controller.type_text(action['selector'], action['text'])
            elif action_type == 'navigate':
                await browser_controller.navigate(action['url'])
            elif action_type == 'upload':
                await browser_controller.upload_file(action['selector'], action['file_path'])
            elif action_type == 'wait':
                await asyncio.sleep(action.get('duration', 1))
            elif action_type == 'highlight':
                await browser_controller.highlight(action['selector'])
            elif action_type == 'scroll':
                await browser_controller.scroll_to(action['selector'])

            # Brief pause between actions
            await asyncio.sleep(action.get('delay', 0.5))


# Example usage
if __name__ == "__main__":
    async def test_voice():
        engine = VoiceEngine()

        # Test TTS
        text = "Hello! I'm Demo Copilot, your AI sales engineer. Let me show you InSign."
        audio = await engine.text_to_speech(text, save_path="./test_audio.mp3")
        print(f"Generated audio: {len(audio)} bytes")

        # List available voices
        voices_list = engine.get_available_voices()
        print(f"\nAvailable voices: {len(voices_list)}")
        for v in voices_list[:5]:
            print(f"  - {v['name']} ({v['voice_id']})")

    asyncio.run(test_voice())
