# Team Agent - Multi-Agent Orchestration Framework

## Overview

Team Agent is a capability-driven multi-agent orchestration framework that coordinates specialized AI agents to execute complex missions. It combines **role-based agents** (Architect, Builder, Critic, Recorder) with **domain-specific capabilities** to deliver high-quality, auditable software and documentation outputs.

## Core Concept

Instead of monolithic AI systems, Team Agent uses a **team of specialized agents** that collaborate through a structured workflow:

```
Mission → Architect → Builder (w/ Capabilities) → Critic → Recorder → Artifacts
```

### Key Innovation: **Capability System**

Capabilities are domain-specific knowledge modules that the Builder dynamically selects based on mission requirements. This allows the system to:

- **Specialize**: Medical guides, code generation, documentation, etc.
- **Extend**: Add new capabilities without modifying core agents
- **Route**: Automatically select the right capability for each mission

## Architecture

### 1. **Orchestrator** (`orchestrator.py`)
- Coordinates the 4-phase workflow
- Manages capability registry
- Handles agent communication and artifact publishing

### 2. **Role Agents** (`roles/`)

#### **Architect**
- Analyzes mission requirements
- Designs system architecture
- Defines technical specifications

#### **Builder** (`dynamic_builder.py`)
- Selects appropriate capability based on mission
- Executes code/document generation
- Falls back to generic builder if no specialized capability matches

#### **Critic**
- Reviews generated code/documents
- Identifies issues and improvements
- Provides quality scores and feedback

#### **Recorder**
- Publishes final artifacts to disk
- Creates comprehensive workflow records
- Generates metadata and documentation

### 3. **Capability System** (`capabilities/`)

#### **Base Capability** (`base_capability.py`)
Abstract class defining:
- `get_metadata()`: Describes capability (name, type, domains, version)
- `matches(requirements)`: Determines if capability suits a mission
- `execute(context)`: Performs the actual work
- `validate_context(context)`: Ensures required inputs are present

#### **Example: HRT Guide Capability** (`medical/hrt_guide.py`)
Specialized capability for generating hormone replacement therapy clinical guides:
- **Domains**: `["medical", "hrt"]`
- **Type**: `"document_generation"`
- **Output**: Python code that generates structured medical documentation

#### **Registry** (`registry.py`)
Central discovery system:
- Indexes capabilities by type and domain
- Supports keyword search and requirement matching
- Handles both object and dict capability formats

## Workflow Phases

### **Phase 1: Architecture**
```python
architect_output = architect.run({"mission": mission})
# Returns: {components, tech_stack, patterns, interfaces}
```

### **Phase 2: Implementation**
```python
builder_result = dynamic_builder.run(
    mission=mission,
    architecture=json.dumps(architect_output)
)
# Selects capability → executes → returns artifacts
```

### **Phase 3: Review**
```python
critic_output = critic.run({
    "mission": mission,
    "architecture": architect_output,
    "implementation": builder_result,
    "code": extracted_code
})
# Returns: {issues, score, suggestions}
```

### **Phase 4: Recording**
```python
recorder.run({
    "mission": mission,
    "architecture": architect_output,
    "implementation": builder_result,
    "review": critic_output,
    "artifacts": published_paths
})
# Writes: workflow_record.json + all artifacts to disk
```

## Usage

### Basic Example

```python
from swarms.team_agent.orchestrator import Orchestrator

# Initialize with output directory
o = Orchestrator(output_dir="./output")

# Execute a mission
result = o.execute("Generate hormone replacement therapy guide")

print(f"Workflow ID: {result['workflow_id']}")
print(f"Capability Used: {result['final_record']['capability_used']}")
print(f"Artifacts: {result['final_record']['published_artifacts']}")
```

### Creating a Custom Capability

```python
from swarms.team_agent.capabilities.base_capability import BaseCapability

class MyCapability(BaseCapability):
    def get_metadata(self):
        return {
            "name": "my_capability",
            "type": "code_generation",
            "domains": ["web", "api"],
            "description": "Generates REST API code",
            "version": "1.0.0"
        }
    
    def execute(self, context):
        mission = context.get("mission", "")
        architecture = context.get("architecture", "")
        
        # Generate code
        code = f"# API for: {mission}\n..."
        
        return {
            "content": code,
            "artifacts": [{
                "type": "python",
                "name": "api",
                "filename": "api.py",
                "content": code
            }],
            "metadata": self.metadata
        }

# Register it
from swarms.team_agent.capabilities.registry import CapabilityRegistry
registry = CapabilityRegistry()
registry.register(MyCapability())
```

## Testing

The project includes comprehensive test coverage:

```bash
# Run all capability tests
python examples/run_capability_tests.py

# Run specific test suites
pytest utils/tests/test_capabilities.py -v
pytest utils/tests/test_capability_registry.py -v
pytest utils/tests/test_orchestrator_capabilities.py -v
```

### Test Structure

- **`test_capabilities.py`**: BaseCapability, DocumentGenerator, HRTGuideCapability
- **`test_capability_registry.py`**: Registration, indexing, discovery
- **`test_orchestrator_capabilities.py`**: End-to-end workflow integration

## Project Structure

```
team-agent/
├── swarms/
│   └── team_agent/
│       ├── orchestrator.py          # Main coordinator
│       ├── roles/
│       │   ├── architect.py         # Architecture planning
│       │   ├── builder.py           # Generic builder fallback
│       │   ├── critic.py            # Code review
│       │   └── recorder.py          # Artifact publishing
│       └── capabilities/
│           ├── base_capability.py   # Abstract base class
│           ├── registry.py          # Capability discovery
│           ├── document_generator.py # Generic doc generation
│           └── medical/
│               └── hrt_guide.py     # HRT guide specialist
├── utils/
│   ├── capabilities/
│   │   ├── dynamic_builder.py      # Capability-aware builder
│   │   └── __init__.py              # Exports HRTGuideCapability
│   └── tests/                       # Test suites
├── examples/
│   └── run_capability_tests.py     # Test runner
└── README.md                        # This file
```

## Key Design Patterns

### 1. **Strategy Pattern**
Capabilities are interchangeable strategies selected at runtime based on mission requirements.

### 2. **Registry Pattern**
Central capability registry enables discovery without hard dependencies.

### 3. **Template Method Pattern**
BaseCapability defines workflow; subclasses implement domain logic.

### 4. **Adapter Pattern**
`_prepare_context()` normalizes agent inputs (string vs dict).

## Extension Points

### Add a New Capability
1. Subclass `BaseCapability`
2. Implement `get_metadata()` and `execute()`
3. Register with `CapabilityRegistry`

### Add a New Role
1. Subclass `BaseRole`
2. Implement `run(context)` method
3. Add to `Orchestrator._execute_workflow()`

### Add a New Phase
Modify `Orchestrator._execute_workflow()` to insert new phase between existing ones.

## Outputs

Each workflow execution creates:

```
./output/
└── wf_20251123_170918/
    ├── hrt_guide_generator.py       # Generated code
    ├── README.md                     # Documentation (if created)
    └── wf_20251123_170918_record.json # Full workflow record
```

### Workflow Record Structure

```json
{
  "mission": "Generate hormone replacement therapy guide",
  "architecture": { ... },
  "implementation": {
    "artifacts": [ ... ],
    "capability_used": "hrt_guide_generator"
  },
  "review": {
    "issues": [ ... ],
    "score": 8.5
  },
  "artifacts": {
    "hrt_guide": "./output/wf_20251123_170918/hrt_guide_generator.py"
  },
  "timestamp": "2025-11-23T17:09:18.123456"
}
```

## Future Enhancements

1. **Tool System**: Extract role logic into reusable tools (see architectural discussion)
2. **Governance Layer**: Policy enforcement and compliance checking
3. **Parallel Execution**: Run independent capabilities concurrently
4. **Capability Versioning**: Support multiple versions of same capability
5. **Dynamic Agent Composition**: Select roles based on mission complexity

## Contributing

When adding capabilities:
- Include comprehensive metadata
- Provide clear domain/type specifications
- Write unit tests covering `matches()` and `execute()`
- Update registry tests if adding new discovery patterns

## License

[Your License Here]

## Authors

Team Agent Development Team