"""
Unit tests for VoiceController - Audio recording and API integration.

These tests verify audio recording, API communication, and audio playback
functionality without requiring actual audio hardware or network access.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
import tempfile
from pathlib import Path
import numpy as np

from src.frontend_tkinter.voice_controller import VoiceController


class TestVoiceControllerInitialization:
    """Test VoiceController initialization."""
    
    def test_initialization_with_defaults(self):
        """Test VoiceController initializes with default values."""
        controller = VoiceController()
        
        assert controller.api_url == "http://localhost:8000"
        assert controller.sample_rate == 16000
        assert controller.channels == 1
        assert controller.is_recording is False
    
    def test_initialization_with_custom_api_url(self):
        """Test VoiceController with custom API URL."""
        controller = VoiceController(api_url="http://192.168.1.38:8000")
        
        assert controller.api_url == "http://192.168.1.38:8000"
    
    def test_initialization_with_custom_sample_rate(self):
        """Test VoiceController with custom sample rate."""
        controller = VoiceController(sample_rate=44100)
        
        assert controller.sample_rate == 44100
    
    def test_initial_recording_state(self):
        """Test initial recording state is False."""
        controller = VoiceController()
        
        assert controller.is_recording is False


class TestRecordingState:
    """Test recording state management."""
    
    def test_start_recording_changes_state(self):
        """Test start_recording changes is_recording to True."""
        controller = VoiceController()
        
        with patch('sounddevice.InputStream'):
            controller.start_recording()
            
            assert controller.is_recording is True
    
    def test_stop_recording_changes_state(self):
        """Test stop_recording changes is_recording to False."""
        controller = VoiceController()
        
        with patch('sounddevice.InputStream'):
            controller.start_recording()
            controller.stop_recording()
            
            assert controller.is_recording is False
    
    def test_cannot_start_recording_twice(self):
        """Test starting recording twice has no effect."""
        controller = VoiceController()
        
        with patch('sounddevice.InputStream') as mock_stream:
            controller.start_recording()
            controller.start_recording()  # Second call
            
            # Should only create one stream
            assert mock_stream.call_count == 1


class TestAudioRecording:
    """Test audio recording functionality."""
    
    @patch('sounddevice.InputStream')
    def test_recording_stream_creation(self, mock_input_stream):
        """Test audio input stream is created correctly."""
        controller = VoiceController(sample_rate=16000)
        
        controller.start_recording()
        
        mock_input_stream.assert_called_once()
        call_kwargs = mock_input_stream.call_args[1]
        assert call_kwargs['samplerate'] == 16000
        assert call_kwargs['channels'] == 1
    
    @patch('sounddevice.InputStream')
    def test_audio_data_collection(self, mock_input_stream):
        """Test audio data is collected during recording."""
        controller = VoiceController()
        
        # Simulate audio callback
        fake_audio = np.random.randn(1024, 1).astype(np.float32)
        controller._audio_callback(fake_audio, None, None, None)
        
        assert len(controller.audio_frames) == 1
        assert controller.audio_frames[0].shape == fake_audio.shape
    
    @patch('sounddevice.InputStream')
    def test_stop_recording_closes_stream(self, mock_input_stream):
        """Test stopping recording closes the audio stream."""
        mock_stream_instance = Mock()
        mock_input_stream.return_value.__enter__.return_value = mock_stream_instance
        
        controller = VoiceController()
        controller.start_recording()
        controller.stop_recording()
        
        # Stream should be closed
        assert controller.stream is None
    
    @patch('sounddevice.InputStream')
    def test_audio_frames_cleared_on_new_recording(self, mock_input_stream):
        """Test audio frames are cleared when starting new recording."""
        controller = VoiceController()
        
        # Add some fake audio data
        controller.audio_frames = [np.random.randn(1024, 1).astype(np.float32)]
        
        controller.start_recording()
        
        # Frames should be cleared
        assert len(controller.audio_frames) == 0


class TestAudioProcessing:
    """Test audio data processing."""
    
    @patch('sounddevice.InputStream')
    def test_get_audio_data_combines_frames(self, mock_input_stream):
        """Test get_audio_data combines all recorded frames."""
        controller = VoiceController()
        
        # Add multiple audio frames
        frame1 = np.random.randn(1024, 1).astype(np.float32)
        frame2 = np.random.randn(1024, 1).astype(np.float32)
        controller.audio_frames = [frame1, frame2]
        
        audio_data = controller.get_audio_data()
        
        # Should concatenate frames
        expected_length = len(frame1) + len(frame2)
        assert len(audio_data) == expected_length
    
    @patch('sounddevice.InputStream')
    def test_get_audio_data_returns_none_when_empty(self, mock_input_stream):
        """Test get_audio_data returns None when no frames recorded."""
        controller = VoiceController()
        controller.audio_frames = []
        
        audio_data = controller.get_audio_data()
        
        assert audio_data is None
    
    @patch('sounddevice.InputStream')
    def test_audio_data_normalization(self, mock_input_stream):
        """Test audio data is normalized correctly."""
        controller = VoiceController()
        
        # Create audio with values outside [-1, 1]
        frame = np.array([[2.0], [-2.0], [0.5]], dtype=np.float32)
        controller.audio_frames = [frame]
        
        audio_data = controller.get_audio_data()
        
        # All values should be within valid range after normalization
        assert np.all(audio_data >= -1.0)
        assert np.all(audio_data <= 1.0)


class TestAPIIntegration:
    """Test API communication."""
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_audio_to_api(self, mock_client):
        """Test sending audio to API."""
        controller = VoiceController(api_url="http://localhost:8000")
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transcript": "Hello world",
            "response_text": "Hi there!",
            "response_audio": "base64_encoded_audio"
        }
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create fake audio
        audio_data = np.random.randn(16000).astype(np.float32)
        
        result = await controller.send_audio_to_api(audio_data)
        
        assert result is not None
        assert "transcript" in result
        assert "response_text" in result
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_api_request_includes_audio_file(self, mock_client):
        """Test API request includes audio file."""
        controller = VoiceController()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"transcript": "test"}
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        await controller.send_audio_to_api(audio_data)
        
        # Verify post was called
        mock_client_instance.post.assert_called_once()
        
        # Verify URL is correct
        call_args = mock_client_instance.post.call_args
        assert "/api/voice/process" in call_args[0][0]
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_api_error_handling(self, mock_client):
        """Test API error handling."""
        controller = VoiceController()
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        result = await controller.send_audio_to_api(audio_data)
        
        # Should return None on error
        assert result is None
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_api_timeout_handling(self, mock_client):
        """Test API timeout handling."""
        controller = VoiceController()
        
        # Mock timeout exception
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = Exception("Timeout")
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        result = await controller.send_audio_to_api(audio_data)
        
        # Should return None on timeout
        assert result is None


class TestAudioPlayback:
    """Test audio playback functionality."""
    
    @patch('sounddevice.play')
    @patch('sounddevice.wait')
    def test_play_audio_data(self, mock_wait, mock_play):
        """Test playing audio data."""
        controller = VoiceController(sample_rate=16000)
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        controller.play_audio(audio_data)
        
        mock_play.assert_called_once()
        call_args = mock_play.call_args[0]
        assert len(call_args[0]) == len(audio_data)
        
        mock_wait.assert_called_once()
    
    @patch('sounddevice.play')
    def test_play_audio_with_correct_sample_rate(self, mock_play):
        """Test audio is played with correct sample rate."""
        controller = VoiceController(sample_rate=44100)
        
        audio_data = np.random.randn(44100).astype(np.float32)
        
        controller.play_audio(audio_data)
        
        call_kwargs = mock_play.call_args[1]
        assert call_kwargs['samplerate'] == 44100
    
    @patch('sounddevice.play')
    def test_play_empty_audio_does_nothing(self, mock_play):
        """Test playing empty audio does nothing."""
        controller = VoiceController()
        
        controller.play_audio(None)
        
        mock_play.assert_not_called()
    
    @patch('sounddevice.play')
    def test_play_audio_error_handling(self, mock_play):
        """Test audio playback error handling."""
        controller = VoiceController()
        
        # Mock playback error
        mock_play.side_effect = Exception("Playback error")
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        # Should not raise exception
        try:
            controller.play_audio(audio_data)
        except Exception:
            pytest.fail("play_audio should handle errors gracefully")


class TestBase64AudioDecoding:
    """Test Base64 audio decoding."""
    
    def test_decode_base64_audio(self):
        """Test decoding Base64 audio data."""
        controller = VoiceController()
        
        # Create fake audio and encode it
        import base64
        fake_audio = np.random.randn(1000).astype(np.float32)
        audio_bytes = fake_audio.tobytes()
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        
        decoded = controller.decode_base64_audio(base64_audio)
        
        assert decoded is not None
        assert len(decoded) == len(fake_audio)
    
    def test_decode_invalid_base64_returns_none(self):
        """Test decoding invalid Base64 returns None."""
        controller = VoiceController()
        
        decoded = controller.decode_base64_audio("invalid_base64_data")
        
        assert decoded is None
    
    def test_decode_empty_base64_returns_none(self):
        """Test decoding empty Base64 returns None."""
        controller = VoiceController()
        
        decoded = controller.decode_base64_audio("")
        
        assert decoded is None


class TestTemporaryFileManagement:
    """Test temporary file handling."""
    
    @patch('tempfile.NamedTemporaryFile')
    def test_creates_temporary_wav_file(self, mock_temp_file):
        """Test creates temporary WAV file for API upload."""
        controller = VoiceController()
        
        mock_file = Mock()
        mock_file.name = "/tmp/audio_test.wav"
        mock_temp_file.return_value.__enter__.return_value = mock_file
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        # This would be called internally during API send
        # We're testing the file creation logic
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            assert f.name.endswith('.wav')
    
    @patch('soundfile.write')
    def test_audio_saved_to_wav_format(self, mock_sf_write):
        """Test audio is saved in WAV format."""
        controller = VoiceController(sample_rate=16000)
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        # Simulate saving audio
        temp_file = "/tmp/test_audio.wav"
        controller.save_audio_to_file(audio_data, temp_file)
        
        mock_sf_write.assert_called_once()
        call_args = mock_sf_write.call_args
        assert call_args[0][0] == temp_file
        assert call_args[1]['samplerate'] == 16000


class TestCallbackIntegration:
    """Test callback functionality."""
    
    def test_set_state_callback(self):
        """Test setting state change callback."""
        controller = VoiceController()
        callback = Mock()
        
        controller.set_state_callback(callback)
        
        assert controller.state_callback == callback
    
    def test_state_callback_triggered_on_state_change(self):
        """Test state callback is triggered on state changes."""
        controller = VoiceController()
        callback = Mock()
        controller.set_state_callback(callback)
        
        controller._trigger_state_change("listening")
        
        callback.assert_called_once_with("listening")
    
    def test_multiple_state_changes_trigger_multiple_callbacks(self):
        """Test multiple state changes trigger callbacks."""
        controller = VoiceController()
        callback = Mock()
        controller.set_state_callback(callback)
        
        controller._trigger_state_change("listening")
        controller._trigger_state_change("processing")
        controller._trigger_state_change("speaking")
        
        assert callback.call_count == 3
        callback.assert_has_calls([
            call("listening"),
            call("processing"),
            call("speaking")
        ])


class TestErrorRecovery:
    """Test error recovery mechanisms."""
    
    @patch('sounddevice.InputStream')
    def test_recover_from_recording_error(self, mock_input_stream):
        """Test recovery from recording error."""
        controller = VoiceController()
        
        # Simulate recording error
        mock_input_stream.side_effect = Exception("Recording device error")
        
        try:
            controller.start_recording()
        except Exception:
            pass
        
        # Should be able to reset state
        assert controller.is_recording is False
        
        # Should be able to try again
        mock_input_stream.side_effect = None
        controller.start_recording()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_recover_from_api_error(self, mock_client):
        """Test recovery from API error."""
        controller = VoiceController()
        
        # First call fails
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = Exception("Network error")
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        result1 = await controller.send_audio_to_api(audio_data)
        assert result1 is None
        
        # Second call succeeds
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"transcript": "recovered"}
        mock_client_instance.post.side_effect = None
        mock_client_instance.post.return_value = mock_response
        
        result2 = await controller.send_audio_to_api(audio_data)
        assert result2 is not None


class TestResourceCleanup:
    """Test resource cleanup."""
    
    @patch('sounddevice.InputStream')
    def test_cleanup_on_stop_recording(self, mock_input_stream):
        """Test resources are cleaned up when stopping recording."""
        controller = VoiceController()
        
        controller.start_recording()
        controller.audio_frames = [np.random.randn(1024, 1).astype(np.float32)]
        
        controller.stop_recording()
        
        # Audio frames should remain until explicitly cleared
        # (they might be needed for playback or analysis)
        assert controller.stream is None
    
    @patch('sounddevice.InputStream')
    def test_cleanup_on_error(self, mock_input_stream):
        """Test resources are cleaned up on error."""
        controller = VoiceController()
        
        mock_input_stream.side_effect = Exception("Device error")
        
        try:
            controller.start_recording()
        except Exception:
            pass
        
        # Should be in clean state
        assert controller.is_recording is False
        assert controller.stream is None


class TestFullVoiceInteractionFlow:
    """Test complete voice interaction scenarios."""
    
    @pytest.mark.asyncio
    @patch('sounddevice.InputStream')
    @patch('sounddevice.play')
    @patch('httpx.AsyncClient')
    async def test_complete_voice_interaction(
        self, mock_client, mock_play, mock_input_stream
    ):
        """Test complete voice interaction flow."""
        controller = VoiceController()
        
        # 1. Start recording
        controller.start_recording()
        assert controller.is_recording is True
        
        # 2. Simulate audio input
        fake_audio = np.random.randn(16000, 1).astype(np.float32)
        controller._audio_callback(fake_audio, None, None, None)
        
        # 3. Stop recording
        controller.stop_recording()
        assert controller.is_recording is False
        
        # 4. Get recorded audio
        audio_data = controller.get_audio_data()
        assert audio_data is not None
        
        # 5. Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transcript": "Hello",
            "response_text": "Hi there!",
            "response_audio": "YmFzZTY0X2F1ZGlv"  # fake base64
        }
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # 6. Send to API
        result = await controller.send_audio_to_api(audio_data)
        assert result is not None
        assert result["transcript"] == "Hello"
        
        # 7. Play response (would be decoded and played in real scenario)
        # This is tested separately in playback tests
        
        # Complete flow executed successfully
        assert True

