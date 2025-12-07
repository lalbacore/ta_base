"""
Agent2Agent (A2A) Protocol Implementation.

Provides client and server components for agent discovery and interoperability.
"""

from .registry import (
    CapabilityRegistry,
    CapabilityType,
    CapabilityStatus,
    Provider,
    Capability,
    CapabilityRequirement,
    CapabilityMatch
)

try:
    from .client import A2AClient
except ImportError:
    pass

try:
    from .discovery import AgentDiscovery, DiscoveryConfig
    from .matcher import AgentMatcher, MatchCriteria, MatchResult
except ImportError:
    pass

__all__ = [
    'A2AClient',
    'CapabilityManifest',
    'AgentDiscovery',
    'DiscoveryConfig',
    'AgentMatcher',
    'MatchCriteria',
    'MatchResult'
]
