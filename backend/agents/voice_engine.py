"""
Voice Engine - Text-to-speech using ElevenLabs
Handles narration generation and audio streaming for demos
"""
import asyncio
import os
from typing import Optional, Callable, List
from datetime import datetime
import logging
from io import BytesIO

try:
    from elevenlabs import VoiceSettings
    from elevenlabs.client import ElevenLabs
except ImportError:
    logging.warning("ElevenLabs not installed. Install with: pip install elevenlabs")

logger = logging.getLogger(__name__)


class VoiceEngine:
    """
    Manages text-to-speech for demo narration using ElevenLabs
    """

    # Popular ElevenLabs voices for demos
    VOICES = {
        "Rachel": "21m00Tcm4TlvDq8ikWAM",  # Professional, friendly
        "Adam": "pNInz6obpgDQGcFmaJgB",    # Deep, authoritative
        "Bella": "EXAVITQu4vr4xnSDxMaL",   # Warm, conversational
        "Antoni": "ErXwobaYiN019PkySvjV",  # Well-rounded, versatile
        "Elli": "MF3mGyEYCl7XYWbV9V6O",    # Energetic, young
        "Josh": "TxGEqnHWrfWFTfGW9XjX",    # Natural, casual
        "Arnold": "VR6AewLTigWG4xSOukaG",  # Crisp, clear
        "Domi": "AZnzlk1XvdvUeBnXmlld",    # Strong, confident
        "Sam": "yoZ06aMxZJJ28mfd3POQ"      # Dynamic, raspy
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: str = "Rachel",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")

        if not self.api_key:
            raise ValueError("ElevenLabs API key required")

        self.client = ElevenLabs(api_key=self.api_key)

        # Voice configuration
        self.voice_id = self.VOICES.get(voice_id, voice_id)
        self.voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost
        )

        # Callbacks
        self.on_audio_chunk: Optional[Callable] = None
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None

        # Tracking
        self.narration_log: List[dict] = []

    async def speak(self, text: str, stream: bool = True) -> Optional[bytes]:
        """
        Convert text to speech

        Args:
            text: Text to convert to speech
            stream: If True, streams audio chunks; if False, returns full audio

        Returns:
            Audio bytes if stream=False, else None
        """
        logger.info(f"Speaking: {text[:50]}...")

        # Log narration
        self.narration_log.append({
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "voice_id": self.voice_id
        })

        if self.on_speech_start:
            await self.on_speech_start(text)

        try:
            if stream:
                # Stream audio chunks
                audio_stream = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=self.voice_id,
                    model_id="eleven_turbo_v2_5",  # Fastest model
                    output_format="mp3_44100_128",
                    voice_settings=self.voice_settings
                )

                for chunk in audio_stream:
                    if self.on_audio_chunk:
                        await self.on_audio_chunk(chunk)

                if self.on_speech_end:
                    await self.on_speech_end(text)

                return None

            else:
                # Get full audio
                audio = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=self.voice_id,
                    model_id="eleven_turbo_v2_5",
                    output_format="mp3_44100_128",
                    voice_settings=self.voice_settings
                )

                # Convert generator to bytes
                audio_bytes = b"".join(chunk for chunk in audio)

                if self.on_speech_end:
                    await self.on_speech_end(text)

                return audio_bytes

        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            raise

    async def speak_with_timing(
        self,
        text: str,
        pre_delay: float = 0.0,
        post_delay: float = 0.5
    ) -> bytes:
        """
        Speak text with timing delays

        Args:
            text: Text to speak
            pre_delay: Seconds to wait before speaking
            post_delay: Seconds to wait after speaking

        Returns:
            Audio bytes
        """
        if pre_delay > 0:
            await asyncio.sleep(pre_delay)

        audio = await self.speak(text, stream=False)

        if post_delay > 0:
            await asyncio.sleep(post_delay)

        return audio

    async def narrate_action(self, action_description: str) -> bytes:
        """
        Narrate a demo action naturally

        Args:
            action_description: Description of the action being performed

        Returns:
            Audio bytes
        """
        # Add natural speech patterns
        narration = f"{action_description}"

        return await self.speak(narration, stream=False)

    def get_narration_log(self) -> List[dict]:
        """Get all narrations"""
        return self.narration_log

    def clear_narration_log(self):
        """Clear narration history"""
        self.narration_log = []

    async def list_voices(self) -> List[dict]:
        """Get available voices from ElevenLabs"""
        try:
            voices = self.client.voices.get_all()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category
                }
                for voice in voices.voices
            ]
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []

    def set_voice(self, voice_name_or_id: str):
        """Change the voice"""
        if voice_name_or_id in self.VOICES:
            self.voice_id = self.VOICES[voice_name_or_id]
            logger.info(f"Voice set to: {voice_name_or_id}")
        else:
            self.voice_id = voice_name_or_id
            logger.info(f"Voice set to custom ID: {voice_name_or_id}")

    def adjust_voice_settings(
        self,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None,
        style: Optional[float] = None
    ):
        """Adjust voice characteristics"""
        if stability is not None:
            self.voice_settings.stability = stability

        if similarity_boost is not None:
            self.voice_settings.similarity_boost = similarity_boost

        if style is not None:
            self.voice_settings.style = style

        logger.info(f"Voice settings updated: stability={self.voice_settings.stability}, "
                   f"similarity={self.voice_settings.similarity_boost}")


class DemoNarrator:
    """
    High-level narrator for demos with pre-defined phrases
    """

    def __init__(self, voice_engine: VoiceEngine):
        self.voice = voice_engine

    async def greet(self, customer_name: Optional[str] = None):
        """Opening greeting"""
        if customer_name:
            text = f"Hello {customer_name}! Welcome to this live product demonstration. " \
                   f"I'm your AI demo assistant, and I'll be walking you through the key features today."
        else:
            text = "Hello! Welcome to this live product demonstration. " \
                   "I'm your AI demo assistant, and I'll be walking you through the key features today."

        return await self.voice.speak(text, stream=False)

    async def introduce_section(self, section_name: str):
        """Introduce a new demo section"""
        text = f"Now, let's take a look at {section_name}."
        return await self.voice.speak(text, stream=False)

    async def explain_feature(self, feature_description: str):
        """Explain a feature"""
        return await self.voice.speak(feature_description, stream=False)

    async def pause_for_question(self):
        """Indicate readiness for questions"""
        text = "I'm pausing here if you have any questions about what we just covered."
        return await self.voice.speak(text, stream=False)

    async def answer_question(self, answer: str):
        """Answer a customer question"""
        text = f"Great question. {answer}"
        return await self.voice.speak(text, stream=False)

    async def conclude(self):
        """Closing remarks"""
        text = "That concludes our demonstration today. Thank you for your time! " \
               "Feel free to reach out if you have any additional questions."
        return await self.voice.speak(text, stream=False)


# Example usage
async def demo_example():
    """Example of voice engine usage"""
    voice = VoiceEngine(voice_id="Rachel")
    narrator = DemoNarrator(voice)

    # Test speech
    await narrator.greet("John")
    await voice.speak("This is a test of the voice engine.")


if __name__ == "__main__":
    asyncio.run(demo_example())
