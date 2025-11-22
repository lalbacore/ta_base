# Team Agent - Modular AI Agent System

## Overview

**Team Agent** is a modular Python framework for building composable AI agent systems. It implements the **Intent → Capability → Governance** triangle as the core design principle.

The system supports:
- **Standalone agents** with specific roles and capabilities
- **Composable teams** that orchestrate multi-agent workflows
- **Policy enforcement** through governance agents
- **Comprehensive logging** with cryptographic signing
- **Multi-system integration** (SIEMs, A2A networks, MCP servers, blockchains)

## Architecture

### Core Components

#### Base Agent (`base/base_agent.py`)
The foundation class for all agents. Provides:
- `__init__(name, id, capabilities, policy)` - Agent initialization
- `evaluate_intent(intent)` - Compliance checking
- `act(intent)` - Action execution or refusal
- `record(event)` - Event logging
- `describe()` - Metadata about the agent

#### Agent Roles (`swarms/team_agent/roles/`)

**Architect** (`architect.py`)
- Designs system architecture based on requirements
- Produces detailed architectural specifications
- Tracks design artifacts and complexity

**Builder** (`builder.py`)
- Implements designs into buildable components
- Generates code and deployment artifacts
- Validates implementation feasibility

**Critic** (`critic.py`)
- Reviews designs and implementations
- Scores quality and compliance
- Identifies risks and provides feedback
- Pass/fail determination based on thresholds

**Governance** (`governance.py`)
- Enforces organizational policies
- Validates compliance across workflow stages
- Creates audit trails
- Makes final approval decisions

**Recorder** (`recorder.py`)
- Logs complete workflow history
- Calculates composite scores
- Creates cryptographic signatures (SHA256)
- Prepares exports for multiple systems:
  - SIEM (Common Event Format)
  - A2A (Agent-to-Agent networks)
  - MCP (Model Context Protocol servers)
  - Blockchain transactions

### Workflow

```
Request
  ↓
[Architect] → Design
  ↓
[Builder] → Build
  ↓
[Critic] → Review
  ↓
[Governance] → Approve/Reject
  ↓
[Recorder] → Log & Sign
  ↓
Result (with signature and audit trail)
```

## Directory Structure

```
team-agent/
├── base/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   └── base_team.py           # Team orchestration (coming soon)
├── swarms/
│   └── team_agent/
│       ├── __init__.py
│       └── roles/
│           ├── __init__.py
│           ├── architect.py
│           ├── builder.py
│           ├── critic.py
│           ├── governance.py
│           └── recorder.py
├── utils/
│   ├── __init__.py
│   └── tests/
│       ├── __init__.py
│       ├── test_base_agent.py
│       ├── test_architect.py
│       ├── test_builder.py
│       ├── test_critic.py
│       ├── test_governance.py
│       └── test_recorder.py
├── .env.example
├── .gitignore
├── .dockerignore
├── pyproject.toml
├── .pylintrc
├── Makefile
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- pip or conda

### Installation

```bash
# Clone the repository
git clone <repo>
cd team-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Running Tests

```bash
# Run all tests
make test

# Run specific role tests
python -m unittest utils.tests.test_architect -v
python -m unittest utils.tests.test_builder -v
python -m unittest utils.tests.test_critic -v
python -m unittest utils.tests.test_governance -v
python -m unittest utils.tests.test_recorder -v

# Run with coverage
make test-coverage

# Lint the code
make lint

# Format the code
make format
```

## Design Principles

### Intent → Capability → Governance Triangle
- **Intent**: What is needed (from request/user)
- **Capability**: What can be done (agent roles & abilities)
- **Governance**: What is allowed (policies & compliance)

This triangle guides all architectural decisions and agent behaviors.

### Key Features
- **Modular**: Each role is independently testable and replaceable
- **Auditable**: Complete audit trails with cryptographic signatures
- **Compliant**: Policy enforcement at every stage
- **Scalable**: Designed for extension to SIEMs, A2A, MCP, blockchains
- **Type-safe**: Strong typing with clear interfaces

## Testing

### Current Test Coverage
- ✅ BaseAgent (5 tests)
- ✅ Architect (7 tests)
- ✅ Builder (9 tests)
- ✅ Critic (12 tests)
- ✅ Governance (13 tests)
- ✅ Recorder (14 tests)

**Total: 60+ tests passing**

### Test Philosophy
- One test file per role
- Incremental testing as roles are developed
- Integration tests for multi-agent workflows
- End-to-end tests for complete workflows

## Development Roadmap

### Phase 1: ✅ Core Agents (Complete)
- [x] Base agent class
- [x] All 5 role implementations
- [x] Unit tests per role
- [x] Integration tests (3-agent, 4-agent, 5-agent workflows)

### Phase 2: Team Orchestration (In Progress)
- [ ] BaseTeam class for workflow coordination
- [ ] End-to-end team tests
- [ ] Error handling and recovery
- [ ] Async/parallel agent execution

### Phase 3: Integrations (Planned)
- [ ] SIEM export adapters
- [ ] A2A protocol implementation
- [ ] MCP server compatibility
- [ ] Blockchain transaction interface

### Phase 4: Enterprise Features (Planned)
- [ ] Advanced policy engine
- [ ] Multi-tenant support
- [ ] Performance monitoring
- [ ] Distributed tracing

## Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Docstring every class and method
- Run `make lint` before committing

### Adding New Roles
1. Create `swarms/team_agent/roles/new_role.py`
2. Extend `BaseAgent`
3. Create `utils/tests/test_new_role.py`
4. Implement role-specific logic
5. Ensure 100% test coverage
6. Update this README

## License

[License information here]

## Credits

**Founding Idea**: Intent → Capability → Governance Triangle

Built with the Team Agent framework for modular, composable AI systems.