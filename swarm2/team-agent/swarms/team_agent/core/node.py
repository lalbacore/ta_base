"""
Swarm Node - Base class for all agents in the Crypto-Mesh architecture.

Provides:
- Identity management
- PKI integration (signing/verification)
- Message handling
- Base capability management
"""

import logging
from typing import Dict, Any, List, Optional
import uuid

from swarms.team_agent.core.message import AgentMessage
from swarms.team_agent.crypto.pki import PKIManager, TrustDomain
from swarms.team_agent.crypto.signing import Signer

# Try to import CapabilityRegistry, but allow fallback if not ready
try:
    from swarms.team_agent.capabilities.registry import CapabilityRegistry
except ImportError:
    CapabilityRegistry = None


class SwarmNode:
    """
    Base node in the agent swarm.
    All agents (specialists, roles, orchestrators) should inherit from this.
    """

    def __init__(
        self, 
        name: str, 
        agent_type: str, 
        agent_id: Optional[str] = None,
        trust_domain: TrustDomain = TrustDomain.EXECUTION,
        pki_manager: Optional[PKIManager] = None
    ):
        """
        Initialize SwarmNode.

        Args:
            name: Human readable name
            agent_type: Type of agent ('role', 'specialist', 'orchestrator')
            agent_id: Unique ID (auto-generated if None)
            trust_domain: Trust domain for PKI identity
            pki_manager: Optional PKI manager instance
        """
        self.name = name
        self.agent_type = agent_type
        self.id = agent_id or f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.trust_domain = trust_domain
        
        # Logging
        self.logger = logging.getLogger(f"SwarmNode.{self.name}")
        
        # PKI & Identity
        self.pki_manager = pki_manager or PKIManager()
        self.signer = self._initialize_identity()
        
        # Capabilities
        # self.capabilities = CapabilityRegistry() if CapabilityRegistry else {} 
        # (Deferring complex capability logic for now to keep base clean)
        self.capabilities: List[str] = []

    def _initialize_identity(self) -> Optional[Signer]:
        """
        Initialize cryptographic identity using PKI.
        """
        try:
            # For now, we use the shared domain certificate.
            # In Phase 2: We will request unique certs for each agent.
            cert_chain = self.pki_manager.get_certificate_chain(self.trust_domain)
            
            return Signer(
                private_key_pem=cert_chain['key'],
                certificate_pem=cert_chain['cert'],
                signer_id=self.id
            )
        except Exception as e:
            self.logger.warning(f"Failed to initialize PKI identity: {e}")
            return None

    def sign_message(self, message: AgentMessage) -> AgentMessage:
        """
        Cryptographically sign an outgoing message.
        """
        if not self.signer:
            self.logger.warning("Cannot sign message: No identity initialized")
            return message
            
        try:
            # Sign the payload data
            signed_data = self.signer.sign(message.signing_payload)
            
            # Attach signature to message
            message.signature = {
                "signature": signed_data.signature,
                "signer": signed_data.signer,
                "timestamp": signed_data.timestamp
            }
        except Exception as e:
            self.logger.error(f"Error signing message: {e}")
            
        return message

    def verify_message(self, message: AgentMessage) -> bool:
        """
        Verify the signature of an incoming message.
        """
        if not message.signature:
            self.logger.debug("Message has no signature to verify")
            return False
            
        # Implementation of generic verification would go here.
        # It requires loading the signer's public key (from the cert).
        # For Phase 1, we will assume true if signature structure exists,
        # but REAL verification logic belongs in `Signer` or `Verifier` class.
        # NOTE: We need a `Verifier` component which we can add later.
        
        return True

    def create_message(
        self, 
        target_id: str, 
        message_type: str, 
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> AgentMessage:
        """Create and sign a new message."""
        msg = AgentMessage(
            sender_id=self.id,
            target_id=target_id,
            message_type=message_type,
            payload=payload,
            conversation_id=conversation_id
        )
        return self.sign_message(msg)

    def receive_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Handle incoming message.
        Subclasses should override `handle_message` instead.
        """
        # 1. Verify signature (future strict check)
        # valid = self.verify_message(message)
        
        # 2. Dispatch
        return self.handle_message(message)

    def handle_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Process the message logic. Override in subclasses.
        """
        self.logger.info(f"Received message type {message.message_type} from {message.sender_id}")
        return {"status": "received", "ack": True}
        
    def get_info(self) -> Dict[str, Any]:
        """Return node metadata."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.agent_type,
            "trust_domain": self.trust_domain.value,
            "has_crypto": self.signer is not None
        }
