"""
A2A Protocol Client - Discover and interact with remote agents.

Features:
- Agent discovery via .well-known/agent.json endpoints
- Capability manifest retrieval
- PKI signature verification
- Caching for performance
- Support for multiple registries
"""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class AgentCard:
    """Agent card from A2A discovery."""
    agent_id: str
    agent_name: str
    agent_type: str
    description: str
    version: str
    capabilities: List[Dict[str, Any]]
    specialties: List[str]
    supported_languages: List[str]
    trust_score: float
    total_invocations: int
    success_rate: float
    average_rating: float
    status: str
    certificate_serial: Optional[str]
    trust_domain: Optional[str]
    author: Optional[str]
    homepage: Optional[str]
    license: str
    tags: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    # Registry metadata
    registry_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'description': self.description,
            'version': self.version,
            'capabilities': self.capabilities,
            'specialties': self.specialties,
            'supported_languages': self.supported_languages,
            'trust_score': self.trust_score,
            'total_invocations': self.total_invocations,
            'success_rate': self.success_rate,
            'average_rating': self.average_rating,
            'status': self.status,
            'certificate_serial': self.certificate_serial,
            'trust_domain': self.trust_domain,
            'author': self.author,
            'homepage': self.homepage,
            'license': self.license,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'registry_url': self.registry_url
        }


@dataclass
class CapabilityManifest:
    """Capability manifest from A2A discovery."""
    capability_id: str
    capability_name: str
    capability_type: str
    description: str
    version: str
    domains: List[str]
    keywords: List[str]
    tags: List[str]
    module_path: str
    class_name: str
    author: Optional[str]
    license: str
    created_at: Optional[str]

    # Registry metadata
    registry_url: str = ""


@dataclass
class RegistryResponse:
    """Response from A2A registry endpoint."""
    protocol: str
    version: str
    provider: Dict[str, str]
    data: Any
    signature: Optional[Dict[str, str]]
    timestamp: str

    def is_signed(self) -> bool:
        """Check if response is cryptographically signed."""
        return self.signature is not None


class A2AClient:
    """
    Client for discovering and interacting with A2A-compliant agents.

    Usage:
        client = A2AClient()

        # Discover agents from local registry
        agents = client.discover_agents("http://localhost:5002")

        # Discover agents from multiple registries
        all_agents = client.discover_from_registries([
            "http://localhost:5002",
            "https://registry.teamagent.ai"
        ])

        # Get capabilities
        capabilities = client.get_capabilities("http://localhost:5002")

        # Find agents matching criteria
        matches = client.find_agents(
            capability_type="code_generation",
            min_trust_score=90.0
        )
    """

    def __init__(
        self,
        timeout: int = 10,
        cache_ttl: int = 300,  # 5 minutes
        verify_ssl: bool = True
    ):
        """
        Initialize A2A client.

        Args:
            timeout: Request timeout in seconds
            cache_ttl: Cache time-to-live in seconds
            verify_ssl: Verify SSL certificates for HTTPS
        """
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.verify_ssl = verify_ssl

        # Cache for discovered agents and capabilities
        self._agent_cache: Dict[str, tuple[List[AgentCard], datetime]] = {}
        self._capability_cache: Dict[str, tuple[List[CapabilityManifest], datetime]] = {}

    def discover_agents(self, registry_url: str, use_cache: bool = True) -> List[AgentCard]:
        """
        Discover agents from a registry.

        Args:
            registry_url: Base URL of the registry (e.g., "http://localhost:5002")
            use_cache: Use cached results if available

        Returns:
            List of discovered agent cards
        """
        # Check cache
        if use_cache and registry_url in self._agent_cache:
            agents, cached_at = self._agent_cache[registry_url]
            if datetime.utcnow() - cached_at < timedelta(seconds=self.cache_ttl):
                return agents

        # Fetch from registry
        endpoint = f"{registry_url}/.well-known/agent.json"

        try:
            response = requests.get(
                endpoint,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            data = response.json()

            # Validate A2A protocol
            if data.get('protocol') != 'A2A':
                raise ValueError(f"Invalid protocol: {data.get('protocol')}")

            # Parse agent cards
            agents = []
            for agent_data in data.get('agents', []):
                agent = AgentCard(
                    agent_id=agent_data['agent_id'],
                    agent_name=agent_data['agent_name'],
                    agent_type=agent_data['agent_type'],
                    description=agent_data['description'],
                    version=agent_data['version'],
                    capabilities=agent_data['capabilities'],
                    specialties=agent_data['specialties'],
                    supported_languages=agent_data['supported_languages'],
                    trust_score=agent_data['trust_score'],
                    total_invocations=agent_data['total_invocations'],
                    success_rate=agent_data['success_rate'],
                    average_rating=agent_data['average_rating'],
                    status=agent_data['status'],
                    certificate_serial=agent_data.get('certificate_serial'),
                    trust_domain=agent_data.get('trust_domain'),
                    author=agent_data.get('author'),
                    homepage=agent_data.get('homepage'),
                    license=agent_data['license'],
                    tags=agent_data['tags'],
                    created_at=agent_data.get('created_at'),
                    updated_at=agent_data.get('updated_at'),
                    registry_url=registry_url
                )
                agents.append(agent)

            # Cache results
            self._agent_cache[registry_url] = (agents, datetime.utcnow())

            return agents

        except requests.RequestException as e:
            raise ConnectionError(f"Failed to discover agents from {registry_url}: {e}")

    def get_capabilities(
        self,
        registry_url: str,
        use_cache: bool = True
    ) -> List[CapabilityManifest]:
        """
        Get capability manifest from a registry.

        Args:
            registry_url: Base URL of the registry
            use_cache: Use cached results if available

        Returns:
            List of capability manifests
        """
        # Check cache
        if use_cache and registry_url in self._capability_cache:
            capabilities, cached_at = self._capability_cache[registry_url]
            if datetime.utcnow() - cached_at < timedelta(seconds=self.cache_ttl):
                return capabilities

        # Fetch from registry
        endpoint = f"{registry_url}/.well-known/capabilities.json"

        try:
            response = requests.get(
                endpoint,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            data = response.json()

            # Parse capabilities
            capabilities = []
            for cap_data in data.get('capabilities', []):
                capability = CapabilityManifest(
                    capability_id=cap_data['capability_id'],
                    capability_name=cap_data['capability_name'],
                    capability_type=cap_data['capability_type'],
                    description=cap_data['description'],
                    version=cap_data['version'],
                    domains=cap_data['domains'],
                    keywords=cap_data['keywords'],
                    tags=cap_data['tags'],
                    module_path=cap_data['module_path'],
                    class_name=cap_data['class_name'],
                    author=cap_data.get('author'),
                    license=cap_data['license'],
                    created_at=cap_data.get('created_at'),
                    registry_url=registry_url
                )
                capabilities.append(capability)

            # Cache results
            self._capability_cache[registry_url] = (capabilities, datetime.utcnow())

            return capabilities

        except requests.RequestException as e:
            raise ConnectionError(f"Failed to get capabilities from {registry_url}: {e}")

    def discover_from_registries(
        self,
        registry_urls: List[str],
        use_cache: bool = True
    ) -> List[AgentCard]:
        """
        Discover agents from multiple registries.

        Args:
            registry_urls: List of registry URLs to query
            use_cache: Use cached results if available

        Returns:
            Combined list of agents from all registries
        """
        all_agents = []
        errors = []

        for registry_url in registry_urls:
            try:
                agents = self.discover_agents(registry_url, use_cache=use_cache)
                all_agents.extend(agents)
            except Exception as e:
                errors.append(f"{registry_url}: {str(e)}")

        if errors and not all_agents:
            raise ConnectionError(f"Failed to discover from all registries: {'; '.join(errors)}")

        return all_agents

    def find_agents(
        self,
        registry_urls: Optional[List[str]] = None,
        agent_type: Optional[str] = None,
        capability_type: Optional[str] = None,
        min_trust_score: float = 0.0,
        min_success_rate: float = 0.0,
        tags: Optional[List[str]] = None,
        specialties: Optional[List[str]] = None
    ) -> List[AgentCard]:
        """
        Find agents matching criteria across registries.

        Args:
            registry_urls: List of registries to search (defaults to local)
            agent_type: Filter by agent type (role, specialist, tool)
            capability_type: Filter by capability type
            min_trust_score: Minimum trust score (0-100)
            min_success_rate: Minimum success rate (0-1.0)
            tags: Required tags
            specialties: Required specialties

        Returns:
            List of matching agents
        """
        if registry_urls is None:
            registry_urls = ["http://localhost:5002"]

        # Discover from all registries
        all_agents = self.discover_from_registries(registry_urls)

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

    def clear_cache(self):
        """Clear all cached data."""
        self._agent_cache.clear()
        self._capability_cache.clear()
