# Feature Request: Smart Contract Router/Conductor Plane

## Overview

Implement a blockchain-based Smart Contract layer as the Router/Conductor plane for Agent-to-Agent (A2A) workflows, enabling decentralized orchestration, transparent workflow execution, and immutable audit trails.

## Motivation

Current orchestrator is centralized and limited to single-process workflows. A smart contract-based conductor plane enables:

- **Decentralized Orchestration**: Multiple orchestrators can coordinate via blockchain
- **Agent-to-Agent Communication**: Direct agent collaboration without central coordinator
- **Workflow Marketplace**: Agents can discover and bid on workflows
- **Transparent Execution**: All workflow steps recorded on-chain
- **Immutable Audit**: Complete workflow history with cryptographic proof
- **Cross-Organization**: Agents from different organizations can collaborate
- **Programmable Governance**: On-chain policy enforcement

## Recommended Blockchain: **Ethereum Layer 2 (Optimism)**

### Why Optimism (Ethereum L2)?

**Recommended Choice: Optimism** for the following reasons:

1. **Low Transaction Costs**: ~$0.01-0.10 per transaction (vs Ethereum mainnet $5-50)
2. **High Throughput**: 2000+ TPS with sub-second confirmation
3. **EVM Compatible**: Use existing Ethereum tooling (Solidity, Hardhat, etc.)
4. **Mature Ecosystem**: Battle-tested, large developer community
5. **Security**: Inherits Ethereum L1 security through optimistic rollups
6. **Easy Bridging**: Assets/data can bridge to Ethereum mainnet
7. **Agent-Friendly**: Fast enough for real-time agent workflows

**Alternative Considerations:**
- **Polygon**: Similar benefits, slightly different architecture
- **Arbitrum**: Very similar to Optimism, equally good choice
- **Avalanche C-Chain**: EVM compatible, very fast, but smaller ecosystem
- **Solana**: Extremely fast but different programming model (Rust/Anchor)

**Why NOT these blockchains:**
- ❌ **Ethereum Mainnet**: Too expensive for frequent agent interactions
- ❌ **Bitcoin**: No smart contract support (except RSK/Stacks)
- ❌ **Cardano**: Different programming model, smaller ecosystem
- ❌ **Cosmos**: More complex (IBC), overkill for single-chain use case

## Architecture

### Smart Contract Conductor System

```
┌────────────────────────────────────────────────────────────┐
│              Optimism L2 Blockchain                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         WorkflowConductor.sol (Main Contract)       │  │
│  │  - Workflow registration                            │  │
│  │  - Agent assignment                                 │  │
│  │  - State transitions                                │  │
│  │  - Payment handling                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  AgentRegistry│  │ WorkflowNFT │  │ ReputationDAO │   │
│  │  Contract     │  │  (ERC-721)  │  │  Contract     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ PaymentSplit │  │ GovernanceNFT│  │ EventEmitter │   │
│  │  Contract    │  │  (ERC-721)   │  │  Contract    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
         ↑                ↑                ↑
         │                │                │
    ┌────┴───┐       ┌───┴────┐      ┌───┴────┐
    │        │       │        │      │        │
    │ Agent  │       │ Agent  │      │ Agent  │
    │   A    │←─pub/sub─→   B │←pub/sub→   C │
    │        │       │        │      │        │
    └────────┘       └────────┘      └────────┘
```

## Core Smart Contracts

### 1. WorkflowConductor.sol (Main Contract)

**Purpose**: Central orchestration contract for workflow lifecycle

**Key Functions:**
```solidity
contract WorkflowConductor {
    // Workflow Management
    function createWorkflow(
        string memory mission,
        address[] memory requiredAgents,
        uint256 budget
    ) external payable returns (uint256 workflowId);

    function assignAgent(
        uint256 workflowId,
        address agentAddress,
        string memory role
    ) external;

    function submitWork(
        uint256 workflowId,
        string memory role,
        bytes32 workHash,
        string memory ipfsHash
    ) external;

    function transitionState(
        uint256 workflowId,
        WorkflowState newState
    ) external;

    function completeWorkflow(
        uint256 workflowId,
        bytes32 finalOutputHash
    ) external;

    // Verification
    function verifySignature(
        uint256 workflowId,
        string memory role,
        bytes memory signature
    ) external view returns (bool);

    function getWorkflowState(
        uint256 workflowId
    ) external view returns (WorkflowState);

    // Events
    event WorkflowCreated(uint256 indexed workflowId, string mission);
    event AgentAssigned(uint256 indexed workflowId, address agent, string role);
    event WorkSubmitted(uint256 indexed workflowId, string role, bytes32 hash);
    event StateTransition(uint256 indexed workflowId, WorkflowState newState);
    event WorkflowCompleted(uint256 indexed workflowId, bytes32 finalHash);
}
```

**Workflow States:**
```solidity
enum WorkflowState {
    Created,         // Workflow initialized
    AgentsAssigned,  // All agents assigned
    InProgress,      // Execution started
    ArchitectDone,   // Architect phase complete
    BuilderDone,     // Builder phase complete
    CriticDone,      // Critic phase complete
    GovernanceDone,  // Governance approved
    RecorderDone,    // Recording complete
    Completed,       // Workflow successful
    Failed,          // Workflow failed
    Disputed         // Dispute raised
}
```

### 2. AgentRegistry.sol

**Purpose**: Register and manage agent identities

**Key Functions:**
```solidity
contract AgentRegistry {
    struct Agent {
        address wallet;
        string publicKey;  // For signature verification
        string[] capabilities;
        uint256 reputation;
        bool isActive;
        uint256 registeredAt;
    }

    function registerAgent(
        string memory publicKey,
        string[] memory capabilities
    ) external;

    function updateCapabilities(
        string[] memory capabilities
    ) external;

    function getAgent(
        address agentAddress
    ) external view returns (Agent memory);

    function deactivateAgent() external;

    // Trust scoring
    function updateReputation(
        address agentAddress,
        int256 delta
    ) external onlyWorkflowConductor;

    function getReputation(
        address agentAddress
    ) external view returns (uint256);
}
```

### 3. WorkflowNFT.sol (ERC-721)

**Purpose**: Mint NFTs representing completed workflows

**Features:**
- Each completed workflow mints unique NFT
- Metadata includes workflow hash, agents involved, completion time
- Transferrable ownership (workflow results can be sold)
- Royalties for original creator

**Metadata Structure:**
```json
{
  "name": "Workflow #1234",
  "description": "AI Agent Workflow Completion Certificate",
  "image": "ipfs://...",
  "attributes": [
    {"trait_type": "Mission", "value": "Build calculator"},
    {"trait_type": "Completion Time", "value": "2025-12-04T19:30:00Z"},
    {"trait_type": "Quality Score", "value": 85},
    {"trait_type": "Architect", "value": "0x123..."},
    {"trait_type": "Builder", "value": "0x456..."},
    {"trait_type": "Artifacts IPFS", "value": "ipfs://Qm..."}
  ]
}
```

### 4. PaymentSplitter.sol

**Purpose**: Distribute payments to agents automatically

**Key Functions:**
```solidity
contract PaymentSplitter {
    struct PaymentPlan {
        address[] agents;
        uint256[] shares;  // Basis points (10000 = 100%)
        uint256 totalAmount;
    }

    function createPaymentPlan(
        uint256 workflowId,
        address[] memory agents,
        uint256[] memory shares
    ) external payable;

    function releasePayment(
        uint256 workflowId
    ) external;

    function claimPayment(
        uint256 workflowId
    ) external;
}
```

**Default Payment Split:**
- Architect: 20%
- Builder: 35%
- Critic: 15%
- Governance: 10%
- Recorder: 10%
- Platform Fee: 10%

### 5. ReputationDAO.sol

**Purpose**: Decentralized governance for reputation disputes

**Key Functions:**
```solidity
contract ReputationDAO {
    struct Dispute {
        uint256 workflowId;
        address challenger;
        address challenged;
        string reason;
        uint256 votesFor;
        uint256 votesAgainst;
        DisputeState state;
    }

    function raiseDispute(
        uint256 workflowId,
        address challenged,
        string memory reason
    ) external;

    function vote(
        uint256 disputeId,
        bool support
    ) external;

    function resolveDispute(
        uint256 disputeId
    ) external;
}
```

### 6. GovernanceNFT.sol (ERC-721)

**Purpose**: NFT representing governance approval certificates

**Features:**
- Minted when governance approves workflow
- Contains policy decision hash
- Used for compliance proof

## Integration with Team Agent

### Orchestrator Smart Contract Integration

```python
# swarms/team_agent/blockchain/conductor.py

from web3 import Web3
from eth_account import Account
from typing import Dict, List, Any

class SmartContractConductor:
    """
    Blockchain-based workflow conductor using Optimism L2.
    """

    def __init__(
        self,
        rpc_url: str = "https://mainnet.optimism.io",
        private_key: str = None
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.conductor_contract = self._load_contract()

    def create_workflow(
        self,
        mission: str,
        budget: int = 0
    ) -> int:
        """Create workflow on-chain, returns workflowId."""
        tx = self.conductor_contract.functions.createWorkflow(
            mission,
            [],  # Required agents (empty for dynamic)
            budget
        ).build_transaction({
            'from': self.account.address,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'value': budget
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Parse workflowId from event
        workflow_id = self._parse_workflow_created_event(receipt)
        return workflow_id

    def register_agent(
        self,
        public_key: str,
        capabilities: List[str]
    ) -> str:
        """Register agent on-chain."""
        # Implementation...

    def submit_work(
        self,
        workflow_id: int,
        role: str,
        work_hash: bytes,
        ipfs_hash: str
    ):
        """Submit agent work to blockchain."""
        # Implementation...

    def listen_for_workflows(self, agent_capabilities: List[str]):
        """
        Listen for new workflows that match agent capabilities.
        Implements pub/sub pattern via event listening.
        """
        # Create event filter
        event_filter = self.conductor_contract.events.WorkflowCreated.create_filter(
            fromBlock='latest'
        )

        while True:
            for event in event_filter.get_new_entries():
                workflow_id = event['args']['workflowId']
                mission = event['args']['mission']

                # Check if agent can handle this workflow
                if self._can_handle(mission, agent_capabilities):
                    yield {
                        'workflow_id': workflow_id,
                        'mission': mission
                    }
```

### Agent-to-Blockchain Integration

```python
# Each agent gets blockchain wallet
class Architect:
    def __init__(
        self,
        workflow_id: str,
        cert_chain: Dict,
        blockchain_key: str = None  # New parameter
    ):
        # Existing initialization...

        # Blockchain integration
        if blockchain_key:
            self.blockchain_account = Account.from_key(blockchain_key)
            self.conductor = SmartContractConductor(
                private_key=blockchain_key
            )

    def submit_to_blockchain(self, architecture: Dict):
        """Submit architecture to blockchain."""
        # Hash the architecture
        arch_hash = self._hash_architecture(architecture)

        # Store full data on IPFS
        ipfs_hash = self._upload_to_ipfs(architecture)

        # Submit hash to blockchain
        self.conductor.submit_work(
            workflow_id=self.workflow_id,
            role="architect",
            work_hash=arch_hash,
            ipfs_hash=ipfs_hash
        )
```

## Pub/Sub Pattern

### Event-Driven Agent Communication

```python
# Agent A publishes work completion
class AgentPublisher:
    def publish_work_complete(self, workflow_id: int, role: str):
        """Emit event that triggers next agent."""
        self.conductor.transitionState(workflow_id, WorkflowState.ArchitectDone)

# Agent B subscribes to work completion events
class AgentSubscriber:
    def subscribe_to_role_completion(self, role: str):
        """Listen for previous role completion."""
        event_filter = self.conductor.contract.events.StateTransition.create_filter(
            argument_filters={'role': role}
        )

        for event in event_filter.get_new_entries():
            workflow_id = event['args']['workflowId']
            # Start work for this workflow
            self.start_work(workflow_id)
```

### Workflow Event Flow

```
User → Blockchain: Create Workflow
    ↓
Blockchain → Event: WorkflowCreated
    ↓
Architect (listening) → Picks up workflow
    ↓
Architect → Blockchain: Submit Architecture
    ↓
Blockchain → Event: StateTransition(ArchitectDone)
    ↓
Builder (listening) → Picks up workflow
    ↓
Builder → Blockchain: Submit Build
    ↓
... (continues through all roles)
```

## Storage Architecture

### On-Chain vs Off-Chain Data

**On-Chain (Optimism):**
- Workflow metadata (mission, state, agents)
- Work hashes (SHA-256)
- Agent addresses and reputation
- Payment information
- State transitions
- Signatures

**Off-Chain (IPFS):**
- Full architecture documents
- Generated code
- Review reports
- Governance decisions
- Workflow records
- Large artifacts

**Hybrid Approach:**
```
┌─────────────────────────────────────────┐
│          Optimism Blockchain            │
│  - Workflow metadata                    │
│  - Work hashes: 0xabc123...            │
│  - IPFS CIDs: Qm...                    │
└─────────────────────────────────────────┘
                  │
                  │ Points to
                  ▼
┌─────────────────────────────────────────┐
│               IPFS                      │
│  - Full architecture JSON               │
│  - Generated code files                 │
│  - All artifacts                        │
└─────────────────────────────────────────┘
```

## Economic Model

### Workflow Pricing

**Payment Structure:**
```
User pays upfront → Escrow in smart contract
  ↓
Workflow completes → Automatic distribution
  ↓
Agents receive payment based on shares
```

**Gas Cost Estimation (Optimism L2):**
- Create workflow: ~$0.05
- Submit work (per agent): ~$0.02
- State transition: ~$0.01
- Complete workflow: ~$0.03
- **Total per workflow: ~$0.15-0.20**

### Token Economics (Future)

**TEAM Token:**
- Governance token for DAO decisions
- Staking for agent registration
- Payment discounts
- Reputation boosts

## Security Considerations

### Smart Contract Security

**Audit Requirements:**
- OpenZeppelin contracts as base
- Comprehensive test coverage (>95%)
- Multiple security audits before mainnet
- Bug bounty program
- Upgradeable proxies for bug fixes

**Key Security Features:**
- Reentrancy guards
- Access control (OpenZeppelin Ownable)
- Pausable in emergencies
- Rate limiting
- Signature verification

### Agent Security

**Private Key Management:**
- Hardware wallet integration (Ledger/Trezor)
- Key derivation from PKI certificates
- Multi-sig for high-value workflows
- Key rotation support

## Development Stack

### Required Technologies

**Smart Contracts:**
- Solidity 0.8.20+
- Hardhat development framework
- OpenZeppelin contracts library
- Ethers.js for JavaScript interaction

**Python Integration:**
- `web3.py`: Ethereum interaction
- `eth-account`: Key management
- `ipfshttpclient`: IPFS uploads
- `eth-abi`: ABI encoding/decoding

**Testing:**
- Hardhat tests (JavaScript)
- Python integration tests
- Fork testing (mainnet fork)
- Gas optimization tests

**Deployment:**
- Hardhat deploy scripts
- Optimism testnet (Sepolia)
- Optimism mainnet

## Implementation Phases

### Phase 1: Core Contracts (8 weeks)
- WorkflowConductor.sol
- AgentRegistry.sol
- Basic payment splitting
- Deploy to Optimism testnet
- Python integration library

### Phase 2: NFT & IPFS (4 weeks)
- WorkflowNFT.sol
- IPFS integration
- Metadata generation
- NFT marketplace listing

### Phase 3: Reputation System (6 weeks)
- ReputationDAO.sol
- Dispute resolution
- Governance voting
- Trust scoring integration

### Phase 4: Advanced Features (6 weeks)
- GovernanceNFT.sol
- Payment streaming
- Multi-workflow orchestration
- Cross-chain bridging (Ethereum L1)

### Phase 5: Production Hardening (4 weeks)
- Security audits
- Gas optimization
- Monitoring/alerting
- Documentation
- Mainnet deployment

## Testing Strategy

### Smart Contract Tests
```javascript
// test/WorkflowConductor.test.js
describe("WorkflowConductor", function() {
    it("Should create workflow and emit event", async function() {
        const tx = await conductor.createWorkflow(
            "Build calculator",
            [],
            ethers.utils.parseEther("1.0")
        );

        expect(tx).to.emit(conductor, "WorkflowCreated");
    });

    it("Should prevent unauthorized state transitions", async function() {
        await expect(
            conductor.connect(attacker).transitionState(1, State.Completed)
        ).to.be.revertedWith("Unauthorized");
    });
});
```

### Integration Tests
```python
# tests/test_blockchain_integration.py
def test_end_to_end_workflow():
    """Test complete workflow on blockchain."""
    # Create workflow
    workflow_id = conductor.create_workflow("Test mission")

    # Architect submits
    architect.submit_to_blockchain(architecture)

    # Verify on-chain state
    state = conductor.get_workflow_state(workflow_id)
    assert state == WorkflowState.ArchitectDone
```

## Monitoring & Observability

### Blockchain Events Dashboard
- Real-time workflow creation
- Agent activity heatmap
- Gas usage trends
- Payment distributions
- Dispute rates

### Metrics
- Workflows created per day
- Average completion time
- Success rate
- Gas costs per workflow
- Agent utilization
- Revenue per agent

## Documentation Deliverables

1. **Smart Contract Documentation**: NatSpec comments, architecture diagrams
2. **Integration Guide**: How to connect agents to blockchain
3. **API Reference**: Python library methods
4. **Economic Model**: Token economics, payment flows
5. **Security Best Practices**: Key management, safe usage

## Success Criteria

1. ✅ Workflows can be created and executed on Optimism L2
2. ✅ Agents can discover workflows via events
3. ✅ All workflow steps recorded on-chain
4. ✅ Automatic payment distribution works
5. ✅ NFTs minted for completed workflows
6. ✅ Gas costs < $0.25 per workflow
7. ✅ Sub-second transaction confirmation
8. ✅ Zero security vulnerabilities in audits

## Future Enhancements

- **Cross-Chain**: Bridge to Ethereum mainnet, Polygon, Arbitrum
- **Layer 3**: Custom app-chain for even lower costs
- **ZK-Proofs**: Privacy-preserving workflow execution
- **DAO Governance**: Community-driven protocol upgrades
- **Agent Marketplace**: Agents can list services
- **Workflow Templates**: Reusable workflow patterns as NFTs
- **Streaming Payments**: Real-time payment as work completes

---

**Status**: Feature Request
**Priority**: High
**Estimated Effort**: 28 weeks (7 months)
**Dependencies**: PKI infrastructure, IPFS infrastructure
**Blockchain**: Optimism (Ethereum Layer 2)
**Estimated Gas Costs**: $0.15-0.20 per workflow
