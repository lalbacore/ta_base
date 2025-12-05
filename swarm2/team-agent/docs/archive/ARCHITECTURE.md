# Team Agent Architecture

## System Design Philosophy

Team Agent is built on three core principles:

1. **Separation of Concerns**: Each agent has a single, well-defined responsibility
2. **Capability-Driven Execution**: Domain knowledge lives in pluggable capabilities, not hardcoded in agents
3. **Auditability**: Every decision and artifact is logged and traceable

## Data Flow

```
┌─────────────┐
│   Mission   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATOR                                │
│  - Creates workflow ID                                   │
│  - Initializes agents                                    │
│  - Manages capability registry                           │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 1: ARCHITECTURE                                   │
│  ┌────────────┐                                          │
│  │ Architect  │ → Architecture Design                    │
│  └────────────┘   {components, tech_stack, patterns}     │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 2: IMPLEMENTATION                                 │
│  ┌─────────────────┐                                     │
│  │ Dynamic Builder │                                     │
│  │   ┌─────────────┴────────────┐                        │
│  │   │ 1. Analyze Mission       │                        │
│  │   │ 2. Query Registry        │                        │
│  │   │ 3. Select Capability     │                        │
│  │   │ 4. Execute               │                        │
│  │   └──────────────────────────┘                        │
│  │        │                                               │
│  │        ▼                                               │
│  │   ┌──────────────────────────┐                        │
│  │   │ Capability (e.g. HRT)    │                        │
│  │   │  - Domain logic          │                        │
│  │   │  - Code generation       │                        │
│  │   │  - Artifact creation     │                        │
│  │   └──────────────────────────┘                        │
│  └────────────┬─────────────────                         │
│               │                                           │
│               ▼                                           │
│          Artifacts [{type, name, content}]                │
└──────┬────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 3: REVIEW                                         │
│  ┌────────────┐                                          │
│  │   Critic   │ → Review Report                          │
│  └────────────┘   {issues, score, suggestions}           │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 4: RECORDING                                      │
│  ┌────────────┐                                          │
│  │  Recorder  │ → Published Artifacts + Workflow Record  │
│  └────────────┘                                          │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### Orchestrator

**Responsibilities**:
- Workflow lifecycle management
- Agent initialization
- Capability registry management
- Context preparation and normalization
- Artifact publishing coordination

**Key Methods**:
- `execute(mission)`: Entry point for workflow execution
- `_execute_workflow()`: 4-phase orchestration
- `_prepare_context()`: Normalizes agent inputs
- `_run_agent()`: Wraps agent execution with context prep

**Design Decision**: Orchestrator is stateful (tracks `current_workflow_id`) to support concurrent workflow tracking in future.

### Role Agents

All agents inherit from `BaseRole` which provides:
- Structured logging (JSON format)
- Workflow ID tracking
- Stage timing/profiling

#### Architect
**Input**: Mission string
**Output**: Architecture dict with:
- `components`: List of system components
- `tech_stack`: Technologies/frameworks
- `patterns`: Design patterns to use
- `interfaces`: API/integration points

**Logic**: Currently mock implementation. Future: LLM-based architecture planning.

#### Dynamic Builder
**Input**: Mission + architecture (JSON string)
**Output**: Implementation dict with:
- `artifacts`: List or dict of generated content
- `capability_used`: Name of selected capability
- `metadata`: Capability metadata

**Selection Logic**:
1. Check for explicit keyword matches (e.g., "hormone" + "therapy" → HRT)
2. Query registry with mission string
3. Fall back to generic builder if no match

#### Critic
**Input**: Mission + architecture + implementation + code
**Output**: Review dict with:
- `issues`: List of identified problems
- `score`: Quality score (0-10)
- `suggestions`: Improvement recommendations

**Logic**: Currently mock implementation. Future: Static analysis + LLM review.

#### Recorder
**Input**: Full workflow context (mission, architecture, implementation, review)
**Output**: Published artifacts on disk
**Side Effects**: Writes:
- Individual artifact files
- Comprehensive JSON workflow record

### Capability System

#### BaseCapability

Abstract base providing:

```python
class BaseCapability:
    def get_metadata(self) -> Dict:
        """Describe this capability"""
        raise NotImplementedError
    
    def matches(self, requirements: Dict) -> bool:
        """Does this capability suit the requirements?"""
        # Default: type and domain matching
    
    def execute(self, context: Dict) -> Dict:
        """Perform the work"""
        raise NotImplementedError
    
    def validate_context(self, context: Dict) -> None:
        """Ensure required inputs present"""
        # Default: check for 'mission' key
```

**Metadata Schema**:
```python
{
    "name": str,           # Unique identifier
    "type": str,           # E.g., "code_generation", "document_generation"
    "domain": str,         # Primary domain (optional)
    "domains": List[str],  # All relevant domains
    "description": str,    # Human-readable summary
    "version": str,        # Semantic version
    # ... capability-specific fields
}
```

**Artifact Schema**:
```python
{
    "type": str,         # "python", "markdown", "json", etc.
    "name": str,         # Artifact identifier
    "filename": str,     # Suggested filename
    "content": str,      # The actual content
    "summary": str       # Brief description (optional)
}
```

#### CapabilityRegistry

**Data Structures**:
- `_capabilities: Dict[str, Capability]` - Name → capability mapping
- `_by_type: Dict[str, List[str]]` - Type → capability names index
- `_by_domain: Dict[str, List[str]]` - Domain → capability names index

**Query Methods**:
- `find(query)`: String or dict query → single best match
- `find_all(requirements)`: Dict requirements → all matches
- `get_by_type(type)`: All capabilities of a type
- `get_by_domain(domain)`: All capabilities in a domain

**Registration**:
Handles both capability objects and plain dicts, extracting metadata from:
1. `get_metadata()` method
2. `metadata` attribute
3. Dict itself (for test mocks)

### Context Normalization

Agents expect dict inputs with an `"input"` key, but various parts of the system pass different formats (strings, dicts without "input", etc.).

**Solution**: `_prepare_context(base)` ensures every agent receives:
```python
{
    "input": str,        # String representation
    "raw_input": Any,    # Original value
    # ... original dict keys preserved
}
```

This prevents `AttributeError: 'str' object has no attribute 'get'` errors.

## Error Handling Strategy

1. **Registry Queries**: Return `None` on no match (never raise)
2. **Agent Execution**: Wrap in try/except at orchestrator level
3. **Governance**: Optional; failures silently logged
4. **Context Validation**: Raise `ValueError` with clear message

## Performance Considerations

Current implementation is **synchronous** for simplicity. Future optimizations:

1. **Parallel Phase 2**: Run multiple capabilities concurrently if mission is decomposable
2. **Async Agent Calls**: Use `asyncio` for agent execution
3. **Capability Caching**: Reuse capability instances across workflows
4. **Lazy Registry Loading**: Load capabilities on-demand

## Security Considerations

1. **Code Execution**: Generated code is **not** executed automatically
2. **File Writes**: Artifacts written to sandboxed `output_dir`
3. **Input Validation**: Capability `validate_context()` checks required fields
4. **Governance**: Optional layer for policy enforcement (future)

## Testing Strategy

### Unit Tests
- `test_capabilities.py`: Individual capability behavior
- `test_capability_registry.py`: Registry operations

### Integration Tests
- `test_orchestrator_capabilities.py`: End-to-end workflows

### Test Fixtures
Mock capabilities with minimal metadata for fast testing:
```python
class TestCapability:
    type = "test"
    name = "test_cap"
    domains = ["test"]
```

## Extension Architecture

### Adding a Phase

Insert between existing phases in `_execute_workflow()`:

```python
# New Phase 2.5: Validation
self.logger.info("Phase 2.5: Validation")
validator = Validator(self.current_workflow_id)
validation_result = self._run_agent(validator, {
    "architecture": architect_output,
    "implementation": builder_result
})
```

### Adding a Capability Discovery Method

Extend `CapabilityRegistry.find()`:

```python
# Semantic similarity search
if isinstance(query, str):
    for cap in self._capabilities.values():
        if self._semantic_match(query, cap.metadata):
            return cap
```

### Adding Agent Communication

Agents currently don't directly communicate. To enable:

1. Add message bus to orchestrator
2. Agents publish events to bus
3. Other agents subscribe to relevant events

## Future: Tool-Based Architecture

Current roles have hardcoded logic. Proposed evolution:

```python
class Architect(BaseRole):
    def __init__(self, workflow_id, tool_registry):
        self.tools = tool_registry
    
    def run(self, context):
        # Select tools based on mission
        planner = self.tools.select("architecture_planner", context)
        decomposer = self.tools.select("task_decomposer", context)
        
        # Execute tool chain
        plan = planner.execute(context)
        tasks = decomposer.execute({"plan": plan})
        
        return {"plan": plan, "tasks": tasks}
```

Benefits:
- Reuse tools across roles
- Test tools independently
- Compose new behaviors without changing roles