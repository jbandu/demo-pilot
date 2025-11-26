import asyncio
import os
import hashlib
from typing import Optional, Dict, Any
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from openai import AsyncOpenAI
import io
import logging
import tempfile
import subprocess
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

        # Initialize ElevenLabs client (optional - demos can run without voice)
        self.elevenlabs_client = None
        if self.elevenlabs_api_key:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)
                logger.info("ElevenLabs voice engine initialized")
            except Exception as e:
                logger.warning(f"Could not initialize ElevenLabs: {e}")
                logger.warning("Demos will run without voice narration")
        else:
            logger.warning("ELEVENLABS_API_KEY not set - demos will run without voice")

        # Voice configuration - use custom voice from environment, or default to Rachel
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
        # Default: "EXAVITQu4vr4xnSDxMaL" - Rachel (professional female)
        # Alternative built-in voices:
        # "pNInz6obpgDQGcFmaJgB" - Adam (professional male)
        # "21m00Tcm4TlvDq8ikWAM" - Antoni (calm, narration)
        # Or use your custom cloned voice ID from ElevenLabs

        self.voice_settings = VoiceSettings(
            stability=0.5,  # 0-1: Lower = more expressive, Higher = more stable
            similarity_boost=0.75,  # 0-1: How closely to match the voice
            style=0.5,  # 0-1: Exaggeration of the style
            use_speaker_boost=True
        )

        # Audio cache (in-memory)
        self.audio_cache: Dict[str, bytes] = {}

        # Persistent cache directory (on disk - survives server restarts)
        self.cache_dir = Path(os.getenv("AUDIO_CACHE_DIR", "./audio_cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Audio cache directory: {self.cache_dir}")

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

        # Skip if ElevenLabs is not available
        if not self.elevenlabs_client:
            logger.info("Voice generation skipped (ElevenLabs not available)")
            return b""

        try:
            # Create cache key from text hash
            cache_key = f"{self.voice_id}:{text}"
            text_hash = hashlib.md5(cache_key.encode()).hexdigest()
            cache_file = self.cache_dir / f"{text_hash}.mp3"

            # Check in-memory cache first
            if cache_key in self.audio_cache:
                logger.info("Using in-memory cached audio")
                return self.audio_cache[cache_key]

            # Check persistent disk cache
            if cache_file.exists():
                logger.info(f"Using disk-cached audio from {cache_file.name}")
                audio_bytes = cache_file.read_bytes()
                # Also populate in-memory cache for faster access
                self.audio_cache[cache_key] = audio_bytes
                return audio_bytes

            # Generate full audio (better quality) using new client API
            logger.info("Generating new audio via ElevenLabs API...")
            audio_generator = self.elevenlabs_client.generate(
                text=text,
                voice=self.voice_id,
                model="eleven_multilingual_v2",  # Best quality
                voice_settings=self.voice_settings
            )

            # Collect all audio chunks into bytes
            audio_bytes = b"".join(audio_generator)

            # Cache the audio (both in-memory and on disk)
            self.audio_cache[cache_key] = audio_bytes
            cache_file.write_bytes(audio_bytes)
            logger.info(f"Audio cached to {cache_file.name}")

            # Save to file if requested
            if save_path:
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(audio_bytes)
                logger.info(f"Audio saved to: {save_path}")

            return audio_bytes

        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            logger.warning("Continuing without voice generation...")
            return b""  # Return empty bytes instead of crashing

    async def text_to_speech_stream(self, text: str):
        """
        Stream text-to-speech audio in real-time for lower latency.

        Args:
            text: Text to convert to speech

        Yields:
            Audio chunks as they are generated
        """
        logger.info(f"Streaming speech for: {text[:50]}...")

        # Skip if ElevenLabs is not available
        if not self.elevenlabs_client:
            logger.info("Voice streaming skipped (ElevenLabs not available)")
            yield b""
            return

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
            logger.warning("Voice streaming failed, continuing without audio...")
            yield b""  # Yield empty bytes instead of crashing

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

        # Calculate REAL duration from audio file using pydub
        duration_ms = 0
        if audio_bytes:
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
                duration_ms = len(audio)  # Actual duration in milliseconds
                logger.debug(f"Actual audio duration: {duration_ms}ms ({duration_ms/1000:.1f}s)")
            except Exception as e:
                logger.warning(f"Could not determine audio duration, estimating: {e}")
                # Fallback: estimate based on word count
                word_count = len(text.split())
                duration_ms = int((word_count / 150) * 60 * 1000)
                logger.debug(f"Estimated audio duration: {duration_ms}ms ({duration_ms/1000:.1f}s)")

        # Play audio locally if enabled (for testing/development)
        if audio_bytes and os.getenv("PLAY_AUDIO_LOCALLY", "false").lower() in ("true", "1", "yes"):
            await self._play_audio_locally(audio_bytes)

        return {
            "audio_bytes": audio_bytes,
            "duration_ms": duration_ms,
            "file_path": save_path,
            "text": text
        }

    async def _play_audio_locally(self, audio_bytes: bytes):
        """
        Play audio on the local machine (for development/testing).
        Requires mpg123, ffplay, or similar installed.

        IMPORTANT: This method BLOCKS until audio finishes playing to prevent overlapping audio.
        """
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            # Try different audio players
            players = ['mpg123', 'ffplay', 'mpv', 'vlc']
            player_found = False

            for player in players:
                try:
                    logger.info(f"Playing audio using {player}")

                    if player == 'ffplay':
                        # ffplay needs -nodisp -autoexit flags
                        result = await asyncio.create_subprocess_exec(
                            player, '-nodisp', '-autoexit', temp_path,
                            stdout=asyncio.subprocess.DEVNULL,
                            stderr=asyncio.subprocess.DEVNULL
                        )
                    else:
                        # Run audio player and WAIT for it to finish (blocks until done)
                        result = await asyncio.create_subprocess_exec(
                            player, temp_path,
                            stdout=asyncio.subprocess.DEVNULL,
                            stderr=asyncio.subprocess.DEVNULL
                        )

                    # CRITICAL: Wait for audio to finish playing before continuing
                    await result.wait()
                    player_found = True
                    logger.info(f"Audio playback completed with {player}")
                    break

                except FileNotFoundError:
                    continue

            if not player_found:
                logger.warning("No audio player found. Install mpg123, ffplay, mpv, or vlc to play audio locally.")

            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

        except Exception as e:
            logger.error(f"Error playing audio locally: {e}")

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
        # Estimate audio duration for pacing (will be refined once generated)
        word_count = len(narration.split())
        estimated_duration_ms = int((word_count / 150) * 60 * 1000)

        # Start both tasks in parallel
        audio_task = asyncio.create_task(
            self.voice_engine.narrate_and_wait(narration)
        )

        # Smart delay: give audio time to start, but scale with narration length
        # Shorter narration = shorter delay, longer narration = longer delay (max 2s)
        start_delay = min(word_count * 0.05, 2.0)  # 50ms per word, max 2 seconds
        logger.debug(f"Starting browser actions after {start_delay:.2f}s delay")
        await asyncio.sleep(start_delay)

        # Start browser actions with estimated duration (will adjust on the fly)
        action_task = asyncio.create_task(
            self._execute_browser_actions(
                browser_actions,
                browser_controller,
                audio_duration_ms=estimated_duration_ms
            )
        )

        # Wait for both to complete
        audio_result, _ = await asyncio.gather(audio_task, action_task)

        # Log actual vs estimated duration for tuning
        actual_duration_ms = audio_result.get('duration_ms', 0)
        if actual_duration_ms > 0:
            diff_ms = abs(actual_duration_ms - estimated_duration_ms)
            logger.debug(
                f"Audio duration: estimated={estimated_duration_ms}ms, "
                f"actual={actual_duration_ms}ms, diff={diff_ms}ms"
            )

        return audio_result

    async def _execute_browser_actions(
        self,
        actions: list,
        browser_controller,
        audio_duration_ms: int = 0
    ) -> None:
        """
        Execute list of browser actions sequentially, paced across audio duration.

        Args:
            actions: List of browser actions
            browser_controller: BrowserController instance
            audio_duration_ms: Duration of narration audio to pace actions across
        """
        logger.info(f"Executing {len(actions)} browser actions...")

        # Calculate time budget per action to stay in sync with audio
        if audio_duration_ms > 0 and len(actions) > 0:
            # Reserve 20% of time for action execution, 80% for pacing delays
            action_budget_ms = audio_duration_ms * 0.8
            time_per_action_ms = action_budget_ms / len(actions)
            logger.debug(f"Pacing actions: {time_per_action_ms:.0f}ms per action")
        else:
            time_per_action_ms = 500  # Default 500ms if no audio duration

        for i, action in enumerate(actions):
            action_type = action.get('type')
            logger.debug(f"Action {i+1}/{len(actions)}: {action_type}")

            action_start_time = asyncio.get_event_loop().time()

            try:
                if action_type == 'click':
                    await browser_controller.click(action['selector'])
                elif action_type == 'type':
                    await browser_controller.type_text(action['selector'], action['text'])
                elif action_type == 'navigate':
                    await browser_controller.navigate(action['url'])
                elif action_type == 'upload':
                    await browser_controller.upload_file(action['selector'], action['file_path'])
                elif action_type == 'wait':
                    # Wait actions respect their own duration
                    await asyncio.sleep(action.get('duration', 1))
                elif action_type == 'highlight':
                    # Use highlight_element with duration parameter
                    duration_ms = action.get('duration', 1000)
                    await browser_controller.highlight_element(
                        action['selector'],
                        duration_ms=duration_ms
                    )
                elif action_type == 'scroll':
                    # Handle scroll - can be to selector or direction
                    if 'selector' in action:
                        await browser_controller.smooth_scroll_to(action['selector'])
                    else:
                        direction = action.get('direction', 'down')
                        pixels = action.get('pixels', 500)
                        await browser_controller.scroll(direction, pixels)
                else:
                    logger.warning(f"Unknown action type: {action_type}")

                # Calculate remaining time in action budget and sleep to maintain pace
                action_elapsed_ms = (asyncio.get_event_loop().time() - action_start_time) * 1000

                # Use action's custom delay if specified, otherwise use pacing delay
                if 'delay' in action:
                    pace_delay_ms = action['delay'] * 1000
                else:
                    pace_delay_ms = max(0, time_per_action_ms - action_elapsed_ms)

                if pace_delay_ms > 0:
                    await asyncio.sleep(pace_delay_ms / 1000)

            except Exception as e:
                logger.error(f"Error executing browser action {action_type}: {e}", exc_info=True)
                # Continue with next action instead of failing completely
                continue


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
