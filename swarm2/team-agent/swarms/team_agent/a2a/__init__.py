"""
Agent-to-Agent (A2A) communication and capability discovery.

This package provides:
- Capability registry for publishing and discovering agent capabilities
- A2A protocol for direct agent-to-agent communication
- Smart contract integration for decentralized capability marketplace
- Trust-based capability matching and ranking
"""

from .registry import (
    CapabilityRegistry,
    Capability,
    CapabilityType,
    CapabilityStatus,
    Provider,
    CapabilityRequirement,
    CapabilityMatch,
)

from .protocol import (
    A2AClient,
    A2AServer,
    A2AMessage,
    A2ARequest,
    MessageType,
    RequestStatus,
)

__all__ = [
    # Registry
    "CapabilityRegistry",
    "Capability",
    "CapabilityType",
    "CapabilityStatus",
    "Provider",
    "CapabilityRequirement",
    "CapabilityMatch",
    # Protocol
    "A2AClient",
    "A2AServer",
    "A2AMessage",
    "A2ARequest",
    "MessageType",
    "RequestStatus",
]
