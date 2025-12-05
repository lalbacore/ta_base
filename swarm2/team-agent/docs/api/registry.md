# Capability Registry API

Complete API reference for the Capability Registry system.

---

## Overview

The Capability Registry enables agents to publish, discover, and match capabilities across a decentralized network.

**Module**: `swarms.team_agent.a2a.registry`

---

## Classes

### CapabilityRegistry

Central registry for capability management.

```python
from swarms.team_agent.a2a import CapabilityRegistry

registry = CapabilityRegistry(
    db_path: Optional[Path] = None,
    trust_tracker: Optional[AgentReputationTracker] = None,
    pki_manager: Optional[PKIManager] = None
)
```

**Parameters**:
- `db_path` - Path to SQLite database (default: `~/.team_agent/registry.db`)
- `trust_tracker` - Trust scoring system instance
- `pki_manager` - PKI manager for certificate validation

---

## Provider Management

### register_provider()

Register a capability provider.

```python
provider = registry.register_provider(
    provider_id: str,
    provider_type: str = "agent",
    trust_domain: TrustDomain = TrustDomain.EXECUTION,
    certificate_serial: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Provider
```

**Returns**: `Provider` object with trust score integration

---

## Capability Management

### register_capability()

Publish a new capability.

```python
capability = registry.register_capability(
    provider_id: str,
    capability_type: CapabilityType,
    name: str,
    description: str,
    version: str = "1.0.0",
    input_schema: Optional[Dict] = None,
    output_schema: Optional[Dict] = None,
    requirements: Optional[Dict] = None,
    price: float = 0.0,
    estimated_duration: Optional[float] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Capability
```

**Returns**: `Capability` object with unique ID

---

## Discovery

### discover_capabilities()

Find capabilities by criteria.

```python
capabilities = registry.discover_capabilities(
    capability_type: Optional[CapabilityType] = None,
    tags: Optional[List[str]] = None,
    min_reputation: float = 0.0,
    min_trust_score: float = 0.0,
    status: CapabilityStatus = CapabilityStatus.ACTIVE,
    limit: int = 100
) -> List[Tuple[Capability, Provider]]
```

---

## Matching

### match_capabilities()

Match capabilities against requirements.

```python
matches = registry.match_capabilities(
    requirement: CapabilityRequirement,
    limit: int = 10
) -> List[CapabilityMatch]
```

**Scoring Algorithm**:
- 40% - Type and feature match
- 30% - Provider trust score
- 20% - Capability reputation
- 10% - Cost efficiency

---

## Invocation Tracking

### record_invocation()

Track capability usage.

```python
invocation_id = registry.record_invocation(
    capability_id: str,
    requester_id: str,
    status: str,
    duration: Optional[float] = None,
    rating: Optional[float] = None,
    feedback: Optional[str] = None,
    error_message: Optional[str] = None
) -> str
```

---

## Complete Reference

For complete implementation details, see:
- Source: `swarms/team_agent/a2a/registry.py`
- Tests: `utils/tests/test_a2a_system.py`
- Examples: [A2A Examples](../getting-started/examples.md#a2a-examples)
