"""
Base Specialist Agent - Foundation for all domain specialist agents.

Specialist agents are registered in agent_cards with type="specialist" and use
one or more capabilities from the capability registry.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import uuid


from swarms.team_agent.core.node import SwarmNode
from swarms.team_agent.crypto.pki import TrustDomain


class BaseSpecialist(SwarmNode):
    """
    Base class for all specialist agents.

    Specialist agents:
    - Inherit from SwarmNode (Identity + Crypto)
    - Are registered in agent_cards with type="specialist"
    - Use one or more capabilities from capability registry
    """

    def __init__(self, agent_id: str = None, workflow_id: str = None, cert_chain: List[Dict] = None):
        """
        Initialize specialist agent.

        Args:
            agent_id: Unique agent identifier
            workflow_id: Current workflow ID
            cert_chain: Optional manual cert chain (legacy/override)
        """
        # Initialize SwarmNode base (handles ID, Name, PKI)
        super().__init__(
            name="BaseSpecialist",
            agent_type="specialist",
            agent_id=agent_id,
            trust_domain=TrustDomain.EXECUTION
        )
        
        self.workflow_id = workflow_id
        
        # Backward compatibility for cert_chain manual override
        # If cert_chain provided manually, override what SwarmNode loaded
        if cert_chain:
            try:
                from swarms.team_agent.crypto import Signer
                self.signer = Signer(
                    private_key_pem=cert_chain['key'],
                    certificate_pem=cert_chain['cert'],
                    signer_id=self.id
                )
            except Exception:
                pass

        # Metadata (default values, subclasses should override)
        self.description = ""
        self.version = "1.0.0"

        # Capabilities
        self.primary_capability = None
        self.secondary_capabilities = []

    # Removed _generate_agent_id as SwarmNode handles it


    @abstractmethod
    def get_primary_capability(self):
        """
        Get the primary capability this specialist uses.

        Returns:
            Capability instance (e.g., LegalDocumentGenerator)
        """
        pass

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the specialist's task.

        Args:
            context: Execution context with:
                - mission: str - Task description
                - architecture: str - Optional architecture from Architect
                - Additional context from orchestrator

        Returns:
            dict with:
                - agent_id: str
                - agent_name: str
                - capability_used: str
                - artifacts: list - Generated artifacts
                - metadata: dict - Additional metadata
        """
        pass

    def get_capabilities(self) -> List[str]:
        """
        Get list of capability IDs this specialist uses.

        Returns:
            List of capability IDs
        """
        capabilities = []

        if self.primary_capability:
            cap_metadata = self.primary_capability.get_metadata()
            capabilities.append(cap_metadata["name"])

        for cap in self.secondary_capabilities:
            cap_metadata = cap.get_metadata()
            capabilities.append(cap_metadata["name"])

        return capabilities

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get specialist metadata for registration.

        Returns:
            dict with agent metadata
        """
        trust_domain_str = self.trust_domain.value if hasattr(self.trust_domain, "value") else str(self.trust_domain)
        
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_type": self.agent_type,
            "description": self.description,
            "version": self.version,
            "trust_domain": trust_domain_str,
            "capabilities": self.get_capabilities(),
            "module_path": f"{self.__class__.__module__}",
            "class_name": self.__class__.__name__
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name='{self.name}')>"
