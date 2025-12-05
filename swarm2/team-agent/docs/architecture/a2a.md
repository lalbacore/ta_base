# Architecture: Agent-to-Agent (A2A) & MCP Integration

**Status:** 📋 Planning Phase
**Target:** Phase 6 - Dynamic Capability Discovery & Orchestration
**Last Updated:** 2025-12-04

---

## Executive Summary

This document outlines the architecture for integrating Agent-to-Agent (A2A) communication and Model Context Protocol (MCP) workloads with the Team Agent orchestrator through a smart contract-based registry system.

### Goals

1. **Dynamic Capability Discovery**: Orchestrator finds best-match external agents/tools
2. **Smart Contract Registry**: Publish and register capabilities on-chain
3. **Intelligent Matching**: Sort and select based on mission requirements
4. **Human-in-the-Loop**: Respect mission breakpoints for approvals
5. **Secure Integration**: Leverage PKI, trust scoring, and secrets management

---

## Current State

### What We Have (Phases 1-5)

✅ **PKI Infrastructure** (Phase 1-2)
- Certificate-based agent identity
- CRL and OCSP for revocation
- Trust domains for separation

✅ **Certificate Lifecycle** (Phase 3)
- Expiration monitoring
- Auto-renewal and rotation

✅ **Trust Scoring** (Phase 4)
- Agent reputation tracking
- Behavior-based trust scores (0-100)
- Access control based on trust

✅ **Secrets Management** (Phase 5)
- Encrypted storage of API keys, credentials
- Trust-based access control
- Short-lived plaintext exposure

### What We Need (Phase 6)

🔲 **A2A Communication Protocol**
- Agent discovery and registration
- Capability advertisement
- Secure communication channels

🔲 **MCP Integration**
- MCP server/client implementation
- Tool/resource registration
- Context sharing

🔲 **Smart Contract Registry**
- On-chain capability registry
- Reputation and payment tracking
- Discovery and matching

🔲 **Enhanced Orchestrator**
- Dynamic capability matching
- External agent integration
- Mission-aware orchestration

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Mission File                             │
│  - Requirements (capabilities, tools, resources)                 │
│  - Human-in-the-Loop Breakpoints                                 │
│  - Budget/Cost Constraints                                       │
│  - Trust Requirements                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced Orchestrator                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. Parse Mission Requirements                           │   │
│  │ 2. Inventory Internal Agents & Tools                    │   │
│  │ 3. Query Registry for External Capabilities             │   │
│  │ 4. Score & Rank All Options                             │   │
│  │ 5. Present Best Matches                                 │   │
│  │ 6. Request Human Approval (if breakpoint)               │   │
│  │ 7. Execute with Selected Capabilities                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Internal Agents │  │  A2A Agents      │  │  MCP Servers     │
│  - architect     │  │  - External AI   │  │  - Tools         │
│  - builder       │  │  - Specialists   │  │  - Resources     │
│  - critic        │  │  - Services      │  │  - Prompts       │
└──────────────────┘  └──────────────────┘  └──────────────────┘
                              ↓
                   ┌────────────────────────┐
                   │  Smart Contract        │
                   │  Registry              │
                   │  - Capabilities        │
                   │  - Reputation          │
                   │  - Pricing             │
                   │  - Trust Scores        │
                   └────────────────────────┘
```

---

## Component Design

### 1. Mission File Format

**Enhanced mission file with capability requirements:**

```yaml
mission:
  id: "MISSION-2025-001"
  description: "Build a web application with user authentication"

  requirements:
    capabilities:
      - type: "code_generation"
        language: "python"
        framework: "fastapi"
        min_trust_score: 75

      - type: "database_design"
        database: "postgresql"
        min_trust_score: 80

      - type: "frontend_development"
        framework: "react"
        min_trust_score: 70

    resources:
      - type: "database"
        provider: "mcp://postgresql-server"

      - type: "api_key"
        service: "openai"
        secret_id: "openai-api-key"

  constraints:
    max_cost: 100.00  # USD
    max_duration: 3600  # seconds
    prefer_internal: true  # Prefer internal agents

  breakpoints:
    - stage: "capability_selection"
      type: "human_approval"
      message: "Review and approve selected external capabilities"

    - stage: "before_external_call"
      type: "human_approval"
      message: "Approve call to external agent: {agent_id}"

    - stage: "final_review"
      type: "human_approval"
      message: "Review final artifacts before delivery"

  trust_requirements:
    min_internal_agent_score: 70
    min_external_agent_score: 85
    require_pki_cert: true
```

### 2. Capability Registry (Smart Contract)

**On-chain registry for capability advertisement and discovery:**

```solidity
// Simplified Solidity-style pseudocode
contract CapabilityRegistry {
    struct Capability {
        bytes32 capabilityId;
        address provider;
        string capabilityType;  // e.g., "code_generation"
        string metadata;  // JSON with details
        uint256 pricePerCall;  // in wei
        uint256 reputationScore;  // 0-100
        bytes32[] certHashes;  // PKI certificate hashes
        bool active;
    }

    struct CapabilityCall {
        bytes32 capabilityId;
        address caller;
        uint256 timestamp;
        bool success;
        uint256 costPaid;
    }

    mapping(bytes32 => Capability) public capabilities;
    mapping(bytes32 => CapabilityCall[]) public callHistory;

    function registerCapability(
        string memory capabilityType,
        string memory metadata,
        uint256 price,
        bytes32 certHash
    ) public returns (bytes32);

    function updateReputation(
        bytes32 capabilityId,
        uint256 newScore
    ) public;

    function queryCapabilities(
        string memory capabilityType,
        uint256 minReputation
    ) public view returns (Capability[] memory);

    function recordCall(
        bytes32 capabilityId,
        bool success,
        uint256 cost
    ) public;
}
```

**Off-chain registry alternative (for MVP):**

```python
class CapabilityRegistry:
    """
    Off-chain capability registry with on-chain backup.

    For MVP, use SQLite with optional blockchain sync.
    For production, full smart contract implementation.
    """

    def __init__(self, db_path: Path, blockchain_enabled: bool = False):
        self.db_path = db_path
        self.blockchain_enabled = blockchain_enabled
        # Initialize database tables

    def register_capability(
        self,
        provider_id: str,
        capability_type: str,
        metadata: Dict[str, Any],
        price_per_call: float,
        cert_hash: str
    ) -> str:
        """Register a new capability."""

    def search_capabilities(
        self,
        capability_type: str,
        filters: Dict[str, Any] = None,
        min_reputation: float = 0.0
    ) -> List[CapabilityMatch]:
        """Search for capabilities matching criteria."""

    def update_reputation(
        self,
        capability_id: str,
        success: bool,
        cost: float,
        response_time: float
    ):
        """Update capability reputation based on usage."""
```

### 3. A2A Protocol

**Agent-to-Agent communication protocol:**

```python
class A2AProtocol:
    """
    Agent-to-Agent communication protocol.

    Features:
    - Mutual TLS authentication
    - Certificate verification
    - Trust score validation
    - Encrypted communication
    - Audit logging
    """

    def __init__(
        self,
        pki_manager: PKIManager,
        trust_tracker: AgentReputationTracker,
        secrets_mgr: SecretsManager
    ):
        self.pki_manager = pki_manager
        self.trust_tracker = trust_tracker
        self.secrets_mgr = secrets_mgr

    def call_external_agent(
        self,
        agent_id: str,
        endpoint: str,
        payload: Dict[str, Any],
        caller_cert: bytes,
        min_trust: float = 75.0
    ) -> A2AResponse:
        """
        Call an external agent.

        1. Verify caller certificate
        2. Check caller trust score
        3. Establish mTLS connection
        4. Send encrypted payload
        5. Verify response signature
        6. Update reputation based on result
        7. Log all interactions
        """

    def register_endpoint(
        self,
        capability: str,
        handler: Callable,
        required_trust: float = 0.0
    ):
        """Register an A2A endpoint."""

    def verify_caller(
        self,
        cert: bytes,
        min_trust: float
    ) -> tuple[bool, str]:
        """Verify calling agent's certificate and trust."""
```

### 4. MCP Integration

**Model Context Protocol server and client:**

```python
class MCPIntegration:
    """
    MCP (Model Context Protocol) integration.

    Supports:
    - Tool registration and discovery
    - Resource access
    - Prompt templates
    - Context sharing
    """

    def __init__(
        self,
        server_config: Dict[str, Any],
        secrets_mgr: SecretsManager
    ):
        self.server_config = server_config
        self.secrets_mgr = secrets_mgr
        self.mcp_servers: Dict[str, MCPServer] = {}

    def register_mcp_server(
        self,
        server_id: str,
        server_url: str,
        capabilities: List[str],
        auth_secret_id: Optional[str] = None
    ):
        """Register an MCP server."""

    def query_tools(
        self,
        server_id: str,
        tool_type: Optional[str] = None
    ) -> List[MCPTool]:
        """Query available tools from MCP server."""

    def call_tool(
        self,
        server_id: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> MCPResponse:
        """Call an MCP tool."""

    def access_resource(
        self,
        server_id: str,
        resource_uri: str
    ) -> MCPResource:
        """Access an MCP resource."""
```

### 5. Enhanced Orchestrator

**Orchestrator with dynamic capability matching:**

```python
class EnhancedOrchestrator:
    """
    Enhanced orchestrator with dynamic capability discovery.

    Features:
    - Mission parsing and analysis
    - Internal + external capability inventory
    - Smart matching and ranking
    - Human-in-the-loop breakpoints
    - Cost optimization
    - Trust-based selection
    """

    def __init__(
        self,
        internal_agents: Dict[str, Agent],
        capability_registry: CapabilityRegistry,
        a2a_protocol: A2AProtocol,
        mcp_integration: MCPIntegration,
        trust_tracker: AgentReputationTracker,
        secrets_mgr: SecretsManager
    ):
        self.internal_agents = internal_agents
        self.registry = capability_registry
        self.a2a = a2a_protocol
        self.mcp = mcp_integration
        self.trust_tracker = trust_tracker
        self.secrets_mgr = secrets_mgr

    def execute_mission(
        self,
        mission_file: Path,
        human_approver: Optional[Callable] = None
    ) -> MissionResult:
        """
        Execute mission with dynamic capability discovery.

        Workflow:
        1. Parse mission requirements
        2. Inventory internal capabilities
        3. Query registry for external options
        4. Score and rank all options
        5. Present best matches
        6. Request human approval (if breakpoint)
        7. Execute with selected capabilities
        8. Update reputations
        9. Return results with audit trail
        """
        mission = self._parse_mission(mission_file)

        # Step 1: Analyze requirements
        required_caps = mission.requirements.capabilities

        # Step 2: Inventory internal agents
        internal_matches = self._match_internal_agents(required_caps)

        # Step 3: Query external capabilities
        external_matches = self._query_external_capabilities(required_caps)

        # Step 4: Score and rank
        all_matches = self._score_and_rank(
            internal_matches,
            external_matches,
            mission.constraints,
            mission.trust_requirements
        )

        # Step 5: Human approval (if breakpoint)
        if self._has_breakpoint(mission, "capability_selection"):
            if human_approver:
                approved = human_approver(all_matches)
                if not approved:
                    return MissionResult(status="cancelled_by_user")

        # Step 6: Execute
        result = self._execute_with_capabilities(mission, all_matches)

        # Step 7: Update reputations
        self._update_reputations(result)

        return result

    def _score_capability_match(
        self,
        capability: Capability,
        requirement: CapabilityRequirement,
        constraints: MissionConstraints
    ) -> float:
        """
        Score a capability match (0-100).

        Factors:
        - Exact match vs partial match
        - Trust score
        - Reputation history
        - Cost efficiency
        - Response time
        - Internal vs external preference
        """
        score = 0.0

        # Exact match: +40 points
        if capability.type == requirement.type:
            score += 40

        # Trust score: +30 points
        trust_factor = min(capability.trust_score / 100.0, 1.0)
        score += trust_factor * 30

        # Reputation: +20 points
        reputation_factor = capability.reputation / 100.0
        score += reputation_factor * 20

        # Cost: +10 points (cheaper is better)
        if constraints.max_cost:
            cost_factor = 1.0 - min(capability.price / constraints.max_cost, 1.0)
            score += cost_factor * 10

        # Internal preference bonus
        if capability.is_internal and constraints.prefer_internal:
            score += 10

        return score
```

### 6. Capability Matching Algorithm

**Scoring and ranking algorithm:**

```python
class CapabilityMatcher:
    """
    Intelligent capability matching and ranking.
    """

    def match_and_rank(
        self,
        requirements: List[CapabilityRequirement],
        available: List[Capability],
        constraints: MissionConstraints,
        trust_requirements: TrustRequirements
    ) -> List[RankedMatch]:
        """
        Match requirements to available capabilities and rank results.

        Returns sorted list of matches with scores.
        """
        matches = []

        for req in requirements:
            candidates = self._find_candidates(req, available)
            filtered = self._filter_by_trust(candidates, trust_requirements)
            scored = self._score_candidates(filtered, req, constraints)
            ranked = sorted(scored, key=lambda x: x.score, reverse=True)

            matches.append(RankedMatch(
                requirement=req,
                candidates=ranked[:5],  # Top 5
                best_match=ranked[0] if ranked else None
            ))

        return matches

    def _score_candidates(
        self,
        candidates: List[Capability],
        requirement: CapabilityRequirement,
        constraints: MissionConstraints
    ) -> List[ScoredCapability]:
        """Score each candidate."""
        scored = []

        for cap in candidates:
            score = self._calculate_score(cap, requirement, constraints)
            scored.append(ScoredCapability(
                capability=cap,
                score=score,
                reasons=self._explain_score(cap, requirement, score)
            ))

        return scored

    def _explain_score(
        self,
        capability: Capability,
        requirement: CapabilityRequirement,
        score: float
    ) -> List[str]:
        """Provide human-readable explanation of score."""
        reasons = []

        if capability.type == requirement.type:
            reasons.append(f"✓ Exact capability match ({capability.type})")

        if capability.trust_score >= requirement.min_trust_score:
            reasons.append(f"✓ Meets trust requirement ({capability.trust_score:.1f} >= {requirement.min_trust_score})")

        if capability.reputation >= 80:
            reasons.append(f"✓ High reputation ({capability.reputation:.1f}/100)")

        if capability.is_internal:
            reasons.append("✓ Internal agent (preferred)")

        return reasons
```

---

## Human-in-the-Loop (HITL) Design

### Breakpoint Types

**1. Capability Selection**
```python
# Before selecting external capabilities
if mission.has_breakpoint("capability_selection"):
    print("\n🔍 Capability Selection Review:")
    print("\nTop Matches:")
    for i, match in enumerate(top_matches):
        print(f"{i+1}. {match.capability.name}")
        print(f"   Type: {match.capability.type}")
        print(f"   Trust: {match.capability.trust_score:.1f}")
        print(f"   Cost: ${match.capability.price:.2f}")
        print(f"   Reasons: {', '.join(match.reasons)}")

    approved = input("\nProceed with these selections? [y/N]: ")
    if approved.lower() != 'y':
        return "cancelled"
```

**2. External Call Approval**
```python
# Before calling external agent
if mission.has_breakpoint("before_external_call"):
    print(f"\n📞 External Call Request:")
    print(f"Agent: {agent.name}")
    print(f"Endpoint: {endpoint}")
    print(f"Estimated Cost: ${cost:.2f}")
    print(f"Trust Score: {agent.trust_score:.1f}")

    approved = input("\nApprove this call? [y/N]: ")
    if approved.lower() != 'y':
        return "call_cancelled"
```

**3. Final Review**
```python
# Before completing mission
if mission.has_breakpoint("final_review"):
    print("\n📋 Final Artifact Review:")
    print(f"Artifacts: {len(artifacts)}")
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Duration: {duration}s")

    for artifact in artifacts:
        print(f"\n{artifact.name}:")
        print(artifact.preview())

    approved = input("\nApprove delivery? [y/N]: ")
    if approved.lower() != 'y':
        return "delivery_cancelled"
```

---

## Security Considerations

### 1. Certificate-Based Authentication

All external agents must:
- Have valid PKI certificates
- Pass CRL/OCSP revocation checks
- Meet minimum trust score requirements
- Use mTLS for all communications

### 2. Trust Score Validation

```python
def validate_external_agent(agent_id: str, min_trust: float) -> bool:
    """Validate external agent before use."""

    # Check certificate
    cert = get_agent_certificate(agent_id)
    if not verify_certificate(cert):
        return False

    # Check revocation
    if is_revoked(cert):
        return False

    # Check trust score
    metrics = trust_tracker.get_agent_metrics(agent_id)
    if not metrics or metrics.trust_score < min_trust:
        return False

    return True
```

### 3. Secrets Protection

```python
# Never expose secrets to external agents directly
# Use secrets manager to inject credentials at call time

with secrets_mgr.access_secret("api-key", "orchestrator") as secret:
    # Secret only exists in memory during this block
    response = a2a_protocol.call_external_agent(
        agent_id="external-ai",
        payload={"task": "...", "api_key": secret.get_value()}
    )
# Secret automatically cleared from memory
```

### 4. Audit Trail

All A2A interactions logged:
```python
{
    "timestamp": "2025-12-04T10:30:00Z",
    "mission_id": "MISSION-2025-001",
    "caller_id": "orchestrator",
    "callee_id": "external-ai-agent",
    "capability": "code_generation",
    "cost": 5.00,
    "success": true,
    "trust_score": 87.5,
    "response_time": 2.3,
    "human_approved": true
}
```

---

## Implementation Phases

### Phase 6.1: Foundation (Week 1)
- [ ] Capability registry (off-chain MVP)
- [ ] Basic A2A protocol
- [ ] Mission file parser
- [ ] Internal capability inventory

### Phase 6.2: External Integration (Week 2)
- [ ] MCP client implementation
- [ ] External agent discovery
- [ ] Certificate validation for external agents
- [ ] Basic capability matching

### Phase 6.3: Orchestration (Week 3)
- [ ] Enhanced orchestrator
- [ ] Scoring and ranking algorithm
- [ ] Human-in-the-loop breakpoints
- [ ] Cost tracking and optimization

### Phase 6.4: Smart Contracts (Week 4)
- [ ] Solidity contract development
- [ ] On-chain registry deployment
- [ ] Blockchain integration
- [ ] Reputation tracking on-chain

### Phase 6.5: Production Hardening (Week 5)
- [ ] Comprehensive testing
- [ ] Security audit
- [ ] Performance optimization
- [ ] Documentation

---

## Success Criteria

### Functional Requirements

✅ **Capability Discovery**
- Orchestrator can query registry for capabilities
- Results ranked by relevance and trust

✅ **Dynamic Selection**
- Orchestrator selects best internal or external option
- Respects mission constraints and preferences

✅ **Secure Communication**
- All A2A calls use mTLS
- Certificates verified
- Trust scores validated

✅ **Human Control**
- Breakpoints honored
- Clear approval prompts
- Full visibility into selections

✅ **Cost Management**
- Budget constraints enforced
- Cost estimates provided
- Actual costs tracked

✅ **Audit Trail**
- All decisions logged
- All external calls recorded
- Reputation updates tracked

### Non-Functional Requirements

✅ **Performance**
- Registry queries < 100ms
- Capability scoring < 50ms
- Total overhead < 500ms per mission

✅ **Scalability**
- Support 1000+ registered capabilities
- Handle 100+ concurrent missions
- Scale to distributed deployments

✅ **Security**
- No credential leaks
- All communications encrypted
- Complete audit trail

---

## Next Steps

1. **Review this architecture** with stakeholders
2. **Refine requirements** based on feedback
3. **Create Phase 6.1 implementation plan**
4. **Begin development** with capability registry
5. **Iterate** based on testing and feedback

---

**Document Status:** 📋 Draft for Review
**Next Review:** TBD
**Owner:** Team Agent Development Team

---

*This architecture enables the Team Agent system to dynamically discover and integrate external capabilities while maintaining security, trust, and human oversight.*
