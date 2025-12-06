"""
Agent2Agent (A2A) Protocol Implementation.

Provides client and server components for agent discovery and interoperability.
"""

from .client import A2AClient, AgentCard, CapabilityManifest
from .discovery import AgentDiscovery, DiscoveryConfig
from .matcher import AgentMatcher, MatchCriteria, MatchResult

__all__ = [
    'A2AClient',
    'AgentCard',
    'CapabilityManifest',
    'AgentDiscovery',
    'DiscoveryConfig',
    'AgentMatcher',
    'MatchCriteria',
    'MatchResult'
]
