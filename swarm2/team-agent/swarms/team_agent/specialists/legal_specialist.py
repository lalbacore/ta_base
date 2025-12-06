"""
Legal Specialist Agent - Domain expert for legal document generation.

Uses LegalDocumentGenerator capability to create legal documents, contracts,
NDAs, privacy policies, and compliance documentation.
"""

from typing import Dict, Any
from swarms.team_agent.specialists.base import BaseSpecialist
from swarms.team_agent.capabilities.legal import LegalDocumentGenerator


class LegalSpecialist(BaseSpecialist):
    """
    Specialist agent for legal document generation.

    Primary Capability: LegalDocumentGenerator
    Domains: legal, contracts, compliance, nda, privacy
    Keywords: nda, contract, privacy, legal, compliance, gdpr, terms, agreement

    Use Cases:
    - Non-disclosure agreements (NDAs)
    - Service contracts and agreements
    - Terms of service / Terms and conditions
    - Privacy policies
    - Compliance documentation
    """

    def __init__(self, agent_id: str = None, workflow_id: str = None, cert_chain=None):
        """
        Initialize Legal Specialist agent.

        Args:
            agent_id: Unique agent ID (auto-generated if not provided)
            workflow_id: Current workflow ID
            cert_chain: PKI certificate chain for signing
        """
        super().__init__(agent_id, workflow_id, cert_chain)

        # Agent metadata
        self.name = "Legal Specialist"
        self.description = (
            "Specialist agent for legal document generation. "
            "Generates NDAs, contracts, privacy policies, terms of service, "
            "and compliance documentation."
        )
        self.version = "1.0.0"

        # Load primary capability
        self.primary_capability = LegalDocumentGenerator()

    def get_primary_capability(self):
        """Get the primary capability this specialist uses."""
        return self.primary_capability

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute legal document generation.

        Args:
            context: dict with:
                - mission: str - Description of legal document to generate
                - architecture: str - Optional architecture from Architect (optional)

        Returns:
            dict with:
                - agent_id: str
                - agent_name: str
                - capability_used: str - "legal_document_generator"
                - artifacts: list - Generated legal documents
                - metadata: dict - Capability metadata
        """
        mission = context.get("mission", "")
        architecture = context.get("architecture", "")

        # Execute primary capability
        result = self.primary_capability.execute({
            "mission": mission,
            "architecture": architecture
        })

        # Return standardized result
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_type": self.agent_type,
            "capability_used": "legal_document_generator",
            "artifacts": result.get("artifacts", []),
            "content": result.get("content", ""),
            "metadata": {
                **result.get("metadata", {}),
                "specialist": self.name,
                "specialist_version": self.version
            }
        }

    @classmethod
    def get_keywords(cls) -> list:
        """
        Get keywords for specialist discovery.

        Returns:
            List of keywords that trigger this specialist
        """
        return [
            "nda", "non-disclosure", "confidentiality",
            "contract", "agreement", "legal",
            "privacy", "privacy policy",
            "terms", "terms of service", "tos", "terms and conditions",
            "compliance", "regulatory", "gdpr", "hipaa",
            "service agreement", "partnership agreement"
        ]
