"""
Tests for ConversationService (Application Layer).

Tests:
- Service orchestration
- Multiple conversation management
- Repository-like behavior
"""

import pytest
from uuid import uuid4
from src.application.conversation_service import ConversationService
from src.domain.conversation import Conversation


class TestConversationServiceCreation:
    """Tests for ConversationService creation."""
    
    def test_create_service_with_defaults(self):
        """Test creating service with default configuration."""
        service = ConversationService()
        
        assert service.get_active_conversations_count() == 0
    
    def test_create_service_with_max_messages(self):
        """Test creating service with max_messages configuration."""
        service = ConversationService(max_messages_per_conversation=10)
        
        # Create conversation - should respect max_messages
        conv = service.create_conversation()
        
        # Add more than 10 messages
        for i in range(15):
            conv.add_user_message(f"Message {i}")
        
        assert conv.message_count <= 10


class TestConversationManagement:
    """Tests for conversation management."""
    
    def test_create_conversation(self):
        """Test creating a conversation."""
        service = ConversationService()
        
        conv = service.create_conversation()
        
        assert conv is not None
        assert conv.session_id is not None
        assert service.get_active_conversations_count() == 1
    
    def test_create_conversation_with_custom_prompt(self):
        """Test creating conversation with custom system prompt."""
        service = ConversationService()
        
        custom_prompt = "You are a specialized assistant"
        conv = service.create_conversation(system_prompt=custom_prompt)
        
        messages = conv.get_messages_for_llm()
        assert messages[0]["content"] == custom_prompt
    
    def test_get_conversation(self):
        """Test retrieving existing conversation."""
        service = ConversationService()
        
        conv1 = service.create_conversation()
        
        # Retrieve same conversation
        conv2 = service.get_conversation(conv1.session_id)
        
        assert conv2 is not None
        assert conv1.session_id == conv2.session_id
        assert conv1 is conv2  # Same object
    
    def test_get_nonexistent_conversation_returns_none(self):
        """Test getting non-existent conversation returns None."""
        service = ConversationService()
        
        fake_id = uuid4()
        conv = service.get_conversation(fake_id)
        
        assert conv is None
    
    def test_get_or_create_creates_new(self):
        """Test get_or_create creates new conversation if not exists."""
        service = ConversationService()
        session_id = uuid4()
        
        # Should create new
        conv1 = service.get_or_create_conversation(session_id)
        
        assert conv1.session_id == session_id
        assert service.get_active_conversations_count() == 1
    
    def test_get_or_create_returns_existing(self):
        """Test get_or_create returns existing conversation."""
        service = ConversationService()
        session_id = uuid4()
        
        # Create
        conv1 = service.get_or_create_conversation(session_id)
        conv1.add_user_message("Test message")
        
        # Get existing
        conv2 = service.get_or_create_conversation(session_id)
        
        assert conv1 is conv2
        assert conv2.message_count > 1  # Has the test message


class TestMultipleConversations:
    """Tests for handling multiple conversations simultaneously."""
    
    def test_multiple_independent_conversations(self):
        """Test that multiple conversations are independent."""
        service = ConversationService()
        
        # Create 3 conversations
        conv1 = service.create_conversation()
        conv2 = service.create_conversation()
        conv3 = service.create_conversation()
        
        assert service.get_active_conversations_count() == 3
        
        # Add different messages to each
        conv1.add_user_message("I am conversation 1")
        conv2.add_user_message("I am conversation 2")
        conv3.add_user_message("I am conversation 3")
        
        # Verify independence
        msg1 = conv1.get_last_user_message()
        msg2 = conv2.get_last_user_message()
        msg3 = conv3.get_last_user_message()
        
        assert msg1.content == "I am conversation 1"
        assert msg2.content == "I am conversation 2"
        assert msg3.content == "I am conversation 3"
    
    def test_conversation_isolation(self):
        """Test that conversations don't interfere with each other."""
        service = ConversationService()
        
        conv1 = service.create_conversation()
        conv2 = service.create_conversation()
        
        # Add many messages to conv1
        for i in range(10):
            conv1.add_user_message(f"Conv1 message {i}")
        
        # conv2 should be unaffected
        assert conv2.message_count == 1  # Only system message


class TestConversationModification:
    """Tests for modifying conversations through service."""
    
    def test_add_user_message_through_service(self):
        """Test adding user message via service."""
        service = ConversationService()
        
        conv = service.create_conversation()
        session_id = conv.session_id
        
        service.add_user_message(session_id, "Hello")
        
        updated_conv = service.get_conversation(session_id)
        last_msg = updated_conv.get_last_user_message()
        
        assert last_msg.content == "Hello"
    
    def test_add_user_message_to_nonexistent_raises_error(self):
        """Test adding message to non-existent conversation raises error."""
        service = ConversationService()
        fake_id = uuid4()
        
        with pytest.raises(ValueError, match="Conversation not found"):
            service.add_user_message(fake_id, "Test")
    
    def test_add_assistant_message_through_service(self):
        """Test adding assistant message via service."""
        service = ConversationService()
        
        conv = service.create_conversation()
        session_id = conv.session_id
        
        service.add_assistant_message(session_id, "Hello! How can I help?")
        
        updated_conv = service.get_conversation(session_id)
        last_msg = updated_conv.get_last_assistant_message()
        
        assert last_msg.content == "Hello! How can I help?"
    
    def test_clear_conversation_through_service(self):
        """Test clearing conversation via service."""
        service = ConversationService()
        
        conv = service.create_conversation()
        conv.add_user_message("Test")
        conv.add_assistant_message("Response")
        
        initial_count = conv.message_count
        assert initial_count > 1
        
        service.clear_conversation(conv.session_id, keep_system=True)
        
        # Verify cleared
        assert conv.message_count == 1


class TestConversationDeletion:
    """Tests for deleting conversations."""
    
    def test_delete_conversation(self):
        """Test deleting a conversation."""
        service = ConversationService()
        
        conv = service.create_conversation()
        session_id = conv.session_id
        
        assert service.get_active_conversations_count() == 1
        
        deleted = service.delete_conversation(session_id)
        
        assert deleted is True
        assert service.get_active_conversations_count() == 0
        assert service.get_conversation(session_id) is None
    
    def test_delete_nonexistent_conversation_returns_false(self):
        """Test deleting non-existent conversation returns False."""
        service = ConversationService()
        
        fake_id = uuid4()
        deleted = service.delete_conversation(fake_id)
        
        assert deleted is False


class TestConversationCleanup:
    """Tests for cleaning up inactive conversations."""
    
    def test_cleanup_inactive_conversations(self):
        """Test cleanup of inactive conversations."""
        service = ConversationService()
        
        # Create and deactivate some conversations
        conv1 = service.create_conversation()
        conv2 = service.create_conversation()
        conv3 = service.create_conversation()
        
        conv1.deactivate()
        conv3.deactivate()
        
        assert service.get_active_conversations_count() == 3
        
        cleaned = service.cleanup_inactive_conversations()
        
        assert cleaned == 2
        assert service.get_active_conversations_count() == 1
    
    def test_cleanup_when_all_active(self):
        """Test cleanup when all conversations are active."""
        service = ConversationService()
        
        service.create_conversation()
        service.create_conversation()
        
        cleaned = service.cleanup_inactive_conversations()
        
        assert cleaned == 0
        assert service.get_active_conversations_count() == 2
    
    def test_cleanup_when_no_conversations(self):
        """Test cleanup when no conversations exist."""
        service = ConversationService()
        
        cleaned = service.cleanup_inactive_conversations()
        
        assert cleaned == 0


class TestActiveConversationsCount:
    """Tests for getting active conversations count."""
    
    def test_count_starts_at_zero(self):
        """Test count starts at 0."""
        service = ConversationService()
        
        assert service.get_active_conversations_count() == 0
    
    def test_count_increases_with_creation(self):
        """Test count increases as conversations are created."""
        service = ConversationService()
        
        service.create_conversation()
        assert service.get_active_conversations_count() == 1
        
        service.create_conversation()
        assert service.get_active_conversations_count() == 2
        
        service.create_conversation()
        assert service.get_active_conversations_count() == 3
    
    def test_count_decreases_with_deletion(self):
        """Test count decreases as conversations are deleted."""
        service = ConversationService()
        
        conv1 = service.create_conversation()
        conv2 = service.create_conversation()
        
        assert service.get_active_conversations_count() == 2
        
        service.delete_conversation(conv1.session_id)
        assert service.get_active_conversations_count() == 1
        
        service.delete_conversation(conv2.session_id)
        assert service.get_active_conversations_count() == 0

