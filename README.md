# Team Agent - Modular AI Agent System

A multi-agent orchestration framework implementing the **Intent → Capability → Governance** triangle for AI/Human collaborative workflows with enterprise-grade security, auditability, and interoperability.

---

## 🎯 Core Concept

Every workflow follows three principles:

| Principle | Description |
|-----------|-------------|
| **Intent** | What the user/system wants to accomplish |
| **Capability** | What agents can do to fulfill the intent |
| **Governance** | Policy checks ensuring compliance and safety |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SYSTEMS                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   MCP    │  │   A2A    │  │  SIEM/   │  │   Key    │  │  Policy  │      │
│  │ Clients  │  │  Agents  │  │   SOC    │  │  Vault   │  │  Engine  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │             │             │             │             │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┘
        │             │             │             │             │
        ▼             ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ MCP Server  │  │  A2A Bus    │  │ Log Router  │  │ Crypto Svc  │        │
│  │ (Tools API) │  │ (Agent Msg) │  │ (SIEM/CEF)  │  │ (Sign/Enc)  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │                │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ORCHESTRATOR                                      │
│         Coordinates workflow: Design → Build → Review → Record               │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │                    TURING TAPE (Audit Trail)                   │         │
│  │  [Intent] → [Design] → [Build] → [Review] → [Approve] → [Sign] │         │
│  └────────────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│    ARCHITECT    │      │     BUILDER     │      │     CRITIC      │
│   Designs the   │─────▶│   Implements    │─────▶│    Reviews      │
│    solution     │      │    the code     │      │    quality      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
          │                         │                         │
          ▼                         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   GOVERNANCE    │      │    RECORDER     │      │   CAPABILITY    │
│  Policy checks  │      │   Audit trail   │      │    Registry     │
│   & approval    │      │   & signing     │      │   & routing     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## 🔐 Security & Compliance Architecture

### Cryptographic Controls

```
┌─────────────────────────────────────────────────────────────────┐
│                    CRYPTOGRAPHIC SERVICES                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Signing    │    │  Encryption  │    │    Key       │       │
│  │   Service    │    │   Service    │    │  Management  │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    KEY VAULT INTEGRATION                 │    │
│  │  • HashiCorp Vault    • AWS KMS    • Azure Key Vault    │    │
│  │  • GCP KMS            • HSM        • Local Dev Keys     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

SIGNING FLOW:
┌────────┐    ┌────────────┐    ┌─────────┐    ┌──────────┐
│ Action │───▶│ Hash (SHA) │───▶│  Sign   │───▶│  Record  │
│ Output │    │  256/512   │    │ (ECDSA) │    │ to Tape  │
└────────┘    └────────────┘    └─────────┘    └──────────┘

ENCRYPTION FLOW:
┌────────┐    ┌────────────┐    ┌─────────┐    ┌──────────┐
│  Data  │───▶│  Classify  │───▶│ Encrypt │───▶│  Store   │
│ Input  │    │  (PII/PHI) │    │(AES-256)│    │ Secure   │
└────────┘    └────────────┘    └─────────┘    └──────────┘
```

### Data Classification & Handling

| Classification | Examples | Encryption | Retention | Access |
|---------------|----------|------------|-----------|--------|
| **Public** | Docs, guides | Optional | 7 years | All |
| **Internal** | Designs, code | At-rest | 5 years | Team |
| **Confidential** | API keys, configs | At-rest + Transit | 3 years | Role-based |
| **Restricted** | PII, PHI, secrets | At-rest + Transit + Field | 1 year | Need-to-know |

---

## 📊 Logging & Observability

### Log Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT OPERATIONS                            │
│  Architect │ Builder │ Critic │ Governance │ Recorder           │
└──────┬─────┴────┬────┴───┬────┴─────┬──────┴────┬───────────────┘
       │          │        │          │           │
       ▼          ▼        ▼          ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STRUCTURED LOG EMITTER                        │
│  • JSON-structured events                                        │
│  • Correlation IDs (workflow_id, trace_id, span_id)             │
│  • Timestamp (ISO 8601 UTC)                                      │
│  • Classification tags                                           │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   LOCAL LOGS    │  │   LOG ROUTER    │  │  TURING TAPE    │
│  (JSONL files)  │  │   (Fluentd/     │  │ (Immutable      │
│                 │  │    Vector)      │  │  Audit Trail)   │
└─────────────────┘  └────────┬────────┘  └─────────────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│    SIEM     │      │  METRICS    │      │   ALERTS    │
│  Splunk     │      │  Datadog    │      │  PagerDuty  │
│  Sentinel   │      │  Prometheus │      │  OpsGenie   │
│  QRadar     │      │  Grafana    │      │  Slack      │
│  Elastic    │      │  CloudWatch │      │  Teams      │
└─────────────┘      └─────────────┘      └─────────────┘
```

### Log Event Schema

```json
{
  "timestamp": "2024-11-24T15:30:00.000Z",
  "level": "INFO",
  "workflow_id": "wf_20241124_153000",
  "trace_id": "abc123",
  "span_id": "def456",
  "agent": "builder",
  "action": "code_generation",
  "capability": "hrt_guide_generator",
  "classification": "internal",
  "duration_ms": 1250,
  "status": "success",
  "governance": {
    "policy_checked": true,
    "approved": true,
    "approver": "governance_agent"
  },
  "signature": "sha256:abc123..."
}
```

### SIEM Integration Formats

| Target | Format | Transport |
|--------|--------|-----------|
| Splunk | HEC JSON | HTTPS |
| Sentinel | CEF | Syslog/HTTPS |
| QRadar | LEEF | Syslog |
| Elastic | ECS JSON | HTTPS |
| Datadog | JSON | Agent/HTTPS |

---

## 🔗 Interoperability

### Model Context Protocol (MCP)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP SERVER (Team Agent)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  EXPOSED TOOLS:                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • generate_document(type, params) → Document               │ │
│  │ • run_workflow(mission_yaml) → WorkflowResult              │ │
│  │ • check_governance(action, context) → ApprovalResult       │ │
│  │ • query_capabilities(domain) → CapabilityList              │ │
│  │ • get_audit_trail(workflow_id) → TuringTape                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  RESOURCES:                                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • missions:// - Available mission templates                │ │
│  │ • capabilities:// - Registered capabilities                │ │
│  │ • workflows:// - Running/completed workflows               │ │
│  │ • policies:// - Governance policies                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MCP CLIENTS                                │
│  • Claude Desktop    • VS Code Copilot    • Custom Agents       │
│  • Cursor            • Continue           • Automation Scripts  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent-to-Agent (A2A) Protocol

```
┌─────────────────────────────────────────────────────────────────┐
│                    A2A MESSAGE BUS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MESSAGE TYPES:                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   REQUEST   │  │  RESPONSE   │  │   EVENT     │              │
│  │  (Task Req) │  │ (Task Resp) │  │ (Broadcast) │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  ROUTING:                                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Direct: agent://architect/design                         │ │
│  │ • Broadcast: agent://*/notify                              │ │
│  │ • Capability: capability://medical/generate                │ │
│  │ • External: a2a://external-system/endpoint                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

A2A MESSAGE SCHEMA:
┌─────────────────────────────────────────────────────────────────┐
│ {                                                                │
│   "id": "msg_uuid",                                             │
│   "type": "request|response|event",                             │
│   "from": "agent://builder",                                    │
│   "to": "agent://critic",                                       │
│   "correlation_id": "workflow_123",                             │
│   "timestamp": "2024-11-24T15:30:00Z",                          │
│   "payload": { ... },                                           │
│   "signature": "sha256:...",                                    │
│   "ttl": 300                                                    │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

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
│   │   ├── mcp/                # MCP server & client
│   │   ├── agents/             # A2A communication
│   │   ├── state/              # HITL, Turing tape
│   │   └── orchestrator.py     # Workflow coordinator
│   ├── examples/               # Demo scripts
│   ├── scripts/                # Utility scripts
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

## ✅ Current Status (v0.2.0)

| Component | Status |
|-----------|--------|
| Core Agents | ✅ 5 roles implemented |
| Test Suite | ✅ 171 passed, 6 skipped |
| Capability Registry | ✅ Domain routing |
| PDF Generation | ✅ Working |
| Governance | ✅ Policy enforcement |
| MCP Server | 🔲 Stub only |
| A2A Protocol | 🔲 Stub only |
| SIEM Integration | 🔲 Planned |
| Key Vault | 🔲 Planned |

## 🔮 Roadmap

### Phase 1: Core (Current)
- [x] Multi-agent orchestration
- [x] Capability registry
- [x] Governance framework
- [x] Audit trail (Turing tape)

### Phase 2: LLM Integration
- [ ] Claude/GPT-4 integration
- [ ] Local model support (Ollama)
- [ ] Prompt management
- [ ] Cost tracking

### Phase 3: Interoperability
- [ ] MCP server implementation
- [ ] A2A protocol implementation
- [ ] External agent federation
- [ ] Webhook integrations

### Phase 4: Enterprise Security
- [ ] Key vault integration (HashiCorp, AWS KMS)
- [ ] Field-level encryption
- [ ] SIEM log shipping
- [ ] SOC alert integration
- [ ] Compliance reporting (SOC2, HIPAA)

### Phase 5: Scale
- [ ] Kubernetes deployment
- [ ] Horizontal scaling
- [ ] Multi-region support
- [ ] Workflow persistence

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

*Founded on the Intent → Capability → Governance triangle concept.*

*Enterprise-ready AI orchestration with security, auditability, and interoperability built-in.*