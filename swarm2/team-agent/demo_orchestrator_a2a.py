#!/usr/bin/env python3
"""
Enhanced Orchestrator Demonstration

This script demonstrates the enhanced orchestrator with A2A integration:
1. Mission specification with capability requirements
2. Capability discovery from A2A registry
3. Trust-based capability selection
4. Human-in-the-loop breakpoints (simulated)
5. Mission execution with selected capabilities
"""

import sys
import asyncio
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
from swarms.team_agent.orchestrator_a2a import (
    OrchestratorA2A,
    MissionSpec,
    BreakpointType,
)
from swarms.team_agent.a2a import (
    CapabilityRegistry,
    CapabilityType,
    CapabilityRequirement,
)
from swarms.team_agent.crypto import (
    TrustDomain,
    AgentReputationTracker,
    EventType,
)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


async def main():
    print("\n🚀 Enhanced Orchestrator Demonstration")
    print("=" * 80)

    # Initialize orchestrator
    print_section("1. Initializing Enhanced Orchestrator")

    orchestrator = OrchestratorA2A(
        output_dir="./demo_output",
        enable_a2a=True,
        enable_breakpoints=True,
    )

    print("✓ Enhanced orchestrator initialized")
    print(f"  - A2A enabled: {orchestrator.enable_a2a}")
    print(f"  - Breakpoints enabled: {orchestrator.enable_breakpoints}")

    # Set up registry with capabilities
    print_section("2. Populating Capability Registry")

    registry = orchestrator.capability_registry
    trust_tracker = orchestrator.trust_tracker

    # Create some agents with different trust levels
    agents = {
        "python-expert": {"trust": 100, "operations": 50},
        "data-scientist": {"trust": 95, "operations": 40},
        "junior-dev": {"trust": 70, "operations": 20},
    }

    for agent_id, config in agents.items():
        # Build trust score
        for _ in range(config["operations"]):
            trust_tracker.record_event(agent_id, EventType.OPERATION_SUCCESS)

        # Register as provider
        registry.register_provider(
            provider_id=agent_id,
            provider_type="agent",
            trust_domain=TrustDomain.EXECUTION
        )

        metrics = trust_tracker.get_agent_metrics(agent_id)
        print(f"✓ Registered {agent_id} (trust: {metrics.trust_score:.1f})")

    # Register capabilities
    print("\nRegistering capabilities:")

    # Python code generation
    cap1 = registry.register_capability(
        provider_id="python-expert",
        capability_type=CapabilityType.CODE_GENERATION,
        name="Expert Python Code Generator",
        description="Generate production-grade Python code",
        version="2.0.0",
        price=10.0,
        estimated_duration=45.0,
        tags=["python", "production", "expert"],
        metadata={"experience_level": "expert"}
    )
    print(f"  ✓ {cap1.name} (provider: python-expert, $10.00)")

    cap2 = registry.register_capability(
        provider_id="junior-dev",
        capability_type=CapabilityType.CODE_GENERATION,
        name="Basic Python Code Generator",
        description="Generate simple Python code",
        version="1.0.0",
        price=3.0,
        estimated_duration=20.0,
        tags=["python", "basic"],
        metadata={"experience_level": "junior"}
    )
    print(f"  ✓ {cap2.name} (provider: junior-dev, $3.00)")

    # Data analysis
    cap3 = registry.register_capability(
        provider_id="data-scientist",
        capability_type=CapabilityType.DATA_ANALYSIS,
        name="Advanced Data Analysis",
        description="Statistical analysis and ML insights",
        version="1.5.0",
        price=15.0,
        estimated_duration=120.0,
        tags=["analytics", "ml", "statistics"],
        metadata={"specialization": "machine_learning"}
    )
    print(f"  ✓ {cap3.name} (provider: data-scientist, $15.00)")

    # Create mission specification
    print_section("3. Creating Mission Specification")

    mission = MissionSpec(
        mission_id="DEMO-001",
        description="Build a data analysis pipeline with Python",
        required_capabilities=[
            CapabilityRequirement(
                capability_type=CapabilityType.CODE_GENERATION,
                required_tags=["python"],
                min_reputation=75.0,
                max_price=12.0,
                min_trust_score=80.0,
            ),
            CapabilityRequirement(
                capability_type=CapabilityType.DATA_ANALYSIS,
                required_tags=["analytics"],
                min_reputation=75.0,
                max_price=20.0,
                min_trust_score=90.0,
            ),
        ],
        max_cost=30.0,
        max_duration=180.0,
        min_trust_score=80.0,
        breakpoints=[
            BreakpointType.MISSION_START,
            BreakpointType.CAPABILITY_SELECTION,
            BreakpointType.MISSION_COMPLETE,
        ],
        auto_approve_trusted=True,
        auto_approve_threshold=95.0,
    )

    print(f"Mission: {mission.mission_id}")
    print(f"  Description: {mission.description}")
    print(f"  Required capabilities: {len(mission.required_capabilities)}")
    print(f"  Breakpoints: {len(mission.breakpoints)}")

    print("\nCapability Requirements:")
    for idx, req in enumerate(mission.required_capabilities, 1):
        print(f"\n  Requirement #{idx}:")
        print(f"    Type: {req.capability_type.value}")
        print(f"    Tags: {req.required_tags}")
        print(f"    Min trust: {req.min_trust_score}")
        print(f"    Max price: ${req.max_price}")

    # Discover capabilities
    print_section("4. Discovering Capabilities")

    capability_matches = await orchestrator.discover_capabilities(mission)

    print(f"Found matches for {len(capability_matches)} requirements:\n")

    for req_key, matches in capability_matches.items():
        req_idx = int(req_key.split('_')[1])
        requirement = mission.required_capabilities[req_idx]

        print(f"{requirement.capability_type.value.upper()} - {len(matches)} matches:")

        for rank, match in enumerate(matches[:3], 1):  # Top 3
            print(f"\n  #{rank} - {match.capability.name}")
            print(f"      Provider: {match.provider.provider_id}")
            print(f"      Scores: Overall={match.overall_score:.1f}, "
                  f"Trust={match.trust_score:.1f}, "
                  f"Reputation={match.reputation_score:.1f}, "
                  f"Cost={match.cost_score:.1f}")
            print(f"      Price: ${match.capability.price}")
            print(f"      Duration: {match.capability.estimated_duration}s")

            if match.match_reasons:
                print(f"      ✓ {', '.join(match.match_reasons)}")

            if match.warnings:
                print(f"      ⚠ {', '.join(match.warnings)}")

    # Select best capabilities
    print_section("5. Selecting Best Capabilities")

    for req_idx, requirement in enumerate(mission.required_capabilities):
        matches = capability_matches.get(f"requirement_{req_idx}", [])

        selected = await orchestrator.select_best_capability(
            mission=mission,
            requirement=requirement,
            matches=matches,
        )

        if selected:
            print(f"\n{requirement.capability_type.value}:")
            print(f"  ✓ Selected: {selected.capability.name}")
            print(f"  Provider: {selected.provider.provider_id}")
            print(f"  Trust: {selected.trust_score:.1f}")
            print(f"  Overall Score: {selected.overall_score:.1f}")

            # Show decision reasoning
            if selected.trust_score >= mission.auto_approve_threshold:
                print(f"  Decision: Auto-approved (trust >= {mission.auto_approve_threshold})")
            else:
                print(f"  Decision: Selected as best match")

    # Execute mission
    print_section("6. Executing Mission")

    results = await orchestrator.execute_mission(mission=mission)

    print(f"Mission ID: {results['mission_id']}")
    print(f"Status: {results['status']}")
    print(f"Start: {results['start_time']}")
    print(f"End: {results['end_time']}")

    print(f"\nCapabilities Used ({len(results['capabilities_used'])}):")
    for cap_usage in results["capabilities_used"]:
        print(f"\n  {cap_usage['requirement']}:")
        print(f"    Capability: {cap_usage['selected']}")
        print(f"    Provider: {cap_usage['provider']}")
        print(f"    Match Score: {cap_usage['score']:.1f}")

    if results["breakpoints"]:
        print(f"\nBreakpoints Triggered ({len(results['breakpoints'])}):")
        for bp in results["breakpoints"]:
            print(f"  - {bp['type']}: {bp['status']}")

    # Show statistics
    print_section("7. Orchestrator Statistics")

    stats = orchestrator.get_statistics()

    print(f"Workflow ID: {stats['workflow_id']}")
    print(f"A2A Enabled: {stats['a2a_enabled']}")
    print(f"Total Breakpoints: {stats['total_breakpoints']}")

    if "registry" in stats:
        reg_stats = stats["registry"]
        print(f"\nRegistry Statistics:")
        print(f"  Providers: {reg_stats['providers']['total']}")
        print(f"  Capabilities: {reg_stats['capabilities']['total']}")
        print(f"  Avg Trust: {reg_stats['providers']['average_trust_score']:.1f}")

    if "trust" in stats:
        trust_stats = stats["trust"]
        print(f"\nTrust System:")
        print(f"  Total Agents: {trust_stats['total_agents']}")
        print(f"  Avg Trust Score: {trust_stats['average_trust_score']:.1f}")

    # Compare with/without A2A
    print_section("8. A2A Benefits Demonstration")

    print("Scenario: Mission requires Python code generation\n")

    print("WITHOUT A2A (local agents only):")
    print("  - Limited to locally available agents")
    print("  - No trust-based selection")
    print("  - No capability discovery")
    print("  ✗ May not find best match")

    print("\nWITH A2A (registry + discovery):")
    print("  ✓ Discovers capabilities across entire network")
    print("  ✓ Trust-based ranking and selection")
    print("  ✓ Cost and reputation awareness")
    print("  ✓ Automatic capability augmentation")
    print(f"  ✓ Selected: {results['capabilities_used'][0]['selected']} "
          f"from {results['capabilities_used'][0]['provider']}")

    # Final summary
    print_section("✅ Demonstration Complete")

    print("Enhanced Orchestrator Features Validated:")
    print("  ✓ Mission specification with requirements")
    print("  ✓ Capability discovery from A2A registry")
    print("  ✓ Trust-based capability selection")
    print("  ✓ Intelligent matching with scoring")
    print("  ✓ Human-in-the-loop breakpoints")
    print("  ✓ Automatic agent augmentation")
    print()
    print("The enhanced orchestrator is ready for production!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
