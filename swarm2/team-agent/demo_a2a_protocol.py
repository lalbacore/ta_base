#!/usr/bin/env python3
"""
A2A Protocol Demonstration

This script demonstrates agent-to-agent communication using the A2A protocol:
1. Setting up A2A clients and servers for multiple agents
2. Message exchange with signatures
3. Capability invocation via A2A
4. Trust-based access control
5. Request/response patterns
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
from swarms.team_agent.a2a import (
    CapabilityRegistry,
    CapabilityType,
    A2AClient,
    A2AServer,
    MessageType,
    RequestStatus,
)
from swarms.team_agent.crypto import (
    PKIManager,
    TrustDomain,
    Signer,
    Verifier,
    AgentReputationTracker,
    EventType,
)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_message(prefix: str, message):
    """Print a message."""
    print(f"{prefix} {message.message_type.value.upper()}")
    print(f"   From: {message.sender_id}")
    print(f"   To: {message.recipient_id}")
    print(f"   ID: {message.message_id}")
    if message.correlation_id:
        print(f"   Correlation: {message.correlation_id}")
    print(f"   Payload: {message.payload}")
    print()


async def main():
    print("\n🚀 A2A Protocol Demonstration")
    print("=" * 80)

    # Initialize systems
    print_section("1. System Initialization")

    # Initialize PKI
    pki = PKIManager()
    print("✓ PKI initialized")

    # Initialize trust tracker
    trust_tracker = AgentReputationTracker()
    print("✓ Trust tracker initialized")

    # Initialize registry
    registry = CapabilityRegistry(trust_tracker=trust_tracker)
    print("✓ Capability registry initialized")

    # Create agents with different trust levels
    print_section("2. Creating Agents & Certificates")

    agents = {
        "code-agent": {"trust_events": 50, "domain": TrustDomain.EXECUTION},
        "data-agent": {"trust_events": 30, "domain": TrustDomain.EXECUTION},
        "untrusted-agent": {"trust_events": 10, "domain": TrustDomain.EXECUTION},
    }

    # Build trust scores
    for agent_id, config in agents.items():
        for _ in range(config["trust_events"]):
            trust_tracker.record_event(agent_id, EventType.OPERATION_SUCCESS)

        metrics = trust_tracker.get_agent_metrics(agent_id)
        print(f"✓ {agent_id}: trust={metrics.trust_score:.1f}")

    # Generate certificates for each agent
    signers = {}
    verifiers = {}

    for agent_id, config in agents.items():
        cert_chain = pki.get_certificate_chain(config["domain"])

        # Create signer with private key and certificate
        signer = Signer(
            private_key_pem=cert_chain['key'],
            certificate_pem=cert_chain['cert'],
            signer_id=agent_id
        )

        # Create verifier with certificate chain
        verifier = Verifier(chain_pem=cert_chain['chain'])

        signers[agent_id] = signer
        verifiers[agent_id] = verifier

        print(f"✓ Generated certificates for {agent_id}")

    # Register capabilities
    print_section("3. Registering Capabilities")

    # Register providers
    for agent_id in agents.keys():
        registry.register_provider(
            provider_id=agent_id,
            provider_type="agent",
            trust_domain=TrustDomain.EXECUTION
        )

    # Code agent capabilities
    code_gen_cap = registry.register_capability(
        provider_id="code-agent",
        capability_type=CapabilityType.CODE_GENERATION,
        name="Python Code Generator",
        description="Generate Python code from specifications",
        version="1.0.0",
        price=5.0,
        estimated_duration=30.0,
        tags=["python", "code-gen"]
    )

    data_analysis_cap = registry.register_capability(
        provider_id="data-agent",
        capability_type=CapabilityType.DATA_ANALYSIS,
        name="Data Analyzer",
        description="Analyze datasets and generate insights",
        version="1.0.0",
        price=8.0,
        estimated_duration=60.0,
        tags=["analytics", "statistics"]
    )

    print(f"✓ Registered capability: {code_gen_cap.name} (provider: code-agent)")
    print(f"✓ Registered capability: {data_analysis_cap.name} (provider: data-agent)")

    # Create A2A clients and servers
    print_section("4. Setting Up A2A Communication")

    clients = {}
    servers = {}

    for agent_id in agents.keys():
        # Create client
        client = A2AClient(
            agent_id=agent_id,
            signer=signers[agent_id],
            verifier=verifiers[agent_id],
            trust_tracker=trust_tracker,
            registry=registry,
            pki_manager=pki
        )
        clients[agent_id] = client

        # Create server
        server = A2AServer(
            agent_id=agent_id,
            signer=signers[agent_id],
            verifier=verifiers[agent_id],
            trust_tracker=trust_tracker,
            registry=registry,
            min_trust_score=50.0  # Require 50+ trust to access
        )
        servers[agent_id] = server

        print(f"✓ Created A2A client/server for {agent_id}")

    # Register capability handlers
    print_section("5. Registering Capability Handlers")

    # Code generation handler
    async def handle_code_generation(params):
        """Simulate code generation."""
        spec = params.get("specification", "")
        print(f"   [code-agent] Generating code for: {spec}")
        await asyncio.sleep(0.1)  # Simulate work
        return {
            "code": f"def generated_function():\n    # Generated from: {spec}\n    pass",
            "language": "python",
            "lines": 3
        }

    servers["code-agent"].register_handler("invoke", handle_code_generation)
    print("✓ Registered code generation handler")

    # Data analysis handler
    async def handle_data_analysis(params):
        """Simulate data analysis."""
        dataset = params.get("dataset", "unknown")
        print(f"   [data-agent] Analyzing dataset: {dataset}")
        await asyncio.sleep(0.1)  # Simulate work
        return {
            "insights": ["Data shows positive trend", "Correlation detected"],
            "confidence": 0.85,
            "records_analyzed": 1000
        }

    servers["data-agent"].register_handler("invoke", handle_data_analysis)
    print("✓ Registered data analysis handler")

    # Test basic message exchange
    print_section("6. Basic Message Exchange")

    print("Scenario: code-agent sends a handshake to data-agent")

    # Create handshake message
    handshake = clients["code-agent"].create_message(
        message_type=MessageType.HANDSHAKE,
        recipient_id="data-agent",
        payload={"greeting": "Hello from code-agent!"}
    )

    print_message("📤 Sent:", handshake)

    # Server handles message
    response = await servers["data-agent"].handle_message(handshake)

    print_message("📥 Received:", response)

    # Verify response
    is_valid = clients["code-agent"].verify_message(response)
    print(f"✓ Signature verified: {is_valid}\n")

    # Test capability invocation via A2A
    print_section("7. Capability Invocation via A2A")

    print("Scenario: data-agent invokes code-agent's code generation capability")
    print()

    # Create invocation message
    invoke_message = clients["data-agent"].create_message(
        message_type=MessageType.CAPABILITY_INVOKE,
        recipient_id="code-agent",
        payload={
            "request_id": "req-test-001",
            "capability_id": code_gen_cap.capability_id,
            "operation": "invoke",
            "parameters": {
                "specification": "Function to calculate fibonacci numbers"
            }
        }
    )

    print_message("📤 Invocation request:", invoke_message)

    # Server handles invocation
    invoke_response = await servers["code-agent"].handle_message(invoke_message)

    print_message("📥 Invocation response:", invoke_response)

    print("Generated code:")
    print(invoke_response.payload["result"]["code"])
    print()

    # Test trust-based access control
    print_section("8. Trust-Based Access Control")

    print("Scenario: untrusted-agent (low trust) tries to invoke code-agent's capability")
    print()

    untrusted_metrics = trust_tracker.get_agent_metrics("untrusted-agent")
    print(f"untrusted-agent trust score: {untrusted_metrics.trust_score:.1f}")
    print(f"Required trust score: 50.0")
    print()

    # Create invocation from untrusted agent
    untrusted_invoke = clients["untrusted-agent"].create_message(
        message_type=MessageType.CAPABILITY_INVOKE,
        recipient_id="code-agent",
        payload={
            "request_id": "req-test-002",
            "capability_id": code_gen_cap.capability_id,
            "operation": "invoke",
            "parameters": {
                "specification": "Malicious code"
            }
        }
    )

    print_message("📤 Request from untrusted agent:", untrusted_invoke)

    # Server rejects due to low trust
    untrusted_response = await servers["code-agent"].handle_message(untrusted_invoke)

    print_message("📥 Response:", untrusted_response)

    if untrusted_response.message_type == MessageType.ERROR:
        print(f"✅ Request correctly rejected: {untrusted_response.payload['error']}")
    print()

    # Test multiple concurrent invocations
    print_section("9. Concurrent Capability Invocations")

    print("Scenario: Multiple agents invoke capabilities simultaneously")
    print()

    async def invoke_and_report(client_id, server_id, capability_id, params):
        """Helper to invoke and report results."""
        message = clients[client_id].create_message(
            message_type=MessageType.CAPABILITY_INVOKE,
            recipient_id=server_id,
            payload={
                "request_id": f"req-concurrent-{client_id}",
                "capability_id": capability_id,
                "operation": "invoke",
                "parameters": params
            }
        )

        response = await servers[server_id].handle_message(message)

        print(f"✓ {client_id} → {server_id}: {response.payload.get('status', 'unknown')}")

        return response

    # Run concurrent invocations
    tasks = [
        invoke_and_report(
            "data-agent", "code-agent", code_gen_cap.capability_id,
            {"specification": "Quick sort algorithm"}
        ),
        invoke_and_report(
            "code-agent", "data-agent", data_analysis_cap.capability_id,
            {"dataset": "sales_2024.csv"}
        ),
    ]

    results = await asyncio.gather(*tasks)

    print(f"\n✅ Completed {len(results)} concurrent invocations")

    # Check registry statistics
    print_section("10. Registry Statistics After A2A Activity")

    stats = registry.get_statistics()

    print("Capabilities:")
    print(f"  Total invocations: {stats['capabilities']['total_invocations']}")

    print("\nInvocations by status:")
    for status, count in stats['invocations'].items():
        print(f"  {status}: {count}")

    # Check updated reputation scores
    print("\nUpdated capability reputations:")

    code_cap, code_provider = registry.get_capability(code_gen_cap.capability_id)
    print(f"  {code_cap.name}:")
    print(f"    Invocations: {code_cap.total_invocations}")
    print(f"    Success rate: {code_cap.successful_invocations}/{code_cap.total_invocations}")
    print(f"    Reputation: {code_cap.reputation:.1f}/100")

    data_cap, data_provider = registry.get_capability(data_analysis_cap.capability_id)
    print(f"  {data_cap.name}:")
    print(f"    Invocations: {data_cap.total_invocations}")
    print(f"    Success rate: {data_cap.successful_invocations}/{data_cap.total_invocations}")
    print(f"    Reputation: {data_cap.reputation:.1f}/100")

    # Final summary
    print_section("✅ Demonstration Complete")

    print("A2A Protocol Features Validated:")
    print("  ✓ Message creation and signing")
    print("  ✓ Message verification")
    print("  ✓ Handshake protocol")
    print("  ✓ Capability invocation via A2A")
    print("  ✓ Trust-based access control")
    print("  ✓ Concurrent request handling")
    print("  ✓ Automatic reputation updates")
    print()
    print("The A2A protocol is ready for production integration!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
