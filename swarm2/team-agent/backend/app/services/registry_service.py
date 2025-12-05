"""
Registry Service - Bridges Flask API to CapabilityRegistry.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import Dict, Any, List, Optional
from app.data.seed_data import SAMPLE_CAPABILITIES


class RegistryService:
    """
    Service layer for capability registry.
    Bridges Flask API to CapabilityRegistry.
    """

    def __init__(self):
        # TODO: Initialize registry when ready
        # from swarms.team_agent.a2a.registry import CapabilityRegistry
        # self.registry = CapabilityRegistry()

        # Load seed data
        self.capabilities = {cap['capability_id']: cap for cap in SAMPLE_CAPABILITIES}

        # Build providers list from agents (using provider_id from capabilities)
        from app.data.seed_data import SAMPLE_AGENTS
        self.providers = {}
        for agent in SAMPLE_AGENTS:
            self.providers[agent['agent_id']] = {
                'provider_id': agent['agent_id'],
                'name': agent['name'],
                'type': agent['type'],
                'trust_score': agent['trust_score'],
                'reputation': agent['reputation'],
                'total_operations': agent['total_operations']
            }

    def get_capabilities(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List/search capabilities with optional filters."""
        # TODO: Get from registry.list_capabilities(filters)
        capabilities = list(self.capabilities.values())

        # Apply filters if provided
        if 'capability_type' in filters:
            capabilities = [c for c in capabilities if c['capability_type'] == filters['capability_type']]
        if 'min_trust_score' in filters:
            capabilities = [c for c in capabilities if c['trust_score'] >= filters['min_trust_score']]
        if 'max_price' in filters:
            capabilities = [c for c in capabilities if c['price'] <= filters['max_price']]

        return capabilities

    def get_capability(self, capability_id: str) -> Optional[Dict[str, Any]]:
        """Get capability details."""
        # TODO: Get from registry
        return self.capabilities.get(capability_id)

    def get_providers(self) -> List[Dict[str, Any]]:
        """List all capability providers."""
        # TODO: Get from registry
        return list(self.providers.values())

    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get provider details."""
        # TODO: Get from registry.get_provider(provider_id)
        return self.providers.get(provider_id)

    def discover_capabilities(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover capabilities based on requirements."""
        # TODO: Call registry.discover_capabilities(requirements)
        return []

    def match_capabilities(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match and score capabilities against requirements."""
        # TODO: Call registry.match_capabilities(requirements)
        return []

    def revoke_capability(self, capability_id: str) -> None:
        """Revoke a capability."""
        # TODO: Call registry.revoke_capability(capability_id)
        pass


# Singleton instance
registry_service = RegistryService()
