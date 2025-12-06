# Team Agent: Decentralized Agent Marketplace Vision

**Date:** December 6, 2025
**Status:** Architecture Planning
**Vision:** Decentralized marketplace for autonomous agent workflows on Ethereum Optimism L2

---

## Executive Summary

Team Agent is evolving from a standalone multi-agent orchestrator into a **decentralized marketplace** where autonomous agents can discover each other, collaborate on complex missions, publish capabilities, build reputation, and transact value through flexible payment systems.

**Core Vision:**
- Agents publish capabilities via **Agent2Agent (A2A) protocol**
- External systems invoke capabilities via **Model Context Protocol (MCP)**
- Workflows execute on **Ethereum Optimism L2** smart contracts
- Artifacts stored on **IPFS/Filecoin** for permanent decentralized storage
- **Reputation and trust** managed through DAO governance
- **Flexible payment systems** supporting tokens, staking, and alternative value stores
- **Research assistant platform** for scientists to build specialized agent swarms

---

## Current State (Phase 1: Foundation)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Mission Input                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PKI Manager (Root CA + 3 Trust Domains)             │   │
│  │  - Government CA    - Execution CA    - Logging CA   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Agent Manager (Registration & Tracking)             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Capability Registry (Dynamic Discovery)             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Workflow Execution Pipeline                    │
│                                                              │
│  Phase 1: Architecture                                      │
│  ┌────────────────────────────────────────────────┐         │
│  │  Architect (Execution Domain)                  │         │
│  │  - Analyzes requirements                       │         │
│  │  - Designs system architecture                 │         │
│  │  - Signs output with execution cert            │         │
│  └────────────────────────────────────────────────┘         │
│                     │                                        │
│                     ▼                                        │
│  Phase 2: Implementation                                    │
│  ┌────────────────────────────────────────────────┐         │
│  │  DynamicBuilder + Specialist Selection         │         │
│  │  - Matches mission to specialist agent         │         │
│  │  - Specialist uses capability to execute       │         │
│  │  - Current: Legal, AWS, Azure, GCP, OCI        │         │
│  │  - Fallback: Generic Builder                   │         │
│  └────────────────────────────────────────────────┘         │
│                     │                                        │
│                     ▼                                        │
│  Phase 3: Review                                            │
│  ┌────────────────────────────────────────────────┐         │
│  │  Critic (Execution Domain)                     │         │
│  │  - Reviews generated code/documents            │         │
│  │  - Identifies issues                           │         │
│  │  - Assigns quality score (0-10)                │         │
│  └────────────────────────────────────────────────┘         │
│                     │                                        │
│                     ▼                                        │
│  Phase 4: Recording                                         │
│  ┌────────────────────────────────────────────────┐         │
│  │  Recorder (Logging Domain)                     │         │
│  │  - Publishes artifacts to filesystem           │         │
│  │  - Creates comprehensive workflow record       │         │
│  │  - Logs to TuringTape (JSONL audit log)        │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  Optional: Governance (Government Domain)                   │
│  ┌────────────────────────────────────────────────┐         │
│  │  - Pre-build policy checks                     │         │
│  │  - Post-review compliance verification         │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Artifacts & Records                        │
│  - Generated code/documents                                 │
│  - Workflow JSON record                                     │
│  - TuringTape audit log                                     │
│  - All cryptographically signed                             │
└─────────────────────────────────────────────────────────────┘
```

### Current Agents (9 Total)

**Role Agents (4):**
- **Architect**: Mission analysis and architecture design
- **Critic**: Quality review and scoring
- **Recorder**: Artifact publishing and audit logging
- **Governance**: Policy enforcement and compliance

**Specialist Agents (5):**
- **Legal Specialist**: Contract and legal document generation
- **AWS Cloud Specialist**: AWS infrastructure provisioning (Terraform, CloudFormation, boto3)
- **Azure Cloud Specialist**: Azure infrastructure (Terraform, ARM templates, Azure SDK)
- **GCP Cloud Specialist**: GCP infrastructure (Terraform, Deployment Manager, gcloud)
- **OCI Cloud Specialist**: Oracle Cloud Infrastructure (Terraform, OCI CLI, OCI SDK)

### Database Schema

**Agent Cards Table (`agent_cards`):**
```sql
CREATE TABLE agent_cards (
    agent_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    agent_type TEXT NOT NULL,  -- 'role' or 'specialist'
    description TEXT,
    capabilities TEXT,  -- JSON array
    module_path TEXT,
    class_name TEXT,
    trust_domain TEXT,  -- 'EXECUTION', 'GOVERNMENT', 'LOGGING'
    trust_score REAL DEFAULT 0.0,
    total_invocations INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    status TEXT DEFAULT 'active',
    version TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Capability Registry Table (`capability_registry`):**
```sql
CREATE TABLE capability_registry (
    capability_id TEXT PRIMARY KEY,
    capability_name TEXT NOT NULL,
    capability_type TEXT NOT NULL,  -- 'code_generation', 'document_generation'
    description TEXT,
    version TEXT,
    domains TEXT,  -- JSON array (e.g., ['legal', 'healthcare', 'cloud'])
    keywords TEXT,  -- JSON array
    module_path TEXT,
    class_name TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Agent-Capability Mapping (`agent_capabilities`):**
```sql
CREATE TABLE agent_capabilities (
    agent_id TEXT,
    capability_id TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    priority INTEGER,
    times_used INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    FOREIGN KEY (agent_id) REFERENCES agent_cards(agent_id),
    FOREIGN KEY (capability_id) REFERENCES capability_registry(capability_id)
);
```

### PKI Infrastructure

**Three-Tier Certificate Hierarchy:**
```
Root CA (self-signed, 10-year validity)
├── Government/Control Plane CA (5-year validity)
│   └── Governance Agent
├── Execution Plane CA (5-year validity)
│   ├── Architect Agent
│   ├── Builder/Specialists
│   └── Critic Agent
└── Logging/Artifact Plane CA (5-year validity)
    └── Recorder Agent
```

**All workflow operations are cryptographically signed:**
- TuringTape entries
- Agent outputs
- Artifact manifests
- Audit logs

---

## Phase 2: Agent Discovery & Interoperability (Weeks 1-4)

### 2.1 Agent2Agent (A2A) Protocol Implementation

**Goal:** Enable external Team Agent instances to discover and invoke our agents' capabilities.

**A2A Agent Card Format:**
```json
{
  "agent_card_version": "1.0",
  "agent_id": "specialist_aws_01234567",
  "agent_name": "AWS Cloud Specialist",
  "agent_type": "specialist",
  "description": "Provisions AWS cloud infrastructure using Terraform, CloudFormation, and boto3",
  "capabilities": [
    {
      "capability_id": "aws_infrastructure",
      "capability_name": "AWS Infrastructure Provisioning",
      "capability_type": "code_generation",
      "domains": ["cloud", "aws", "infrastructure"],
      "keywords": ["terraform", "cloudformation", "boto3", "ec2", "s3", "lambda"],
      "version": "1.0.0",
      "input_schema": {
        "type": "object",
        "properties": {
          "mission": {"type": "string", "description": "Infrastructure mission description"},
          "architecture": {"type": "string", "description": "High-level architecture plan"}
        },
        "required": ["mission"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "artifacts": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "type": {"type": "string"},
                "name": {"type": "string"},
                "filename": {"type": "string"},
                "content": {"type": "string"}
              }
            }
          }
        }
      }
    }
  ],
  "trust_domain": "EXECUTION",
  "trust_score": 95.0,
  "total_invocations": 42,
  "success_rate": 0.95,
  "reputation": {
    "score": 4.5,
    "reviews": 12,
    "slashing_events": 0
  },
  "pricing": {
    "model": "flexible",
    "accepted_tokens": ["ETH", "OP", "USDC", "TEAM_TOKEN"],
    "price_per_invocation": "0.001 ETH",
    "stake_required": "100 TEAM_TOKEN"
  },
  "endpoints": {
    "well_known": "https://team-agent.example.com/.well-known/agent.json",
    "mcp_server": "https://team-agent.example.com/mcp",
    "blockchain_registry": "0x1234567890abcdef1234567890abcdef12345678"
  },
  "signature": "0xabcdef...",  // Signed by agent's private key
  "certificate_chain": "-----BEGIN CERTIFICATE-----\n..."
}
```

**Implementation Steps:**

1. **Create `.well-known/agent.json` endpoint:**
```python
# backend/app/api/well_known.py

from flask import Blueprint, jsonify
from app.database import get_backend_session
from app.models.agent import AgentCard, CapabilityRegistry, AgentCapabilityMapping
from swarms.team_agent.crypto import Signer, PKIManager, TrustDomain

well_known_bp = Blueprint('well_known', __name__)

@well_known_bp.route('/.well-known/agent.json')
def agent_card():
    """Return A2A-compliant agent card."""
    with get_backend_session() as session:
        # Get all active specialist agents
        specialists = session.query(AgentCard).filter_by(
            agent_type='specialist',
            status='active'
        ).all()

        # Build agent card
        agents = []
        for specialist in specialists:
            # Get capabilities
            mappings = session.query(AgentCapabilityMapping).filter_by(
                agent_id=specialist.agent_id
            ).all()

            capabilities = []
            for mapping in mappings:
                cap = session.query(CapabilityRegistry).filter_by(
                    capability_id=mapping.capability_id
                ).first()

                if cap:
                    capabilities.append({
                        "capability_id": cap.capability_id,
                        "capability_name": cap.capability_name,
                        "capability_type": cap.capability_type,
                        "domains": json.loads(cap.domains) if cap.domains else [],
                        "keywords": json.loads(cap.keywords) if cap.keywords else [],
                        "version": cap.version,
                        # Add input/output schemas
                    })

            agent_data = {
                "agent_card_version": "1.0",
                "agent_id": specialist.agent_id,
                "agent_name": specialist.agent_name,
                "agent_type": specialist.agent_type,
                "description": specialist.description,
                "capabilities": capabilities,
                "trust_domain": specialist.trust_domain,
                "trust_score": specialist.trust_score,
                "total_invocations": specialist.total_invocations,
                "success_rate": specialist.success_rate,
                "pricing": {
                    "model": "flexible",
                    "accepted_tokens": ["ETH", "OP", "USDC", "TEAM_TOKEN"],
                    "price_per_invocation": "0.001 ETH"
                },
                "endpoints": {
                    "well_known": "https://team-agent.example.com/.well-known/agent.json",
                    "mcp_server": "https://team-agent.example.com/mcp"
                }
            }

            # Sign agent card
            pki = PKIManager()
            domain = TrustDomain[specialist.trust_domain]
            chain = pki.get_certificate_chain(domain)
            signer = Signer(
                private_key_path=pki._get_key_path(domain),
                chain_pem=chain['chain']
            )
            signature = signer.sign(json.dumps(agent_data, sort_keys=True))
            agent_data["signature"] = signature
            agent_data["certificate_chain"] = chain['chain']

            agents.append(agent_data)

        return jsonify({
            "version": "1.0",
            "team_agent_instance": "primary",
            "agents": agents,
            "timestamp": datetime.now().isoformat()
        })
```

2. **Create A2A client library for external discovery:**
```python
# swarms/team_agent/a2a/client.py

import requests
from typing import List, Dict, Any

class A2AClient:
    """Client for discovering and invoking remote Team Agent instances."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def discover_agents(self) -> List[Dict[str, Any]]:
        """Fetch agent cards from remote instance."""
        response = requests.get(f"{self.base_url}/.well-known/agent.json")
        response.raise_for_status()
        data = response.json()
        return data.get("agents", [])

    def find_capability(self, capability_type: str, domains: List[str]) -> List[Dict]:
        """Find agents matching capability requirements."""
        agents = self.discover_agents()
        matches = []

        for agent in agents:
            for cap in agent.get("capabilities", []):
                if cap["capability_type"] == capability_type:
                    cap_domains = set(cap.get("domains", []))
                    if cap_domains.intersection(set(domains)):
                        matches.append({
                            "agent": agent,
                            "capability": cap
                        })

        return matches
```

### 2.2 Model Context Protocol (MCP) Server Completion

**Goal:** Expose all capabilities as MCP tools for external invocation.

**Current State:**
- Stub exists in `swarms/team_agent/mcp/mcp_server.py`
- Tool registry and base classes exist

**MCP Tool Format:**
```json
{
  "tool": {
    "name": "aws_infrastructure_provision",
    "description": "Provisions AWS cloud infrastructure using Terraform and CloudFormation",
    "input_schema": {
      "type": "object",
      "properties": {
        "mission": {
          "type": "string",
          "description": "Infrastructure provisioning mission"
        },
        "architecture": {
          "type": "string",
          "description": "Architecture plan from Architect agent"
        }
      },
      "required": ["mission"]
    }
  }
}
```

**Implementation Steps:**

1. **Complete MCP Server (HTTP + WebSocket endpoints):**
```python
# swarms/team_agent/mcp/mcp_server.py

from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit
from app.database import get_backend_session
from app.models.agent import AgentCard, CapabilityRegistry, AgentCapabilityMapping
import importlib

mcp_bp = Blueprint('mcp', __name__, url_prefix='/mcp')

@mcp_bp.route('/tools', methods=['GET'])
def list_tools():
    """List all available MCP tools."""
    with get_backend_session() as session:
        capabilities = session.query(CapabilityRegistry).filter_by(status='active').all()

        tools = []
        for cap in capabilities:
            tools.append({
                "name": cap.capability_id,
                "description": cap.description,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "mission": {"type": "string"},
                        "architecture": {"type": "string"}
                    },
                    "required": ["mission"]
                }
            })

        return jsonify({"tools": tools})


@mcp_bp.route('/tools/<tool_name>/invoke', methods=['POST'])
def invoke_tool(tool_name):
    """Invoke a capability via MCP."""
    payload = request.json

    # Authenticate request (API key, JWT, etc.)
    api_key = request.headers.get('X-API-Key')
    if not validate_api_key(api_key):
        return jsonify({"error": "Unauthorized"}), 401

    # Find capability and agent
    with get_backend_session() as session:
        cap = session.query(CapabilityRegistry).filter_by(
            capability_id=tool_name,
            status='active'
        ).first()

        if not cap:
            return jsonify({"error": "Tool not found"}), 404

        # Find agent that can execute this capability
        mapping = session.query(AgentCapabilityMapping).filter_by(
            capability_id=tool_name,
            is_primary=True
        ).first()

        if not mapping:
            return jsonify({"error": "No agent available for this capability"}), 404

        agent_card = session.query(AgentCard).filter_by(
            agent_id=mapping.agent_id
        ).first()

        # Dynamically load and instantiate agent
        module = importlib.import_module(agent_card.module_path)
        specialist_class = getattr(module, agent_card.class_name)
        specialist = specialist_class()

        # Execute capability
        result = specialist.execute(payload)

        # Track invocation
        from swarms.team_agent.agent_manager import AgentManager
        agent_manager = AgentManager()
        agent_manager.track_invocation(
            agent_card.agent_id,
            workflow_id=f"mcp_{tool_name}_{datetime.now().isoformat()}",
            result=result,
            success=True
        )

        return jsonify(result)


def validate_api_key(api_key: str) -> bool:
    """Validate API key for MCP access."""
    # TODO: Implement proper API key validation
    # For now, check against environment variable or database
    import os
    valid_key = os.getenv('MCP_API_KEY', 'dev_key_12345')
    return api_key == valid_key
```

2. **Add WebSocket support for streaming responses:**
```python
# WebSocket endpoint for long-running capability executions
@socketio.on('invoke_tool_stream')
def handle_invoke_tool_stream(data):
    """Invoke tool with streaming progress updates."""
    tool_name = data['tool_name']
    payload = data['payload']

    # Execute capability with progress callbacks
    def progress_callback(message):
        emit('progress', {'message': message})

    # Execute (with modified capability execute methods to support callbacks)
    # ... implementation
```

---

## Phase 3: Ethereum Optimism L2 Integration (Weeks 5-20)

### 3.1 Smart Contract Architecture

**Three Core Smart Contracts:**

#### 1. WorkflowConductor.sol - Workflow Execution & State Management

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract WorkflowConductor is AccessControl, ReentrancyGuard {
    bytes32 public constant AGENT_ROLE = keccak256("AGENT_ROLE");

    enum WorkflowStatus {
        Submitted,
        ArchitectureComplete,
        ImplementationComplete,
        ReviewComplete,
        Published,
        Failed
    }

    struct Workflow {
        bytes32 workflowId;
        address submitter;
        string mission;
        string ipfsArchitecture;  // CID for architecture JSON
        string ipfsImplementation;  // CID for implementation artifacts
        string ipfsReview;  // CID for critic review
        WorkflowStatus status;
        uint256 timestamp;
        address[] agentsInvolved;
        mapping(address => bool) agentApprovals;
        uint256 totalPayment;
        bool paymentReleased;
    }

    mapping(bytes32 => Workflow) public workflows;
    bytes32[] public workflowIds;

    event WorkflowSubmitted(bytes32 indexed workflowId, address indexed submitter, string mission);
    event WorkflowPhaseComplete(bytes32 indexed workflowId, WorkflowStatus status, string ipfsCid);
    event WorkflowPublished(bytes32 indexed workflowId, string ipfsArtifacts);
    event AgentApproval(bytes32 indexed workflowId, address indexed agent);
    event PaymentReleased(bytes32 indexed workflowId, uint256 amount);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function submitWorkflow(
        string memory mission,
        address[] memory agents
    ) external payable returns (bytes32) {
        bytes32 workflowId = keccak256(
            abi.encodePacked(msg.sender, mission, block.timestamp)
        );

        Workflow storage wf = workflows[workflowId];
        wf.workflowId = workflowId;
        wf.submitter = msg.sender;
        wf.mission = mission;
        wf.status = WorkflowStatus.Submitted;
        wf.timestamp = block.timestamp;
        wf.agentsInvolved = agents;
        wf.totalPayment = msg.value;

        workflowIds.push(workflowId);

        emit WorkflowSubmitted(workflowId, msg.sender, mission);

        return workflowId;
    }

    function submitArchitecture(
        bytes32 workflowId,
        string memory ipfsCid
    ) external onlyRole(AGENT_ROLE) {
        Workflow storage wf = workflows[workflowId];
        require(wf.status == WorkflowStatus.Submitted, "Invalid workflow state");

        wf.ipfsArchitecture = ipfsCid;
        wf.status = WorkflowStatus.ArchitectureComplete;

        emit WorkflowPhaseComplete(workflowId, WorkflowStatus.ArchitectureComplete, ipfsCid);
    }

    function submitImplementation(
        bytes32 workflowId,
        string memory ipfsCid
    ) external onlyRole(AGENT_ROLE) {
        Workflow storage wf = workflows[workflowId];
        require(wf.status == WorkflowStatus.ArchitectureComplete, "Invalid workflow state");

        wf.ipfsImplementation = ipfsCid;
        wf.status = WorkflowStatus.ImplementationComplete;

        emit WorkflowPhaseComplete(workflowId, WorkflowStatus.ImplementationComplete, ipfsCid);
    }

    function submitReview(
        bytes32 workflowId,
        string memory ipfsCid,
        bool approved
    ) external onlyRole(AGENT_ROLE) {
        Workflow storage wf = workflows[workflowId];
        require(wf.status == WorkflowStatus.ImplementationComplete, "Invalid workflow state");

        wf.ipfsReview = ipfsCid;

        if (approved) {
            wf.status = WorkflowStatus.ReviewComplete;
            emit WorkflowPhaseComplete(workflowId, WorkflowStatus.ReviewComplete, ipfsCid);
        } else {
            wf.status = WorkflowStatus.Failed;
            // Refund submitter
            payable(wf.submitter).transfer(wf.totalPayment);
            wf.paymentReleased = true;
        }
    }

    function publishArtifacts(
        bytes32 workflowId,
        string memory ipfsCid
    ) external onlyRole(AGENT_ROLE) {
        Workflow storage wf = workflows[workflowId];
        require(wf.status == WorkflowStatus.ReviewComplete, "Invalid workflow state");

        wf.status = WorkflowStatus.Published;

        emit WorkflowPublished(workflowId, ipfsCid);

        // Release payment to agents
        _releasePayment(workflowId);
    }

    function _releasePayment(bytes32 workflowId) internal nonReentrant {
        Workflow storage wf = workflows[workflowId];
        require(!wf.paymentReleased, "Payment already released");

        uint256 perAgentPayment = wf.totalPayment / wf.agentsInvolved.length;

        for (uint i = 0; i < wf.agentsInvolved.length; i++) {
            payable(wf.agentsInvolved[i]).transfer(perAgentPayment);
        }

        wf.paymentReleased = true;
        emit PaymentReleased(workflowId, wf.totalPayment);
    }

    function getWorkflow(bytes32 workflowId) external view returns (
        address submitter,
        string memory mission,
        WorkflowStatus status,
        uint256 timestamp,
        string memory ipfsArchitecture,
        string memory ipfsImplementation,
        string memory ipfsReview
    ) {
        Workflow storage wf = workflows[workflowId];
        return (
            wf.submitter,
            wf.mission,
            wf.status,
            wf.timestamp,
            wf.ipfsArchitecture,
            wf.ipfsImplementation,
            wf.ipfsReview
        );
    }
}
```

#### 2. CapabilityMarketplace.sol - Capability & Agent Discovery

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract CapabilityMarketplace is Ownable {
    struct Capability {
        bytes32 capabilityId;
        address provider;
        string name;
        string capabilityType;  // 'code_generation', 'document_generation'
        string[] domains;  // ['legal', 'cloud', 'medical']
        string metadataUri;  // IPFS CID with full capability metadata
        uint256 pricePerInvocation;  // In wei
        uint256 stakeRequired;  // Stake in TEAM tokens
        bool active;
        uint256 totalInvocations;
        uint256 successfulInvocations;
        uint256 reputation;  // 0-100 score
    }

    struct AgentCard {
        address agentAddress;
        string agentName;
        string agentType;  // 'specialist', 'role'
        bytes32[] capabilityIds;
        string metadataUri;  // IPFS CID for A2A agent card
        uint256 trustScore;
        uint256 totalEarnings;
        bool active;
    }

    mapping(bytes32 => Capability) public capabilities;
    mapping(address => AgentCard) public agents;

    bytes32[] public capabilityIds;
    address[] public agentAddresses;

    event CapabilityRegistered(bytes32 indexed capabilityId, address indexed provider, string name);
    event CapabilityInvoked(bytes32 indexed capabilityId, address indexed invoker, bool success);
    event AgentRegistered(address indexed agentAddress, string agentName);
    event ReputationUpdated(bytes32 indexed capabilityId, uint256 newReputation);

    function registerCapability(
        string memory name,
        string memory capabilityType,
        string[] memory domains,
        string memory metadataUri,
        uint256 pricePerInvocation,
        uint256 stakeRequired
    ) external returns (bytes32) {
        bytes32 capabilityId = keccak256(
            abi.encodePacked(msg.sender, name, block.timestamp)
        );

        capabilities[capabilityId] = Capability({
            capabilityId: capabilityId,
            provider: msg.sender,
            name: name,
            capabilityType: capabilityType,
            domains: domains,
            metadataUri: metadataUri,
            pricePerInvocation: pricePerInvocation,
            stakeRequired: stakeRequired,
            active: true,
            totalInvocations: 0,
            successfulInvocations: 0,
            reputation: 50  // Start at neutral reputation
        });

        capabilityIds.push(capabilityId);

        emit CapabilityRegistered(capabilityId, msg.sender, name);

        return capabilityId;
    }

    function registerAgent(
        string memory agentName,
        string memory agentType,
        bytes32[] memory capabilityIds_,
        string memory metadataUri
    ) external {
        agents[msg.sender] = AgentCard({
            agentAddress: msg.sender,
            agentName: agentName,
            agentType: agentType,
            capabilityIds: capabilityIds_,
            metadataUri: metadataUri,
            trustScore: 0,
            totalEarnings: 0,
            active: true
        });

        agentAddresses.push(msg.sender);

        emit AgentRegistered(msg.sender, agentName);
    }

    function recordInvocation(
        bytes32 capabilityId,
        bool success
    ) external {
        Capability storage cap = capabilities[capabilityId];
        require(cap.active, "Capability not active");

        cap.totalInvocations++;
        if (success) {
            cap.successfulInvocations++;
        }

        // Update reputation: success_rate * 100
        cap.reputation = (cap.successfulInvocations * 100) / cap.totalInvocations;

        emit CapabilityInvoked(capabilityId, msg.sender, success);
        emit ReputationUpdated(capabilityId, cap.reputation);
    }

    function searchCapabilities(
        string memory capabilityType,
        uint256 minReputation
    ) external view returns (bytes32[] memory) {
        uint256 count = 0;

        // Count matches
        for (uint i = 0; i < capabilityIds.length; i++) {
            Capability storage cap = capabilities[capabilityIds[i]];
            if (
                cap.active &&
                keccak256(bytes(cap.capabilityType)) == keccak256(bytes(capabilityType)) &&
                cap.reputation >= minReputation
            ) {
                count++;
            }
        }

        // Build results array
        bytes32[] memory results = new bytes32[](count);
        uint256 index = 0;

        for (uint i = 0; i < capabilityIds.length; i++) {
            Capability storage cap = capabilities[capabilityIds[i]];
            if (
                cap.active &&
                keccak256(bytes(cap.capabilityType)) == keccak256(bytes(capabilityType)) &&
                cap.reputation >= minReputation
            ) {
                results[index] = capabilityIds[i];
                index++;
            }
        }

        return results;
    }

    function getCapability(bytes32 capabilityId) external view returns (
        address provider,
        string memory name,
        string memory capabilityType,
        uint256 pricePerInvocation,
        uint256 reputation,
        uint256 totalInvocations
    ) {
        Capability storage cap = capabilities[capabilityId];
        return (
            cap.provider,
            cap.name,
            cap.capabilityType,
            cap.pricePerInvocation,
            cap.reputation,
            cap.totalInvocations
        );
    }
}
```

#### 3. ReputationDAO.sol - Decentralized Reputation & Governance

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/governance/Governor.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorSettings.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";

contract ReputationDAO is Governor, GovernorSettings, GovernorCountingSimple, GovernorVotes {
    struct ReputationStake {
        address agent;
        uint256 stakeAmount;
        uint256 lockedUntil;
        uint256 slashingEvents;
    }

    mapping(address => ReputationStake) public stakes;

    event AgentStaked(address indexed agent, uint256 amount);
    event AgentSlashed(address indexed agent, uint256 amount, string reason);
    event AgentRewardeded(address indexed agent, uint256 amount);

    constructor(IVotes _token)
        Governor("Team Agent Reputation DAO")
        GovernorSettings(1, 50400, 0)  // 1 block delay, ~1 week voting period, no proposal threshold
        GovernorVotes(_token)
    {}

    function stakeReputation(uint256 amount) external payable {
        require(msg.value == amount, "Incorrect stake amount");

        ReputationStake storage stake = stakes[msg.sender];
        stake.agent = msg.sender;
        stake.stakeAmount += amount;
        stake.lockedUntil = block.timestamp + 30 days;

        emit AgentStaked(msg.sender, amount);
    }

    function proposeSlashing(
        address agent,
        uint256 slashAmount,
        string memory reason
    ) external returns (uint256) {
        // Create governance proposal to slash agent's stake
        // Requires DAO voting to execute
    }

    function executeSlashing(
        address agent,
        uint256 slashAmount
    ) internal {
        ReputationStake storage stake = stakes[agent];
        require(stake.stakeAmount >= slashAmount, "Insufficient stake");

        stake.stakeAmount -= slashAmount;
        stake.slashingEvents++;

        // Transfer slashed amount to DAO treasury
        payable(address(this)).transfer(slashAmount);

        emit AgentSlashed(agent, slashAmount, "DAO voted to slash");
    }

    // Required overrides for multiple inheritance
    function votingDelay() public view override(IGovernor, GovernorSettings) returns (uint256) {
        return super.votingDelay();
    }

    function votingPeriod() public view override(IGovernor, GovernorSettings) returns (uint256) {
        return super.votingPeriod();
    }

    function quorum(uint256) public pure override returns (uint256) {
        return 100e18;  // 100 tokens
    }

    function proposalThreshold() public view override(Governor, GovernorSettings) returns (uint256) {
        return super.proposalThreshold();
    }
}
```

### 3.2 IPFS Integration for Artifact Storage

**Goal:** Store all workflow artifacts (architecture, code, reviews) on IPFS/Filecoin for permanent decentralized storage.

**Implementation:**

```python
# swarms/team_agent/storage/ipfs_client.py

import requests
import json
from typing import Dict, Any

class IPFSClient:
    """Client for uploading/retrieving artifacts from IPFS."""

    def __init__(self, api_url: str = "http://127.0.0.1:5001"):
        self.api_url = api_url

    def upload_json(self, data: Dict[str, Any]) -> str:
        """
        Upload JSON data to IPFS.

        Returns:
            IPFS CID (Content Identifier)
        """
        json_str = json.dumps(data, indent=2)

        response = requests.post(
            f"{self.api_url}/api/v0/add",
            files={'file': ('data.json', json_str, 'application/json')}
        )

        response.raise_for_status()
        result = response.json()
        return result['Hash']  # CID

    def upload_file(self, file_path: str) -> str:
        """Upload file to IPFS."""
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.api_url}/api/v0/add",
                files={'file': f}
            )

        response.raise_for_status()
        result = response.json()
        return result['Hash']

    def retrieve(self, cid: str) -> bytes:
        """Retrieve data from IPFS by CID."""
        response = requests.post(
            f"{self.api_url}/api/v0/cat",
            params={'arg': cid}
        )

        response.raise_for_status()
        return response.content

    def pin(self, cid: str):
        """Pin CID to ensure persistence."""
        response = requests.post(
            f"{self.api_url}/api/v0/pin/add",
            params={'arg': cid}
        )
        response.raise_for_status()
```

**Integration with Orchestrator:**

```python
# Modified orchestrator.py _execute_workflow method

def _execute_workflow(self, mission: str, architect, critic, recorder, governance=None) -> dict:
    # ... existing workflow phases ...

    # Phase 4: Recording/Publishing
    self.logger.info("Phase 4: Recording/Publishing")

    # Upload artifacts to IPFS
    ipfs_client = IPFSClient()

    # Upload architecture
    architecture_cid = ipfs_client.upload_json(architect_output)
    ipfs_client.pin(architecture_cid)

    # Upload implementation
    implementation_cid = ipfs_client.upload_json(builder_result)
    ipfs_client.pin(implementation_cid)

    # Upload review
    review_cid = ipfs_client.upload_json(critic_output)
    ipfs_client.pin(review_cid)

    # Publish to blockchain
    blockchain_client = OptimismClient()
    tx_hash = blockchain_client.submit_workflow(
        mission=mission,
        architecture_cid=architecture_cid,
        implementation_cid=implementation_cid,
        review_cid=review_cid,
        agents=[architect.id, builder_id, critic.id, recorder.id]
    )

    self.logger.info(f"Workflow published to blockchain: {tx_hash}")

    return {
        "workflow_id": self.current_workflow_id,
        "mission": mission,
        "architecture_cid": architecture_cid,
        "implementation_cid": implementation_cid,
        "review_cid": review_cid,
        "blockchain_tx": tx_hash,
        "timestamp": datetime.now().isoformat(),
    }
```

### 3.3 Blockchain Client for Workflow Submission

```python
# swarms/team_agent/blockchain/optimism_client.py

from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

class OptimismClient:
    """Client for interacting with Optimism L2 smart contracts."""

    def __init__(self, rpc_url: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.account = self.w3.eth.account.from_key(private_key)

        # Load contract ABIs
        with open('contracts/WorkflowConductor.json') as f:
            conductor_abi = json.load(f)['abi']

        self.conductor = self.w3.eth.contract(
            address='0x...',  # Deployed contract address
            abi=conductor_abi
        )

    def submit_workflow(
        self,
        mission: str,
        architecture_cid: str,
        implementation_cid: str,
        review_cid: str,
        agents: list,
        payment_amount: int = 0
    ) -> str:
        """Submit workflow to blockchain."""

        # Submit workflow
        tx = self.conductor.functions.submitWorkflow(
            mission,
            agents
        ).build_transaction({
            'from': self.account.address,
            'value': payment_amount,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for transaction receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Get workflow ID from event logs
        workflow_id = receipt['logs'][0]['topics'][1].hex()

        # Submit phases
        self._submit_architecture(workflow_id, architecture_cid)
        self._submit_implementation(workflow_id, implementation_cid)
        self._submit_review(workflow_id, review_cid, approved=True)

        return tx_hash.hex()

    def _submit_architecture(self, workflow_id: str, cid: str):
        """Submit architecture phase."""
        tx = self.conductor.functions.submitArchitecture(
            workflow_id,
            cid
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
```

---

## Phase 4: Flexible Payment System (Weeks 21-24)

### 4.1 Multi-Token Payment Support

**Supported Payment Methods:**
1. **ETH (Ethereum native token)**
2. **OP (Optimism native token)**
3. **USDC/USDT (Stablecoins)**
4. **TEAM Token (Custom ERC-20 governance token)**
5. **Alternative Value Stores** (configurable per agent)

**Implementation:**

```solidity
// contracts/PaymentRouter.sol

contract PaymentRouter {
    enum PaymentMethod {
        ETH,
        OP,
        USDC,
        TEAM_TOKEN,
        CUSTOM
    }

    struct Payment {
        PaymentMethod method;
        address tokenAddress;  // For ERC-20 tokens
        uint256 amount;
        address recipient;
        bool released;
    }

    mapping(bytes32 => Payment[]) public workflowPayments;

    function submitPayment(
        bytes32 workflowId,
        PaymentMethod method,
        address tokenAddress,
        uint256 amount
    ) external payable {
        if (method == PaymentMethod.ETH || method == PaymentMethod.OP) {
            require(msg.value == amount, "Incorrect ETH amount");
        } else {
            // Transfer ERC-20 tokens to escrow
            IERC20(tokenAddress).transferFrom(msg.sender, address(this), amount);
        }

        workflowPayments[workflowId].push(Payment({
            method: method,
            tokenAddress: tokenAddress,
            amount: amount,
            recipient: address(0),  // Set when workflow completes
            released: false
        }));
    }

    function releasePayments(
        bytes32 workflowId,
        address[] memory recipients
    ) external {
        Payment[] storage payments = workflowPayments[workflowId];

        for (uint i = 0; i < payments.length; i++) {
            Payment storage payment = payments[i];
            require(!payment.released, "Payment already released");

            uint256 perRecipient = payment.amount / recipients.length;

            for (uint j = 0; j < recipients.length; j++) {
                if (payment.method == PaymentMethod.ETH || payment.method == PaymentMethod.OP) {
                    payable(recipients[j]).transfer(perRecipient);
                } else {
                    IERC20(payment.tokenAddress).transfer(recipients[j], perRecipient);
                }
            }

            payment.released = true;
        }
    }
}
```

### 4.2 "Magic Jelly Beans" - Custom Value Systems

**Concept:** Allow researchers and organizations to create custom value stores for agent payments.

**Examples:**
- **Research Credits**: Universities issue research credits that can be exchanged for agent services
- **Compute Time**: Cloud providers issue compute time tokens
- **Data Access**: Data providers issue tokens for dataset access
- **Reputation Points**: Community reputation scores that can be staked

**Implementation:**

```solidity
// contracts/CustomValueRegistry.sol

contract CustomValueRegistry {
    struct CustomValue {
        string name;
        string symbol;
        address tokenContract;  // ERC-20 or custom implementation
        address issuer;
        bool accepted;  // DAO-approved for payments
    }

    mapping(bytes32 => CustomValue) public customValues;
    bytes32[] public acceptedValueIds;

    event CustomValueProposed(bytes32 indexed valueId, string name, address issuer);
    event CustomValueAccepted(bytes32 indexed valueId);

    function proposeCustomValue(
        string memory name,
        string memory symbol,
        address tokenContract
    ) external returns (bytes32) {
        bytes32 valueId = keccak256(abi.encodePacked(name, symbol, msg.sender));

        customValues[valueId] = CustomValue({
            name: name,
            symbol: symbol,
            tokenContract: tokenContract,
            issuer: msg.sender,
            accepted: false
        });

        emit CustomValueProposed(valueId, name, msg.sender);

        return valueId;
    }

    // DAO governance votes to accept custom value
    function acceptCustomValue(bytes32 valueId) external {
        // Requires DAO approval
        customValues[valueId].accepted = true;
        acceptedValueIds.push(valueId);

        emit CustomValueAccepted(valueId);
    }
}
```

---

## Phase 5: Research Assistant Platform (Weeks 25-32)

### 5.1 Research Use Cases

**Target Users:**
- Academic researchers (universities, labs)
- Data scientists
- Biotech/pharma researchers
- Climate scientists
- Social science researchers

**Specialized Research Agents:**

1. **Literature Review Agent**
   - Capability: `literature_search`
   - Domains: `['academic', 'research', 'literature']`
   - Tools: PubMed API, arXiv API, Semantic Scholar API

2. **Data Analysis Agent**
   - Capability: `statistical_analysis`
   - Domains: `['research', 'statistics', 'data_science']`
   - Tools: Pandas, NumPy, SciPy, Statsmodels

3. **Experiment Design Agent**
   - Capability: `experiment_planning`
   - Domains: `['research', 'experimental_design', 'methodology']`
   - Tools: DOE (Design of Experiments) libraries

4. **Grant Writing Agent**
   - Capability: `grant_proposal_generation`
   - Domains: `['research', 'writing', 'grants']`
   - Tools: NIH/NSF template libraries

5. **Lab Automation Agent**
   - Capability: `protocol_generation`
   - Domains: `['research', 'biology', 'chemistry', 'automation']`
   - Tools: Protocol libraries, equipment APIs

### 5.2 Research Workflow Example

```python
# examples/research_workflow.py

from swarms.team_agent.orchestrator import Orchestrator

# Initialize orchestrator
orchestrator = Orchestrator()

# Research mission
mission = """
Conduct a systematic review of CRISPR gene editing applications in treating
sickle cell disease, published in the last 5 years. Analyze study methodologies,
success rates, and safety profiles. Generate a comprehensive literature review
with statistical meta-analysis.
"""

# Execute workflow
result = orchestrator.execute(mission)

# Expected specialist selection: Literature Review Agent + Data Analysis Agent
# Output artifacts:
# - literature_review.md
# - studies_database.csv
# - meta_analysis.ipynb
# - bibliography.bib
```

### 5.3 Research Payment Models

**1. Institution Credits:**
```solidity
// Universities purchase bulk credits
function purchaseInstitutionCredits(uint256 creditAmount) external payable {
    // Mint research credits as ERC-20 tokens
}
```

**2. Grant-Funded Workflows:**
```solidity
// NSF/NIH grants fund specific research workflows
function fundResearchGrant(
    string memory grantId,
    uint256 workflowBudget
) external {
    // Allocate grant funds to workflow escrow
}
```

**3. Open Science Bounties:**
```solidity
// Community-funded bounties for open research
function createResearchBounty(
    string memory researchQuestion,
    uint256 bountyAmount
) external payable {
    // Anyone can complete the research and claim bounty
}
```

---

## Phase 6: Complete Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                          User/Client Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Web Frontend │  │ CLI Client   │  │ API Client   │  │ External     │      │
│  │              │  │              │  │              │  │ Team Agent   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │                  │
          ▼                  ▼                  ▼                  ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                      Discovery & Invocation Layer                              │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  A2A Protocol Endpoints                                                 │   │
│  │  - /.well-known/agent.json (Agent card discovery)                      │   │
│  │  - Published capabilities, pricing, reputation                         │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  MCP Server (Model Context Protocol)                                   │   │
│  │  - /mcp/tools (List all capabilities as tools)                         │   │
│  │  - /mcp/tools/{tool_name}/invoke (Execute capability)                  │   │
│  │  - WebSocket streaming for long-running operations                     │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
          │                                    │
          ▼                                    ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                        Orchestration Layer                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  Orchestrator                                                           │   │
│  │  - Workflow coordination                                               │   │
│  │  - PKI certificate distribution (3 trust domains)                      │   │
│  │  - Agent lifecycle management                                          │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  Agent Manager                                                          │   │
│  │  - Agent registration (role + specialist agents)                       │   │
│  │  - Invocation tracking                                                 │   │
│  │  - Trust score updates                                                 │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  Capability Registry                                                    │   │
│  │  - Dynamic capability discovery                                        │   │
│  │  - Keyword matching                                                    │   │
│  │  - Agent-capability mapping                                            │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                      Workflow Execution Pipeline                               │
│                                                                                │
│  ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐        │
│  │   Architect     │────▶│ DynamicBuilder + │────▶│     Critic      │        │
│  │   (EXECUTION)   │     │   Specialist     │     │   (EXECUTION)   │        │
│  │                 │     │   Selection      │     │                 │        │
│  │ - Requirements  │     │   (EXECUTION)    │     │ - Code review   │        │
│  │ - Architecture  │     │                  │     │ - Quality score │        │
│  │ - Design        │     │ Current:         │     │ - Issue list    │        │
│  └─────────────────┘     │ - Legal          │     └─────────────────┘        │
│                          │ - AWS            │              │                  │
│  ┌─────────────────┐     │ - Azure          │     ┌─────────────────┐        │
│  │   Governance    │     │ - GCP            │────▶│    Recorder     │        │
│  │  (GOVERNMENT)   │     │ - OCI            │     │    (LOGGING)    │        │
│  │                 │     │                  │     │                 │        │
│  │ - Policy check  │     │ Future:          │     │ - Publish       │        │
│  │ - Compliance    │     │ - Medical        │     │ - Audit log     │        │
│  └─────────────────┘     │ - Financial      │     │ - TuringTape    │        │
│                          │ - Research       │     └─────────────────┘        │
│                          └──────────────────┘                                 │
└───────────────────────────────────────────────────────────────────────────────┘
          │                                            │
          ▼                                            ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                       Storage & Persistence Layer                              │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  IPFS/Filecoin (Decentralized Artifact Storage)                        │   │
│  │  - Architecture JSON                                                   │   │
│  │  - Implementation artifacts (code, documents)                          │   │
│  │  - Review reports                                                      │   │
│  │  - Final workflow record                                               │   │
│  │  - Pinned for permanent availability                                   │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  SQLite Databases (Local State)                                        │   │
│  │  - backend.db (agent_cards, capability_registry, mappings)             │   │
│  │  - trust.db (PKI certificates, trust chains)                           │   │
│  │  - TuringTape (JSONL audit log - cryptographically signed)             │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                    Ethereum Optimism L2 Blockchain                             │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  WorkflowConductor.sol                                                  │   │
│  │  - submitWorkflow(mission, agents, payment)                            │   │
│  │  - submitArchitecture(workflowId, ipfsCid)                             │   │
│  │  - submitImplementation(workflowId, ipfsCid)                           │   │
│  │  - submitReview(workflowId, ipfsCid, approved)                         │   │
│  │  - publishArtifacts(workflowId, ipfsCid)                               │   │
│  │  - releasePayment(workflowId) → Distribute to agents                   │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  CapabilityMarketplace.sol                                              │   │
│  │  - registerCapability(name, type, domains, price, stake)               │   │
│  │  - registerAgent(name, capabilities, metadataUri)                      │   │
│  │  - searchCapabilities(type, minReputation)                             │   │
│  │  - recordInvocation(capabilityId, success)                             │   │
│  │  - updateReputation(capabilityId, newScore)                            │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  ReputationDAO.sol                                                      │   │
│  │  - stakeReputation(amount) → Lock ETH/tokens for trust                 │   │
│  │  - proposeSlashing(agent, amount, reason) → Create DAO proposal        │   │
│  │  - vote(proposalId, support) → DAO governance voting                   │   │
│  │  - executeSlashing(agent) → Penalize malicious agents                  │   │
│  │  - rewardAgent(agent, amount) → Reward high performers                 │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  PaymentRouter.sol                                                      │   │
│  │  - submitPayment(workflowId, method, token, amount)                    │   │
│  │  - releasePayments(workflowId, recipients[])                           │   │
│  │  - Supported: ETH, OP, USDC, TEAM_TOKEN, Custom Value Stores           │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  CustomValueRegistry.sol                                                │   │
│  │  - proposeCustomValue(name, symbol, tokenContract)                     │   │
│  │  - acceptCustomValue(valueId) → DAO approval required                  │   │
│  │  - Examples: Research Credits, Compute Time, Data Access, Jelly Beans  │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Weeks 1-4: Agent Discovery & Interoperability (Phase 2)
- ✅ Week 1: `.well-known/agent.json` endpoint implementation
- ✅ Week 1: A2A agent card schema and signing
- ✅ Week 2: A2A client library for external discovery
- ✅ Week 3: MCP server HTTP endpoints (list tools, invoke tool)
- ✅ Week 4: MCP WebSocket streaming support
- ✅ Week 4: API key authentication for MCP

**Deliverables:**
- External Team Agent instances can discover our capabilities
- External systems can invoke capabilities via MCP
- All capabilities exposed as MCP tools
- Comprehensive documentation and examples

---

### Weeks 5-12: Smart Contract Development (Phase 3A)
- ✅ Week 5: WorkflowConductor.sol implementation
- ✅ Week 6: WorkflowConductor unit tests (Hardhat/Foundry)
- ✅ Week 7: CapabilityMarketplace.sol implementation
- ✅ Week 8: CapabilityMarketplace unit tests
- ✅ Week 9: ReputationDAO.sol implementation
- ✅ Week 10: ReputationDAO unit tests
- ✅ Week 11: PaymentRouter.sol and CustomValueRegistry.sol
- ✅ Week 12: End-to-end contract integration tests

**Deliverables:**
- Fully tested smart contracts
- Contract deployment scripts
- Gas optimization analysis
- Security audit preparation

---

### Weeks 13-16: Optimism L2 Deployment (Phase 3B)
- ✅ Week 13: Deploy to Optimism Sepolia testnet
- ✅ Week 14: Integration testing on testnet
- ✅ Week 14: Frontend for blockchain interaction
- ✅ Week 15: IPFS client integration (Pinata or Web3.Storage)
- ✅ Week 16: End-to-end workflow: Mission → Blockchain → IPFS

**Deliverables:**
- Contracts deployed to Optimism Sepolia
- Python blockchain client library
- IPFS artifact storage working
- Frontend blockchain explorer integration

---

### Weeks 17-20: IPFS & Blockchain Integration (Phase 3C)
- ✅ Week 17: Orchestrator blockchain client integration
- ✅ Week 18: Automatic workflow publishing to blockchain
- ✅ Week 19: IPFS pinning service integration (Pinata)
- ✅ Week 20: Artifact retrieval from IPFS by CID

**Deliverables:**
- All workflows automatically published to blockchain
- Artifacts stored on IPFS with pinning
- Blockchain event listeners for workflow updates
- Comprehensive logging and monitoring

---

### Weeks 21-24: Flexible Payment System (Phase 4)
- ✅ Week 21: Multi-token payment router implementation
- ✅ Week 22: Custom value registry (research credits, compute time)
- ✅ Week 23: Frontend payment method selection
- ✅ Week 24: Payment escrow and release automation

**Deliverables:**
- Support for ETH, OP, USDC, TEAM_TOKEN payments
- Custom value store registration via DAO governance
- Frontend UI for payment method selection
- Automated payment release after successful workflows

---

### Weeks 25-28: Research Assistant Specialists (Phase 5A)
- ✅ Week 25: Literature Review Agent (PubMed, arXiv, Semantic Scholar APIs)
- ✅ Week 26: Data Analysis Agent (Pandas, SciPy, Statsmodels)
- ✅ Week 27: Experiment Design Agent (DOE libraries)
- ✅ Week 28: Grant Writing Agent (NIH/NSF templates)

**Deliverables:**
- 4 new research-focused specialist agents
- Integration with academic APIs
- Example research workflows
- Documentation for researchers

---

### Weeks 29-32: Research Platform & Documentation (Phase 5B)
- ✅ Week 29: Lab Automation Agent (protocol generation)
- ✅ Week 30: Research payment models (institution credits, grants, bounties)
- ✅ Week 31: Research use case documentation
- ✅ Week 32: Open science bounty system

**Deliverables:**
- Complete research assistant platform
- Flexible payment options for academic institutions
- Comprehensive research use case examples
- Open science community integration

---

### Weeks 33-36: Security & Mainnet Preparation (Phase 6)
- ✅ Week 33: Smart contract security audit (external firm)
- ✅ Week 34: Audit remediation
- ✅ Week 35: Optimism mainnet deployment
- ✅ Week 36: DAO governance launch

**Deliverables:**
- Security audit report with all issues resolved
- Contracts deployed to Optimism mainnet
- DAO governance operational
- Public launch announcement

---

## Success Metrics

### Technical Metrics
1. **Capability Discovery**: >95% uptime for `.well-known/agent.json` endpoint
2. **MCP Invocations**: <2s average response time for tool invocations
3. **Blockchain Throughput**: >100 workflows/day publishable to Optimism L2
4. **IPFS Availability**: >99.9% artifact retrieval success rate
5. **Payment Success**: 100% payment release automation (no manual intervention)

### Business Metrics
1. **Agent Adoption**: 50+ registered specialist agents within 6 months
2. **External Integrations**: 10+ external Team Agent instances discovering our capabilities
3. **Research Use Cases**: 20+ academic institutions using research assistant platform
4. **Custom Value Stores**: 5+ DAO-approved custom payment methods
5. **Transaction Volume**: $10K+ in monthly workflow payments (across all payment methods)

### Community Metrics
1. **DAO Participation**: 100+ staking participants within 3 months
2. **Governance Proposals**: 10+ proposals per month
3. **Reputation Scores**: <1% slashing rate (high trust environment)
4. **Open Science Bounties**: $50K+ in total bounties funded

---

## Risk Mitigation

### Technical Risks
1. **Smart Contract Vulnerabilities**
   - Mitigation: Professional security audit, bug bounty program, gradual mainnet rollout
   - Contingency: Emergency pause functionality, insurance fund

2. **IPFS Content Availability**
   - Mitigation: Multiple pinning services (Pinata, Web3.Storage), redundancy
   - Contingency: Fallback to centralized storage for critical workflows

3. **Optimism L2 Gas Costs**
   - Mitigation: Gas optimization in contracts, batching workflow submissions
   - Contingency: Multi-chain support (Arbitrum, Base as alternatives)

### Business Risks
1. **Low Agent Adoption**
   - Mitigation: Developer grants, hackathons, comprehensive documentation
   - Contingency: Direct partnerships with research institutions

2. **Payment Method Complexity**
   - Mitigation: Simple defaults (ETH), optional advanced payment methods
   - Contingency: Fiat on-ramp partnerships

### Regulatory Risks
1. **DAO Governance Compliance**
   - Mitigation: Legal review of DAO structure, compliance framework
   - Contingency: Traditional governance fallback option

---

## Open Questions for User

1. **Payment Token**: Should we create a custom TEAM governance token, or use existing tokens (OP, USDC)?
2. **DAO Launch**: Launch DAO immediately in Phase 3, or wait until Phase 6 after mainnet deployment?
3. **Research Platform Priority**: Should we prioritize research assistant agents earlier (move Phase 5 before Phase 4)?
4. **Security Audit Budget**: What budget is available for smart contract security audit ($20K-$50K typical)?
5. **Mainnet Launch Timeline**: Is 36-week timeline (9 months) acceptable, or should we accelerate?

---

## Conclusion

This comprehensive architecture plan transforms Team Agent from a standalone orchestrator into a **decentralized marketplace for autonomous agent workflows**, enabling:

✅ **Agent Discovery**: Via A2A protocol and MCP servers
✅ **Blockchain Execution**: On Ethereum Optimism L2 for transparency and trust
✅ **Decentralized Storage**: IPFS/Filecoin for permanent artifact availability
✅ **Flexible Payments**: Multi-token support including custom value stores
✅ **Research Platform**: Specialized agents for academic and scientific use cases
✅ **DAO Governance**: Community-driven reputation and policy enforcement

**Next Steps:**
1. Review and approve this architecture plan
2. Begin Phase 2 implementation (A2A + MCP endpoints)
3. Set up Optimism Sepolia testnet account
4. Create IPFS/Pinata account for artifact storage
5. Begin smart contract development (Weeks 5-12)

---

**Document Version:** 1.0
**Last Updated:** December 6, 2025
**Status:** Awaiting User Approval
