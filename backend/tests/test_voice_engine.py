import pytest
from unittest.mock import Mock, patch, AsyncMock
from agents.voice_engine import VoiceEngine


@pytest.fixture
def voice_engine():
    """Create VoiceEngine instance"""
    return VoiceEngine()


@pytest.mark.asyncio
@patch('agents.voice_engine.generate')
async def test_text_to_speech(mock_generate, voice_engine):
    """Test text-to-speech generation"""
    mock_generate.return_value = b"fake_audio_data"

    audio = await voice_engine.text_to_speech("Hello world")

    assert audio is not None
    assert len(audio) > 0
    mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_narrate_and_wait(voice_engine):
    """Test narrate_and_wait returns correct structure"""
    with patch.object(voice_engine, 'text_to_speech', return_value=b"fake_audio"):
        result = await voice_engine.narrate_and_wait("Test narration")

        assert 'audio_bytes' in result
        assert 'duration_ms' in result
        assert 'text' in result
        assert result['text'] == "Test narration"


def test_get_available_voices(voice_engine):
    """Test getting available voices"""
    with patch('agents.voice_engine.voices') as mock_voices:
        mock_voices.return_value = [
            Mock(voice_id="voice1", name="Voice 1", category="premade"),
            Mock(voice_id="voice2", name="Voice 2", category="premade"),
        ]

        voices = voice_engine.get_available_voices()

        assert len(voices) == 2
        assert voices[0]['name'] == "Voice 1"


def test_set_voice(voice_engine):
    """Test changing voice"""
    original_voice = voice_engine.voice_id
    voice_engine.set_voice("new_voice_id")

    assert voice_engine.voice_id == "new_voice_id"
    assert voice_engine.voice_id != original_voice
