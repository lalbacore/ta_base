# API Reference

Complete API documentation for Team Agent.

---

## Overview

This section provides detailed API reference for all Team Agent components.

---

## Core Components

### Orchestration
- **[Orchestrator API](orchestrator.md)** - Workflow orchestration and execution
- **[OrchestratorA2A API](orchestrator-a2a.md)** - A2A-enhanced orchestrator with capability discovery

### Agent-to-Agent (A2A)
- **[Capability Registry API](registry.md)** - Publishing and discovering capabilities
- **[A2A Protocol API](protocol.md)** - Secure agent-to-agent messaging
- **[Mission Specifications](mission.md)** - Mission and requirement definitions

### PKI & Security
- **[PKI Manager API](pki.md)** - Certificate authority and PKI operations
- **[Signer API](signer.md)** - Digital signature creation
- **[Verifier API](verifier.md)** - Signature verification
- **[Trust Tracker API](trust.md)** - Agent reputation and trust scoring
- **[Secrets Manager API](secrets.md)** - Encrypted secrets management

### Roles
- **[Base Role API](roles.md)** - Base class for all agent roles
- **[Architect API](roles.md#architect)** - Architecture design agent
- **[Builder API](roles.md#builder)** - Implementation agent
- **[Critic API](roles.md#critic)** - Review and quality assurance agent

---

## Quick Navigation

### By Use Case

**Building Workflows:**
1. [Orchestrator API](orchestrator.md) - Start here
2. [Mission Specifications](mission.md) - Define requirements
3. [Capability Registry API](registry.md) - Discover capabilities

**Security & Trust:**
1. [PKI Manager API](pki.md) - Certificate management
2. [Trust Tracker API](trust.md) - Reputation tracking
3. [Signer/Verifier APIs](signer.md) - Cryptographic operations

**Agent Communication:**
1. [A2A Protocol API](protocol.md) - Messaging infrastructure
2. [Capability Registry API](registry.md) - Service discovery

---

## Common Patterns

### Pattern 1: Initialize System

```python
from swarms.team_agent.crypto import PKIManager, AgentReputationTracker
from swarms.team_agent.a2a import CapabilityRegistry

# PKI
pki = PKIManager()
pki.initialize_pki()

# Trust
trust_tracker = AgentReputationTracker()

# Registry
registry = CapabilityRegistry(
    trust_tracker=trust_tracker,
    pki_manager=pki
)
```

### Pattern 2: Execute Mission

```python
from swarms.team_agent.orchestrator_a2a import OrchestratorA2A, MissionSpec
from swarms.team_agent.a2a import CapabilityRequirement, CapabilityType

# Create orchestrator
orchestrator = OrchestratorA2A(enable_a2a=True)
orchestrator.capability_registry = registry

# Define mission
mission = MissionSpec(
    mission_id="MISSION-001",
    description="Build application",
    required_capabilities=[
        CapabilityRequirement(
            capability_type=CapabilityType.CODE_GENERATION,
            min_trust_score=80.0
        )
    ]
)

# Execute
results = await orchestrator.execute_mission(mission)
```

### Pattern 3: Sign and Verify

```python
from swarms.team_agent.crypto import Signer, Verifier

# Sign
signer = Signer(
    private_key_pem=cert_chain['key'],
    certificate_pem=cert_chain['cert'],
    signer_id="my-agent"
)
signed_data = signer.sign_dict({"key": "value"})

# Verify
verifier = Verifier(chain_pem=cert_chain['chain'])
is_valid = verifier.verify_dict(signed_data)
```

---

## Type Definitions

### Common Types

```python
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Trust domains
class TrustDomain(Enum):
    GOVERNMENT = "government"
    EXECUTION = "execution"
    LOGGING = "logging"

# Capability types
class CapabilityType(Enum):
    CODE_GENERATION = "code_generation"
    DATA_ANALYSIS = "data_analysis"
    # ... see full list in registry.md

# Event types
class EventType(Enum):
    OPERATION_SUCCESS = "operation_success"
    OPERATION_FAILURE = "operation_failure"
    SECURITY_INCIDENT = "security_incident"
    # ... see full list in trust.md
```

---

## Error Handling

### Common Exceptions

```python
# PKI Exceptions
class CertificateRevokedException(Exception):
    """Certificate has been revoked"""
    pass

class CertificateExpiredException(Exception):
    """Certificate has expired"""
    pass

# Registry Exceptions
class ProviderNotFoundException(Exception):
    """Provider not found in registry"""
    pass

class CapabilityNotFoundException(Exception):
    """Capability not found"""
    pass

# Trust Exceptions
class InsufficientTrustException(Exception):
    """Agent trust score below threshold"""
    pass
```

### Error Handling Pattern

```python
try:
    result = await orchestrator.execute_mission(mission)
except CertificateRevokedException as e:
    print(f"Certificate revoked: {e}")
    # Handle revocation
except InsufficientTrustException as e:
    print(f"Trust too low: {e}")
    # Handle low trust
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other errors
```

---

## Configuration

### Default Values

```python
# PKI Configuration
DEFAULT_KEY_SIZE = 4096
DEFAULT_HASH_ALGORITHM = "SHA256"
DEFAULT_CERT_VALIDITY_DAYS = 365

# Trust Configuration
DEFAULT_BASE_TRUST_SCORE = 100.0
DEFAULT_MIN_TRUST_THRESHOLD = 50.0

# Registry Configuration
DEFAULT_DB_PATH = "~/.team_agent/registry.db"
DEFAULT_MATCH_LIMIT = 10
```

### Environment Variables

```bash
# Override PKI directory
export TEAM_AGENT_PKI_DIR="~/.team_agent/pki"

# Override database location
export TEAM_AGENT_DB_DIR="~/.team_agent"

# Enable debug mode
export TEAM_AGENT_DEBUG=1
```

---

## Versioning

API versioning follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

**Current Version**: See [CHANGELOG.md](../../CHANGELOG.md)

---

## Related Documentation

- [Architecture Overview](../architecture/overview.md) - System design
- [Quick Start Guide](../getting-started/quick-start.md) - Get started quickly
- [Examples](../getting-started/examples.md) - Practical examples
- [Development Setup](../development/setup.md) - For contributors

---

**Need help?** Check the [examples](../getting-started/examples.md) or open an issue on [GitHub](https://github.com/lalbacore/ta_base/issues).
