"""
Tests for Message Value Object.

Tests DDD principles:
- Immutability
- Value equality
- Factory methods
- Validation
"""

import pytest
from datetime import datetime, timezone
from src.domain.message import Message


class TestMessage:
    """Tests for Message Value Object."""
    
    def test_create_user_message(self):
        """Test creating user message with factory method."""
        msg = Message.create_user_message("Hola")
        
        assert msg.role == "user"
        assert msg.content == "Hola"
        assert msg.timestamp is not None
        assert isinstance(msg.timestamp, datetime)
    
    def test_create_assistant_message(self):
        """Test creating assistant message with factory method."""
        msg = Message.create_assistant_message("Hola! Cómo estás?")
        
        assert msg.role == "assistant"
        assert msg.content == "Hola! Cómo estás?"
        assert msg.timestamp is not None
    
    def test_create_system_message(self):
        """Test creating system message with factory method."""
        msg = Message.create_system_message("You are a helpful assistant")
        
        assert msg.role == "system"
        assert msg.content == "You are a helpful assistant"
    
    def test_message_immutability(self):
        """Test that Message is immutable (frozen dataclass)."""
        msg = Message.create_user_message("Test")
        
        with pytest.raises(Exception):  # dataclass frozen
            msg.content = "Changed"
        
        with pytest.raises(Exception):
            msg.role = "assistant"
    
    def test_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message.create_user_message("")
        
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message.create_user_message("   ")
        
        with pytest.raises(ValueError):
            Message.create_assistant_message("\t\n")
    
    def test_invalid_role_raises_error(self):
        """Test that invalid role raises ValueError."""
        with pytest.raises(ValueError, match="Invalid role"):
            Message(
                role="invalid",  # type: ignore
                content="Test",
                timestamp=datetime.now(timezone.utc)
            )
    
    def test_to_dict_format_for_llm(self):
        """Test conversion to LLM format (OpenAI compatible)."""
        msg = Message.create_user_message("Test message")
        d = msg.to_dict()
        
        assert d["role"] == "user"
        assert d["content"] == "Test message"
        assert "timestamp" not in d  # Timestamp excluded for LLM
        assert len(d) == 2  # Only role and content
    
    def test_to_display_dict_format(self):
        """Test conversion to display format (with timestamp)."""
        msg = Message.create_user_message("Test")
        d = msg.to_display_dict()
        
        assert d["role"] == "user"
        assert d["content"] == "Test"
        assert "timestamp" in d
        assert isinstance(d["timestamp"], str)  # ISO format
    
    def test_message_strips_whitespace(self):
        """Test that content is stripped of leading/trailing whitespace."""
        msg = Message.create_user_message("  Test  ")
        
        assert msg.content == "Test"  # Stripped
    
    def test_message_preserves_internal_whitespace(self):
        """Test that internal whitespace is preserved."""
        msg = Message.create_user_message("Hola    mundo")
        
        assert msg.content == "Hola    mundo"
    
    def test_message_equality_by_value(self):
        """Test that Messages are equal by value (not identity)."""
        msg1 = Message(
            role="user",
            content="Test",
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        msg2 = Message(
            role="user",
            content="Test",
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        
        assert msg1 == msg2
        assert msg1 is not msg2  # Different objects
    
    def test_message_inequality_different_content(self):
        """Test that Messages with different content are not equal."""
        msg1 = Message.create_user_message("Hello")
        msg2 = Message.create_user_message("Goodbye")
        
        assert msg1 != msg2
    
    def test_message_hash(self):
        """Test that Message can be hashed (for use in sets/dicts)."""
        msg1 = Message.create_user_message("Test")
        msg2 = Message.create_user_message("Test")
        
        # Should be hashable
        message_set = {msg1, msg2}
        assert len(message_set) >= 1  # Can be used in sets

