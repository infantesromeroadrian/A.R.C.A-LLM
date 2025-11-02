"""
Tests for Conversation Aggregate Root.

Tests DDD principles:
- Aggregate Root behavior
- Invariants enforcement
- Entity identity
- Business logic encapsulation
"""

import pytest
from uuid import uuid4, UUID
from src.domain.conversation import Conversation
from src.domain.message import Message


class TestConversationCreation:
    """Tests for Conversation creation and initialization."""
    
    def test_create_conversation_with_defaults(self):
        """Test creating conversation with default parameters."""
        conv = Conversation()
        
        assert conv.session_id is not None
        assert isinstance(conv.session_id, UUID)
        assert conv.message_count > 0  # System message
        assert conv.is_active
    
    def test_create_conversation_with_custom_session_id(self):
        """Test creating conversation with custom session_id."""
        custom_id = uuid4()
        conv = Conversation(session_id=custom_id)
        
        assert conv.session_id == custom_id
    
    def test_create_conversation_with_custom_system_prompt(self):
        """Test creating conversation with custom system prompt."""
        custom_prompt = "You are a specialized AI assistant"
        conv = Conversation(system_prompt=custom_prompt)
        
        messages = conv.get_messages_for_llm()
        system_msg = messages[0]
        
        assert system_msg["role"] == "system"
        assert system_msg["content"] == custom_prompt
    
    def test_create_conversation_with_max_messages(self):
        """Test creating conversation with max_messages limit."""
        conv = Conversation(max_messages=5)
        
        assert conv.message_count == 1  # System message


class TestConversationProperties:
    """Tests for Conversation properties."""
    
    def test_session_id_is_immutable(self):
        """Test that session_id cannot be changed."""
        conv = Conversation()
        original_id = conv.session_id
        
        # session_id is a property without setter
        with pytest.raises(AttributeError):
            conv.session_id = uuid4()  # type: ignore
        
        assert conv.session_id == original_id
    
    def test_message_count_property(self):
        """Test message_count property."""
        conv = Conversation()
        
        initial_count = conv.message_count
        conv.add_user_message("Test")
        
        assert conv.message_count == initial_count + 1
    
    def test_is_active_property(self):
        """Test is_active property."""
        conv = Conversation()
        
        assert conv.is_active
        
        conv.deactivate()
        assert not conv.is_active
        
        conv.reactivate()
        assert conv.is_active


class TestAddingMessages:
    """Tests for adding messages to conversation."""
    
    def test_add_user_message(self):
        """Test adding user message."""
        conv = Conversation()
        initial_count = conv.message_count
        
        conv.add_user_message("Hola, me llamo Adrian")
        
        assert conv.message_count == initial_count + 1
        
        last_msg = conv.get_last_user_message()
        assert last_msg is not None
        assert last_msg.content == "Hola, me llamo Adrian"
        assert last_msg.role == "user"
    
    def test_add_assistant_message(self):
        """Test adding assistant message."""
        conv = Conversation()
        
        conv.add_user_message("Hola")
        conv.add_assistant_message("Hola! Cómo estás?")
        
        last_msg = conv.get_last_assistant_message()
        assert last_msg is not None
        assert last_msg.content == "Hola! Cómo estás?"
        assert last_msg.role == "assistant"
    
    def test_add_multiple_messages_maintains_order(self):
        """Test that messages maintain order."""
        conv = Conversation()
        
        conv.add_user_message("Message 1")
        conv.add_assistant_message("Response 1")
        conv.add_user_message("Message 2")
        conv.add_assistant_message("Response 2")
        
        messages = conv.get_messages_for_llm()
        
        # Find user messages
        user_messages = [m for m in messages if m["role"] == "user"]
        assert user_messages[0]["content"] == "Message 1"
        assert user_messages[1]["content"] == "Message 2"
    
    def test_cannot_add_message_to_inactive_conversation(self):
        """Test business rule: cannot add messages to inactive conversation."""
        conv = Conversation()
        conv.deactivate()
        
        with pytest.raises(ValueError, match="inactive conversation"):
            conv.add_user_message("Test")
        
        with pytest.raises(ValueError, match="inactive conversation"):
            conv.add_assistant_message("Test")


class TestConversationMemory:
    """Tests for conversation memory and context."""
    
    def test_conversation_maintains_full_memory(self):
        """Test that conversation maintains complete history."""
        conv = Conversation()
        
        # Simulate conversation
        conv.add_user_message("Hola, me llamo Adrian")
        conv.add_assistant_message("Hola Adrian!")
        conv.add_user_message("Qué día es hoy?")
        conv.add_assistant_message("Hoy es viernes")
        conv.add_user_message("Recuerdas mi nombre?")
        
        # Verify all messages are present
        messages = conv.get_messages_for_llm()
        
        assert len(messages) >= 5  # system + 5 exchanges
        assert any("Adrian" in msg["content"] for msg in messages)
    
    def test_get_messages_for_llm_format(self):
        """Test LLM message format (OpenAI compatible)."""
        conv = Conversation()
        conv.add_user_message("Test")
        
        messages = conv.get_messages_for_llm()
        
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
            assert msg["role"] in ["system", "user", "assistant"]
            assert isinstance(msg["content"], str)
            assert "timestamp" not in msg  # Not included for LLM
    
    def test_get_messages_for_display_format(self):
        """Test display message format (with timestamps)."""
        conv = Conversation()
        conv.add_user_message("Test")
        
        messages = conv.get_messages_for_display()
        
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
            assert "timestamp" in msg  # Included for display


class TestMaxMessagesLimit:
    """Tests for max_messages limit feature."""
    
    def test_max_messages_limit_enforced(self):
        """Test that max_messages limit is enforced."""
        conv = Conversation(max_messages=5)
        
        # Add many messages
        for i in range(10):
            conv.add_user_message(f"Message {i}")
            conv.add_assistant_message(f"Response {i}")
        
        # Should maintain only last messages
        assert conv.message_count <= 5
    
    def test_max_messages_preserves_system_message(self):
        """Test that system message is always preserved."""
        conv = Conversation(max_messages=3, system_prompt="You are helpful")
        
        # Add many messages
        for i in range(10):
            conv.add_user_message(f"Message {i}")
        
        messages = conv.get_messages_for_llm()
        
        # System message should still be first
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are helpful"
    
    def test_max_messages_keeps_recent_messages(self):
        """Test that most recent messages are kept."""
        conv = Conversation(max_messages=5)
        
        for i in range(10):
            conv.add_user_message(f"Message {i}")
        
        messages = conv.get_messages_for_llm()
        
        # Should have recent messages
        last_message = messages[-1]
        assert "Message 9" in last_message["content"]


class TestConversationOperations:
    """Tests for conversation operations."""
    
    def test_clear_conversation_keeping_system(self):
        """Test clearing conversation while keeping system message."""
        conv = Conversation()
        
        conv.add_user_message("Test 1")
        conv.add_assistant_message("Response 1")
        conv.add_user_message("Test 2")
        
        initial_count = conv.message_count
        assert initial_count > 1
        
        conv.clear_history(keep_system=True)
        
        # Only system message should remain
        assert conv.message_count == 1
        messages = conv.get_messages_for_llm()
        assert messages[0]["role"] == "system"
    
    def test_clear_conversation_removing_all(self):
        """Test clearing conversation including system message."""
        conv = Conversation()
        
        conv.add_user_message("Test")
        conv.clear_history(keep_system=False)
        
        assert conv.message_count == 0
    
    def test_get_last_user_message(self):
        """Test getting last user message."""
        conv = Conversation()
        
        conv.add_user_message("First")
        conv.add_assistant_message("Response")
        conv.add_user_message("Second")
        
        last_msg = conv.get_last_user_message()
        assert last_msg is not None
        assert last_msg.content == "Second"
    
    def test_get_last_user_message_returns_none_when_empty(self):
        """Test that get_last_user_message returns None when no user messages."""
        conv = Conversation()
        conv.clear_history(keep_system=False)
        
        last_msg = conv.get_last_user_message()
        assert last_msg is None
    
    def test_get_last_assistant_message(self):
        """Test getting last assistant message."""
        conv = Conversation()
        
        conv.add_user_message("Test")
        conv.add_assistant_message("First response")
        conv.add_user_message("Another test")
        conv.add_assistant_message("Second response")
        
        last_msg = conv.get_last_assistant_message()
        assert last_msg is not None
        assert last_msg.content == "Second response"
    
    def test_deactivate_and_reactivate(self):
        """Test deactivating and reactivating conversation."""
        conv = Conversation()
        
        assert conv.is_active
        
        conv.deactivate()
        assert not conv.is_active
        
        conv.reactivate()
        assert conv.is_active


class TestConversationEquality:
    """Tests for conversation equality and hashing (Entity behavior)."""
    
    def test_conversation_equality_by_session_id(self):
        """Test that conversations are equal if session_id matches."""
        session_id = uuid4()
        
        conv1 = Conversation(session_id=session_id)
        conv2 = Conversation(session_id=session_id)
        
        assert conv1 == conv2
    
    def test_conversation_inequality_different_session_ids(self):
        """Test that conversations with different session_ids are not equal."""
        conv1 = Conversation()
        conv2 = Conversation()
        
        assert conv1 != conv2
    
    def test_conversation_can_be_hashed(self):
        """Test that conversation can be used in sets/dicts."""
        conv1 = Conversation()
        conv2 = Conversation()
        
        conv_set = {conv1, conv2}
        assert len(conv_set) == 2
    
    def test_conversation_repr(self):
        """Test conversation string representation."""
        conv = Conversation()
        
        repr_str = repr(conv)
        
        assert "Conversation" in repr_str
        assert str(conv.session_id) in repr_str
        assert "messages=" in repr_str
        assert "active=" in repr_str

