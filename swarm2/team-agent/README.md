# Team Agent

> **Multi-agent orchestration framework with PKI-secured Agent-to-Agent (A2A) communication and intelligent capability discovery**

[![Tests](https://img.shields.io/badge/tests-163%20passing-brightgreen)](utils/tests/)
[![Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen)](docs/testing/code-coverage.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)

---

## 🎯 Overview

Team Agent is a **production-ready multi-agent orchestration framework** that enables AI agents to discover, invoke, and coordinate with each other across a decentralized network. Built with enterprise-grade security (PKI infrastructure) and intelligent trust-based selection, it provides:

- **🤝 Agent-to-Agent (A2A) Communication** - Secure, PKI-based messaging between agents
- **🔍 Intelligent Capability Discovery** - Find and rank capabilities across the network
- **🔐 PKI Control Plane** - Enterprise cryptography with CRL, OCSP, and trust scoring
- **🎯 Dynamic Orchestration** - Mission-driven workflow coordination
- **📊 Trust-Based Selection** - Automatic quality and security assessment

**Perfect for:** Distributed AI systems, multi-agent workflows, secure agent coordination, decentralized capability marketplaces

---

## ✨ Key Features

### 🔐 Enterprise Security (PKI Infrastructure)

```python
# Three-tier Certificate Authority
Root CA (air-gapped)
├── Government CA (policy & governance)
├── Execution CA (runtime operations)
└── Logging CA (audit trail)

# Automatic trust scoring
agent_metrics = trust_tracker.get_agent_metrics("agent-id")
# → trust_score: 95.2/100, success_rate: 98.5%
```

**Features:**
- ✅ RSA-4096 digital signatures
- ✅ Certificate Revocation Lists (CRL)
- ✅ Online Certificate Status Protocol (OCSP)
- ✅ Automated trust scoring (0-100 scale)
- ✅ AES-256-GCM secrets management

### 🤝 Agent-to-Agent Communication

```python
# Secure messaging with automatic signing
client = A2AClient(agent_id="requester", signer=my_signer, ...)
result = await client.invoke_capability(
    capability_id="cap-123",
    parameters={"spec": "Generate fibonacci function"}
)
# → Automatically signed, verified, and trust-checked
```

**Features:**
- ✅ PKI-based message signing
- ✅ Trust-based access control
- ✅ Request/response correlation
- ✅ Automatic capability invocation
- ✅ Concurrent request handling

### 🔍 Intelligent Capability Discovery

```python
# Register a capability
registry.register_capability(
    provider_id="code-agent",
    capability_type=CapabilityType.CODE_GENERATION,
    name="Python Expert",
    price=10.0,
    tags=["python", "production"]
)

# Discover and match
requirement = CapabilityRequirement(
    capability_type=CapabilityType.CODE_GENERATION,
    required_tags=["python"],
    min_trust_score=80.0,
    max_price=15.0
)

matches = registry.match_capabilities(requirement)
# → Ranked by: 40% type match + 30% trust + 20% reputation + 10% cost
```

**Matching Algorithm:**
- **40%** - Type & feature exactness
- **30%** - Provider trust score
- **20%** - Capability reputation
- **10%** - Cost efficiency

### 🎯 Dynamic Orchestration

```python
# Mission-driven coordination
orchestrator = OrchestratorA2A(enable_a2a=True)

mission = MissionSpec(
    mission_id="BUILD-PIPELINE",
    description="Build data analysis pipeline",
    required_capabilities=[
        CapabilityRequirement(
            capability_type=CapabilityType.CODE_GENERATION,
            min_trust_score=85.0,
            max_price=20.0
        )
    ],
    auto_approve_threshold=95.0  # Auto-approve trusted agents
)

results = await orchestrator.execute_mission(mission)
# → Automatically discovers, selects, and coordinates capabilities
```

**Features:**
- ✅ Mission specification with requirements
- ✅ Network-wide capability discovery
- ✅ Auto-approval for high-trust agents (≥95.0)
- ✅ Human-in-the-loop breakpoints
- ✅ Complete audit trail

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/lalbacore/ta_base.git
cd ta_base/swarm2/team-agent

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
python -m pytest utils/tests/ -v
```

### Basic Usage

#### 1. Initialize Systems

```python
from swarms.team_agent.crypto import PKIManager, AgentReputationTracker
from swarms.team_agent.a2a import CapabilityRegistry

# Initialize PKI
pki = PKIManager()

# Initialize trust tracker
trust_tracker = AgentReputationTracker()

# Initialize capability registry
registry = CapabilityRegistry(
    trust_tracker=trust_tracker,
    pki_manager=pki
)
```

#### 2. Register a Capability

```python
from swarms.team_agent.a2a import CapabilityType

# Register your agent as a provider
registry.register_provider(
    provider_id="my-agent",
    provider_type="agent",
    trust_domain=TrustDomain.EXECUTION
)

# Publish a capability
capability = registry.register_capability(
    provider_id="my-agent",
    capability_type=CapabilityType.CODE_GENERATION,
    name="Python Code Generator",
    description="Generate Python code from specifications",
    version="1.0.0",
    price=5.0,
    tags=["python", "code-gen"]
)
```

#### 3. Discover and Match Capabilities

```python
from swarms.team_agent.a2a import CapabilityRequirement

# Create requirement
requirement = CapabilityRequirement(
    capability_type=CapabilityType.CODE_GENERATION,
    required_tags=["python"],
    min_reputation=75.0,
    max_price=10.0,
    min_trust_score=80.0
)

# Find matches
matches = registry.match_capabilities(requirement, limit=5)

# Review matches
for match in matches:
    print(f"{match.capability.name}: {match.overall_score:.1f}/100")
    print(f"  Trust: {match.trust_score:.1f}, Price: ${match.capability.price}")
```

#### 4. Execute a Mission

```python
from swarms.team_agent.orchestrator_a2a import OrchestratorA2A, MissionSpec

# Create orchestrator
orchestrator = OrchestratorA2A(enable_a2a=True)

# Define mission
mission = MissionSpec(
    mission_id="MY-MISSION",
    description="Build a simple calculator",
    required_capabilities=[requirement]
)

# Execute
results = await orchestrator.execute_mission(mission)
print(f"Status: {results['status']}")
print(f"Capabilities used: {len(results['capabilities_used'])}")
```

**See [Quick Start Guide](docs/getting-started/quick-start.md) for detailed tutorial**

---

## 📊 System Status

### Test Coverage

| Component | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| **PKI Infrastructure** | 107 tests | ~85% | ✅ Production Ready |
| **A2A System** | 20 tests | 80% | ✅ Production Ready |
| **Trust Scoring** | 31 tests | ~90% | ✅ Production Ready |
| **Orchestrator** | 5 tests | ~75% | ✅ Production Ready |
| **Overall** | **163 tests** | **~82%** | ✅ **Excellent** |

**All tests passing** • **1.86s test suite** • **Zero critical issues**

### Implementation Status

| Phase | Component | Status | Documentation |
|-------|-----------|--------|---------------|
| 1-4 | PKI Infrastructure | ✅ Complete | [PKI Control Plane](docs/features/pki-control-plane.md) |
| 5 | Secrets Management | ✅ Complete | [Secrets](docs/features/secrets-management.md) |
| 6.1 | Capability Registry | ✅ Complete | [A2A System](docs/features/a2a-system.md) |
| 6.2 | A2A Protocol | ✅ Complete | [A2A Protocol](docs/api/protocol.md) |
| 6.3 | Enhanced Orchestrator | ✅ Complete | [Orchestrator](docs/api/orchestrator.md) |
| 6.4 | Smart Contracts | ⏳ Planned | [Roadmap](docs/architecture/a2a.md#future) |
| 6.5 | MCP Integration | ⏳ Planned | Coming Soon |

---

## 📖 Documentation

**📚 [Complete Documentation Index](docs/DOCUMENTATION_INDEX.md)**

### Quick Links

**Getting Started:**
- [Quick Start Tutorial](docs/getting-started/quick-start.md)
- [Installation Guide](docs/getting-started/installation.md)
- [Examples](docs/getting-started/examples.md)

**Architecture:**
- [System Overview](docs/architecture/overview.md)
- [PKI Infrastructure](docs/architecture/pki.md)
- [A2A System](docs/architecture/a2a.md)

**Features:**
- [PKI Control Plane](docs/features/pki-control-plane.md)
- [A2A Capability Discovery](docs/features/a2a-system.md)
- [Trust Scoring](docs/features/trust-scoring.md)

**Development:**
- [Contributing Guide](CONTRIBUTING.md)
- [Development Setup](docs/development/setup.md)
- [Testing Guide](docs/development/testing.md)

**API Reference:**
- [Capability Registry API](docs/api/registry.md)
- [A2A Protocol API](docs/api/protocol.md)
- [Orchestrator API](docs/api/orchestrator.md)

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  Enhanced Orchestrator                        │
│  • Mission coordination with capability requirements         │
│  • Automatic capability discovery and matching              │
│  • Trust-based selection and auto-approval                  │
└───────────────────┬──────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Capability       │    │  A2A Protocol    │
│ Registry         │◄───┤  • Secure msgs   │
│ • Providers      │    │  • PKI signing   │
│ • Capabilities   │    │  • Trust checks  │
│ • Matching       │    │  • Invocation    │
└────────┬─────────┘    └──────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│      PKI & Trust Infrastructure          │
│  • 3-tier CA (Government/Execution/Log)  │
│  • CRL & OCSP revocation                 │
│  • Trust scoring (0-100)                 │
│  • Secrets management (AES-256-GCM)      │
└──────────────────────────────────────────┘
```

**See [Architecture Overview](docs/architecture/overview.md) for details**

---

## 🎓 Examples

### Complete Workflow Example

```python
import asyncio
from swarms.team_agent.crypto import PKIManager, AgentReputationTracker, TrustDomain
from swarms.team_agent.a2a import CapabilityRegistry, CapabilityType, CapabilityRequirement
from swarms.team_agent.orchestrator_a2a import OrchestratorA2A, MissionSpec

async def main():
    # 1. Initialize
    trust_tracker = AgentReputationTracker()
    pki = PKIManager()
    registry = CapabilityRegistry(trust_tracker=trust_tracker, pki_manager=pki)

    # 2. Build trust for an agent
    for _ in range(50):
        trust_tracker.record_event("expert-agent", EventType.OPERATION_SUCCESS)

    # 3. Register provider and capability
    registry.register_provider("expert-agent", trust_domain=TrustDomain.EXECUTION)
    registry.register_capability(
        provider_id="expert-agent",
        capability_type=CapabilityType.CODE_GENERATION,
        name="Expert Python Developer",
        description="Production-grade Python code generation",
        version="2.0.0",
        price=10.0,
        tags=["python", "expert", "production"]
    )

    # 4. Create and execute mission
    orchestrator = OrchestratorA2A(enable_a2a=True)
    orchestrator.capability_registry = registry

    mission = MissionSpec(
        mission_id="BUILD-001",
        description="Build data processing pipeline",
        required_capabilities=[
            CapabilityRequirement(
                capability_type=CapabilityType.CODE_GENERATION,
                required_tags=["python"],
                min_trust_score=90.0,
                max_price=15.0
            )
        ],
        auto_approve_threshold=95.0
    )

    results = await orchestrator.execute_mission(mission)

    print(f"✅ Mission {results['status']}")
    print(f"Selected: {results['capabilities_used'][0]['selected']}")
    print(f"Provider: {results['capabilities_used'][0]['provider']}")
    print(f"Match Score: {results['capabilities_used'][0]['score']:.1f}/100")

if __name__ == "__main__":
    asyncio.run(main())
```

**More examples:** [docs/getting-started/examples.md](docs/getting-started/examples.md)

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest utils/tests/ -v

# Run specific test suites
python -m pytest utils/tests/test_pki.py -v        # PKI tests (107 tests)
python -m pytest utils/tests/test_a2a_system.py -v # A2A tests (20 tests)

# Run with coverage
python -m pytest utils/tests/test_a2a_system.py \
    --cov=swarms/team_agent/a2a \
    --cov=swarms/team_agent/orchestrator_a2a \
    --cov-report=term-missing \
    --cov-report=html

# View coverage report
open htmlcov/index.html
```

**See [Testing Guide](docs/development/testing.md) for details**

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:

- Code standards and style guide
- Development workflow
- Testing requirements
- Pull request process

**Quick Start:**
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/ta_base.git
cd ta_base/swarm2/team-agent

# Create feature branch
git checkout -b feat/your-feature

# Make changes and test
python -m pytest utils/tests/ -v

# Commit and push
git commit -m "feat: add amazing feature"
git push origin feat/your-feature

# Open pull request on GitHub
```

---

## 📋 Roadmap

### ✅ Completed

- [x] PKI Infrastructure (Phases 1-4)
- [x] Secrets Management (Phase 5)
- [x] Capability Registry (Phase 6.1)
- [x] A2A Protocol (Phase 6.2)
- [x] Enhanced Orchestrator (Phase 6.3)
- [x] Comprehensive test suite (163 tests, 82% coverage)

### 🚧 In Progress

- [ ] Documentation consolidation
- [ ] Performance benchmarks
- [ ] Production deployment guide

### 📅 Planned

**Phase 6.4: Smart Contracts** (Q1 2026)
- On-chain capability registry
- Decentralized trust consensus
- Payment and escrow

**Phase 6.5: MCP Integration** (Q2 2026)
- Model Context Protocol support
- Bridge between A2A and MCP
- Unified tool/capability interface

**Phase 6.6: Production Hardening** (Q2 2026)
- Distributed registry with consensus
- WebSocket/gRPC transport
- Advanced monitoring and alerting

**See [Architecture Roadmap](docs/architecture/a2a.md#roadmap) for details**

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **PKI Infrastructure** - Built on industry-standard cryptography (RSA-4096, AES-256-GCM)
- **Trust Scoring** - Inspired by PageRank and EigenTrust algorithms
- **A2A Protocol** - Designed for decentralized multi-agent systems

---

## 📞 Support

- **Documentation:** [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)
- **Issues:** [GitHub Issues](https://github.com/lalbacore/ta_base/issues)
- **Discussions:** [GitHub Discussions](https://github.com/lalbacore/ta_base/discussions)

---

<div align="center">

**Built with ❤️ by the Team Agent community**

[Documentation](docs/DOCUMENTATION_INDEX.md) • [Contributing](CONTRIBUTING.md) • [Changelog](CHANGELOG.md)

</div>
