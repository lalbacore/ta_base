"""
Bridge package to maintain backward compatibility for tests expecting utils.capabilities.*
Re-exports objects from swarms.team_agent.capabilities.
"""
from swarms.team_agent.capabilities.registry import CapabilityRegistry
from swarms.team_agent.capabilities.base_capability import BaseCapability

# Optional capabilities
try:
    from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability
except ImportError:
    HRTGuideCapability = None