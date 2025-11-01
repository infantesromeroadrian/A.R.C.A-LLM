"""
Configuración de pytest.

Fixtures compartidos para todos los tests.
"""

import pytest
from uuid import uuid4
from src.domain.conversation import Conversation
from src.application.conversation_service import ConversationService


@pytest.fixture
def sample_conversation():
    """Fixture: Conversación de prueba."""
    return Conversation()


@pytest.fixture
def conversation_service():
    """Fixture: ConversationService."""
    return ConversationService()


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

