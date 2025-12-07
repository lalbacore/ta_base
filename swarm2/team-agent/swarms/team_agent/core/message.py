"""
Agent Message Protocol - Standardized envelope for inter-agent communication.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json


@dataclass
class AgentMessage:
    """
    Standardized message envelope for crypto-mesh communication.
    
    Attributes:
        sender_id: ID of the sending agent
        target_id: ID of the intended recipient (or 'broadcast')
        message_type: Type of message (e.g., 'task_request', 'task_result')
        payload: Actual message content
        timestamp: Creation time
        message_id: Unique message identifier
        signature: Cryptographic signature of the sender (optional)
        conversation_id: Thread/mission correlation ID (optional)
    """
    sender_id: str
    target_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signature: Optional[Dict[str, str]] = None
    conversation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "target_id": self.target_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "conversation_id": self.conversation_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create from dictionary."""
        return cls(
            sender_id=data["sender_id"],
            target_id=data["target_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            timestamp=data.get("timestamp"),
            message_id=data.get("message_id"),
            signature=data.get("signature"),
            conversation_id=data.get("conversation_id")
        )
    
    def serialize(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())

    @property
    def signing_payload(self) -> Dict[str, Any]:
        """
        Get the data subset that should be signed.
        
        Excludes the signature itself and metadata that might change (like timestamp
        if we were strict, but here we include it against replay attacks).
        """
        return {
            "sender_id": self.sender_id,
            "target_id": self.target_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id
        }
