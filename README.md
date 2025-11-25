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

## 🔒 Air Gap Architecture

The system enforces **cryptographic air gaps** between trust domains. Agents in the Execution Plane cannot access or tamper with the Control Plane, and vice versa. This enables true security isolation and audit integrity.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                      CONTROL PLANE (Trust Domain A)                   ║  │
│  ║                        Cryptographic Air Gap                          ║  │
│  ║                                                                       ║  │
│  ║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ║  │
│  ║  │ GOVERNANCE  │  │   POLICY    │  │  TURING     │  │    KEY      │  ║  │
│  ║  │   AGENT     │  │   ENGINE    │  │   TAPE      │  │  CUSTODIAN  │  ║  │
│  ║  │             │  │             │  │  (Audit)    │  │             │  ║  │
│  ║  │ • Approve   │  │ • Rules     │  │ • Immutable │  │ • Signing   │  ║  │
│  ║  │ • Veto      │  │ • Policies  │  │ • Signed    │  │ • Verify    │  ║  │
│  ║  │ • Escalate  │  │ • Triggers  │  │ • Chained   │  │ • Rotate    │  ║  │
│  ║  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  ║  │
│  ║                                                                       ║  │
│  ║  Keys: Control Plane keys NEVER cross the air gap                    ║  │
│  ║  Auth: Mutual TLS / SPIFFE-SPIRE / Hardware attestation              ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│                    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                       │
│                    ░░░░░░░░░  AIR GAP #1  ░░░░░░░░░░░░                       │
│                    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                       │
│                    ░  • Signed Request/Response Only  ░                      │
│                    ░  • No Direct Memory Access       ░                      │
│                    ░  • No Shared Keys                ░                      │
│                    ░  • Rate Limited                  ░                      │
│                    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                       │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                    EXECUTION PLANE (Trust Domain B)                   ║  │
│  ║                        Cryptographic Air Gap                          ║  │
│  ║                                                                       ║  │
│  ║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ║  │
│  ║  │  ARCHITECT  │  │   BUILDER   │  │   CRITIC    │  │  RECORDER   │  ║  │
│  ║  │             │  │             │  │             │  │             │  ║  │
│  ║  │ • Design    │  │ • Code      │  │ • Review    │  │ • Log       │  ║  │
│  ║  │ • Plan      │  │ • Generate  │  │ • Score     │  │ • Forward   │  ║  │
│  ║  │ • Specify   │  │ • Execute   │  │ • Flag      │  │ • Sign*     │  ║  │
│  ║  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  ║  │
│  ║                                                                       ║  │
│  ║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   ║  │
│  ║  │ CAPABILITY  │  │    MCP      │  │    A2A      │                   ║  │
│  ║  │  REGISTRY   │  │   SERVER    │  │    BUS      │                   ║  │
│  ║  │             │  │             │  │             │                   ║  │
│  ║  │ • Tools     │  │ • Expose    │  │ • Messages  │                   ║  │
│  ║  │ • Domains   │  │ • External  │  │ • Route     │                   ║  │
│  ║  │ • Route     │  │ • Clients   │  │ • Federate  │                   ║  │
│  ║  └─────────────┘  └─────────────┘  └─────────────┘                   ║  │
│  ║                                                                       ║  │
│  ║  Keys: Execution Plane has LIMITED signing (counter-sign only)       ║  │
│  ║  Auth: Service mesh / Workload identity / Scoped tokens              ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│                    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                       │
│                    ░░░░░░░░░  AIR GAP #2  ░░░░░░░░░░░░                       │
│                    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                       │
│                    ░  • One-Way Data Flow Only        ░                      │
│                    ░  • Append-Only Access            ░                      │
│                    ░  • No Write-Back Channel         ░                      │
│                    ░  • Verification Keys Only        ░                      │
│                    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                       │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                   OBSERVATION PLANE (Trust Domain C)                  ║  │
│  ║                      Read-Only / Append-Only Access                   ║  │
│  ║                                                                       ║  │
│  ║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ║  │
│  ║  │    SIEM     │  │   METRICS   │  │   ALERTS    │  │  FORENSICS  │  ║  │
│  ║  │             │  │             │  │             │  │             │  ║  │
│  ║  │ • Splunk    │  │ • Datadog   │  │ • PagerDuty │  │ • Replay    │  ║  │
│  ║  │ • Sentinel  │  │ • Prometheus│  │ • OpsGenie  │  │ • Analysis  │  ║  │
│  ║  │ • QRadar    │  │ • Grafana   │  │ • Slack     │  │ • Evidence  │  ║  │
│  ║  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  ║  │
│  ║                                                                       ║  │
│  ║  Keys: Read-only verification keys / No signing authority            ║  │
│  ║  Auth: One-way data flow / Append-only / No write-back               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Air Gap Enforcement

### Cross-Domain Communication

All communication across air gaps requires cryptographic signing and verification. No direct access is permitted.

```
EXECUTION → CONTROL (Approval Request) [Crosses Air Gap #1]
┌────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌────────────┐
│  Builder   │───▶│ Sign Request    │───▶│    AIR GAP      │───▶│ Governance │
│  (action)  │    │ (Exec Key)      │    │ • Verify sig    │    │  (approve) │
│            │    │                 │    │ • Check policy  │    │            │
│            │    │                 │    │ • Rate limit    │    │            │
└────────────┘    └─────────────────┘    └─────────────────┘    └────────────┘
                                                                       │
                                                                       ▼
┌────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌────────────┐
│  Builder   │◀───│ Verify Response │◀───│    AIR GAP      │◀───│ Governance │
│ (continue) │    │ (Control sig)   │    │ • Sign response │    │ (decision) │
│            │    │                 │    │ • Log to Tape   │    │            │
└────────────┘    └─────────────────┘    └─────────────────┘    └────────────┘


CONTROL → OBSERVATION (Audit Append) [Crosses Air Gap #2]
┌────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌────────────┐
│  Turing    │───▶│ Sign + Chain    │───▶│    AIR GAP      │───▶│    SIEM    │
│   Tape     │    │ (Control Key)   │    │ • One-way only  │    │  (ingest)  │
│            │    │                 │    │ • No write-back │    │            │
└────────────┘    └─────────────────┘    └─────────────────┘    └────────────┘
```

### Key Hierarchy & Air Gap Separation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KEY HIERARCHY                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ROOT OF TRUST (Hardware Security Module / Offline)                         │
│  └── Never exposed, used only for key ceremony                              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ CONTROL PLANE KEYS (Behind Air Gap #1)                              │   │
│  │   ├── Governance Signing Key (approve/deny decisions)               │   │
│  │   ├── Policy Engine Key (rule attestation)                          │   │
│  │   ├── Turing Tape Key (audit chain integrity)                       │   │
│  │   └── Key Custodian Key (key operations, rotation)                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│                    ░░░░░░░░░░ AIR GAP #1 ░░░░░░░░░░░                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ EXECUTION PLANE KEYS (Between Air Gaps)                             │   │
│  │   ├── Agent Identity Keys (per-agent authentication)                │   │
│  │   ├── Session Keys (short-lived, scoped)                            │   │
│  │   └── Counter-Sign Keys (attest to own actions only)                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│                    ░░░░░░░░░░ AIR GAP #2 ░░░░░░░░░░░                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ OBSERVATION PLANE KEYS (Behind Air Gap #2)                          │   │
│  │   └── Verification Keys Only (public keys, no signing)              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

KEY PROPERTIES BY DOMAIN:

| Domain      | Can Sign        | Can Verify      | Can Encrypt     | Can Decrypt     |
|-------------|-----------------|-----------------|-----------------|-----------------|
| Control     | ✅ All          | ✅ All          | ✅ All          | ✅ All          |
| Execution   | ⚠️ Own actions  | ✅ Control sigs | ✅ To Control   | ❌ No           |
| Observation | ❌ No           | ✅ All          | ❌ No           | ❌ No           |
```

---

## 🔐 Air Gap Security Guarantees

### What Execution Plane Agents CANNOT Do:

| Action | Blocked By |
|--------|-----------|
| Forge governance approval | Air Gap #1 - No access to Control Plane signing keys |
| Modify audit trail | Air Gap #1 - Turing Tape signed by Control Plane |
| Bypass policy checks | Air Gap #1 - All actions require Control Plane counter-signature |
| Access other agent's data | Scoped session keys, no cross-agent access |
| Exfiltrate keys | Keys bound to hardware/TEE, non-exportable |
| Replay old approvals | Nonce + timestamp + chain linking |

### What Control Plane CANNOT Do:

| Action | Blocked By |
|--------|-----------|
| Execute agent code | Air Gap #1 - No execution capabilities, policy only |
| Access raw data | Only sees metadata, hashes, requests |
| Modify agent behavior | Can only approve/deny, not instruct |
| Hide decisions | Air Gap #2 - All decisions logged to Observation Plane |

### What Observation Plane CANNOT Do:

| Action | Blocked By |
|--------|-----------|
| Modify logs | Air Gap #2 - Append-only, signed by Control Plane |
| Inject false data | Air Gap #2 - No signing authority |
| Influence decisions | Air Gap #2 - One-way data flow, no write-back |
| Access decrypted data | Verification keys only |

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SYSTEMS                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   MCP    │  │   A2A    │  │  SIEM/   │  │   Key    │  │  Policy  │      │
│  │ Clients  │  │  Agents  │  │   SOC    │  │  Vault   │  │  Engine  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┘
        │             │             │             │             │
        ▼             ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ MCP Server  │  │  A2A Bus    │  │ Log Router  │  │ Crypto Svc  │        │
│  │ (Tools API) │  │ (Agent Msg) │  │ (SIEM/CEF)  │  │ (Sign/Enc)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
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

### Log Event Schema

```json
{
  "timestamp": "2024-11-24T15:30:00.000Z",
  "level": "INFO",
  "workflow_id": "wf_20241124_153000",
  "trace_id": "abc123",
  "span_id": "def456",
  "trust_domain": "execution",
  "agent": "builder",
  "action": "code_generation",
  "capability": "hrt_guide_generator",
  "classification": "internal",
  "duration_ms": 1250,
  "status": "success",
  "governance": {
    "policy_checked": true,
    "approved": true,
    "approver": "governance_agent",
    "control_plane_sig": "sha256:def789..."
  },
  "execution_sig": "sha256:abc123...",
  "chain_prev": "sha256:xyz456..."
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
│  TRUST: MCP clients connect through Air Gap (external boundary) │
└─────────────────────────────────────────────────────────────────┘
```

### Agent-to-Agent (A2A) Protocol

```
A2A MESSAGE SCHEMA:
┌─────────────────────────────────────────────────────────────────┐
│ {                                                                │
│   "id": "msg_uuid",                                             │
│   "type": "request|response|event",                             │
│   "from": "agent://builder",                                    │
│   "to": "agent://critic",                                       │
│   "trust_domain": "execution",                                  │
│   "correlation_id": "workflow_123",                             │
│   "timestamp": "2024-11-24T15:30:00Z",                          │
│   "payload": { ... },                                           │
│   "signature": "sha256:...",                                    │
│   "requires_governance": true,                                  │
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
├── governance/                 # Policy framework (Control Plane)
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
| Core Agents (Execution Plane) | ✅ 5 roles implemented |
| Test Suite | ✅ 171 passed, 6 skipped |
| Capability Registry | ✅ Domain routing |
| PDF Generation | ✅ Working |
| Governance (Control Plane) | ✅ Policy enforcement |
| Air Gap Enforcement | 🔲 Design complete, implementation pending |
| MCP Server | 🔲 Stub only |
| A2A Protocol | 🔲 Stub only |
| SIEM Integration (Observation Plane) | 🔲 Planned |
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

### Phase 3: Air Gap Implementation
- [ ] Cryptographic separation of planes
- [ ] Control Plane key hierarchy
- [ ] Execution Plane scoped keys
- [ ] Air gap enforcement layer
- [ ] Cross-domain signing protocol

### Phase 4: Interoperability
- [ ] MCP server implementation
- [ ] A2A protocol implementation
- [ ] External agent federation
- [ ] Webhook integrations

### Phase 5: Enterprise Security
- [ ] Key vault integration (HashiCorp, AWS KMS, Azure Key Vault)
- [ ] Hardware Security Module (HSM) support
- [ ] Field-level encryption
- [ ] SIEM log shipping (Observation Plane)
- [ ] SOC alert integration
- [ ] Compliance reporting (SOC2, HIPAA, FedRAMP)

### Phase 6: Scale
- [ ] Kubernetes deployment
- [ ] Horizontal scaling
- [ ] Multi-region support
- [ ] Workflow persistence
- [ ] Cross-region trust federation

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

*Founded on the Intent → Capability → Governance triangle concept.*

*Enterprise-ready AI orchestration with cryptographically-enforced air gaps.*