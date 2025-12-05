"""
Registry Service - Bridges Flask API to CapabilityRegistry.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import Dict, Any, List, Optional
from app.data.seed_data import SAMPLE_CAPABILITIES, SAMPLE_PROVIDERS


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
        self.providers = {p['provider_id']: p for p in SAMPLE_PROVIDERS}

    def get_capabilities(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List/search capabilities with optional filters.

        Filters:
        - capability_type: Filter by capability type
        - min_trust_score: Minimum trust score
        - max_price: Maximum price
        - tags: Search by tags (comma-separated or list)
        - search: Search in name and description
        """
        # TODO: Get from registry.list_capabilities(filters)
        capabilities = list(self.capabilities.values())

        if not filters:
            # Sort by trust score by default
            capabilities.sort(key=lambda x: x['trust_score'], reverse=True)
            return capabilities

        # Apply filters
        if 'capability_type' in filters and filters['capability_type']:
            capabilities = [c for c in capabilities if c['capability_type'] == filters['capability_type']]

        if 'min_trust_score' in filters and filters['min_trust_score'] is not None:
            min_trust = float(filters['min_trust_score'])
            capabilities = [c for c in capabilities if c['trust_score'] >= min_trust]

        if 'max_price' in filters and filters['max_price'] is not None:
            max_price = float(filters['max_price'])
            capabilities = [c for c in capabilities if c['price'] <= max_price]

        if 'tags' in filters and filters['tags']:
            # Handle both comma-separated string and list
            if isinstance(filters['tags'], str):
                tags = [t.strip() for t in filters['tags'].split(',')]
            else:
                tags = filters['tags']
            capabilities = [
                c for c in capabilities
                if any(tag.lower() in [t.lower() for t in c['tags']] for tag in tags)
            ]

        if 'search' in filters and filters['search']:
            search_term = filters['search'].lower()
            capabilities = [
                c for c in capabilities
                if search_term in c['name'].lower() or search_term in c['description'].lower()
            ]

        # Sort by trust score
        capabilities.sort(key=lambda x: x['trust_score'], reverse=True)

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

    def discover_capabilities(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Discover capabilities based on requirements.

        Requirements format:
        [
            {
                'capability_type': 'code_generation',
                'min_trust_score': 85,
                'max_cost': 100
            }
        ]
        """
        # TODO: Call registry.discover_capabilities(requirements)

        matched_capabilities = []

        for req in requirements:
            cap_type = req.get('capability_type')
            min_trust = req.get('min_trust_score', 0)
            max_cost = req.get('max_cost', float('inf'))

            matches = [
                cap for cap in self.capabilities.values()
                if cap['capability_type'] == cap_type
                and cap['trust_score'] >= min_trust
                and cap['price'] <= max_cost
            ]

            # Sort by trust score
            matches.sort(key=lambda x: x['trust_score'], reverse=True)

            matched_capabilities.extend(matches)

        return matched_capabilities

    def match_capabilities(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Match and score capabilities based on weighted criteria.

        Scoring:
        - Type match: 40%
        - Trust score: 30%
        - Reputation: 20%
        - Cost: 10%
        """
        # TODO: Call registry.match_capabilities(requirements)

        matched = []

        for req in requirements:
            cap_type = req.get('capability_type')
            min_trust = req.get('min_trust_score', 0)
            max_cost = req.get('max_cost', float('inf'))

            for cap in self.capabilities.values():
                # Type match (required)
                if cap['capability_type'] != cap_type:
                    continue

                # Trust score check
                if cap['trust_score'] < min_trust:
                    continue

                # Price check
                if cap['price'] > max_cost:
                    continue

                # Calculate match score (0-100)
                type_score = 40  # Type matches (required)
                trust_score = (cap['trust_score'] / 100) * 30
                reputation_score = (cap['reputation'] / 5.0) * 20

                # Cost score (inverse - lower cost is better)
                if max_cost > 0:
                    cost_score = (1 - min(cap['price'] / max_cost, 1.0)) * 10
                else:
                    cost_score = 0

                match_score = type_score + trust_score + reputation_score + cost_score

                matched.append({
                    **cap,
                    'match_score': round(match_score, 2),
                    'requirement': req
                })

        # Sort by match score
        matched.sort(key=lambda x: x['match_score'], reverse=True)

        return matched

    def revoke_capability(self, capability_id: str) -> None:
        """Revoke a capability."""
        # TODO: Call registry.revoke_capability(capability_id)
        if capability_id in self.capabilities:
            del self.capabilities[capability_id]

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        # TODO: Get from registry

        total_capabilities = len(self.capabilities)
        total_providers = len(self.providers)

        # Count by type
        types_count = {}
        for cap in self.capabilities.values():
            cap_type = cap['capability_type']
            types_count[cap_type] = types_count.get(cap_type, 0) + 1

        # Average metrics
        caps = list(self.capabilities.values())
        avg_trust = sum(c['trust_score'] for c in caps) / total_capabilities if total_capabilities > 0 else 0
        avg_price = sum(c['price'] for c in caps) / total_capabilities if total_capabilities > 0 else 0
        avg_reputation = sum(c['reputation'] for c in caps) / total_capabilities if total_capabilities > 0 else 0
        total_invocations = sum(c['invocations'] for c in caps)

        return {
            'total_capabilities': total_capabilities,
            'total_providers': total_providers,
            'capabilities_by_type': types_count,
            'average_trust_score': round(avg_trust, 1),
            'average_price': round(avg_price, 2),
            'average_reputation': round(avg_reputation, 2),
            'total_invocations': total_invocations
        }


# Singleton instance
registry_service = RegistryService()
