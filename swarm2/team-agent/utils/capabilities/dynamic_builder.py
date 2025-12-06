"""
DynamicBuilder: Selects and runs specialist agents based on mission keywords.

New Architecture (Agent-Capability Model):
- Selects specialist agents (not raw capabilities)
- Specialists are registered in agent_cards with type="specialist"
- Specialists use capabilities from capability_registry
- Falls back to generic builder if no specialist matches
"""
from typing import Optional, Dict, Any
from . import CapabilityRegistry

# Import for fallback generic capability usage
try:
    from swarms.team_agent.capabilities.legal import LegalDocumentGenerator
except ImportError:
    LegalDocumentGenerator = None


class DynamicBuilder:
    """
    Dynamic agent selector and builder.

    Selects specialist agents based on mission keywords and executes them.
    Falls back to generic code generation if no specialist matches.
    """

    def __init__(self, registry: Optional[CapabilityRegistry] = None, agent_manager=None):
        """
        Initialize DynamicBuilder.

        Args:
            registry: CapabilityRegistry (legacy, kept for compatibility)
            agent_manager: AgentManager instance for specialist discovery
        """
        self.registry = registry or CapabilityRegistry()
        self.agent_manager = agent_manager
        self.workflow_id = None

    def set_workflow_id(self, workflow_id: str):
        """Set current workflow ID for agent instantiation."""
        self.workflow_id = workflow_id

    def select_agent(self, mission: str):
        """
        Select specialist agent based on mission keywords.

        Args:
            mission: Mission description string

        Returns:
            Specialist agent instance if match found, None for fallback
        """
        if not self.agent_manager:
            return None

        # Try to find matching specialist agent
        specialist = self.agent_manager.find_specialist_by_keywords(mission)

        if specialist:
            # Set workflow ID if available
            if self.workflow_id:
                specialist.workflow_id = self.workflow_id

            return specialist

        return None

    def run(self, mission: str, architecture: str = "") -> Dict[str, Any]:
        """
        Execute mission using selected specialist agent or fallback.

        Args:
            mission: Mission description string
            architecture: Optional architecture from Architect phase

        Returns:
            dict with:
                - capability_used: str - Agent/capability identifier
                - artifacts: list or dict - Generated artifacts
                - metadata: dict - Additional metadata
        """
        # Try to select specialist agent
        specialist = self.select_agent(mission)

        if specialist:
            try:
                # Execute specialist agent
                result = specialist.run({
                    "mission": mission,
                    "architecture": architecture
                })

                # Standardize result format
                artifacts = result.get("artifacts", [])

                return {
                    "agent_used": result.get("agent_name", "unknown_agent"),
                    "capability_used": result.get("capability_used", "unknown_capability"),
                    "artifacts": artifacts,
                    "metadata": {
                        **result.get("metadata", {}),
                        "agent_id": result.get("agent_id"),
                        "agent_type": result.get("agent_type", "specialist")
                    }
                }

            except Exception as e:
                # Log error and fall through to fallback
                if self.agent_manager:
                    self.agent_manager.logger.error(f"Specialist execution failed: {e}")

        # Fallback: Generic code generation
        return self._fallback_generic(mission, architecture)

    def _fallback_generic(self, mission: str, architecture: str) -> Dict[str, Any]:
        """
        Fallback generic builder when no specialist matches.

        Args:
            mission: Mission description
            architecture: Optional architecture

        Returns:
            dict with fallback artifacts
        """
        # Generate simple fallback code
        fallback_code = (
            f"# Generic implementation for mission:\n"
            f"# {mission}\n\n"
            f"def main():\n"
            f"    \"\"\"\n"
            f"    TODO: Implement mission logic\n"
            f"    Mission: {mission}\n"
            f"    \"\"\"\n"
            f"    print('Mission: {mission}')\n"
            f"    # Add implementation here\n\n"
            f"if __name__ == '__main__':\n"
            f"    main()\n"
        )

        return {
            "agent_used": "FallbackBuilder",
            "capability_used": "fallback",
            "artifacts": [
                {
                    "type": "code",
                    "name": "fallback_implementation",
                    "filename": "fallback_implementation.py",
                    "content": fallback_code
                }
            ],
            "metadata": {
                "type": "fallback",
                "domains": [],
                "note": "No specialist agent matched mission keywords. Generic fallback used."
            }
        }
