# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Team Agent is a capability-driven multi-agent orchestration framework that coordinates specialized AI agents (Architect, Builder, Critic, Recorder) to execute complex missions. The key innovation is a **capability system** that allows the Builder to dynamically select domain-specific knowledge modules at runtime.

**Working Directory**: All commands should be run from `team-agent/` directory.

## Essential Commands

### Setup
```bash
cd team-agent
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
# Run all tests
pytest utils/tests/ -v

# Run specific test suites
pytest utils/tests/test_capabilities.py -v
pytest utils/tests/test_capability_registry.py -v
pytest utils/tests/test_orchestrator_capabilities.py -v
pytest utils/tests/test_siem_integration.py -v  # Requires ELK stack running

# Run capability tests via helper script
python examples/run_capability_tests.py

# Run with coverage
pytest utils/tests/ -v --cov=swarms --cov=utils

# PKI system tests
python utils/tests/test_pki.py
```

### Running Examples
```bash
# Simple demo
python examples/simple_demo.py

# Interactive demo
python examples/interactive_demo.py

# Mission-based execution
python examples/mission_demo.py --simple
python examples/mission_demo.py --yaml missions/calculator.yaml
```

### Code Quality
```bash
# Format code
black swarms/ utils/ --line-length 100

# Sort imports
isort swarms/ utils/ --profile black

# Lint
pylint swarms/ utils/
flake8 swarms/ utils/

# Type checking
mypy swarms/ utils/
```

## Architecture Overview

### PKI Infrastructure (Cryptographic Trust Layer)

Team Agent implements a **three-tier Public Key Infrastructure (PKI)** that provides cryptographic signing and verification across all workflow operations:

**Certificate Hierarchy:**
```
Root CA (self-signed, 10-year validity)
├── Government/Control Plane CA (5-year validity)
│   └── Used by: governance.py
├── Execution Plane CA (5-year validity)
│   └── Used by: architect.py, builder.py, critic.py
└── Logging/Artifact Plane CA (5-year validity)
    └── Used by: recorder.py
```

**Trust Domains:**
- **Government** (`TrustDomain.GOVERNMENT`): Policy enforcement and compliance
- **Execution** (`TrustDomain.EXECUTION`): Design and implementation work
- **Logging** (`TrustDomain.LOGGING`): Artifact publishing and audit trails

**Key Files:**
- Location: `.team_agent/pki/`
- Root CA: `.team_agent/pki/root/root-ca.{key,crt}`
- Intermediate CAs: `.team_agent/pki/{government,execution,logging}/{domain}-ca.{key,crt,chain.pem}`

**Signing Operations:**
- **TuringTape entries**: All workflow state transitions are signed
- **Agent outputs**: Architect, Builder, Critic, Governance, Recorder sign their outputs
- **Artifacts**: Published files include cryptographic signatures
- **Logs**: Structured logs are signed for audit integrity

**PKI Components:**
- `swarms/team_agent/crypto/pki.py`: PKIManager for CA generation
- `swarms/team_agent/crypto/signing.py`: Signer and Verifier classes
- Orchestrator initializes PKI and distributes cert chains to roles

**Testing PKI:**
```bash
python utils/tests/test_pki.py  # 17 comprehensive tests
```

### Core Workflow Pattern
```
Mission → Architect → Builder (w/ Capabilities) → Critic → Recorder → Artifacts
```

The orchestrator (`orchestrator.py`) coordinates this 4-phase workflow where:
1. **Architect** analyzes requirements and designs system architecture
2. **Builder** selects and executes appropriate capability based on mission
3. **Critic** reviews generated code/documents and provides quality scores
4. **Recorder** publishes final artifacts and creates comprehensive records

### Key Architectural Components

#### 1. Capability System (`swarms/team_agent/capabilities/`)
**Strategy Pattern Implementation**: Capabilities are interchangeable plugins selected at runtime.

- **`base_capability.py`**: Abstract base class defining the capability interface
  - `get_metadata()`: Returns name, type, domains, version
  - `matches(requirements)`: Determines if capability suits a mission
  - `execute(context)`: Performs the actual work
  - `validate_context(context)`: Ensures required inputs are present

- **`registry.py`**: Central capability discovery system
  - Indexes capabilities by type (`code_generation`, `document_generation`) and domain (`medical`, `web`, etc.)
  - Supports keyword search and requirement matching
  - Handles both object and dict capability formats

- **Capability Types**:
  - `document_generator.py`: Generic document generation
  - `medical/hrt_guide.py`: Specialized HRT clinical guide generator
  - Custom capabilities: See "Adding a New Capability" section

#### 2. Role System (`swarms/team_agent/roles/`)
All roles inherit from `base_role.py` and implement `run(context: Dict) -> Dict`.

- **`architect.py`**: Architecture planning and technical specifications
- **`builder.py`**: Generic builder (fallback when no specialized capability matches)
- **`critic.py`**: Code review, quality scoring, issue identification
- **`recorder.py`**: Artifact publishing and metadata generation
- **`governance.py`**: Policy enforcement (optional layer)

**Note**: `dynamic_builder.py` (located in `utils/capabilities/`) wraps the capability selection logic.

#### 3. Tool System (`swarms/team_agent/tools/`)
**Reusable functionality exposed via MCP (Model Context Protocol):**

- **`base.py`**: `BaseTool` interface with `ToolMetadata`, `ToolResult`, `ToolStatus`
  - All tools have `execute(params)` method
  - Support governance approval via `requires_governance` flag
  - Trust domains: `execution`, `filesystem`, `network`

- **Tool Categories**:
  - `file_tools.py`: File operations
  - `code_tools.py`: Code analysis and generation
  - `analysis_tools.py`: Data analysis
  - `llm.py`: LLM interactions

- **`mcp_server.py`**: Exposes tools via Model Context Protocol for external agent access

#### 4. State Management (`swarms/team_agent/state/`)

- **`turing_tape.py`**: Append-only JSONL tape for workflow state
  - Location: `.team_agent/tape/{workflow_id}.jsonl`
  - Each record: `{ts, agent, workflow_id, event, state}`
  - Methods: `append()`, `read_all()`, `last_state(agent)`

- **`hitl.py`**: Human-in-the-loop coordination

#### 5. Registry System (`swarms/team_agent/registry.py`)
**Decentralized workflow registry with SQLite and Merkle tree:**

- **Tables**: `workflows`, `audit_log`, `agent_cards`
- **Methods**:
  - `publish_workflow(workflow)`: Register workflow to SQLite
  - `list_workflows()`: Query all workflows
  - `add_audit_entry(entry)`: Append to Merkle-tree-based audit log
  - `register_agent_card(card)`: Register agent capabilities

- **Database**: `team_agent_registry.sqlite3` (configurable via `TEAM_AGENT_REGISTRY_DB` env var)

#### 6. Parallel Execution (`parallel_executor.py`)
- ThreadPoolExecutor-based concurrent agent/capability execution
- Use for running independent capabilities simultaneously
- Methods: `execute_parallel(tasks, executor_func)`

### Workflow Outputs
Each execution creates a timestamped directory:
```
output/wf_YYYYMMDD_HHMMSS/
├── <generated_code>.py
├── README.md (if created)
└── wf_YYYYMMDD_HHMMSS_record.json
```

Workflow record structure:
```json
{
  "mission": "...",
  "architecture": {...},
  "implementation": {
    "artifacts": [...],
    "capability_used": "capability_name"
  },
  "review": {"issues": [...], "score": 8.5},
  "artifacts": {"name": "path/to/file.py"},
  "timestamp": "ISO8601"
}
```

### Logging
- Structured JSONL logs in `logs/` directory
- Log files: `orchestrator.jsonl`, `team_agent.{role}.jsonl`
- Configure via `utils/logging.py` with `get_logger(name)`

## Adding a New Capability

1. **Create capability class** in `swarms/team_agent/capabilities/{domain}/`:
```python
from swarms.team_agent.capabilities.base_capability import BaseCapability

class MyCapability(BaseCapability):
    def get_metadata(self):
        return {
            "name": "my_capability",
            "type": "code_generation",  # or document_generation
            "domains": ["web", "api"],
            "description": "Generates REST API code",
            "version": "1.0.0"
        }

    def execute(self, context):
        mission = context.get("mission", "")
        # Generate artifacts
        return {
            "content": "...",
            "artifacts": [{
                "type": "python",
                "name": "api",
                "filename": "api.py",
                "content": code
            }],
            "metadata": self.metadata
        }
```

2. **Write tests** in `utils/tests/test_my_capability.py`:
```python
def test_metadata():
    cap = MyCapability()
    assert cap.metadata["name"] == "my_capability"

def test_execute():
    result = cap.execute({"mission": "test"})
    assert "artifacts" in result
```

3. **Register in orchestrator** (`orchestrator.py`):
```python
from swarms.team_agent.capabilities.your_domain.your_capability import YourCapability

class Orchestrator:
    def _register_default_capabilities(self):
        self.capability_registry.register(YourCapability())
```

4. **Update exports** (`utils/capabilities/__init__.py`):
```python
from swarms.team_agent.capabilities.your_domain.your_capability import YourCapability
__all__ = ["HRTGuideCapability", "YourCapability"]
```

## Adding a New Tool

1. **Create tool** in `swarms/team_agent/tools/`:
```python
from swarms.team_agent.tools.base import BaseTool, ToolMetadata, ToolResult, ToolStatus

class MyTool(BaseTool):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="my_tool",
            description="What this tool does",
            requires_governance=False,
            trust_domain="execution"
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        # Tool logic
        return ToolResult(status=ToolStatus.SUCCESS, output=result)
```

2. **Register in MCP server** (if exposing externally):
```python
# In mcp_server.py
registry.register(MyTool())
```

## SIEM Integration

The system includes optional Logstash/Elasticsearch integration for audit logging:

- **CEF Format**: Workflow records are formatted as CEF (Common Event Format)
- **Test Suite**: `utils/tests/test_siem_integration.py`
- **Requirements**: Logstash on `localhost:5044`, Elasticsearch on `localhost:9200`
- **Skip Tests**: Tests auto-skip if ELK stack is unavailable

## Context Normalization

**Important**: Agent inputs can be string or dict. Always use `_prepare_context()` in builder implementations:
```python
def _prepare_context(self, mission, architecture):
    if isinstance(mission, str):
        mission = {"mission": mission}
    if isinstance(architecture, str):
        try:
            architecture = json.loads(architecture)
        except:
            architecture = {"raw": architecture}
    return mission, architecture
```

## Design Patterns in Use

- **Strategy Pattern**: Capabilities are interchangeable strategies
- **Registry Pattern**: Central capability/tool discovery
- **Template Method Pattern**: `BaseCapability` and `BaseRole` define workflow
- **Adapter Pattern**: `_prepare_context()` normalizes inputs
- **Observer Pattern**: SIEM integration observes workflow events

## Project Standards

### Code Style
- PEP 8 compliance
- Line length: 100 characters
- Python 3.11+ required
- Type hints on public methods

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```
Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Branch Strategy
- `main`: Stable release
- `develop`: Integration branch
- `feature/*`: New features
- `fix/*`: Bug fixes

## Environment Variables

- `TEAM_AGENT_REGISTRY_DB`: SQLite database path (default: `team_agent_registry.sqlite3`)

## Debugging

### Enable verbose logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect workflow records
```bash
cat output/wf_*/wf_*_record.json | jq
```

### Clear caches
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache
```

## PKI Certificate Management

### Regenerating Certificates

To regenerate all certificates (e.g., before open-sourcing with proper root CA):

```python
from swarms.team_agent.crypto import PKIManager

# Initialize with force=True to regenerate
pki = PKIManager()
pki.initialize_pki(force=True)
```

### Inspecting Certificates

```python
from swarms.team_agent.crypto import PKIManager, TrustDomain

pki = PKIManager()
info = pki.get_certificate_info(TrustDomain.EXECUTION)
print(f"Subject: {info['subject']}")
print(f"Valid until: {info['not_after']}")
```

### Verifying Signed Data

```python
from swarms.team_agent.crypto import Verifier
from swarms.team_agent.state.turing_tape import TuringTape

# Verify all entries in a workflow tape
tape = TuringTape(workflow_id="wf_20251204_120000")
verifier = Verifier(chain_pem=execution_chain['chain'])
results = tape.verify_all(verifier)
print(f"Verified: {results['verified']}/{results['total']}")
```

## Common Issues

### `AttributeError: 'str' object has no attribute 'get'`
**Cause**: Agent received string instead of dict
**Fix**: Ensure `_prepare_context()` is called before `agent.run()`

### `ValueError: Capability must have a name in metadata`
**Cause**: Missing `"name"` field in metadata
**Fix**: Add `"name": "capability_name"` to `get_metadata()`

### `KeyError: 'artifacts'`
**Cause**: Builder result missing expected structure
**Fix**: Ensure capability `execute()` returns dict with `"artifacts"` key
