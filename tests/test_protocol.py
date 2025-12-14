"""
Test Protocol Module
====================
Unit tests for the message protocol.
"""

import pytest
from src.protocol import (
    Message,
    MessageType,
    create_discovery_message,
    create_discovery_response,
    create_chat_message,
    create_disconnect_message
)


class TestMessage:
    """Tests for the Message class."""
    
    def test_create_message(self):
        """Test basic message creation."""
        msg = Message(
            msg_type=MessageType.MESSAGE,
            sender="192.168.1.1",
            payload="Hello, World!"
        )
        
        assert msg.msg_type == MessageType.MESSAGE
        assert msg.sender == "192.168.1.1"
        assert msg.payload == "Hello, World!"
        assert msg.timestamp is not None
    
    def test_to_json(self):
        """Test JSON serialization."""
        msg = Message(
            msg_type=MessageType.MESSAGE,
            sender="192.168.1.1",
            payload="Test message"
        )
        
        json_str = msg.to_json()
        
        assert '"type": "message"' in json_str
        assert '"sender": "192.168.1.1"' in json_str
        assert '"payload": "Test message"' in json_str
    
    def test_from_json(self):
        """Test JSON deserialization."""
        json_str = '{"type": "message", "sender": "10.0.0.1", "payload": "Hello"}'
        
        msg = Message.from_json(json_str)
        
        assert msg.msg_type == MessageType.MESSAGE
        assert msg.sender == "10.0.0.1"
        assert msg.payload == "Hello"
    
    def test_roundtrip(self):
        """Test serialization roundtrip."""
        original = Message(
            msg_type=MessageType.DISCOVERY,
            sender="172.16.0.1",
            payload="DISCOVER_PEERS"
        )
        
        json_str = original.to_json()
        restored = Message.from_json(json_str)
        
        assert restored.msg_type == original.msg_type
        assert restored.sender == original.sender
        assert restored.payload == original.payload
    
    def test_to_bytes(self):
        """Test bytes conversion."""
        msg = Message(
            msg_type=MessageType.MESSAGE,
            sender="192.168.1.1",
            payload="Test"
        )
        
        data = msg.to_bytes()
        
        assert isinstance(data, bytes)
        assert b'"type": "message"' in data
    
    def test_from_bytes(self):
        """Test bytes deserialization."""
        data = b'{"type": "disconnect", "sender": "192.168.1.1", "payload": "GOODBYE"}'
        
        msg = Message.from_bytes(data)
        
        assert msg.msg_type == MessageType.DISCONNECT
        assert msg.payload == "GOODBYE"
    
    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            Message.from_json("not valid json")
    
    def test_missing_type_raises_error(self):
        """Test that missing type field raises ValueError."""
        with pytest.raises(ValueError, match="Missing required field"):
            Message.from_json('{"sender": "192.168.1.1"}')
    
    def test_unknown_type_raises_error(self):
        """Test that unknown message type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown message type"):
            Message.from_json('{"type": "unknown", "sender": "192.168.1.1"}')


class TestFactoryFunctions:
    """Tests for message factory functions."""
    
    def test_create_discovery_message(self):
        """Test discovery message creation."""
        msg = create_discovery_message("192.168.1.1", 5000)
        
        assert msg.msg_type == MessageType.DISCOVERY
        assert msg.sender == "192.168.1.1"
        assert msg.payload == "DISCOVER_PEERS:5000"
    
    def test_create_discovery_response(self):
        """Test discovery response creation."""
        msg = create_discovery_response("192.168.1.2", 5000)
        
        assert msg.msg_type == MessageType.DISCOVERY_RESPONSE
        assert msg.sender == "192.168.1.2"
        assert msg.payload == "5000"
    
    def test_create_chat_message(self):
        """Test chat message creation."""
        msg = create_chat_message("192.168.1.1", "Hello!")
        
        assert msg.msg_type == MessageType.MESSAGE
        assert msg.sender == "192.168.1.1"
        assert msg.payload == "Hello!"
    
    def test_create_disconnect_message(self):
        """Test disconnect message creation."""
        msg = create_disconnect_message("192.168.1.1")
        
        assert msg.msg_type == MessageType.DISCONNECT
        assert msg.sender == "192.168.1.1"
        assert msg.payload == "GOODBYE"


class TestMessageTypes:
    """Tests for MessageType enum."""
    
    def test_all_message_types(self):
        """Verify all expected message types exist."""
        assert MessageType.DISCOVERY.value == "discovery"
        assert MessageType.DISCOVERY_RESPONSE.value == "discovery_response"
        assert MessageType.MESSAGE.value == "message"
        assert MessageType.DISCONNECT.value == "disconnect"
