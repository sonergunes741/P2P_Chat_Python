"""
Protocol Module
===============
Defines the message protocol for P2P communication.
All messages are JSON-formatted for easy parsing and extensibility.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class MessageType(Enum):
    """Enumeration of all supported message types."""
    DISCOVERY = "discovery"
    DISCOVERY_RESPONSE = "discovery_response"
    MESSAGE = "message"
    DISCONNECT = "disconnect"
    CONNECTION_REQUEST = "connection_request"
    CONNECTION_ACCEPT = "connection_accept"
    CONNECTION_REJECT = "connection_reject"


class Message:
    """
    Represents a P2P chat message.
    
    Attributes:
        msg_type: Type of the message (MessageType enum)
        sender: IP address of the sender
        payload: Message content
        timestamp: When the message was created
    """
    
    def __init__(
        self,
        msg_type: MessageType,
        sender: str,
        payload: str = "",
        timestamp: Optional[str] = None
    ):
        self.msg_type = msg_type
        self.sender = sender
        self.payload = payload
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_json(self) -> str:
        """Serialize message to JSON string."""
        data = {
            "type": self.msg_type.value,
            "sender": self.sender,
            "payload": self.payload,
            "timestamp": self.timestamp
        }
        return json.dumps(data)
    
    def to_bytes(self) -> bytes:
        """Serialize message to bytes for network transmission."""
        return self.to_json().encode('utf-8')
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """
        Deserialize message from JSON string.
        
        Args:
            json_str: JSON-formatted message string
            
        Returns:
            Message object
            
        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["type", "sender"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse message type
            try:
                msg_type = MessageType(data["type"])
            except ValueError:
                raise ValueError(f"Unknown message type: {data['type']}")
            
            return cls(
                msg_type=msg_type,
                sender=data["sender"],
                payload=data.get("payload", ""),
                timestamp=data.get("timestamp")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        """Deserialize message from bytes."""
        return cls.from_json(data.decode('utf-8'))
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"[{self.msg_type.value}] {self.sender}: {self.payload}"
    
    def __repr__(self) -> str:
        return f"Message(type={self.msg_type}, sender={self.sender}, payload={self.payload[:20]}...)"


# Factory functions for common message types
def create_discovery_message(sender: str, tcp_port: int) -> Message:
    """Create a peer discovery broadcast message."""
    return Message(
        msg_type=MessageType.DISCOVERY,
        sender=sender,
        payload=f"DISCOVER_PEERS:{tcp_port}"
    )


def create_discovery_response(sender: str, port: int) -> Message:
    """Create a response to a discovery broadcast."""
    return Message(
        msg_type=MessageType.DISCOVERY_RESPONSE,
        sender=sender,
        payload=str(port)
    )


def create_chat_message(sender: str, content: str) -> Message:
    """Create a chat message."""
    return Message(
        msg_type=MessageType.MESSAGE,
        sender=sender,
        payload=content
    )


def create_disconnect_message(sender: str) -> Message:
    """Create a disconnect notification message."""
    return Message(
        msg_type=MessageType.DISCONNECT,
        sender=sender,
        payload="GOODBYE"
    )


def create_connection_request(sender: str) -> Message:
    """Create a connection request message."""
    return Message(
        msg_type=MessageType.CONNECTION_REQUEST,
        sender=sender,
        payload="REQUEST_CONNECTION"
    )


def create_connection_accept(sender: str) -> Message:
    """Create a connection acceptance message."""
    return Message(
        msg_type=MessageType.CONNECTION_ACCEPT,
        sender=sender,
        payload="CONNECTION_ACCEPTED"
    )


def create_connection_reject(sender: str) -> Message:
    """Create a connection rejection message."""
    return Message(
        msg_type=MessageType.CONNECTION_REJECT,
        sender=sender,
        payload="CONNECTION_REJECTED"
    )
