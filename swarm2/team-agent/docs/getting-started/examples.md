# Examples

Practical examples demonstrating Team Agent capabilities.

---

## Table of Contents

- [Basic Examples](#basic-examples)
- [PKI Examples](#pki-examples)
- [A2A Examples](#a2a-examples)
- [Trust Scoring Examples](#trust-scoring-examples)
- [Advanced Examples](#advanced-examples)

---

## Basic Examples

### Example 1: Simple Mission Execution

```python
from swarms.team_agent.orchestrator import Orchestrator

# Create orchestrator
orchestrator = Orchestrator(output_dir="./output")

# Execute simple mission
result = orchestrator.execute("Create a Python function to sort a list")

# Access results
print(f"Status: {result['status']}")
print(f"Output directory: {result['output_dir']}")
```

### Example 2: Custom Output Directory

```python
from swarms.team_agent.orchestrator import Orchestrator
from pathlib import Path

# Custom output location
output_path = Path("./my_projects/mission_001")
orchestrator = Orchestrator(output_dir=str(output_path))

mission = "Build a REST API for user management"
result = orchestrator.execute(mission)

# Find generated files
workflow_record = output_path / f"wf_{result['workflow_id']}" / "workflow_record.json"
print(f"Workflow record: {workflow_record}")
```

---

## PKI Examples

### Example 3: Certificate Generation

```python
from swarms.team_agent.crypto import PKIManager, TrustDomain

# Initialize PKI
pki = PKIManager()
pki.initialize_pki()

# Generate certificate for agent
cert_chain = pki.generate_certificate_chain(
    common_name="my-agent",
    trust_domain=TrustDomain.EXECUTION
)

# Access certificate components
print(f"Private key length: {len(cert_chain['key'])} bytes")
print(f"Certificate: {len(cert_chain['cert'])} bytes")
print(f"Chain: {len(cert_chain['chain'])} bytes")

# Get certificate info
cert_info = pki.get_certificate_info(TrustDomain.EXECUTION)
print(f"Serial: {cert_info['serial']}")
print(f"Subject: {cert_info['subject']}")
print(f"Valid until: {cert_info['not_after']}")
```

### Example 4: Signing and Verifying Data

```python
from swarms.team_agent.crypto import PKIManager, Signer, Verifier, TrustDomain

# Setup
pki = PKIManager()
pki.initialize_pki()
cert_chain = pki.get_certificate_chain("execution")

# Create signer
signer = Signer(
    private_key_pem=cert_chain['key'],
    certificate_pem=cert_chain['cert'],
    signer_id="architect-agent"
)

# Sign data
architecture = {
    "components": ["API", "Database", "Frontend"],
    "tech_stack": ["Python", "PostgreSQL", "React"]
}

signed_data = signer.sign_dict(architecture)
print(f"Signed data includes signature: {'_signature' in signed_data}")

# Verify signature
verifier = Verifier(chain_pem=cert_chain['chain'])
is_valid = verifier.verify_dict(signed_data)
print(f"Signature valid: {is_valid}")

# Tamper detection
signed_data["components"].append("Malicious")
is_valid_after_tamper = verifier.verify_dict(signed_data)
print(f"Valid after tampering: {is_valid_after_tamper}")  # False
```

### Example 5: Certificate Revocation

```python
from swarms.team_agent.crypto import PKIManager, TrustDomain, RevocationReason

pki = PKIManager()
pki.initialize_pki()

# Get certificate serial
cert_info = pki.get_certificate_info(TrustDomain.EXECUTION)
serial = cert_info['serial']

# Revoke certificate
pki.revoke_certificate(
    serial_number=serial,
    reason=RevocationReason.KEY_COMPROMISE,
    revoked_by="security-admin",
    trust_domain=TrustDomain.EXECUTION,
    cert_subject="compromised-agent"
)

# Check revocation status
is_revoked = pki.is_revoked(serial)
print(f"Certificate revoked: {is_revoked}")

# Generate CRL
crl_pem = pki.generate_crl(TrustDomain.EXECUTION, validity_days=7)
print(f"CRL generated: {len(crl_pem)} bytes")
```

---

## A2A Examples

### Example 6: Capability Registration

```python
from swarms.team_agent.crypto import PKIManager, AgentReputationTracker, TrustDomain
from swarms.team_agent.a2a import CapabilityRegistry, CapabilityType

# Initialize
pki = PKIManager()
pki.initialize_pki()
trust_tracker = AgentReputationTracker()
registry = CapabilityRegistry(
    trust_tracker=trust_tracker,
    pki_manager=pki
)

# Register provider
registry.register_provider(
    provider_id="data-expert",
    provider_type="agent",
    trust_domain=TrustDomain.EXECUTION
)

# Publish capability
capability = registry.register_capability(
    provider_id="data-expert",
    capability_type=CapabilityType.DATA_ANALYSIS,
    name="Advanced Data Analyzer",
    description="Statistical analysis and visualization",
    version="2.0.0",
    price=15.0,
    tags=["analytics", "statistics", "visualization"],
    input_schema={
        "type": "object",
        "properties": {
            "data": {"type": "array"},
            "analysis_type": {"type": "string"}
        }
    }
)

print(f"Capability registered: {capability.capability_id}")
print(f"Provider: {capability.provider_id}")
print(f"Reputation: {capability.reputation}/100")
```

### Example 7: Capability Discovery and Matching

```python
from swarms.team_agent.a2a import CapabilityRequirement, CapabilityType

# Create requirement
requirement = CapabilityRequirement(
    capability_type=CapabilityType.CODE_GENERATION,
    required_tags=["python", "backend"],
    min_reputation=70.0,
    max_price=20.0,
    min_trust_score=80.0
)

# Find matches
matches = registry.match_capabilities(requirement, limit=5)

# Display results
print(f"Found {len(matches)} matches:\n")
for i, match in enumerate(matches, 1):
    print(f"{i}. {match.capability.name}")
    print(f"   Overall Score: {match.overall_score:.1f}/100")
    print(f"   Trust Score: {match.trust_score:.1f}/100")
    print(f"   Reputation: {match.reputation_score:.1f}/100")
    print(f"   Price: ${match.capability.price}")
    print(f"   Reasons:")
    for reason in match.reasons:
        print(f"     - {reason}")
    print()
```

### Example 8: Mission with Capability Requirements

```python
import asyncio
from swarms.team_agent.orchestrator_a2a import OrchestratorA2A, MissionSpec
from swarms.team_agent.a2a import CapabilityRequirement, CapabilityType

async def main():
    # Create orchestrator
    orchestrator = OrchestratorA2A(enable_a2a=True)

    # Define mission
    mission = MissionSpec(
        mission_id="DATA-PIPELINE-001",
        description="Build a data processing pipeline with Python",
        required_capabilities=[
            CapabilityRequirement(
                capability_type=CapabilityType.CODE_GENERATION,
                required_tags=["python"],
                min_trust_score=80.0,
                max_price=15.0
            ),
            CapabilityRequirement(
                capability_type=CapabilityType.DATA_ANALYSIS,
                required_tags=["analytics"],
                min_trust_score=85.0,
                max_price=20.0
            )
        ],
        max_cost=50.0,
        auto_approve_threshold=95.0
    )

    # Execute
    results = await orchestrator.execute_mission(mission)

    print(f"Mission Status: {results['status']}")
    print(f"Total Cost: ${results['total_cost']:.2f}")
    print(f"\nCapabilities Used:")
    for cap_usage in results['capabilities_used']:
        print(f"  - {cap_usage['selected']} (score: {cap_usage['score']:.1f})")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Trust Scoring Examples

### Example 9: Agent Reputation Tracking

```python
from swarms.team_agent.crypto import AgentReputationTracker, EventType

# Create tracker
tracker = AgentReputationTracker()

# Register agent
tracker.register_agent("production-agent")

# Record successful operations
for i in range(50):
    tracker.record_event(
        agent_id="production-agent",
        event_type=EventType.OPERATION_SUCCESS,
        response_time=0.3
    )

# Record some failures
for i in range(3):
    tracker.record_event(
        agent_id="production-agent",
        event_type=EventType.OPERATION_FAILURE,
        metadata={"reason": "timeout"}
    )

# Get metrics
metrics = tracker.get_agent_metrics("production-agent")
print(f"Trust Score: {metrics.trust_score:.2f}/100")
print(f"Total Operations: {metrics.total_operations}")
print(f"Success Rate: {metrics.success_rate:.1f}%")
print(f"Failure Rate: {metrics.failure_rate:.1f}%")
print(f"Average Response Time: {metrics.average_response_time:.2f}s")
```

### Example 10: Trust-Based Access Control

```python
from swarms.team_agent.crypto import AgentReputationTracker, EventType

tracker = AgentReputationTracker()

# Create agents with different behaviors
agents = {
    "trusted-agent": 100,    # 100 successes
    "unreliable-agent": 20,  # Only 20 successes
}

for agent_id, successes in agents.items():
    tracker.register_agent(agent_id)

    # Record operations
    for _ in range(successes):
        tracker.record_event(agent_id, EventType.OPERATION_SUCCESS)

    # Add failures for unreliable agent
    if agent_id == "unreliable-agent":
        for _ in range(80):
            tracker.record_event(agent_id, EventType.OPERATION_FAILURE)

# Check trust scores
for agent_id in agents:
    metrics = tracker.get_agent_metrics(agent_id)
    trust = metrics.trust_score

    # Access control logic
    if trust >= 90:
        status = "✅ FULL ACCESS"
    elif trust >= 70:
        status = "⚠️  LIMITED ACCESS"
    elif trust >= 50:
        status = "🔒 RESTRICTED"
    else:
        status = "❌ BLOCKED"

    print(f"{agent_id}: {trust:.1f}/100 - {status}")
```

---

## Advanced Examples

### Example 11: Complete PKI Workflow

```python
from swarms.team_agent.crypto import (
    PKIManager,
    AgentReputationTracker,
    EventType,
    TrustDomain,
    Signer,
    Verifier
)

# 1. Initialize infrastructure
pki = PKIManager()
pki.initialize_pki()

tracker = AgentReputationTracker()

# 2. Build trust for agent
agent_id = "reliable-agent"
tracker.register_agent(agent_id)

for _ in range(100):
    tracker.record_event(agent_id, EventType.OPERATION_SUCCESS)

# 3. Issue certificate
cert_chain = pki.generate_certificate_chain(
    common_name=agent_id,
    trust_domain=TrustDomain.EXECUTION
)

# 4. Sign work output
signer = Signer(
    private_key_pem=cert_chain['key'],
    certificate_pem=cert_chain['cert'],
    signer_id=agent_id
)

work_output = {
    "task": "data_processing",
    "result": {"processed": 1000, "errors": 0}
}

signed_output = signer.sign_dict(work_output)

# 5. Verify work
verifier = Verifier(
    chain_pem=cert_chain['chain'],
    crl_manager=pki.crl_manager
)

is_valid = verifier.verify_dict(signed_output)
print(f"Work verified: {is_valid}")

# 6. Get agent metrics
metrics = tracker.get_agent_metrics(agent_id)
print(f"Agent trust: {metrics.trust_score:.1f}/100")
print(f"Operations: {metrics.total_operations}")
```

### Example 12: Security Incident Response

```python
from swarms.team_agent.crypto import (
    PKIManager,
    AgentReputationTracker,
    EventType,
    TrustDomain,
    RevocationReason
)

pki = PKIManager()
pki.initialize_pki()
tracker = AgentReputationTracker()

# Agent starts with good behavior
agent_id = "suspicious-agent"
tracker.register_agent(agent_id)

for _ in range(50):
    tracker.record_event(agent_id, EventType.OPERATION_SUCCESS)

cert_chain = pki.generate_certificate_chain(
    common_name=agent_id,
    trust_domain=TrustDomain.EXECUTION
)

cert_serial = pki.get_certificate_info(TrustDomain.EXECUTION)['serial']

# Security incidents detected
for _ in range(3):
    tracker.record_event(
        agent_id,
        EventType.SECURITY_INCIDENT,
        metadata={"type": "unauthorized_access"}
    )

# Check trust score
metrics = tracker.get_agent_metrics(agent_id)
print(f"Trust score after incidents: {metrics.trust_score:.1f}/100")

# If trust below threshold, revoke certificate
if metrics.trust_score < 50:
    print("🚨 Trust below threshold - revoking certificate")

    pki.revoke_certificate(
        serial_number=cert_serial,
        reason=RevocationReason.KEY_COMPROMISE,
        revoked_by="security-system",
        trust_domain=TrustDomain.EXECUTION,
        cert_subject=agent_id
    )

    print(f"Certificate revoked: {pki.is_revoked(cert_serial)}")
```

---

## Running the Demonstrations

Team Agent includes several demonstration scripts:

```bash
# Capability registry demonstration
python demo_capability_registry.py

# A2A protocol demonstration
python demo_a2a_protocol.py

# Orchestrator demonstration
python demo_orchestrator_a2a.py

# Trust scoring demonstration
python demo_trust_system.py

# Full PKI integration test
python full_pki_integration_test.py
```

---

## Next Steps

- **[Development Setup](../development/setup.md)** - Build custom capabilities
- **[Architecture Overview](../architecture/overview.md)** - Understand the system
- **[API Reference](../api/README.md)** - Detailed API documentation
- **[PKI Control Plane](../features/pki-control-plane.md)** - Security infrastructure
- **[A2A System](../features/a2a-system.md)** - Capability discovery

---

**Ready to build?** Check out the [Development Guide](../development/setup.md) to create custom capabilities!
