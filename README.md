# Team Agent - Zero-Trust Orchestrator

A multi-agent orchestration framework strictly engineered to generate **Trusted AI Artifacts**. By natively integrating the Tripartite Architectural framework (Governance, Execution, and Cryptographic Ledger nodes), Team Agent guarantees that every AI sub-agent deployment is mathematically verified and permanently chained to a deterministic provenance record.

## 💡 Why This Matters

As AI Agents gain access to structural operations (Cloud Deployment, Database Manipulation, Shell Commands), the concept of "prompt safety" completely degrades under adversarial obfuscation. Team Agent implements structural security bounds rather than suggestions.

- ✅ **Cryptographic Accountability** - All sub-agent interactions are physically audited and locked to a Turing Tape ledger.
- ✅ **Mathematical Governance** - Built-in AST Lexing parses AI payloads prior to execution, neutralizing sandbox escape techniques.
- ✅ **Specialization** - Deploys isolated expert agents: API Builders, Legal Draftsmen, Cloud Architects.

## 🎯 Technical Vision

Team Agent has been stripped back to its purest form. We have excised the previous web-UI and experimental blockchain marketplace logic to focus exclusively on executing robust, high-trust AI pipelines natively via our Model Context Protocol (MCP) server.

## 🏗️ Architecture

```text
┌────────────────────────────────────────────────────────┐
│                      MCP LLM CLIENT                    │
│    (Claude Desktop / Cursor / Anthropics SDK)          │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│             TEAM AGENT ORCHESTRATOR                    │
│  • Agent Manager (Registration & tracking)             │
│  • Capability Registry (Dynamic discovery)             │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│        ZERO-TRUST TRIPARTITE EXECUTION CHAIN           │
│                                                        │
│  1. 🧠 Proposal (Execution Node)                       │
│     Architect Agent designs infrastructure shell       │
│                                                        │
│  2. ⚖️ Evaluation (Governance Node)                    │
│     Heuristic AST Parsing algebraically verifies bounds│
│                                                        │
│  3. 📜 Ledger (Crypto Tape)                            │
│     Records cryptographic execution manifest           │
└────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

Team Agent is now exclusively mounted as an MCP Server.

1. Ensure the primary dependencies are installed.
2. Run the `fastmcp_server.py` to pipe the framework gracefully into standard `stdio`.

```bash
cd swarm2/team-agent
python fastmcp_server.py
```
This single tool invocation pipes the external LLMs directly into the core Orchestrator logic!
