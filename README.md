# Team Agent - Modular AI Agent System

A multi-agent orchestration framework implementing the **Intent → Capability → Governance** triangle for AI/Human collaborative workflows.

## 🎯 Core Concept

Every workflow follows three principles:

| Principle | Description |
|-----------|-------------|
| **Intent** | What the user/system wants to accomplish |
| **Capability** | What agents can do to fulfill the intent |
| **Governance** | Policy checks ensuring compliance and safety |

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                           │
│  Coordinates workflow: Design → Build → Review → Record     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   ARCHITECT   │    │    BUILDER    │    │    CRITIC     │
│  Designs the  │───▶│  Implements   │───▶│   Reviews     │
│   solution    │    │   the code    │    │   quality     │
└───────────────┘    └───────────────┘    └───────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  GOVERNANCE   │    │   RECORDER    │    │  CAPABILITY   │
│ Policy checks │    │  Audit trail  │    │   Registry    │
│  & approval   │    │  & signing    │    │   & routing   │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 🚀 Quick Start

```bash
cd swarm2/team-agent
python examples/simple_demo.py
```

## 📁 Project Structure

```
ta_base/
├── swarm2/team-agent/          # Main implementation
│   ├── swarms/team_agent/      # Agent roles & orchestrator
│   │   ├── roles/              # Architect, Builder, Critic, etc.
│   │   ├── capabilities/       # Domain-specific generators
│   │   └── orchestrator.py     # Workflow coordinator
│   ├── examples/               # Demo scripts
│   ├── scripts/                # Utility scripts (HRT guide, etc.)
│   ├── missions/               # YAML mission definitions
│   └── output/                 # Generated artifacts
├── base/                       # Base agent classes
├── governance/                 # Policy framework
└── workflows/                  # Workflow definitions
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Team Agent README](swarm2/team-agent/README.md) | Detailed usage & API |
| [Architecture](swarm2/team-agent/ARCHITECTURE.md) | System design |
| [Development Guide](swarm2/team-agent/DEVELOPMENT.md) | Contributing |
| [Changelog](swarm2/team-agent/CHANGELOG.md) | Version history |

## 🧪 Example Workflows

| Mission | Command | Output |
|---------|---------|--------|
| Hello World | `python examples/quick_test.py` | Basic workflow |
| Calculator | `python examples/simple_demo.py` | Code generation |
| HRT Guide | `python scripts/generate_hrt_guide.py` | 20-page PDF |
| Interactive | `python examples/interactive_demo.py` | REPL mode |

## ✅ Current Status

- **171 tests passing**, 6 skipped
- 5 core agent roles implemented
- Capability registry with domain routing
- PDF document generation working
- Governance policy enforcement active

## 🔮 Roadmap

- [ ] LLM integration (replace mock responses)
- [ ] MCP server implementation
- [ ] Agent-to-agent communication
- [ ] Parallel capability execution
- [ ] Additional domain capabilities

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

*Founded on the Intent → Capability → Governance triangle concept.*