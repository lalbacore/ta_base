"""
Base Specialist Agent - Foundation for all domain specialist agents.

Specialist agents are registered in agent_cards with type="specialist" and use
one or more capabilities from the capability registry.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import uuid


class BaseSpecialist(ABC):
    """
    Base class for all specialist agents.

    Specialist agents:
    - Are registered in agent_cards with type="specialist"
    - Use one or more capabilities from capability registry
    - Have their own trust scores and invocation history
    - Are selected dynamically by DynamicBuilder based on keywords

    Subclasses must implement:
    - get_primary_capability(): Return the main capability this specialist uses
    - run(context): Execute the specialist's task using capabilities
    """

    def __init__(self, agent_id: str = None, workflow_id: str = None, cert_chain: List[Dict] = None):
        """
        Initialize specialist agent.

        Args:
            agent_id: Unique agent identifier (auto-generated if not provided)
            workflow_id: Current workflow ID
            cert_chain: PKI certificate chain for signing
        """
        self.id = agent_id or self._generate_agent_id()
        self.workflow_id = workflow_id
        self.cert_chain = cert_chain

        # Metadata (set by subclasses)
        self.name = "BaseSpecialist"
        self.agent_type = "specialist"
        self.trust_domain = "EXECUTION"
        self.description = ""
        self.version = "1.0.0"

        # Capabilities
        self.primary_capability = None
        self.secondary_capabilities = []

    def _generate_agent_id(self) -> str:
        """Generate unique agent ID."""
        class_name = self.__class__.__name__.lower().replace("specialist", "")
        return f"specialist_{class_name}_{uuid.uuid4().hex[:8]}"

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
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_type": self.agent_type,
            "description": self.description,
            "version": self.version,
            "trust_domain": self.trust_domain,
            "capabilities": self.get_capabilities(),
            "module_path": f"{self.__class__.__module__}",
            "class_name": self.__class__.__name__
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name='{self.name}')>"
