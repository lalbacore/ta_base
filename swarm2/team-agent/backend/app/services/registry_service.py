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
        # Initialize database access
        from app.database import get_backend_session
        from app.models.agent import CapabilityRegistry as CapabilityRegistryModel
        self._get_session = get_backend_session
        self._CapabilityRegistry = CapabilityRegistryModel

        # Load seed data for fallback (only used if database is empty)
        self.capabilities_fallback = {cap['capability_id']: cap for cap in SAMPLE_CAPABILITIES}
        self.providers_fallback = {p['provider_id']: p for p in SAMPLE_PROVIDERS}

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
        # Get capabilities from database
        with self._get_session() as session:
            query = session.query(self._CapabilityRegistry).filter_by(status="active")

            # Apply database-level filters
            if filters and 'capability_type' in filters and filters['capability_type']:
                query = query.filter_by(capability_type=filters['capability_type'])

            db_capabilities = query.all()

            # Convert to dict format for API response
            capabilities = []
            for cap in db_capabilities:
                # Parse JSON fields
                import json
                domains = json.loads(cap.domains) if cap.domains else []
                keywords = json.loads(cap.keywords) if cap.keywords else []

                capabilities.append({
                    'capability_id': cap.capability_id,
                    'name': cap.capability_name,
                    'capability_type': cap.capability_type,
                    'description': cap.description,
                    'version': cap.version,
                    'domains': domains,
                    'tags': keywords,  # Use keywords as tags for now
                    'module_path': cap.module_path,
                    'class_name': cap.class_name,
                    'status': cap.status,
                    'created_at': cap.created_at.isoformat() if cap.created_at else None,
                    # Default values for fields not in database yet
                    'trust_score': 95,  # Could be computed from agent_capabilities.success_rate
                    'price': 0.0,  # Free for now
                    'invocations': 0,  # Could be summed from agent_capabilities.times_used
                    'success_rate': 1.0,
                    'reputation': 5.0,
                    'provider_id': 'team_agent',
                    'provider_name': 'Team Agent'
                })

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
        """Get registry statistics from actual database."""
        with self._get_session() as session:
            from sqlalchemy import func

            # Get total capabilities count
            total_capabilities = session.query(func.count(self._CapabilityRegistry.capability_id)).scalar()

            # Get capabilities by type
            capabilities_by_type_query = session.query(
                self._CapabilityRegistry.capability_type,
                func.count(self._CapabilityRegistry.capability_id)
            ).group_by(self._CapabilityRegistry.capability_type).all()

            capabilities_by_type = {row[0]: row[1] for row in capabilities_by_type_query}

            # Get agent statistics (for invocations and success rate)
            from app.models.agent import AgentCard
            total_invocations = session.query(func.sum(AgentCard.total_invocations)).scalar() or 0
            avg_success_rate = session.query(func.avg(AgentCard.success_rate)).scalar() or 0.0
            avg_trust_score = session.query(func.avg(AgentCard.trust_score)).scalar() or 0.0

            return {
                'total_capabilities': total_capabilities,
                'total_providers': 1,  # Currently only 'team_agent' provider
                'capabilities_by_type': capabilities_by_type,
                'average_trust_score': round(avg_trust_score, 1),
                'average_price': 0.0,  # All capabilities are free currently
                'average_reputation': round(avg_success_rate * 5.0, 1),  # Map success_rate to 0-5 scale
                'total_invocations': total_invocations
            }


# Singleton instance
registry_service = RegistryService()
