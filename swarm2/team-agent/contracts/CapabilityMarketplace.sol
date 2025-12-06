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
            reputation: 0
        });

        capabilityIds.push(capabilityId);

        // Link to agent
        agents[msg.sender].capabilityIds.push(capabilityId);

        emit CapabilityRegistered(capabilityId, msg.sender, name);

        return capabilityId;
    }

    function registerAgent(
        string memory agentName,
        string memory agentType,
        string memory metadataUri
    ) external {
        agents[msg.sender].agentAddress = msg.sender;
        agents[msg.sender].agentName = agentName;
        agents[msg.sender].agentType = agentType;
        agents[msg.sender].metadataUri = metadataUri;
        agents[msg.sender].active = true;

        agentAddresses.push(msg.sender);

        emit AgentRegistered(msg.sender, agentName);
    }
}
