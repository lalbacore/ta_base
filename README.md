# Team Agent - Decentralized Agent Marketplace

A multi-agent orchestration framework evolving into a **decentralized marketplace** for autonomous agent workflows on Ethereum Optimism L2, with enterprise-grade PKI security, capability-based architecture, and flexible payment systems.

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/YOUR_ORG/team-agent)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-56%2F56_passing-brightgreen.svg)](swarm2/team-agent/utils/tests/)

---

## 🎯 Vision

Team Agent is transforming from a standalone orchestrator into a **decentralized agent marketplace** where:

- 🤝 **Agents discover each other** via Agent2Agent (A2A) protocol
- 🔌 **External systems invoke capabilities** via Model Context Protocol (MCP)
- ⛓️ **Workflows execute on-chain** via Ethereum Optimism L2 smart contracts
- 📦 **Artifacts stored permanently** on IPFS/Filecoin
- 💰 **Flexible payments** supporting ETH, OP, USDC, custom tokens, and alternative value stores
- 🔬 **Research assistant platform** for scientists and academic institutions

See **[Decentralized Marketplace Vision](swarm2/team-agent/docs/DECENTRALIZED_MARKETPLACE_VISION.md)** for the complete roadmap.

---

## 🏗️ Current Architecture (Phase 1: Foundation)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MISSION INPUT                                   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR                                       │
│  • PKI Manager (3-tier CA hierarchy: Government, Execution, Logging)         │
│  • Agent Manager (Registration & tracking)                                  │
│  • Capability Registry (Dynamic discovery)                                  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      WORKFLOW EXECUTION PIPELINE                             │
│                                                                              │
│  Phase 1: Architecture                                                       │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │  Architect (EXECUTION domain)                                  │         │
│  │  - Analyzes requirements and designs system architecture       │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                 ▼                                            │
│  Phase 2: Implementation                                                     │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │  DynamicBuilder + Specialist Selection                         │         │
│  │  Current specialists:                                          │         │
│  │  • Legal Specialist (contracts, legal documents)               │         │
│  │  • AWS Cloud Specialist (Terraform, CloudFormation, boto3)     │         │
│  │  • Azure Cloud Specialist (ARM, Terraform, Azure SDK)          │         │
│  │  • GCP Cloud Specialist (Deployment Manager, gcloud)           │         │
│  │  • OCI Cloud Specialist (OCI CLI, Terraform)                   │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                 ▼                                            │
│  Phase 3: Review                                                             │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │  Critic (EXECUTION domain)                                     │         │
│  │  - Reviews code/documents, identifies issues, scores quality   │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                 ▼                                            │
│  Phase 4: Recording                                                          │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │  Recorder (LOGGING domain)                                     │         │
│  │  - Publishes artifacts, creates audit trail, signs outputs     │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                              │
│  Optional: Governance (GOVERNMENT domain)                                    │
│  • Pre-build policy checks • Post-review compliance verification            │
└─────────────────────────────────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ARTIFACTS & AUDIT TRAIL                               │
│  • Generated code/documents                                                  │
│  • Workflow JSON record                                                      │
│  • TuringTape (JSONL append-only log - cryptographically signed)             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 PKI Infrastructure

Three-tier certificate hierarchy with cryptographic signing on all operations:

```
Root CA (self-signed, 10-year validity)
├── Government/Control Plane CA (5-year) → Governance agent
├── Execution Plane CA (5-year) → Architect, Builder, Critic
└── Logging/Artifact Plane CA (5-year) → Recorder
```

**All workflow operations are signed:**
- ✅ TuringTape entries
- ✅ Agent outputs
- ✅ Artifact manifests
- ✅ Audit logs

**Test Coverage:** 56/56 tests passing (including 17 PKI tests)

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.11+
python --version

# Node.js 20+ (for frontend)
node --version
```

### Installation & Setup
```bash
# Navigate to main directory
cd swarm2/team-agent

# Install Python dependencies
pip install -r requirements.txt
pip install -e .

# Run tests to verify installation
pytest utils/tests/ -v

# Expected: 56/56 tests passing
```

### Run Your First Mission
```bash
# Simple demo
python examples/simple_demo.py

# Interactive mode
python examples/interactive_demo.py

# Mission-based execution
python examples/mission_demo.py --simple
```

### Start the Web UI
```bash
# Terminal 1: Backend
cd swarm2/team-agent/backend
python app.py

# Terminal 2: Frontend
cd swarm2/team-agent/frontend
npm install
npm run dev

# Open http://localhost:5173
```

---

## 📁 Project Structure

```
ta_base/
├── README.md (this file)
│
└── swarm2/team-agent/                # Main implementation
    ├── swarms/team_agent/            # Core system
    │   ├── roles/                    # Architect, Builder, Critic, Recorder, Governance
    │   ├── specialists/              # Domain-specific agents (Legal, AWS, Azure, GCP, OCI)
    │   ├── capabilities/             # Capability implementations
    │   │   ├── cloud/                # Cloud infrastructure (AWS, Azure, GCP, OCI)
    │   │   ├── medical/              # Medical documentation
    │   │   └── legal/                # Legal document generation
    │   ├── crypto/                   # PKI, signing, verification, CRL, OCSP
    │   ├── mcp/                      # Model Context Protocol (MCP) server
    │   ├── state/                    # TuringTape, HITL coordination
    │   ├── orchestrator.py           # Main workflow coordinator
    │   └── agent_manager.py          # Agent registration & tracking
    │
    ├── backend/                      # Flask API server
    │   ├── app/
    │   │   ├── api/                  # REST endpoints
    │   │   ├── models/               # Database models
    │   │   ├── services/             # Business logic
    │   │   └── database.py           # SQLAlchemy setup
    │   └── app.py                    # Flask application entry
    │
    ├── frontend/                     # Vue.js + PrimeVue UI
    │   ├── src/
    │   │   ├── views/                # Page components
    │   │   ├── components/           # Reusable components
    │   │   └── router/               # Vue Router setup
    │   └── package.json
    │
    ├── docs/                         # Comprehensive documentation
    │   ├── DECENTRALIZED_MARKETPLACE_VISION.md  # Complete architecture plan
    │   ├── GITHUB_WORKFLOW.md        # PR/issue management guide
    │   ├── QUICK_START_GITHUB.md     # GitHub CLI quick reference
    │   └── PKI_ENHANCEMENTS_COMPLETE.md  # PKI documentation
    │
    ├── scripts/                      # Utility scripts
    │   ├── cleanup_duplicate_agents.py  # Database maintenance
    │   └── create_prs.sh             # Automated PR creation
    │
    ├── examples/                     # Demo scripts
    ├── missions/                     # YAML mission definitions
    ├── utils/tests/                  # Test suite (56 tests)
    └── output/                       # Generated artifacts
```

---

## 📚 Documentation

| Document | Description | Status |
|----------|-------------|--------|
| **[Decentralized Marketplace Vision](swarm2/team-agent/docs/DECENTRALIZED_MARKETPLACE_VISION.md)** | Complete 36-week roadmap for blockchain integration | ✅ Complete |
| **[GitHub Workflow Guide](swarm2/team-agent/docs/GITHUB_WORKFLOW.md)** | PR/issue management, labels, milestones | ✅ Complete |
| **[Quick Start (GitHub)](swarm2/team-agent/docs/QUICK_START_GITHUB.md)** | GitHub CLI reference for contributors | ✅ Complete |
| **[CLAUDE.md](swarm2/team-agent/CLAUDE.md)** | Development guide for Claude Code | ✅ Complete |
| **[PKI Enhancements](swarm2/team-agent/docs/PKI_ENHANCEMENTS_COMPLETE.md)** | PKI infrastructure details | ✅ Complete |

---

## ✅ Current Status (v1.1.0)

### Implemented (Phase 1: Foundation)
| Component | Status | Details |
|-----------|--------|---------|
| **Core Agents** | ✅ Complete | 4 role agents + 5 specialists |
| **PKI Infrastructure** | ✅ Complete | 3-tier CA, signing, CRL, OCSP |
| **Agent Manager** | ✅ Complete | Registration, tracking, trust scores |
| **Capability Registry** | ✅ Complete | Dynamic discovery, keyword matching |
| **Cloud Specialists** | ✅ Complete | AWS, Azure, GCP, OCI provisioning |
| **Legal Specialist** | ✅ Complete | Contract and legal document generation |
| **Web Frontend** | ✅ Complete | Vue.js + PrimeVue UI |
| **Backend API** | ✅ Complete | Flask + SQLAlchemy REST API |
| **Test Suite** | ✅ Complete | 56/56 tests passing |
| **Database** | ✅ Complete | Agent cards, capabilities, mappings |

### In Progress (Phase 2: Weeks 1-4)
| Component | Status | Target |
|-----------|--------|--------|
| **A2A Protocol** | 🔲 Planned | `.well-known/agent.json` endpoint |
| **MCP Server** | 🔲 Planned | HTTP/WebSocket capability invocation |
| **Agent Discovery** | 🔲 Planned | External agent card discovery |

### Roadmap (Phase 3-6: Weeks 5-36)
| Phase | Component | Timeline |
|-------|-----------|----------|
| **Phase 3** | Ethereum Optimism L2 Integration | Weeks 5-20 |
| | • Smart contracts (3 contracts + DAO) | Weeks 5-12 |
| | • IPFS artifact storage | Weeks 13-16 |
| | • Blockchain client integration | Weeks 17-20 |
| **Phase 4** | Flexible Payment System | Weeks 21-24 |
| | • Multi-token support (ETH, OP, USDC) | Week 21 |
| | • Custom value stores | Week 22 |
| **Phase 5** | Research Assistant Platform | Weeks 25-32 |
| | • Research specialists (5 agents) | Weeks 25-28 |
| | • Academic payment models | Weeks 29-32 |
| **Phase 6** | Security & Mainnet Launch | Weeks 33-36 |
| | • Smart contract audit | Week 33-34 |
| | • Mainnet deployment | Week 35-36 |

See **[full roadmap](swarm2/team-agent/docs/DECENTRALIZED_MARKETPLACE_VISION.md)** for details.

---

## 🧪 Example Workflows

### Code Generation
```python
from swarms.team_agent.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.execute("Create a Python REST API for user management")

# → Architect designs API structure
# → Builder generates FastAPI code
# → Critic reviews code quality
# → Recorder publishes artifacts
```

### Cloud Infrastructure
```python
orchestrator = Orchestrator()
result = orchestrator.execute(
    "Deploy a scalable web application on AWS with auto-scaling and RDS database"
)

# → AWS Specialist selected (keyword matching: "AWS")
# → Generates Terraform + CloudFormation + boto3 code
# → Full infrastructure as code
```

### Legal Documents
```python
result = orchestrator.execute("Generate an employment contract for California")

# → Legal Specialist selected
# → Generates comprehensive employment contract
# → Includes state-specific clauses
```

---

## 🔮 Future Vision

### Decentralized Agent Marketplace

**Team Agent is evolving into a marketplace where:**

1. **Agent Discovery** (Phase 2)
   - Agents publish capabilities via A2A protocol
   - External systems discover and invoke via MCP server
   - Dynamic capability matching and routing

2. **Blockchain Execution** (Phase 3)
   - Workflows execute on Ethereum Optimism L2
   - Smart contracts manage workflow state transitions
   - IPFS storage for permanent artifact availability

3. **Flexible Payments** (Phase 4)
   - Multi-token support: ETH, OP, USDC, custom tokens
   - Alternative value stores (research credits, compute time, "magic jelly beans")
   - DAO governance for custom payment methods

4. **Research Platform** (Phase 5)
   - Specialized agents for academic research
   - Literature review, data analysis, experiment design
   - Grant-funded workflows and open science bounties

5. **DAO Governance** (Phase 6)
   - Reputation staking and slashing
   - Community-driven policy enforcement
   - Decentralized trust scoring

**Read the full vision:** [Decentralized Marketplace Architecture](swarm2/team-agent/docs/DECENTRALIZED_MARKETPLACE_VISION.md)

---

## 🤝 Contributing

We welcome contributions! See our [GitHub Workflow Guide](swarm2/team-agent/docs/GITHUB_WORKFLOW.md) for:

- Branch naming conventions
- PR templates and labels
- Commit message format
- Review process
- Milestone planning

### Quick Contribution Guide

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. **Make changes and commit**
   ```bash
   git commit -m "feat(component): add new feature"
   ```
4. **Push and create PR**
   ```bash
   git push origin feat/your-feature-name
   gh pr create --template feature.md
   ```

See **[Quick Start (GitHub)](swarm2/team-agent/docs/QUICK_START_GITHUB.md)** for detailed examples.

---

## 🧑‍💻 Development Setup

### Backend Development
```bash
cd swarm2/team-agent/backend
pip install -r requirements.txt
python app.py

# API available at http://localhost:5002
```

### Frontend Development
```bash
cd swarm2/team-agent/frontend
npm install
npm run dev

# UI available at http://localhost:5173
```

### Run Tests
```bash
cd swarm2/team-agent

# All tests
pytest utils/tests/ -v

# Specific test suite
pytest utils/tests/test_pki.py -v

# With coverage
pytest utils/tests/ -v --cov=swarms --cov=utils
```

### Code Quality
```bash
# Format code
black swarms/ utils/ backend/ --line-length 100

# Sort imports
isort swarms/ utils/ backend/ --profile black

# Type checking
mypy swarms/ utils/ backend/
```

---

## 📊 Project Stats

- **Total Lines of Code:** ~15,000+
- **Test Coverage:** 56/56 tests passing (100% core functionality)
- **Agents:** 4 role agents + 5 specialist agents = 9 total
- **Capabilities:** 6+ registered (Legal, AWS, Azure, GCP, OCI, HRT Guide)
- **Documentation:** 5 comprehensive guides (2,500+ lines)
- **Smart Contracts:** 5 planned (WorkflowConductor, CapabilityMarketplace, ReputationDAO, PaymentRouter, CustomValueRegistry)

---

## 🌟 Key Features

✅ **Multi-Agent Orchestration** - 4-phase workflow (Architect → Builder → Critic → Recorder)
✅ **Capability-Driven Architecture** - Dynamic specialist selection via keyword matching
✅ **Enterprise PKI Security** - 3-tier CA hierarchy with cryptographic signing
✅ **Cloud Infrastructure Specialists** - AWS, Azure, GCP, OCI provisioning
✅ **Legal Document Generation** - Contracts, agreements, compliance documents
✅ **Web Dashboard** - Modern Vue.js + PrimeVue frontend
✅ **Comprehensive Testing** - 56 tests covering core functionality and PKI
🔲 **A2A Protocol** - Agent discovery and federation (Phase 2)
🔲 **MCP Server** - External capability invocation (Phase 2)
🔲 **Blockchain Integration** - Optimism L2 smart contracts (Phase 3)
🔲 **IPFS Storage** - Decentralized artifact storage (Phase 3)
🔲 **Flexible Payments** - Multi-token and custom value stores (Phase 4)
🔲 **Research Platform** - Academic and scientific agents (Phase 5)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Ethereum Optimism** for L2 blockchain infrastructure
- **IPFS/Filecoin** for decentralized storage
- **OpenAI** and **Anthropic** for LLM technology
- **Vue.js** and **PrimeVue** for frontend framework
- **Flask** and **SQLAlchemy** for backend architecture

---

## 📧 Contact & Support

- **Documentation:** [swarm2/team-agent/docs/](swarm2/team-agent/docs/)
- **Issues:** Use GitHub issue templates (bug reports, feature requests)
- **Discussions:** GitHub Discussions for questions and ideas
- **Contributing:** See [GitHub Workflow Guide](swarm2/team-agent/docs/GITHUB_WORKFLOW.md)

---

**Team Agent**: Building the future of decentralized autonomous agent collaboration.

*From standalone orchestrator to decentralized marketplace - one capability at a time.*
