# Team Agent: Zero-Trust Orchestrator

The modern AI landscape is colliding with physical infrastructure. We are rapidly moving beyond models that merely *generate text* to models that *execute actions*—deploying cloud servers, modifying live databases, and orchestrating shell pipelines. 

However, as AI receives structural permissions, the concept of prompt-based safety (e.g., *"please don't delete my production database"*) fundamentally falls apart against adversarial attacks, logic hallucinations, and injection vectors.

**Team Agent** solves this by enforcing an architectural paradigm shift: **Zero-Trust AI Orchestration**.

Instead of vaguely trusting an AI model with elevated permissions, Team Agent cages the execution context within a strict mathematical framework. Every action an AI proposes is intercepted, algebraically verified via AST logic, and physically restricted before actual execution. The entire workflow generates a **Trusted AI Artifact**—a cryptographically signed ledger mathematically proving that every sub-action was legally bound, evaluated, and safely deployed.

---

## 🎯 The "Why": Solving the Autonomous Execution Crisis

Why do you need Team Agent?

### The Problem: Hallucinations Demand Consequences
If you wire an LLM directly to an AWS deployment script or a Linux terminal, you are implicitly trusting that the LLM will not hallucinate or be manipulated into a destructive payload (e.g., `rm -rf /` or `DROP TABLE users`). Standard "system prompts" cannot safeguard against determined adversarial jailbreaks or accidental token drift.

### The Solution: Tripartite Lexical Governance
Team Agent introduces a **Tripartite Execution Chain**:
1. **The Execution Node**: The AI agent organically proposes an action based on your prompt (e.g., executing a command or firing a database query).
2. **The Governance Node**: An immutable, deterministic heuristic engine safely intercepts the proposal. Instead of executing blind shell string matching, the Governance Node geometrically parses the payload into an Abstract Syntax Tree (AST), guaranteeing no hidden escapes, shell chains (`&&`, `|`), or destructive maneuvers are physically present.
3. **The Cryptographic Ledger**: Every proposal and Governance decision is recorded sequentially onto an append-only "Turing Tape." If approved, the process runs. If denied, the exact bounding violation is safely returned to the LLM without ever touching your host system.

When a pipeline finishes, you don't just receive the raw codebase—you get a **Trusted Manifesto** bundled with cryptographic guarantees exactly establishing the bounds of the AI's origin operations.

---

## 🛠️ How It Works: The `TrustedOrchestrator`

Inside Team Agent, the `TrustedOrchestrator` effectively replaces the traditional reckless agent loop. 

When you initialize a command:
1. The Orchestrator securely spins up local **Execution** and **Governance** asymmetric private keypairs.
2. The agent structurally proposes a payload modification.
3. The mathematical heuristic checks explicitly approve or blockade the payload, cryptographically signing the formal ruling.
4. The execution occurs safely inside the isolated host environment.
5. A `trusted_manifest.json` is exported. This manifest isn't just text; it contains the entire verifiable cryptographic ledger. Any sysadmin or security reviewer can mathematically audit the payload logic trace to prove the AI acted deterministically.

---

## 🚀 Quick Start Guide

Team Agent is heavily optimized for seamless integration directly into standard external LLM environments (such as Claude Desktop or Cursor) via **FastMCP** (Anthropic's standard Model Context Protocol).

### Requirements
Ensure that the primary Python dependencies are installed in your active environment:

```bash
cd ta_base
pip install mcp flask cryptography
```

### Exposing the Tripartite Engine via MCP
Instead of struggling to operate the application through a convoluted Web UI, the entire orchestration framework has been condensed into a native MCP server tool. 

If you point a standard desktop LLM compiler to Team Agent, it transparently translates your complex conversational workflows into structurally secure pipelines natively:

```bash
cd swarm2/team-agent
python fastmcp_server.py
```

Under the hood, this command pipes the `Zero-Trust Artifact Orchestrator` through `stdio` utilizing a single `@mcp.tool()` called `run_mission`.

### A Practical Example
1. Hook up Claude Desktop (or your MCP Client) to exactly execute the `fastmcp_server.py` file.
2. Directly prompt the agent: *"Deploy a highly-available Node.js web architecture."*
3. Claude Desktop utilizes standard conversational tracking to trigger the `run_mission` tool in the background.
4. Team Agent takes control, boots up the Architecture engine, structurally evaluates the code generation inside the execution bounds, logs securely to the `CryptoTape`, and returns the verified execution payload back out to Claude!

*Team Agent definitively establishes that the autonomous revolution can scale efficiently, securely, and algebraically.*
