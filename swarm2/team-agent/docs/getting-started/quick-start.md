# Quick Start Guide

Get up and running with Team Agent in under 10 minutes.

---

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for cloning the repository)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lalbacore/ta_base.git
cd ta_base/swarm2/team-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -m pytest utils/tests/ -v
```

You should see:
```
======================== 163 passed in X.XXs ========================
```

---

## Your First Workflow

### Example 1: Simple Code Generation

Create a Python script `my_first_mission.py`:

```python
from swarms.team_agent.orchestrator import Orchestrator

# Create orchestrator
orchestrator = Orchestrator(output_dir="./my_output")

# Define mission
mission = "Create a Python function that calculates the Fibonacci sequence"

# Execute workflow
result = orchestrator.execute(mission)

print(f"✅ Workflow complete!")
print(f"📁 Output saved to: {result['output_dir']}")
```

Run it:
```bash
python my_first_mission.py
```

Check the output:
```bash
ls my_output/wf_*/
# You'll see:
# - workflow_record.json (complete audit trail)
# - generated code files
```

---

## Example 2: Using A2A Capability Discovery

```python
import asyncio
from swarms.team_agent.crypto import PKIManager, AgentReputationTracker, TrustDomain
from swarms.team_agent.a2a import CapabilityRegistry, CapabilityType, CapabilityRequirement
from swarms.team_agent.orchestrator_a2a import OrchestratorA2A, MissionSpec

async def main():
    # 1. Initialize infrastructure
    pki = PKIManager()
    pki.initialize_pki()

    trust_tracker = AgentReputationTracker()
    registry = CapabilityRegistry(
        trust_tracker=trust_tracker,
        pki_manager=pki
    )

    # 2. Register a capability provider
    registry.register_provider(
        provider_id="code-expert",
        provider_type="agent",
        trust_domain=TrustDomain.EXECUTION
    )

    # 3. Publish a capability
    registry.register_capability(
        provider_id="code-expert",
        capability_type=CapabilityType.CODE_GENERATION,
        name="Python Expert",
        description="Expert Python code generation",
        version="1.0.0",
        price=5.0,
        tags=["python", "expert"]
    )

    # 4. Create mission with requirements
    orchestrator = OrchestratorA2A(enable_a2a=True)
    orchestrator.capability_registry = registry

    mission = MissionSpec(
        mission_id="QUICK-START-001",
        description="Build a calculator application",
        required_capabilities=[
            CapabilityRequirement(
                capability_type=CapabilityType.CODE_GENERATION,
                required_tags=["python"],
                min_trust_score=50.0,
                max_price=10.0
            )
        ]
    )

    # 5. Execute mission
    results = await orchestrator.execute_mission(mission)

    print(f"✅ Mission Status: {results['status']}")
    print(f"🎯 Capabilities Used: {len(results['capabilities_used'])}")

    for cap_usage in results['capabilities_used']:
        print(f"\n📦 Capability: {cap_usage['selected']}")
        print(f"   Provider: {cap_usage['provider']}")
        print(f"   Match Score: {cap_usage['score']:.1f}/100")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python my_a2a_mission.py
```

---

## Example 3: Working with PKI and Trust

```python
from swarms.team_agent.crypto import (
    PKIManager,
    AgentReputationTracker,
    EventType,
    TrustDomain
)

# Initialize PKI
pki = PKIManager()
pki.initialize_pki()

# Create trust tracker
tracker = AgentReputationTracker()

# Register an agent
tracker.register_agent("my-agent")

# Record successful operations
for i in range(10):
    tracker.record_event(
        agent_id="my-agent",
        event_type=EventType.OPERATION_SUCCESS,
        response_time=0.5
    )

# Check trust score
metrics = tracker.get_agent_metrics("my-agent")
print(f"Agent Trust Score: {metrics.trust_score:.2f}/100")
print(f"Success Rate: {metrics.success_rate:.1f}%")
print(f"Total Operations: {metrics.total_operations}")

# Get certificate for agent
cert_chain = pki.generate_certificate_chain(
    common_name="my-agent",
    trust_domain=TrustDomain.EXECUTION
)
print(f"✅ Certificate issued for my-agent")
```

---

## Next Steps

Now that you've completed the quick start, here are some recommended next steps:

### Learn More

1. **[System Architecture](../architecture/overview.md)** - Understand how Team Agent works
2. **[PKI Control Plane](../features/pki-control-plane.md)** - Learn about security infrastructure
3. **[A2A System](../features/a2a-system.md)** - Explore capability discovery
4. **[Development Setup](../development/setup.md)** - Set up for contribution

### Run Demonstrations

```bash
# Capability registry demo
python demo_capability_registry.py

# A2A protocol demo
python demo_a2a_protocol.py

# Orchestrator demo
python demo_orchestrator_a2a.py

# Trust scoring demo
python demo_trust_system.py
```

### Explore Examples

Check out the `examples/` directory for more complex use cases:
- Multi-agent workflows
- Custom capability development
- Integration patterns

### Join the Community

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions and share ideas
- **Contributing Guide**: Learn how to contribute

---

## Troubleshooting

### Common Issues

**Import Error: No module named 'swarms'**
```bash
# Make sure you're in the correct directory
cd ta_base/swarm2/team-agent

# Reinstall dependencies
pip install -r requirements.txt
```

**Tests Failing**
```bash
# Clear cache and retry
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache
python -m pytest utils/tests/ -v
```

**Certificate Errors**
```bash
# Reinitialize PKI
python -c "from swarms.team_agent.crypto import PKIManager; PKIManager().initialize_pki(force=True)"
```

### Getting Help

- Check the [Development Setup Guide](../development/setup.md)
- Review the [Architecture Documentation](../architecture/overview.md)
- Open an issue on [GitHub](https://github.com/lalbacore/ta_base/issues)

---

**Ready to build?** Start creating multi-agent workflows with Team Agent!
