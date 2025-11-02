"""
Configuración de pytest.

Fixtures compartidos para todos los tests.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

from src.domain.conversation import Conversation
from src.application.conversation_service import ConversationService


# ========================================
# Domain Fixtures
# ========================================

@pytest.fixture
def sample_conversation():
    """Fixture: Conversación de prueba."""
    return Conversation()


@pytest.fixture
def session_id():
    """Fixture: Session ID único."""
    return uuid4()


@pytest.fixture
def sample_messages():
    """Fixture: Mensajes de ejemplo para testing."""
    return [
        {"role": "system", "content": "Eres un asistente"},
        {"role": "user", "content": "Hola, me llamo Adrian"},
        {"role": "assistant", "content": "Hola Adrian! Encantado."},
        {"role": "user", "content": "Recuerdas mi nombre?"},
        {"role": "assistant", "content": "Sí, te llamas Adrian."}
    ]


# ========================================
# Application Fixtures
# ========================================

@pytest.fixture
def conversation_service():
    """Fixture: ConversationService."""
    return ConversationService()


# ========================================
# Infrastructure Fixtures (Mocked)
# ========================================

@pytest.fixture
def mock_stt_client():
    """Fixture: Mocked WhisperSTTClient."""
    from src.infrastructure.stt.whisper_client import WhisperSTTClient
    
    client = WhisperSTTClient(
        model_size="base",
        device="cpu",
        compute_type="int8"
    )
    # Mock transcribe method
    client.transcribe_audio = AsyncMock(return_value="Test transcription")
    
    return client


@pytest.fixture
def mock_llm_client():
    """Fixture: Mocked LMStudioClient."""
    from src.infrastructure.llm.lm_studio_client import LMStudioClient
    
    client = LMStudioClient(
        base_url="http://localhost:1234/v1",
        model="test-model",
        max_tokens=150,
        temperature=0.7
    )
    # Mock generate method
    client.generate_response = AsyncMock(return_value="Test response")
    
    return client


@pytest.fixture
def mock_tts_client():
    """Fixture: Mocked Pyttsx3TTSClient."""
    from src.infrastructure.tts.pyttsx3_client import Pyttsx3TTSClient
    
    client = Pyttsx3TTSClient(
        rate=175,
        volume=0.9,
        voice_index=0
    )
    # Mock synthesize method
    client.synthesize_speech = AsyncMock(return_value=b"fake audio data")
    
    return client


# ========================================
# Service Fixtures
# ========================================

@pytest.fixture
def voice_assistant_service(mock_stt_client, mock_llm_client, mock_tts_client, conversation_service):
    """Fixture: VoiceAssistantService with mocked clients."""
    from src.application.voice_assistant_service import VoiceAssistantService
    
    return VoiceAssistantService(
        stt_client=mock_stt_client,
        llm_client=mock_llm_client,
        tts_client=mock_tts_client,
        conversation_service=conversation_service
    )


# ========================================
# Test Data Fixtures
# ========================================

@pytest.fixture
def fake_audio_bytes():
    """Fixture: Fake audio bytes for testing."""
    return b"fake audio data" * 1000


@pytest.fixture
def sample_user_input():
    """Fixture: Sample user text input."""
    return "Hola, me llamo Adrian"


@pytest.fixture
def sample_llm_response():
    """Fixture: Sample LLM response."""
    return "Hola Adrian! Mucho gusto en conocerte."


# ========================================
# Integration Test Fixtures
# ========================================

@pytest.fixture
def mock_voice_service_for_api(mock_stt_client, mock_llm_client, mock_tts_client, conversation_service):
    """
    Fixture: Mocked VoiceAssistantService for API integration tests.
    
    Incluye mocks para todos los métodos usados en los endpoints.
    """
    from src.application.voice_assistant_service import VoiceAssistantService
    
    service = VoiceAssistantService(
        stt_client=mock_stt_client,
        llm_client=mock_llm_client,
        tts_client=mock_tts_client,
        conversation_service=conversation_service
    )
    
    # Mock health_check para que devuelva componentes healthy
    service.health_check = AsyncMock(return_value={
        "overall": True,
        "stt": True,
        "llm": True,
        "tts": True
    })
    
    # Mock process_voice_input
    service.process_voice_input = AsyncMock(return_value={
        "session_id": "test-session-id",
        "transcribed_text": "Test transcription",
        "llm_response": "Test response",
        "audio_response": b"fake audio data"
    })
    
    # Mock process_text_input
    service.process_text_input = AsyncMock(return_value={
        "session_id": "test-session-id",
        "llm_response": "Test response",
        "audio_response": b"fake audio data"
    })
    
    return service

