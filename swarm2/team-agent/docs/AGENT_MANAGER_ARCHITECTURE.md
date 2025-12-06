# Agent Manager Architecture Design

## Current State: Two-Level Agent System

Team Agent currently has **two distinct levels** of agents that serve different purposes:

### Level 1: Workflow Orchestration Agents (Hard-coded)

**Purpose:** Execute workflow phases (currently hard-coded in orchestrator)

| Agent | Phase | Trust Domain | Role |
|-------|-------|--------------|------|
| **Architect** | Phase 1 | EXECUTION | Analyze requirements, design architecture |
| **Builder** (DynamicBuilder) | Phase 2 | EXECUTION | Select capability and generate implementation |
| **Critic** | Phase 3 | EXECUTION | Review output, identify issues, score quality |
| **Recorder** | Phase 4 | LOGGING | Publish artifacts, create workflow record |
| **Governance** | Pre/Post | GOVERNMENT | Optional policy enforcement and compliance |

**Current Implementation:**
```python
# swarms/team_agent/orchestrator.py:execute()
architect = Architect(workflow_id, cert_chain=execution_chain)
# builder removed - now using dynamic_builder
critic = Critic(workflow_id, cert_chain=execution_chain)
recorder = Recorder(workflow_id, cert_chain=logging_chain)
governance = Governance(workflow_id, cert_chain=government_chain)  # optional

# Hard-coded workflow:
# 1. architect.run()
# 2. governance.run() [pre-build]
# 3. dynamic_builder.run()  # <-- This is where capability selection happens
# 4. critic.run()
# 5. governance.run() [post-review]
# 6. recorder.run()
```

**Trust Domains:**
- **EXECUTION** (Architect, Builder, Critic): Design and implementation work
- **LOGGING** (Recorder): Artifact publishing and audit trails
- **GOVERNMENT** (Governance): Policy enforcement and compliance

---

### Level 2: Domain Capability Agents (Dynamic via DynamicBuilder)

**Purpose:** Provide domain-specific expertise (selected at runtime)

| Capability | Domain | Type | Selection Method |
|-----------|--------|------|------------------|
| **LegalDocumentGenerator** | legal, contracts, compliance | document_generation | Keywords: "nda", "contract", "privacy", etc. |
| **HRTGuideCapability** | medical, hrt | document_generation | Keywords: "hormone", "therapy" |
| **FinancialDocumentGenerator** | financial, accounting | document_generation | Keywords: "financial", "budget", etc. |
| *Future capabilities* | Any domain | Any type | Keyword or explicit selection |

**Current Implementation:**
```python
# DynamicBuilder selects capability based on mission keywords
capability = dynamic_builder.select_capability(mission)
# Examples:
#   "Generate NDA" -> LegalDocumentGenerator
#   "Create hormone therapy guide" -> HRTGuideCapability
#   "Build financial report" -> FinancialDocumentGenerator
#   No match -> fallback generic code
```

**This works well!** DynamicBuilder already handles:
- Capability discovery by keywords
- Automatic selection
- Fallback to generic implementation
- Registry integration

---

## The Key Insight: DynamicBuilder is NOT an Agent

**DynamicBuilder is a selector/router**, not an agent itself. It:
- Selects the right capability based on mission
- Executes that capability
- Returns standardized result format

**It doesn't need:**
- Trust scoring (the *capabilities* it selects could be scored)
- Agent card registration
- Invocation tracking for itself

**The Workflow Agents DO need:**
- Registration in agent_cards table
- Trust score tracking
- Invocation history
- Performance metrics

---

## Architecture Design Options

### Option A: Minimal Agent Manager (Recommended)

**Philosophy:** Keep DynamicBuilder for capabilities, manage only workflow agents

**What It Does:**
```python
class AgentManager:
    """Manages Level 1 workflow orchestration agents only."""

    def __init__(self):
        self.db = get_backend_session()

    def register_system_agent(self, agent: BaseRole) -> AgentCard:
        """Register Architect, Critic, Recorder, Governance."""
        return AgentCard(
            agent_id=agent.id,
            agent_name=agent.name,
            agent_type="role",  # "role" for workflow agents
            capabilities=agent.capabilities,
            module_path=f"swarms.team_agent.roles.{agent.__class__.__name__.lower()}",
            class_name=agent.__class__.__name__,
            trust_domain=self._get_trust_domain(agent),
            status="active"
        )

    def track_invocation(self, agent_id: str, result: dict):
        """Record agent execution and update trust score."""
        # Create invocation record
        # Update agent stats (total_invocations, success_rate)
        # Sync with trust scoring system

    def get_agent_stats(self, agent_id: str) -> dict:
        """Get performance metrics for an agent."""
        pass
```

**Orchestrator Integration:**
```python
class Orchestrator:
    def __init__(self):
        # ... existing init ...

        # Add agent manager
        self.agent_manager = AgentManager()
        self._register_system_agents()

    def _register_system_agents(self):
        """Auto-register workflow agents on startup."""
        # Register once per orchestrator lifetime
        # These are the "system agents" that run workflows
        pass

    def execute(self, mission: str):
        # Create agents (as before)
        architect = Architect(...)
        critic = Critic(...)
        recorder = Recorder(...)

        # Register them (if not already registered)
        self.agent_manager.ensure_registered(architect)
        self.agent_manager.ensure_registered(critic)
        self.agent_manager.ensure_registered(recorder)

        # Run workflow
        result = self._execute_workflow(mission, architect, critic, recorder)

        # Track invocations
        self.agent_manager.track_invocation(architect.id, architect_output)
        self.agent_manager.track_invocation("dynamic_builder", builder_result)
        self.agent_manager.track_invocation(critic.id, critic_output)
        self.agent_manager.track_invocation(recorder.id, recorder_output)

        return result
```

**Pros:**
- Simple and focused
- DynamicBuilder keeps working as-is
- Fixes the "bogus agents" trust scoring issue
- Agents properly tracked in agent_cards

**Cons:**
- Still hard-codes workflow (Architect -> Builder -> Critic -> Recorder)
- No custom workflows
- No team/swarm composition

---

### Option B: Full Agent Manager + Team Manager

**Philosophy:** Make everything configurable, support custom workflows

**What It Adds:**
```python
class TeamAgentManager:
    """Manages teams/swarms of agents."""

    def create_workflow_template(self, name: str, agent_sequence: List[str]):
        """Define a custom workflow.

        Examples:
            - "standard": [Architect, DynamicBuilder, Critic, Recorder]
            - "simple": [DynamicBuilder, Recorder]
            - "governed": [Architect, Governance, DynamicBuilder, Governance, Critic, Recorder]
            - "research": [Researcher, Analyzer, Recorder]
        """
        pass

    def create_team(self, name: str, agents: List[str], capabilities: List[str]):
        """Create a team for specific mission types.

        Example:
            legal_team = create_team(
                name="Legal Document Team",
                agents=["architect", "dynamic_builder", "legal_reviewer", "recorder"],
                capabilities=["legal", "compliance", "document_generation"]
            )
        """
        pass
```

**Mission Configuration:**
```python
# Simple mission (string) - uses default workflow
orchestrator.execute("Generate NDA")

# Configured mission (dict) - custom workflow
orchestrator.execute({
    "description": "Generate NDA",
    "workflow_type": "simple",  # Skip Architect and Critic
    "required_capabilities": ["legal", "compliance"],
    "team_id": "legal_team",  # Optional pre-defined team
})

# Advanced mission - explicit agent selection
orchestrator.execute({
    "description": "Generate compliance report",
    "agents": {
        "designer": "compliance_architect",  # Custom architect variant
        "builder": "dynamic_builder",
        "reviewer": "compliance_critic",
        "publisher": "compliance_recorder"
    }
})
```

**Pros:**
- Maximum flexibility
- Custom workflows for different mission types
- Team/swarm support
- Can build specialized workflows (research, analysis, etc.)

**Cons:**
- Much more complex
- May be over-engineering for current needs
- Harder to maintain

---

## Governance and Logging: Current Design

### Governance Agent

**Current Implementation:**
```python
# In orchestrator._execute_workflow()
if governance:
    try:
        # Pre-build check
        governance.run({"stage": "pre_build", "architecture": architect_output})
    except Exception:
        pass  # Optional - failure doesn't stop workflow

# ... build phase ...

if governance:
    try:
        # Post-review check
        governance.run({"stage": "post_review", "review": critic_output})
    except Exception:
        pass
```

**What It Does:**
- Enforces governance policies (from backend.db governance_policies table)
- Can approve/reject workflows
- Currently optional (try/except catches failures)
- Has its own trust domain (GOVERNMENT)

**Current Policies:**
```sql
-- From fresh mission test:
governance_policies: 1 row
governance_decisions: 3 rows
```

**Should It Be Configurable?**
- **Probably not** - Governance is organization-wide
- Either you have governance enabled or you don't
- Policies can be configured in database
- Agent implementation can stay hard-coded

### Recorder/Logging Agent

**Current Implementation:**
```python
# Phase 4: Always runs
recorder = Recorder(workflow_id, cert_chain=logging_chain)
recorder.run({
    "mission": mission,
    "architecture": architect_output,
    "implementation": builder_result,
    "review": critic_output,
    "artifacts": published_artifacts
})
```

**What It Does:**
- Publishes workflow record
- Creates audit trail
- Has its own trust domain (LOGGING)

**Should It Be Configurable?**
- **No** - Logging should always happen
- Audit trails are critical
- Keep hard-coded in workflow

---

## Recommended Architecture: Hybrid Approach

### What to Keep Hard-coded

1. **Core Workflow Roles:**
   - Architect, Critic, Recorder - These are foundational
   - Governance - Optional but always same implementation
   - Trust domains - Security boundary, don't make configurable

2. **DynamicBuilder:**
   - Keep current capability selection system
   - Already works great
   - Don't over-complicate

### What to Make Configurable

1. **Workflow Type Selection:**
```python
WORKFLOW_TYPES = {
    "standard": ["architect", "dynamic_builder", "critic", "recorder"],
    "simple": ["dynamic_builder", "recorder"],  # Quick tasks
    "governed": ["architect", "governance", "dynamic_builder", "governance", "critic", "recorder"],
    "research": ["architect", "dynamic_builder", "recorder"],  # Skip critic
}

# Mission can specify:
orchestrator.execute({
    "description": "Quick NDA generation",
    "workflow_type": "simple"  # Skip architect and critic
})
```

2. **Agent Registration & Tracking:**
   - All workflow agents registered in agent_cards
   - Track invocations
   - Update trust scores
   - Provide stats API

---

## Proposed Implementation: Agent Manager

### Phase 1: Basic Agent Manager (This Week)

**Goal:** Fix "bogus agents" issue, enable tracking

```python
# swarms/team_agent/agent_manager.py

class AgentManager:
    """Manages workflow orchestration agents."""

    def __init__(self):
        self.backend_db = get_backend_session()
        self.trust_db = get_trust_session()

    def ensure_registered(self, agent: BaseRole) -> AgentCard:
        """Register agent if not already in database."""
        existing = self.backend_db.query(AgentCard).filter_by(agent_id=agent.id).first()
        if existing:
            return existing

        card = AgentCard(
            agent_id=agent.id,
            agent_name=agent.name,
            agent_type="role",
            description=agent.metadata.get("description", ""),
            capabilities=json.dumps(agent.capabilities),
            module_path=f"swarms.team_agent.roles.{agent.__class__.__name__.lower()}",
            class_name=agent.__class__.__name__,
            trust_domain=self._infer_trust_domain(agent),
            trust_score=0.0,
            status="active"
        )

        self.backend_db.add(card)
        self.backend_db.commit()
        return card

    def track_invocation(self, agent_id: str, workflow_id: str, result: dict, success: bool):
        """Record agent invocation and update stats."""
        # Create AgentInvocation record
        invocation = AgentInvocation(
            agent_id=agent_id,
            workflow_id=workflow_id,
            timestamp=datetime.now(),
            success=success,
            result_summary=json.dumps(result.get("summary", {}))
        )
        self.backend_db.add(invocation)

        # Update agent_card stats
        card = self.backend_db.query(AgentCard).filter_by(agent_id=agent_id).first()
        if card:
            card.total_invocations += 1
            if success:
                card.success_rate = (
                    (card.success_rate * (card.total_invocations - 1) + 1.0) /
                    card.total_invocations
                )

        self.backend_db.commit()

        # Sync with trust scoring system
        self._update_trust_score(agent_id, success)

    def get_agent_stats(self, agent_id: str) -> dict:
        """Get performance metrics."""
        card = self.backend_db.query(AgentCard).filter_by(agent_id=agent_id).first()
        if not card:
            return {}

        return {
            "agent_id": card.agent_id,
            "agent_name": card.agent_name,
            "trust_score": card.trust_score,
            "total_invocations": card.total_invocations,
            "success_rate": card.success_rate,
            "status": card.status
        }
```

**Integration:**
```python
# swarms/team_agent/orchestrator.py

class Orchestrator:
    def __init__(self):
        # ... existing init ...
        self.agent_manager = AgentManager()

    def execute(self, mission: str | dict) -> dict:
        # Parse mission config
        if isinstance(mission, str):
            mission_config = {"description": mission, "workflow_type": "standard"}
        else:
            mission_config = mission

        # Create agents
        architect = Architect(self.current_workflow_id, cert_chain=...)
        critic = Critic(self.current_workflow_id, cert_chain=...)
        recorder = Recorder(self.current_workflow_id, cert_chain=...)

        # Register agents
        self.agent_manager.ensure_registered(architect)
        self.agent_manager.ensure_registered(critic)
        self.agent_manager.ensure_registered(recorder)

        # Execute workflow
        result = self._execute_workflow(mission_config["description"], architect, critic, recorder)

        # Track invocations
        self.agent_manager.track_invocation(architect.id, self.current_workflow_id, result["architecture"], True)
        self.agent_manager.track_invocation("dynamic_builder", self.current_workflow_id, result["implementation"], True)
        # ... etc

        return result
```

---

### Phase 2: Workflow Type Selection (Next Week)

**Add support for different workflow types:**

```python
class Orchestrator:
    WORKFLOW_TYPES = {
        "standard": {
            "agents": ["architect", "dynamic_builder", "critic", "recorder"],
            "description": "Full workflow with architecture, build, review, publish"
        },
        "simple": {
            "agents": ["dynamic_builder", "recorder"],
            "description": "Quick generation without architecture or review"
        },
        "governed": {
            "agents": ["architect", "governance", "dynamic_builder", "governance", "critic", "recorder"],
            "description": "Workflow with governance checks"
        }
    }

    def _execute_workflow_by_type(self, mission_config: dict):
        workflow_type = mission_config.get("workflow_type", "standard")
        workflow = self.WORKFLOW_TYPES[workflow_type]

        # Dynamically execute based on workflow agent list
        # This enables custom workflows without changing code
        pass
```

---

## Mission Configuration Design

### Simple Mission (String)
```python
# Uses default "standard" workflow
result = orchestrator.execute("Generate NDA for software project")
```

### Configured Mission (Dict)
```python
result = orchestrator.execute({
    "description": "Generate privacy policy",
    "workflow_type": "simple",  # Skip architect and critic
    "required_capabilities": ["legal", "privacy"],
    "output_format": "markdown"
})
```

### Advanced Mission (Full Config)
```python
result = orchestrator.execute({
    "description": "Generate compliance report",
    "workflow_type": "governed",  # Include governance checks
    "required_capabilities": ["legal", "compliance", "gdpr"],
    "team_id": "compliance_team",  # Optional
    "governance_policy": "strict",  # Optional
    "output_dir": "./compliance_reports"
})
```

---

## Summary & Recommendations

### For Your Questions:

1. **"Should I even consider agents or sets of agents or is dynamic_builder good enough?"**
   - **Answer:** DynamicBuilder is great for **capability selection** (Level 2)
   - **Agent Manager** should focus on **workflow agents** (Level 1)
   - Keep both - they serve different purposes

2. **"Would you just accept a mission configuration and then let the orchestrator decide on the allotment?"**
   - **Answer:** Yes! Mission config should specify:
     - `description` (required)
     - `workflow_type` (optional, defaults to "standard")
     - `required_capabilities` (optional, for capability hints)
   - Orchestrator selects agents based on workflow_type
   - DynamicBuilder selects capability based on description keywords

3. **"I'm not quite sure how the government and logging agents are configured to work. I guess that's hard coded for now?"**
   - **Answer:** Yes, hard-coded and **should stay that way**:
     - **Governance** - Optional, organization-wide policy enforcement
     - **Recorder** - Always runs, critical for audit trails
     - Both have dedicated trust domains (GOVERNMENT, LOGGING)
     - Making these configurable adds complexity without value

### Recommended Approach:

**Start with Option A (Minimal Agent Manager):**
1. Build AgentManager to register workflow agents
2. Track invocations and update trust scores
3. Fix "bogus agents" issue
4. Add mission config support (workflow_type)

**Later (if needed), add Option B features:**
5. Team/swarm support
6. Custom workflow templates
7. Advanced mission configuration

This gives you immediate value (fix trust scoring) while keeping the door open for advanced features later.

---

## Next Steps

1. **Implement basic AgentManager** (this week)
2. **Test with fresh mission** - verify agents appear in agent_cards
3. **Add workflow_type support** - enable "simple" and "governed" workflows
4. **Frontend integration** - show agent stats, allow workflow selection

Would you like me to start implementing the basic AgentManager (Phase 1)?
