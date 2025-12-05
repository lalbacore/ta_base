# Orchestrator API

API reference for the mission orchestrator.

---

## Overview

The Orchestrator coordinates multi-agent workflows.

**Module**: `swarms.team_agent.orchestrator_a2a`

---

## OrchestratorA2A

A2A-enhanced orchestrator with capability discovery.

```python
from swarms.team_agent.orchestrator_a2a import OrchestratorA2A

orchestrator = OrchestratorA2A(
    output_dir: str = "./team_output",
    max_iterations: int = 3,
    enable_a2a: bool = True,
    enable_breakpoints: bool = False
)
```

### execute_mission()

Execute a mission specification.

```python
results = await orchestrator.execute_mission(
    mission: MissionSpec,
    local_agents: Optional[List[Any]] = None
) -> Dict[str, Any]
```

**Returns**:
```python
{
    "status": str,              # "completed" or "failed"
    "mission_id": str,
    "capabilities_used": List[Dict],
    "total_cost": float,
    "breakpoints": List[Dict]
}
```

### execute_simple()

Simple text-based execution.

```python
results = await orchestrator.execute_simple(
    mission_text: str
) -> Dict[str, Any]
```

---

## MissionSpec

Mission specification with requirements.

```python
from swarms.team_agent.orchestrator_a2a import MissionSpec
from swarms.team_agent.a2a import CapabilityRequirement, CapabilityType

mission = MissionSpec(
    mission_id: str,
    description: str,
    required_capabilities: List[CapabilityRequirement],
    max_cost: Optional[float] = None,
    max_duration: Optional[float] = None,
    breakpoints: Optional[List[BreakpointType]] = None,
    auto_approve_trusted: bool = False,
    auto_approve_threshold: float = 95.0
)
```

---

## BreakpointType

```python
class BreakpointType(Enum):
    MISSION_START = "mission_start"
    CAPABILITY_SELECTION = "capability_selection"
    AGENT_SELECTION = "agent_selection"
    PHASE_COMPLETION = "phase_completion"
    ERROR_RECOVERY = "error_recovery"
    MISSION_COMPLETE = "mission_complete"
```

---

## Complete Reference

For complete implementation details, see:
- Source: `swarms/team_agent/orchestrator_a2a.py`
- Tests: `utils/tests/test_orchestrator_capabilities.py`
- Examples: [Orchestrator Examples](../getting-started/examples.md)
