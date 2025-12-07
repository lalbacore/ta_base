"""
Writing Specialist Agent - Domain expert for creative and academic writing.

Uses CreativeWritingCapability to help with writer's block, content creation,
and structural organization of written works.
"""

from typing import Dict, Any
from swarms.team_agent.specialists.base import BaseSpecialist
from swarms.team_agent.capabilities.creative_writing import CreativeWritingCapability


class WritingSpecialist(BaseSpecialist):
    """
    Specialist agent for writing assistance.

    Primary Capability: CreativeWritingCapability
    Domains: creative writing, blogging, academic writing, copywriting
    Keywords: writer, blog, story, essay, article, content, writer's block, copy
    """

    def __init__(self, agent_id: str = None, workflow_id: str = None, cert_chain=None):
        """
        Initialize Writing Specialist agent.

        Args:
            agent_id: Unique agent ID (auto-generated if not provided)
            workflow_id: Current workflow ID
            cert_chain: PKI certificate chain for signing
        """
        super().__init__(agent_id, workflow_id, cert_chain)

        # Agent metadata
        self.name = "Writing Specialist"
        self.description = (
            "Expert writing coach and content generator. Helps overcome writer's block, "
            "creates outlines, drafts blog posts, stories, and academic essays."
        )
        self.version = "1.0.0"

        # Load primary capability
        self.primary_capability = CreativeWritingCapability()

    def get_primary_capability(self):
        """Get the primary capability this specialist uses."""
        return self.primary_capability

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute writing task.

        Args:
            context: dict with:
                - mission: str - Description of writing task
                - architecture: str - Optional style/tone guidance

        Returns:
            dict with:
                - agent_id: str
                - agent_name: str
                - capability_used: str - "creative_writing"
                - artifacts: list - Generated content
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
            "capability_used": "creative_writing",
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
            "writer", "writing", "blog", "blog post",
            "story", "creative writing", "narrative",
            "essay", "academic", "thesis",
            "content", "copywriting", "article",
            "writer's block", "outline", "draft"
        ]
