import json
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from .crypto import encode_message, decode_message


class MessageType(Enum):
    DISCOVERY = "discovery"
    DISCOVERY_RESPONSE = "discovery_response"
    MESSAGE = "message"
    DISCONNECT = "disconnect"
    CONNECTION_REQUEST = "connection_request"
    CONNECTION_ACCEPT = "connection_accept"
    CONNECTION_REJECT = "connection_reject"


class Message:
    
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
        encrypted_payload = encode_message(self.payload) if self.payload else ""
        
        data = {
            "type": self.msg_type.value,
            "sender": self.sender,
            "payload": encrypted_payload,
            "timestamp": self.timestamp
        }
        return json.dumps(data)
    
    def to_bytes(self) -> bytes:
        return self.to_json().encode('utf-8')
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        try:
            data = json.loads(json_str)
            
            required_fields = ["type", "sender"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            try:
                msg_type = MessageType(data["type"])
            except ValueError:
                raise ValueError(f"Unknown message type: {data['type']}")
            
            encrypted_payload = data.get("payload", "")
            try:
                decrypted_payload = decode_message(encrypted_payload) if encrypted_payload else ""
            except ValueError:
                decrypted_payload = encrypted_payload
            
            return cls(
                msg_type=msg_type,
                sender=data["sender"],
                payload=decrypted_payload,
                timestamp=data.get("timestamp")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        return cls.from_json(data.decode('utf-8'))
    
    def __str__(self) -> str:
        return f"[{self.msg_type.value}] {self.sender}: {self.payload}"
    
    def __repr__(self) -> str:
        return f"Message(type={self.msg_type}, sender={self.sender}, payload={self.payload[:20]}...)"


def create_discovery_message(sender: str, tcp_port: int) -> Message:
    return Message(
        msg_type=MessageType.DISCOVERY,
        sender=sender,
        payload=f"DISCOVER_PEERS:{tcp_port}"
    )


def create_discovery_response(sender: str, port: int) -> Message:
    return Message(
        msg_type=MessageType.DISCOVERY_RESPONSE,
        sender=sender,
        payload=str(port)
    )


def create_chat_message(sender: str, content: str) -> Message:
    return Message(
        msg_type=MessageType.MESSAGE,
        sender=sender,
        payload=content
    )


def create_disconnect_message(sender: str) -> Message:
    return Message(
        msg_type=MessageType.DISCONNECT,
        sender=sender,
        payload="GOODBYE"
    )


def create_connection_request(sender: str) -> Message:
    return Message(
        msg_type=MessageType.CONNECTION_REQUEST,
        sender=sender,
        payload="REQUEST_CONNECTION"
    )


def create_connection_accept(sender: str) -> Message:
    return Message(
        msg_type=MessageType.CONNECTION_ACCEPT,
        sender=sender,
        payload="CONNECTION_ACCEPTED"
    )


def create_connection_reject(sender: str) -> Message:
    return Message(
        msg_type=MessageType.CONNECTION_REJECT,
        sender=sender,
        payload="CONNECTION_REJECTED"
    )
