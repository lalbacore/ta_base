"""
Unit tests for A2A client library.

Tests:
- Agent discovery (local and remote)
- Capability manifest retrieval
- Agent matching and scoring
- Unified discovery interface
"""

import pytest
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from swarms.team_agent.a2a import (
    A2AClient,
    AgentCard,
    AgentDiscovery,
    DiscoveryConfig,
    AgentMatcher,
    MatchCriteria
)


class TestA2AClient:
    """Test A2A client."""

    def test_discover_local_agents(self):
        """Test discovering agents from local registry."""
        client = A2AClient()

        agents = client.discover_agents("http://localhost:5002")

        assert len(agents) > 0
        assert all(isinstance(agent, AgentCard) for agent in agents)

        # Check first agent has required fields
        agent = agents[0]
        assert agent.agent_id
        assert agent.agent_name
        assert agent.agent_type in ['role', 'specialist', 'tool']
        assert agent.license
        assert 0 <= agent.trust_score <= 100
        assert 0 <= agent.success_rate <= 1.0

    def test_get_capabilities(self):
        """Test getting capability manifest."""
        client = A2AClient()

        capabilities = client.get_capabilities("http://localhost:5002")

        assert len(capabilities) > 0

        # Check first capability structure
        cap = capabilities[0]
        assert cap.capability_id
        assert cap.capability_name
        assert cap.capability_type
        assert isinstance(cap.domains, list)
        assert isinstance(cap.keywords, list)

    def test_find_agents_by_type(self):
        """Test finding agents by type."""
        client = A2AClient()

        # Find specialists
        specialists = client.find_agents(
            registry_urls=["http://localhost:5002"],
            agent_type="specialist"
        )

        assert len(specialists) > 0
        assert all(agent.agent_type == "specialist" for agent in specialists)

        # Find roles
        roles = client.find_agents(
            registry_urls=["http://localhost:5002"],
            agent_type="role"
        )

        assert len(roles) > 0
        assert all(agent.agent_type == "role" for agent in roles)

    def test_find_agents_by_trust_score(self):
        """Test filtering by trust score."""
        client = A2AClient()

        # Find high-trust agents
        high_trust = client.find_agents(
            registry_urls=["http://localhost:5002"],
            min_trust_score=95.0
        )

        assert all(agent.trust_score >= 95.0 for agent in high_trust)

    def test_caching(self):
        """Test that caching works."""
        client = A2AClient(cache_ttl=300)

        # First call - should hit network
        agents1 = client.discover_agents("http://localhost:5002", use_cache=False)

        # Second call with cache - should be instant
        agents2 = client.discover_agents("http://localhost:5002", use_cache=True)

        # Should return same data
        assert len(agents1) == len(agents2)
        assert agents1[0].agent_id == agents2[0].agent_id

        # Clear cache
        client.clear_cache()

        # Should hit network again
        agents3 = client.discover_agents("http://localhost:5002", use_cache=True)
        assert len(agents3) == len(agents1)


class TestAgentDiscovery:
    """Test unified agent discovery."""

    def test_discover_local_only(self):
        """Test local-only discovery (default)."""
        config = DiscoveryConfig(use_local=True, use_remote=False)
        discovery = AgentDiscovery(config)

        agents = discovery.discover_all()

        assert len(agents) > 0
        assert all(isinstance(agent, AgentCard) for agent in agents)

    def test_find_specialists(self):
        """Test finding specialists."""
        discovery = AgentDiscovery()

        specialists = discovery.find_agents(agent_type="specialist")

        assert len(specialists) > 0
        assert all(agent.agent_type == "specialist" for agent in specialists)

    def test_find_cloud_agents(self):
        """Test finding cloud infrastructure agents."""
        discovery = AgentDiscovery()

        # Find agents with cloud_infrastructure capability
        cloud_agents = discovery.find_agents(
            capability_type="cloud_infrastructure"
        )

        # Should find AWS, Azure, GCP, OCI specialists
        assert len(cloud_agents) >= 4

    def test_get_agent_by_id(self):
        """Test getting specific agent by ID."""
        discovery = AgentDiscovery()

        # Get all agents first
        all_agents = discovery.discover_all()
        assert len(all_agents) > 0

        # Get specific agent
        target_id = all_agents[0].agent_id
        agent = discovery.get_agent_by_id(target_id)

        assert agent is not None
        assert agent.agent_id == target_id

    def test_cache_clearing(self):
        """Test cache clearing."""
        discovery = AgentDiscovery()

        # Populate cache
        agents1 = discovery.discover_all()

        # Clear cache
        discovery.clear_cache()

        # Should fetch again
        agents2 = discovery.discover_all()

        assert len(agents1) == len(agents2)


class TestAgentMatcher:
    """Test agent matching and scoring."""

    def test_match_by_capability(self):
        """Test matching agents by capability type."""
        discovery = AgentDiscovery()
        agents = discovery.discover_all()

        matcher = AgentMatcher()
        criteria = MatchCriteria(
            capability_type="cloud_infrastructure",
            min_trust_score=80.0
        )

        matches = matcher.match_agents(agents, criteria)

        assert len(matches) > 0
        assert all(m.score > 0 for m in matches)
        assert all(m.agent.trust_score >= 80.0 for m in matches)

        # Matches should be sorted by score
        for i in range(len(matches) - 1):
            assert matches[i].score >= matches[i+1].score

    def test_match_by_specialties(self):
        """Test matching by required specialties."""
        discovery = AgentDiscovery()
        agents = discovery.discover_all()

        matcher = AgentMatcher()
        criteria = MatchCriteria(
            required_specialties=["aws"],
            agent_type="specialist"
        )

        matches = matcher.match_agents(agents, criteria)

        # Should find AWS specialist
        assert len(matches) > 0
        assert any("aws" in agent.agent_name.lower() for match in matches for agent in [match.agent])

    def test_get_best_match(self):
        """Test getting single best match."""
        discovery = AgentDiscovery()
        agents = discovery.discover_all()

        matcher = AgentMatcher()
        criteria = MatchCriteria(
            agent_type="specialist",
            min_trust_score=90.0,
            min_success_rate=0.9
        )

        best = matcher.get_best_match(agents, criteria)

        assert best is not None
        assert best.score > 0
        assert best.agent.trust_score >= 90.0
        assert best.agent.success_rate >= 0.9

    def test_scoring_weights(self):
        """Test that scoring weights are validated."""
        # Valid weights (sum to 1.0)
        criteria = MatchCriteria(
            trust_score_weight=0.4,
            success_rate_weight=0.3,
            experience_weight=0.2,
            rating_weight=0.1
        )
        assert criteria is not None

        # Invalid weights (don't sum to 1.0)
        with pytest.raises(ValueError):
            MatchCriteria(
                trust_score_weight=0.5,
                success_rate_weight=0.5,
                experience_weight=0.5,
                rating_weight=0.5
            )

    def test_match_reasons(self):
        """Test that match reasons are provided."""
        discovery = AgentDiscovery()
        agents = discovery.discover_all()

        matcher = AgentMatcher()
        criteria = MatchCriteria(min_trust_score=90.0)

        matches = matcher.match_agents(agents, criteria)

        if matches:
            # Best match should have reasons
            best = matches[0]
            assert len(best.match_reasons) > 0
            assert all(isinstance(reason, str) for reason in best.match_reasons)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
