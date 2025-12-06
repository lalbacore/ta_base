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
            // Refund submitter for standard workflow (simplified logic)
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

        if (wf.agentsInvolved.length > 0) {
            uint256 perAgentPayment = wf.totalPayment / wf.agentsInvolved.length;

            for (uint i = 0; i < wf.agentsInvolved.length; i++) {
                payable(wf.agentsInvolved[i]).transfer(perAgentPayment);
            }
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
