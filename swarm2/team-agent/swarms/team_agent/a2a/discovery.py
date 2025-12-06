"""
Agent Discovery - Unified interface for local and remote agent discovery.

Features:
- Discover local agents from database
- Discover remote agents via A2A protocol
- Unified AgentCard interface
- Caching and fallback strategies
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .client import A2AClient, AgentCard


@dataclass
class DiscoveryConfig:
    """Configuration for agent discovery."""

    # Local discovery
    use_local: bool = True
    local_registry_url: str = "http://localhost:5002"

    # Remote discovery
    use_remote: bool = False
    remote_registries: List[str] = None

    # Performance
    cache_ttl: int = 300  # 5 minutes
    timeout: int = 10

    # Fallback behavior
    fallback_to_local: bool = True  # If remote fails, use local

    def __post_init__(self):
        if self.remote_registries is None:
            self.remote_registries = []


class AgentDiscovery:
    """
    Unified agent discovery across local and remote registries.

    Usage:
        # Local only (default)
        discovery = AgentDiscovery()
        agents = discovery.discover_all()

        # Local + remote
        config = DiscoveryConfig(
            use_remote=True,
            remote_registries=["https://registry.teamagent.ai"]
        )
        discovery = AgentDiscovery(config)
        agents = discovery.discover_all()

        # Find specific agents
        specialists = discovery.find_agents(agent_type="specialist")
        cloud_agents = discovery.find_agents(
            capability_type="cloud_infrastructure",
            min_trust_score=90.0
        )
    """

    def __init__(self, config: Optional[DiscoveryConfig] = None):
        """
        Initialize agent discovery.

        Args:
            config: Discovery configuration (defaults to local only)
        """
        self.config = config or DiscoveryConfig()
        self.client = A2AClient(
            timeout=self.config.timeout,
            cache_ttl=self.config.cache_ttl
        )

        # Cache for unified agent list
        self._unified_cache: Optional[List[AgentCard]] = None

    def discover_all(self, use_cache: bool = True) -> List[AgentCard]:
        """
        Discover all agents from configured sources.

        Args:
            use_cache: Use cached results if available

        Returns:
            Combined list of agents from all sources
        """
        # Check unified cache
        if use_cache and self._unified_cache is not None:
            return self._unified_cache

        agents = []
        errors = []

        # Discover from local registry
        if self.config.use_local:
            try:
                local_agents = self.client.discover_agents(
                    self.config.local_registry_url,
                    use_cache=use_cache
                )
                agents.extend(local_agents)
            except Exception as e:
                errors.append(f"Local discovery failed: {e}")

        # Discover from remote registries
        if self.config.use_remote and self.config.remote_registries:
            for registry_url in self.config.remote_registries:
                try:
                    remote_agents = self.client.discover_agents(
                        registry_url,
                        use_cache=use_cache
                    )
                    agents.extend(remote_agents)
                except Exception as e:
                    errors.append(f"Remote discovery from {registry_url} failed: {e}")

        # Handle errors
        if errors and not agents:
            if self.config.fallback_to_local and not self.config.use_local:
                # Try local as fallback
                try:
                    agents = self.client.discover_agents(
                        self.config.local_registry_url,
                        use_cache=False
                    )
                except Exception as e:
                    raise ConnectionError(
                        f"All discovery sources failed. Errors: {'; '.join(errors)}; "
                        f"Fallback error: {e}"
                    )
            else:
                raise ConnectionError(f"Discovery failed: {'; '.join(errors)}")

        # Deduplicate by agent_id (prefer remote over local if duplicates)
        seen_ids = set()
        unique_agents = []
        for agent in agents:
            if agent.agent_id not in seen_ids:
                seen_ids.add(agent.agent_id)
                unique_agents.append(agent)

        # Cache results
        self._unified_cache = unique_agents

        return unique_agents

    def find_agents(
        self,
        agent_type: Optional[str] = None,
        capability_type: Optional[str] = None,
        min_trust_score: float = 0.0,
        min_success_rate: float = 0.0,
        tags: Optional[List[str]] = None,
        specialties: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> List[AgentCard]:
        """
        Find agents matching criteria.

        Args:
            agent_type: Filter by agent type (role, specialist, tool)
            capability_type: Filter by capability type
            min_trust_score: Minimum trust score (0-100)
            min_success_rate: Minimum success rate (0-1.0)
            tags: Required tags
            specialties: Required specialties
            use_cache: Use cached results if available

        Returns:
            List of matching agents sorted by trust score
        """
        all_agents = self.discover_all(use_cache=use_cache)

        # Apply filters
        matches = []
        for agent in all_agents:
            # Type filter
            if agent_type and agent.agent_type != agent_type:
                continue

            # Trust score filter
            if agent.trust_score < min_trust_score:
                continue

            # Success rate filter
            if agent.success_rate < min_success_rate:
                continue

            # Tags filter
            if tags:
                agent_tags_lower = [t.lower() for t in agent.tags]
                if not all(tag.lower() in agent_tags_lower for tag in tags):
                    continue

            # Specialties filter
            if specialties:
                agent_specs_lower = [s.lower() for s in agent.specialties]
                if not all(spec.lower() in agent_specs_lower for spec in specialties):
                    continue

            # Capability type filter
            if capability_type:
                has_capability = any(
                    cap.get('capability_type') == capability_type
                    for cap in agent.capabilities
                )
                if not has_capability:
                    continue

            matches.append(agent)

        # Sort by trust score and success rate
        matches.sort(
            key=lambda a: (a.trust_score, a.success_rate),
            reverse=True
        )

        return matches

    def get_agent_by_id(self, agent_id: str, use_cache: bool = True) -> Optional[AgentCard]:
        """
        Get specific agent by ID.

        Args:
            agent_id: Agent identifier
            use_cache: Use cached results

        Returns:
            Agent card if found, None otherwise
        """
        all_agents = self.discover_all(use_cache=use_cache)

        for agent in all_agents:
            if agent.agent_id == agent_id:
                return agent

        return None

    def get_agents_by_type(self, agent_type: str, use_cache: bool = True) -> List[AgentCard]:
        """
        Get all agents of a specific type.

        Args:
            agent_type: Type to filter by (role, specialist, tool)
            use_cache: Use cached results

        Returns:
            List of agents of the specified type
        """
        return self.find_agents(agent_type=agent_type, use_cache=use_cache)

    def clear_cache(self):
        """Clear all caches."""
        self._unified_cache = None
        self.client.clear_cache()
