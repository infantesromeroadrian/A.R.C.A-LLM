"""
Tests para memoria conversacional.

Verifica que:
- Conversation mantiene memoria completa
- Messages son inmutables
- ConversationService gestiona múltiples sesiones
"""

import pytest
from uuid import uuid4
from src.domain.conversation import Conversation
from src.domain.message import Message
from src.application.conversation_service import ConversationService


class TestMessage:
    """Tests para Message Value Object."""
    
    def test_create_user_message(self):
        """Verificar creación de mensaje de usuario."""
        msg = Message.create_user_message("Hola")
        
        assert msg.role == "user"
        assert msg.content == "Hola"
        assert msg.timestamp is not None
    
    def test_create_assistant_message(self):
        """Verificar creación de mensaje del asistente."""
        msg = Message.create_assistant_message("Hola! Cómo estás?")
        
        assert msg.role == "assistant"
        assert msg.content == "Hola! Cómo estás?"
    
    def test_message_immutability(self):
        """Verificar que Message es inmutable."""
        msg = Message.create_user_message("Test")
        
        with pytest.raises(Exception):  # dataclass frozen
            msg.content = "Changed"
    
    def test_empty_content_raises_error(self):
        """Verificar que contenido vacío lanza error."""
        with pytest.raises(ValueError):
            Message.create_user_message("")
        
        with pytest.raises(ValueError):
            Message.create_user_message("   ")
    
    def test_to_dict_format(self):
        """Verificar formato para LLM."""
        msg = Message.create_user_message("Test")
        d = msg.to_dict()
        
        assert d["role"] == "user"
        assert d["content"] == "Test"
        assert "timestamp" not in d  # No debe incluir timestamp


class TestConversation:
    """Tests para Conversation Aggregate Root."""
    
    def test_create_conversation(self):
        """Verificar creación de conversación."""
        conv = Conversation()
        
        assert conv.session_id is not None
        assert conv.message_count > 0  # System message
        assert conv.is_active
    
    def test_add_user_message(self):
        """Verificar agregar mensaje de usuario."""
        conv = Conversation()
        initial_count = conv.message_count
        
        conv.add_user_message("Hola, me llamo Adrian")
        
        assert conv.message_count == initial_count + 1
        
        last_msg = conv.get_last_user_message()
        assert last_msg.content == "Hola, me llamo Adrian"
    
    def test_add_assistant_message(self):
        """Verificar agregar mensaje del asistente."""
        conv = Conversation()
        
        conv.add_user_message("Hola")
        conv.add_assistant_message("Hola! Cómo estás?")
        
        last_msg = conv.get_last_assistant_message()
        assert last_msg.content == "Hola! Cómo estás?"
    
    def test_conversation_memory(self):
        """Verificar que se mantiene memoria completa."""
        conv = Conversation()
        
        # Simular conversación
        conv.add_user_message("Hola, me llamo Adrian")
        conv.add_assistant_message("Hola Adrian!")
        conv.add_user_message("Qué día es hoy?")
        conv.add_assistant_message("Hoy es viernes")
        conv.add_user_message("Recuerdas mi nombre?")
        
        # Verificar que todos los mensajes están
        messages = conv.get_messages_for_llm()
        
        assert len(messages) >= 5  # system + 5 intercambios
        assert any("Adrian" in msg["content"] for msg in messages)
    
    def test_max_messages_limit(self):
        """Verificar límite de mensajes."""
        conv = Conversation(max_messages=5)
        
        # Agregar muchos mensajes
        for i in range(10):
            conv.add_user_message(f"Mensaje {i}")
            conv.add_assistant_message(f"Respuesta {i}")
        
        # Debe mantener solo los últimos (respetando límite)
        assert conv.message_count <= 5
    
    def test_clear_conversation(self):
        """Verificar limpieza de conversación."""
        conv = Conversation()
        
        conv.add_user_message("Test")
        conv.add_assistant_message("Response")
        
        initial_count = conv.message_count
        assert initial_count > 1
        
        conv.clear_history(keep_system=True)
        
        # Solo debe quedar system message
        assert conv.message_count == 1
    
    def test_inactive_conversation(self):
        """Verificar conversación inactiva."""
        conv = Conversation()
        
        conv.deactivate()
        
        assert not conv.is_active
        
        with pytest.raises(ValueError):
            conv.add_user_message("Test")


class TestConversationService:
    """Tests para ConversationService."""
    
    def test_create_conversation_service(self):
        """Verificar creación del servicio."""
        service = ConversationService()
        
        assert service.get_active_conversations_count() == 0
    
    def test_create_and_get_conversation(self):
        """Verificar creación y obtención de conversación."""
        service = ConversationService()
        
        conv1 = service.create_conversation()
        
        assert service.get_active_conversations_count() == 1
        
        # Obtener la misma conversación
        conv2 = service.get_conversation(conv1.session_id)
        
        assert conv1.session_id == conv2.session_id
    
    def test_get_or_create_conversation(self):
        """Verificar get_or_create."""
        service = ConversationService()
        session_id = uuid4()
        
        # Primera llamada: crea
        conv1 = service.get_or_create_conversation(session_id)
        assert conv1.session_id == session_id
        
        # Segunda llamada: obtiene existente
        conv2 = service.get_or_create_conversation(session_id)
        assert conv1 is conv2
    
    def test_multiple_sessions(self):
        """Verificar múltiples sesiones simultáneas."""
        service = ConversationService()
        
        # Crear 3 conversaciones
        conv1 = service.create_conversation()
        conv2 = service.create_conversation()
        conv3 = service.create_conversation()
        
        assert service.get_active_conversations_count() == 3
        
        # Cada una debe ser independiente
        conv1.add_user_message("Soy sesión 1")
        conv2.add_user_message("Soy sesión 2")
        
        msg1 = conv1.get_last_user_message()
        msg2 = conv2.get_last_user_message()
        
        assert msg1.content == "Soy sesión 1"
        assert msg2.content == "Soy sesión 2"
    
    def test_delete_conversation(self):
        """Verificar eliminación de conversación."""
        service = ConversationService()
        
        conv = service.create_conversation()
        session_id = conv.session_id
        
        assert service.get_active_conversations_count() == 1
        
        deleted = service.delete_conversation(session_id)
        
        assert deleted
        assert service.get_active_conversations_count() == 0
        assert service.get_conversation(session_id) is None
    
    def test_clear_conversation(self):
        """Verificar limpieza de conversación."""
        service = ConversationService()
        
        conv = service.create_conversation()
        conv.add_user_message("Test")
        conv.add_assistant_message("Response")
        
        initial_count = conv.message_count
        assert initial_count > 1
        
        service.clear_conversation(conv.session_id, keep_system=True)
        
        # Verificar que se limpió
        conv_after = service.get_conversation(conv.session_id)
        assert conv_after.message_count == 1  # Solo system

