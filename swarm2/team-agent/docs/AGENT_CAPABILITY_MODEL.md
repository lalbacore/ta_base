# Agent-Capability Relationship Model

**Date:** December 6, 2025
**Status:** Design Proposal

---

## Core Principle

**Agents USE Capabilities** - Agents are identities with trust scores and history. Capabilities are reusable tools/modules from a shared workbench.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        AGENT LAYER                            │
│  (Who executes? Identity, Trust, History)                    │
├──────────────────────────────────────────────────────────────┤
│  1. Workflow Agents (type: "role")                           │
│     - Architect, Critic, Recorder, Governance                │
│     - Orchestration: coordinate workflow phases              │
│     - Trust Domain: EXECUTION, GOVERNMENT, LOGGING           │
│                                                               │
│  2. Specialist Agents (type: "specialist")                   │
│     - LegalSpecialist, MedicalSpecialist, etc.               │
│     - Domain Experts: use specific capabilities              │
│     - Trust Domain: EXECUTION                                │
│                                                               │
│  3. Generic Agents (type: "generic")                         │
│     - FallbackBuilder (generic code generation)              │
│     - Used when no specialist matches                        │
└──────────────────────────────────────────────────────────────┘
                              ↓ uses
┌──────────────────────────────────────────────────────────────┐
│                    CAPABILITY LAYER                           │
│  (What can be done? Tools, Functions, Modules)               │
├──────────────────────────────────────────────────────────────┤
│  - LegalDocumentGenerator (legal, contracts, nda)            │
│  - HRTGuideCapability (medical, hrt)                         │
│  - FinancialReportGenerator (financial, accounting)          │
│  - CodeAnalyzer (code_analysis, review)                      │
│  - DocumentWriter (document_generation)                      │
│                                                               │
│  Registered in: CapabilityRegistry                           │
│  Metadata: name, type, domains, version, keywords            │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Agent Cards (agent_cards table)

```python
class AgentCard:
    agent_id: str              # Primary key: "agent_architect_001", "specialist_legal_001"
    agent_name: str            # Human-readable: "Architect", "Legal Specialist"
    agent_type: str            # "role", "specialist", "generic"
    description: str           # What this agent does

    # Capabilities this agent uses
    capabilities: JSON         # ["legal_document_generator", "contract_analyzer"]

    # Trust & Performance
    trust_domain: str          # EXECUTION, GOVERNMENT, LOGGING
    trust_score: float         # 0-100
    total_invocations: int
    success_rate: float        # 0.0-1.0

    # Registration Info
    module_path: str           # "swarms.team_agent.specialists.legal"
    class_name: str            # "LegalSpecialist"
    version: str               # "1.0.0"
    status: str                # "active", "inactive"
    created_at: datetime
    updated_at: datetime
```

### Capability Registry (capability_registry table)

```python
class CapabilityRegistration:
    capability_id: str         # Primary key: "legal_document_generator"
    capability_name: str       # "Legal Document Generator"
    capability_type: str       # "document_generation", "code_generation", "analysis"

    # What it does
    description: str
    domains: JSON              # ["legal", "contracts", "nda", "compliance"]
    keywords: JSON             # ["nda", "contract", "privacy", "gdpr"]

    # Implementation
    module_path: str           # "swarms.team_agent.capabilities.legal.legal_document_generator"
    class_name: str            # "LegalDocumentGenerator"

    # Metadata
    version: str               # "1.0.0"
    status: str                # "active", "deprecated"
    created_at: datetime
```

### Agent-Capability Mapping (agent_capabilities table) - NEW!

```python
class AgentCapabilityMapping:
    id: int                    # Auto-increment primary key
    agent_id: str              # FK to agent_cards.agent_id
    capability_id: str         # FK to capability_registry.capability_id

    # Usage metadata
    is_primary: bool           # Is this the agent's main capability?
    priority: int              # Order of preference (1=highest)

    # Performance tracking
    times_used: int            # How many times this agent used this capability
    success_rate: float        # Success rate for this agent-capability combo

    created_at: datetime
    updated_at: datetime
```

---

## Agent Types Explained

### 1. Workflow Agents (type: "role")

**Purpose:** Orchestrate workflow phases, coordinate other agents

**Examples:**
- **Architect** - Analyzes requirements, designs architecture
  - Capabilities: `["design_system", "evaluate_intent"]`
  - Does NOT use domain capabilities (legal, medical)

- **Critic** - Reviews outputs, scores quality
  - Capabilities: `["review_design", "review_build", "evaluate_quality"]`

- **Recorder** - Publishes artifacts, creates audit records
  - Capabilities: `["record", "publish"]`

- **Governance** - Enforces policies, compliance checks
  - Capabilities: `["enforce_policy", "evaluate_request"]`

**Characteristics:**
- Hard-coded in orchestrator (not dynamically selected)
- Always execute in fixed workflow order
- Have their own trust domains (EXECUTION, GOVERNMENT, LOGGING)

### 2. Specialist Agents (type: "specialist")

**Purpose:** Execute domain-specific tasks using capabilities

**Examples:**
- **LegalSpecialist** - Legal document generation
  - Primary Capability: `legal_document_generator`
  - Secondary: `contract_analyzer`, `compliance_checker`
  - Keywords: ["nda", "contract", "privacy", "legal"]

- **MedicalSpecialist** - Medical documentation
  - Primary Capability: `hrt_guide_capability`
  - Keywords: ["hormone", "therapy", "medical"]

- **FinancialSpecialist** - Financial reports
  - Primary Capability: `financial_report_generator`
  - Keywords: ["financial", "budget", "accounting"]

**Characteristics:**
- Registered in agent_cards with type="specialist"
- Selected dynamically by DynamicBuilder based on mission keywords
- Use one or more capabilities from registry
- All have trust_domain="EXECUTION"
- Have trust scores, invocation history

### 3. Generic Agents (type: "generic")

**Purpose:** Fallback when no specialist matches

**Example:**
- **FallbackBuilder** - Generic code generation
  - Capability: `generic_code_generator`
  - Used when no specialist matches mission keywords

---

## Workflow Example

**Mission:** "Generate a privacy policy for our web application"

### Phase 1: Agent Selection (by DynamicBuilder)

```python
# DynamicBuilder.select_agent(mission)
keywords = ["privacy", "policy", "legal"]

# Query agent_cards for specialists
query = """
    SELECT ac.*, GROUP_CONCAT(acm.capability_id) as capabilities
    FROM agent_cards ac
    JOIN agent_capabilities acm ON ac.agent_id = acm.agent_id
    JOIN capability_registry cr ON acm.capability_id = cr.capability_id
    WHERE ac.agent_type = 'specialist'
      AND ac.status = 'active'
      AND (cr.keywords LIKE '%privacy%' OR cr.keywords LIKE '%legal%')
    ORDER BY ac.trust_score DESC
"""

# Result: LegalSpecialist (uses legal_document_generator capability)
```

### Phase 2: Agent Execution

```python
# Load specialist agent
legal_specialist = LegalSpecialist(
    agent_id="specialist_legal_001",
    workflow_id="wf_20251206_123456"
)

# Specialist loads its primary capability
capability = legal_specialist.get_capability("legal_document_generator")

# Execute capability
result = capability.execute({
    "mission": "Generate privacy policy",
    "document_type": "privacy_policy"
})

# Track invocation
agent_manager.track_invocation(
    agent_id="specialist_legal_001",
    capability_id="legal_document_generator",
    workflow_id="wf_20251206_123456",
    result=result,
    success=True
)
```

### Phase 3: Trust Score Update

```python
# Update agent card
UPDATE agent_cards
SET total_invocations = total_invocations + 1,
    success_rate = (success_rate * total_invocations + 1.0) / (total_invocations + 1),
    trust_score = success_rate * 100
WHERE agent_id = 'specialist_legal_001'

# Update agent-capability mapping
UPDATE agent_capabilities
SET times_used = times_used + 1,
    success_rate = (success_rate * times_used + 1.0) / (times_used + 1)
WHERE agent_id = 'specialist_legal_001'
  AND capability_id = 'legal_document_generator'
```

---

## Implementation Steps

### Step 1: Database Schema Updates

**Add agent_capabilities table:**

```sql
CREATE TABLE agent_capabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    capability_id TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    priority INTEGER DEFAULT 1,
    times_used INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agent_cards(agent_id),
    FOREIGN KEY (capability_id) REFERENCES capability_registry(capability_id),
    UNIQUE(agent_id, capability_id)
);
```

**Add capability_registry table:**

```sql
CREATE TABLE capability_registry (
    capability_id TEXT PRIMARY KEY,
    capability_name TEXT NOT NULL,
    capability_type TEXT NOT NULL,
    description TEXT,
    domains TEXT,  -- JSON array
    keywords TEXT, -- JSON array
    module_path TEXT NOT NULL,
    class_name TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 2: Create Specialist Agent Classes

```python
# swarms/team_agent/specialists/legal_specialist.py

from swarms.team_agent.specialists.base import BaseSpecialist
from swarms.team_agent.capabilities.legal import LegalDocumentGenerator

class LegalSpecialist(BaseSpecialist):
    """Specialist agent for legal document generation."""

    def __init__(self, agent_id: str, workflow_id: str, cert_chain=None):
        super().__init__(agent_id, workflow_id, cert_chain)

        self.name = "Legal Specialist"
        self.agent_type = "specialist"
        self.trust_domain = "EXECUTION"

        # Register primary capability
        self.primary_capability = LegalDocumentGenerator()

    def run(self, context: dict) -> dict:
        """Execute legal document generation."""
        mission = context.get("mission", "")

        # Use primary capability
        result = self.primary_capability.execute(context)

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "capability_used": "legal_document_generator",
            "artifacts": result.get("artifacts", []),
            "metadata": result.get("metadata", {})
        }
```

### Step 3: Update DynamicBuilder

```python
# utils/capabilities/dynamic_builder.py

class DynamicBuilder:
    def select_agent(self, mission: str):
        """Select specialist agent based on mission keywords."""

        # Try to find matching specialist agent
        agent = self.agent_manager.find_specialist_by_keywords(mission)

        if agent:
            return agent

        # Fallback to generic builder
        return FallbackBuilder()

    def run(self, mission: str, architecture: str = None):
        """Execute mission using selected specialist agent."""

        # Select agent
        agent = self.select_agent(mission)

        # Execute
        result = agent.run({
            "mission": mission,
            "architecture": architecture
        })

        # Track invocation
        self.agent_manager.track_invocation(
            agent_id=agent.id,
            capability_id=result.get("capability_used"),
            workflow_id=self.workflow_id,
            result=result,
            success=True
        )

        return result
```

### Step 4: AgentManager Updates

```python
# swarms/team_agent/agent_manager.py

class AgentManager:
    def register_specialist(self, specialist_class, primary_capability):
        """Register a specialist agent with its capabilities."""

        # Create agent card
        agent_id = f"specialist_{specialist_class.__name__.lower()}_001"

        card = AgentCard(
            agent_id=agent_id,
            agent_name=specialist_class.__name__,
            agent_type="specialist",
            description=specialist_class.__doc__,
            module_path=f"swarms.team_agent.specialists.{specialist_class.__name__.lower()}",
            class_name=specialist_class.__name__,
            trust_domain="EXECUTION",
            status="active"
        )

        # Register in database
        self.backend_db.add(card)

        # Map agent to capability
        mapping = AgentCapabilityMapping(
            agent_id=agent_id,
            capability_id=primary_capability.metadata["name"],
            is_primary=True,
            priority=1
        )

        self.backend_db.add(mapping)
        self.backend_db.commit()

        return card

    def find_specialist_by_keywords(self, mission: str) -> Optional[BaseSpecialist]:
        """Find specialist agent matching mission keywords."""

        mission_lower = mission.lower()

        # Query agent_capabilities joined with capability_registry
        query = """
            SELECT ac.agent_id, ac.class_name, ac.module_path, cr.keywords
            FROM agent_cards ac
            JOIN agent_capabilities acm ON ac.agent_id = acm.agent_id
            JOIN capability_registry cr ON acm.capability_id = cr.capability_id
            WHERE ac.agent_type = 'specialist'
              AND ac.status = 'active'
              AND acm.is_primary = 1
            ORDER BY ac.trust_score DESC
        """

        # Find matches
        for row in results:
            keywords = json.loads(row['keywords'])
            if any(kw in mission_lower for kw in keywords):
                # Dynamically import and instantiate specialist
                module = importlib.import_module(row['module_path'])
                specialist_class = getattr(module, row['class_name'])
                return specialist_class(agent_id=row['agent_id'], workflow_id=self.workflow_id)

        return None
```

---

## Summary

### Agents (Identity Layer)
- **What:** Entities with trust scores, invocation history
- **Where:** Registered in `agent_cards` table
- **Types:** role (workflow), specialist (domain), generic (fallback)

### Capabilities (Tool Layer)
- **What:** Reusable modules, functions, tools
- **Where:** Registered in `capability_registry` table
- **Usage:** Invoked by agents via `agent_capabilities` mapping

### Key Benefits
1. **Separation of Concerns:** Agent identity vs. agent capabilities
2. **Reusability:** Multiple agents can use same capability
3. **Trust Tracking:** Per-agent AND per-agent-capability metrics
4. **Dynamic Selection:** DynamicBuilder selects specialist agents by keywords
5. **Extensibility:** Easy to add new specialists without changing orchestrator

---

## Next Steps

1. ✅ **Database schema migration** - Add agent_capabilities, capability_registry tables
2. ✅ **Create specialist agent base class** - BaseSpecialist
3. ✅ **Implement LegalSpecialist** - First specialist agent
4. ✅ **Update AgentManager** - register_specialist(), find_specialist_by_keywords()
5. ✅ **Update DynamicBuilder** - Use agent selection instead of capability selection
6. ✅ **Test with fresh mission** - Verify specialist agent registered and invoked
