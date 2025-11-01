"""
Tests para clientes de infrastructure (con mocks).

No requieren servicios externos corriendo.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import asyncio


class TestWhisperSTTClient:
    """Tests para WhisperSTTClient (mocked)."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Verificar inicialización del cliente."""
        from src.infrastructure.stt.whisper_client import WhisperSTTClient
        
        client = WhisperSTTClient(
            model_size="base",
            device="cpu",
            compute_type="int8"
        )
        
        assert client.model_size == "base"
        assert client.device == "cpu"
        assert client._model is None  # Lazy loading
    
    @pytest.mark.asyncio
    async def test_transcribe_empty_audio_raises_error(self):
        """Verificar que audio vacío lanza error."""
        from src.infrastructure.stt.whisper_client import WhisperSTTClient
        
        client = WhisperSTTClient(
            model_size="base",
            device="cpu",
            compute_type="int8"
        )
        
        with pytest.raises(ValueError, match="Audio bytes cannot be empty"):
            await client.transcribe_audio(b"", language="es")
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_mock(self):
        """Test transcripción con mock."""
        from src.infrastructure.stt.whisper_client import WhisperSTTClient
        
        client = WhisperSTTClient(
            model_size="base",
            device="cpu",
            compute_type="int8"
        )
        
        # Mock del método _transcribe_sync
        client._transcribe_sync = Mock(return_value="Hola, me llamo Adrian")
        
        # Simular audio bytes
        fake_audio = b"fake audio data" * 100
        
        result = await client.transcribe_audio(fake_audio, language="es")
        
        assert result == "Hola, me llamo Adrian"
        assert client._transcribe_sync.called


class TestLMStudioClient:
    """Tests para LMStudioClient (mocked)."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Verificar inicialización del cliente."""
        from src.infrastructure.llm.lm_studio_client import LMStudioClient
        
        client = LMStudioClient(
            base_url="http://localhost:1234/v1",
            model="test-model",
            max_tokens=150,
            temperature=0.7
        )
        
        assert client.base_url == "http://localhost:1234/v1"
        assert client.model == "test-model"
        assert client.max_tokens == 150
        assert client.temperature == 0.7
    
    @pytest.mark.asyncio
    async def test_generate_response_mock(self):
        """Test generación con mock."""
        from src.infrastructure.llm.lm_studio_client import LMStudioClient
        
        client = LMStudioClient(
            base_url="http://localhost:1234/v1",
            model="test-model",
            max_tokens=150,
            temperature=0.7
        )
        
        # Mock de la respuesta OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hola! Cómo estás?"
        
        client.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        messages = [
            {"role": "user", "content": "Hola"}
        ]
        
        result = await client.generate_response(messages)
        
        assert result == "Hola! Cómo estás?"
        assert client.client.chat.completions.create.called
    
    @pytest.mark.asyncio
    async def test_generate_response_empty_messages_raises_error(self):
        """Verificar que mensajes vacíos lanzan error."""
        from src.infrastructure.llm.lm_studio_client import LMStudioClient
        
        client = LMStudioClient(
            base_url="http://localhost:1234/v1",
            model="test-model",
            max_tokens=150,
            temperature=0.7
        )
        
        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            await client.generate_response([])


class TestPyttsx3TTSClient:
    """Tests para Pyttsx3TTSClient (mocked)."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Verificar inicialización del cliente."""
        from src.infrastructure.tts.pyttsx3_client import Pyttsx3TTSClient
        
        client = Pyttsx3TTSClient(
            rate=175,
            volume=0.9,
            voice_index=0
        )
        
        assert client.rate == 175
        assert client.volume == 0.9
        assert client.voice_index == 0
    
    @pytest.mark.asyncio
    async def test_synthesize_speech_mock(self):
        """Test síntesis con mock."""
        from src.infrastructure.tts.pyttsx3_client import Pyttsx3TTSClient
        
        client = Pyttsx3TTSClient(
            rate=175,
            volume=0.9,
            voice_index=0
        )
        
        # Mock del método _synthesize_sync
        fake_audio = b"fake audio data" * 100
        client._synthesize_sync = Mock(return_value=fake_audio)
        
        result = await client.synthesize_speech("Hola mundo", output_format="wav")
        
        assert result == fake_audio
        assert client._synthesize_sync.called
    
    @pytest.mark.asyncio
    async def test_synthesize_empty_text_raises_error(self):
        """Verificar que texto vacío lanza error."""
        from src.infrastructure.tts.pyttsx3_client import Pyttsx3TTSClient
        
        client = Pyttsx3TTSClient(
            rate=175,
            volume=0.9,
            voice_index=0
        )
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await client.synthesize_speech("", output_format="wav")


class TestVoiceAssistantService:
    """Tests para VoiceAssistantService (mocked)."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Verificar inicialización del servicio."""
        from src.infrastructure.stt.whisper_client import WhisperSTTClient
        from src.infrastructure.llm.lm_studio_client import LMStudioClient
        from src.infrastructure.tts.pyttsx3_client import Pyttsx3TTSClient
        from src.application.conversation_service import ConversationService
        from src.application.voice_assistant_service import VoiceAssistantService
        
        stt = WhisperSTTClient(
            model_size="base",
            device="cpu",
            compute_type="int8"
        )
        llm = LMStudioClient(
            base_url="http://localhost:1234/v1",
            model="test-model",
            max_tokens=150,
            temperature=0.7
        )
        tts = Pyttsx3TTSClient(
            rate=175,
            volume=0.9,
            voice_index=0
        )
        conv_service = ConversationService()
        
        service = VoiceAssistantService(
            stt_client=stt,
            llm_client=llm,
            tts_client=tts,
            conversation_service=conv_service
        )
        
        assert service.stt is stt
        assert service.llm is llm
        assert service.tts is tts
        assert service.conversations is conv_service
    
    @pytest.mark.asyncio
    async def test_process_voice_input_mock(self, session_id):
        """Test pipeline completo con mocks."""
        from src.infrastructure.stt.whisper_client import WhisperSTTClient
        from src.infrastructure.llm.lm_studio_client import LMStudioClient
        from src.infrastructure.tts.pyttsx3_client import Pyttsx3TTSClient
        from src.application.conversation_service import ConversationService
        from src.application.voice_assistant_service import VoiceAssistantService
        
        # Crear clients con config
        stt = WhisperSTTClient(
            model_size="base",
            device="cpu",
            compute_type="int8"
        )
        llm = LMStudioClient(
            base_url="http://localhost:1234/v1",
            model="test-model",
            max_tokens=150,
            temperature=0.7
        )
        tts = Pyttsx3TTSClient(
            rate=175,
            volume=0.9,
            voice_index=0
        )
        conv_service = ConversationService()
        
        # Crear servicio
        service = VoiceAssistantService(stt, llm, tts, conv_service)
        
        # Mock de cada etapa
        stt.transcribe_audio = AsyncMock(return_value="Hola, me llamo Adrian")
        llm.generate_response = AsyncMock(return_value="Hola Adrian! Mucho gusto.")
        tts.synthesize_speech = AsyncMock(return_value=b"fake audio response")
        
        # Ejecutar pipeline
        fake_audio = b"fake audio input" * 100
        transcribed, response_text, response_audio, latency = await service.process_voice_input(
            audio_bytes=fake_audio,
            session_id=session_id,
            language="es"
        )
        
        # Verificar resultados
        assert transcribed == "Hola, me llamo Adrian"
        assert response_text == "Hola Adrian! Mucho gusto."
        assert response_audio == b"fake audio response"
        
        # Verificar latencias
        assert "stt" in latency
        assert "llm" in latency
        assert "tts" in latency
        assert "total" in latency
        
        # Verificar que todos los métodos fueron llamados
        assert stt.transcribe_audio.called
        assert llm.generate_response.called
        assert tts.synthesize_speech.called

