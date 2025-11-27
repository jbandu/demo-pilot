import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from agents.voice_engine import VoiceEngine


@pytest.fixture
def mock_elevenlabs_client():
    """Create a mock ElevenLabs client"""
    mock_client = Mock()
    # Mock the generate method to return an iterator of audio chunks
    mock_client.generate.return_value = iter([b"fake", b"_audio", b"_data"])

    # Mock voices.get_all() with proper attribute values
    mock_voice1 = Mock()
    mock_voice1.voice_id = "voice1"
    mock_voice1.name = "Voice 1"
    mock_voice1.category = "premade"
    mock_voice1.description = "Test voice 1"

    mock_voice2 = Mock()
    mock_voice2.voice_id = "voice2"
    mock_voice2.name = "Voice 2"
    mock_voice2.category = "premade"
    mock_voice2.description = "Test voice 2"

    mock_voices_response = Mock()
    mock_voices_response.voices = [mock_voice1, mock_voice2]
    mock_client.voices.get_all.return_value = mock_voices_response
    return mock_client


@pytest.fixture
def voice_engine(mock_elevenlabs_client):
    """Create VoiceEngine instance with mocked ElevenLabs and OpenAI clients"""
    with patch(
        "agents.voice_engine.ElevenLabs", return_value=mock_elevenlabs_client
    ), patch("agents.voice_engine.AsyncOpenAI") as mock_openai, patch.dict(
        "os.environ", {"ELEVENLABS_API_KEY": "test_key", "OPENAI_API_KEY": "test_key"}
    ):
        engine = VoiceEngine()
        return engine


@pytest.mark.asyncio
async def test_text_to_speech(voice_engine):
    """Test text-to-speech generation"""
    audio = await voice_engine.text_to_speech("Hello world")

    assert audio is not None
    assert len(audio) > 0
    assert audio == b"fake_audio_data"
    # Verify the client's generate method was called
    voice_engine.elevenlabs_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_text_to_speech_caching(voice_engine):
    """Test that audio is cached properly"""
    # First call should generate audio
    audio1 = await voice_engine.text_to_speech("Hello world")

    # Reset mock to check if it's called again
    voice_engine.elevenlabs_client.generate.reset_mock()

    # Second call with same text should use cache
    audio2 = await voice_engine.text_to_speech("Hello world")

    assert audio1 == audio2
    # Generate should not be called second time (used cache)
    voice_engine.elevenlabs_client.generate.assert_not_called()


@pytest.mark.asyncio
async def test_narrate_and_wait(voice_engine):
    """Test narrate_and_wait returns correct structure"""
    with patch.object(voice_engine, "text_to_speech", return_value=b"fake_audio"):
        result = await voice_engine.narrate_and_wait("Test narration")

        assert "audio_bytes" in result
        assert "duration_ms" in result
        assert "text" in result
        assert result["text"] == "Test narration"
        assert result["audio_bytes"] == b"fake_audio"


def test_get_available_voices(voice_engine):
    """Test getting available voices"""
    voices = voice_engine.get_available_voices()

    assert len(voices) == 2
    assert voices[0]["name"] == "Voice 1"
    assert voices[0]["voice_id"] == "voice1"
    assert voices[1]["name"] == "Voice 2"
    # Verify the client method was called
    voice_engine.elevenlabs_client.voices.get_all.assert_called_once()


def test_set_voice(voice_engine):
    """Test changing voice"""
    original_voice = voice_engine.voice_id
    voice_engine.set_voice("new_voice_id")

    assert voice_engine.voice_id == "new_voice_id"
    assert voice_engine.voice_id != original_voice


def test_clear_cache(voice_engine):
    """Test clearing audio cache"""
    # Add something to cache
    voice_engine.audio_cache["test_key"] = b"test_data"
    assert len(voice_engine.audio_cache) > 0

    # Clear cache
    voice_engine.clear_cache()

    assert len(voice_engine.audio_cache) == 0
