#!/usr/bin/env python3
"""
Capability Registry Demonstration

This script demonstrates the A2A capability registry system:
1. Registering providers (agents)
2. Publishing capabilities
3. Discovering capabilities
4. Matching requirements against available capabilities
5. Recording invocations and updating reputation
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from swarms.team_agent.a2a import (
    CapabilityRegistry,
    Capability,
    CapabilityType,
    CapabilityStatus,
    Provider,
    CapabilityRequirement,
    CapabilityMatch,
)
from swarms.team_agent.crypto import TrustDomain, AgentReputationTracker, EventType


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_capability(cap: Capability, provider: Provider):
    """Print capability details."""
    print(f"📦 {cap.name} (v{cap.version})")
    print(f"   ID: {cap.capability_id}")
    print(f"   Type: {cap.capability_type.value}")
    print(f"   Provider: {provider.provider_id} (trust: {provider.trust_score:.1f})")
    print(f"   Reputation: {cap.reputation:.1f}/100")
    print(f"   Price: ${cap.price:.2f}")
    print(f"   Status: {cap.status.value}")
    print(f"   Description: {cap.description}")
    if cap.tags:
        print(f"   Tags: {', '.join(cap.tags)}")
    print()


def print_match(match: CapabilityMatch, rank: int):
    """Print a capability match."""
    print(f"#{rank} - {match.capability.name} (overall score: {match.overall_score:.1f})")
    print(f"     Provider: {match.provider.provider_id}")
    print(f"     Scores: match={match.match_score:.1f}, trust={match.trust_score:.1f}, "
          f"reputation={match.reputation_score:.1f}, cost={match.cost_score:.1f}")

    if match.match_reasons:
        print(f"     ✓ Reasons: {', '.join(match.match_reasons)}")
    if match.warnings:
        print(f"     ⚠ Warnings: {', '.join(match.warnings)}")
    print()


def main():
    print("\n🚀 Capability Registry Demonstration")
    print("=" * 80)

    # Initialize systems
    print_section("1. System Initialization")

    # Initialize trust tracker (for reputation integration)
    trust_tracker = AgentReputationTracker()
    print("✓ Trust tracker initialized")

    # Initialize registry
    registry = CapabilityRegistry(trust_tracker=trust_tracker)
    print("✓ Capability registry initialized")

    # Initialize some agents in the trust system
    agents = ["code-agent", "data-agent", "web-agent", "ml-agent", "security-agent"]

    for agent_id in agents:
        # Simulate different trust levels
        if agent_id == "code-agent":
            # High trust agent
            for _ in range(50):
                trust_tracker.record_event(agent_id, EventType.OPERATION_SUCCESS)
        elif agent_id == "data-agent":
            # Medium trust agent
            for _ in range(30):
                trust_tracker.record_event(agent_id, EventType.OPERATION_SUCCESS)
            for _ in range(5):
                trust_tracker.record_event(agent_id, EventType.OPERATION_FAILURE)
        elif agent_id == "web-agent":
            # Lower trust agent
            for _ in range(20):
                trust_tracker.record_event(agent_id, EventType.OPERATION_SUCCESS)
            for _ in range(10):
                trust_tracker.record_event(agent_id, EventType.OPERATION_FAILURE)

    print(f"✓ Initialized {len(agents)} agents with varying trust levels")

    # Register providers
    print_section("2. Registering Providers")

    providers = {}
    for agent_id in agents:
        provider = registry.register_provider(
            provider_id=agent_id,
            provider_type="agent",
            trust_domain=TrustDomain.EXECUTION,
            metadata={"created_by": "demo"}
        )
        providers[agent_id] = provider
        print(f"✓ Registered provider: {agent_id} (trust: {provider.trust_score:.1f})")

    # Register capabilities
    print_section("3. Publishing Capabilities")

    capabilities = []

    # Code generation capabilities
    cap1 = registry.register_capability(
        provider_id="code-agent",
        capability_type=CapabilityType.CODE_GENERATION,
        name="Python Code Generator",
        description="Generate production-ready Python code from specifications",
        version="2.1.0",
        input_schema={"type": "object", "properties": {"spec": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"code": {"type": "string"}}},
        requirements={"language": "python", "min_python_version": "3.8"},
        price=5.0,
        estimated_duration=30.0,
        tags=["python", "code-gen", "production"],
        categories=["development", "automation"]
    )
    capabilities.append(cap1)
    print(f"✓ Published: {cap1.name}")

    cap2 = registry.register_capability(
        provider_id="code-agent",
        capability_type=CapabilityType.CODE_GENERATION,
        name="JavaScript Code Generator",
        description="Generate JavaScript/TypeScript code",
        version="1.5.0",
        requirements={"language": "javascript"},
        price=4.0,
        estimated_duration=25.0,
        tags=["javascript", "typescript", "code-gen"],
        categories=["development", "web"]
    )
    capabilities.append(cap2)
    print(f"✓ Published: {cap2.name}")

    # Data analysis capabilities
    cap3 = registry.register_capability(
        provider_id="data-agent",
        capability_type=CapabilityType.DATA_ANALYSIS,
        name="Statistical Data Analysis",
        description="Perform statistical analysis on datasets",
        version="1.0.0",
        requirements={"libraries": ["pandas", "numpy", "scipy"]},
        price=8.0,
        estimated_duration=120.0,
        tags=["statistics", "pandas", "analysis"],
        categories=["data-science", "analytics"]
    )
    capabilities.append(cap3)
    print(f"✓ Published: {cap3.name}")

    # Web scraping capabilities
    cap4 = registry.register_capability(
        provider_id="web-agent",
        capability_type=CapabilityType.WEB_SCRAPING,
        name="Advanced Web Scraper",
        description="Scrape data from modern websites with JavaScript rendering",
        version="3.0.0",
        requirements={"tools": ["selenium", "beautifulsoup4"]},
        price=3.0,
        estimated_duration=60.0,
        tags=["scraping", "selenium", "web"],
        categories=["data-collection", "automation"]
    )
    capabilities.append(cap4)
    print(f"✓ Published: {cap4.name}")

    # Machine learning capabilities
    cap5 = registry.register_capability(
        provider_id="ml-agent",
        capability_type=CapabilityType.MACHINE_LEARNING,
        name="Text Classification Model",
        description="Train and deploy text classification models",
        version="1.2.0",
        requirements={"frameworks": ["tensorflow", "transformers"]},
        price=15.0,
        estimated_duration=300.0,
        tags=["ml", "nlp", "classification"],
        categories=["machine-learning", "ai"]
    )
    capabilities.append(cap5)
    print(f"✓ Published: {cap5.name}")

    # Security capabilities
    cap6 = registry.register_capability(
        provider_id="security-agent",
        capability_type=CapabilityType.SECURITY_AUDIT,
        name="Code Security Auditor",
        description="Audit code for security vulnerabilities",
        version="2.0.0",
        requirements={"tools": ["bandit", "safety"]},
        price=10.0,
        estimated_duration=90.0,
        tags=["security", "audit", "vulnerabilities"],
        categories=["security", "quality-assurance"]
    )
    capabilities.append(cap6)
    print(f"✓ Published: {cap6.name}")

    # Free capability (low price)
    cap7 = registry.register_capability(
        provider_id="code-agent",
        capability_type=CapabilityType.CODE_GENERATION,
        name="Simple Python Script Generator",
        description="Generate simple Python scripts for basic tasks",
        version="1.0.0",
        requirements={"language": "python"},
        price=0.0,
        estimated_duration=10.0,
        tags=["python", "simple", "free"],
        categories=["development", "automation"]
    )
    capabilities.append(cap7)
    print(f"✓ Published: {cap7.name}")

    print(f"\n✅ Published {len(capabilities)} capabilities")

    # Discover capabilities
    print_section("4. Discovering Capabilities")

    print("All CODE_GENERATION capabilities:")
    results = registry.discover_capabilities(
        capability_type=CapabilityType.CODE_GENERATION,
        min_reputation=0.0,
        min_trust_score=0.0
    )

    for cap, provider in results:
        print(f"  • {cap.name} (provider: {provider.provider_id}, reputation: {cap.reputation:.1f})")

    print(f"\nFound {len(results)} code generation capabilities\n")

    print("High-trust capabilities (trust >= 90):")
    results = registry.discover_capabilities(
        min_trust_score=90.0
    )

    for cap, provider in results:
        print(f"  • {cap.name} (provider: {provider.provider_id}, trust: {provider.trust_score:.1f})")

    print(f"\nFound {len(results)} high-trust capabilities")

    # Match capabilities against requirements
    print_section("5. Matching Capabilities Against Requirements")

    print("Scenario: Need a Python code generator")
    print("Requirements:")
    print("  - Type: CODE_GENERATION")
    print("  - Must have 'python' tag")
    print("  - Min reputation: 75.0")
    print("  - Max price: $6.00")
    print("  - Min trust score: 80.0")
    print()

    requirement = CapabilityRequirement(
        capability_type=CapabilityType.CODE_GENERATION,
        required_tags=["python"],
        min_reputation=75.0,
        max_price=6.0,
        min_trust_score=80.0
    )

    matches = registry.match_capabilities(requirement, limit=5)

    print(f"Found {len(matches)} matches:\n")
    for idx, match in enumerate(matches, 1):
        print_match(match, idx)

    # Record some invocations
    print_section("6. Recording Invocations & Updating Reputation")

    print("Simulating capability usage...\n")

    # Successful invocations for Python Code Generator
    for i in range(10):
        registry.record_invocation(
            capability_id=cap1.capability_id,
            requester_id="test-user",
            status="success",
            duration=28.5 + i,
            rating=4.5 if i < 8 else 5.0
        )

    print(f"✓ Recorded 10 successful invocations for '{cap1.name}'")

    # Mixed invocations for Data Analysis
    for i in range(5):
        registry.record_invocation(
            capability_id=cap3.capability_id,
            requester_id="test-user",
            status="success" if i < 3 else "failure",
            duration=120.0,
            rating=4.0 if i < 3 else 2.0
        )

    print(f"✓ Recorded 5 invocations (3 success, 2 failure) for '{cap3.name}'")

    # Update and show new stats
    print("\nUpdated capability reputation:")

    updated_cap1 = registry.get_capability(cap1.capability_id)
    if updated_cap1:
        cap, provider = updated_cap1
        print(f"\n{cap.name}:")
        print(f"  Total invocations: {cap.total_invocations}")
        print(f"  Successful: {cap.successful_invocations}")
        print(f"  Success rate: {cap.successful_invocations/cap.total_invocations*100:.1f}%")
        print(f"  Average rating: {cap.average_rating:.2f}/5.0")
        print(f"  Reputation: {cap.reputation:.1f}/100")

    updated_cap3 = registry.get_capability(cap3.capability_id)
    if updated_cap3:
        cap, provider = updated_cap3
        print(f"\n{cap.name}:")
        print(f"  Total invocations: {cap.total_invocations}")
        print(f"  Successful: {cap.successful_invocations}")
        print(f"  Success rate: {cap.successful_invocations/cap.total_invocations*100:.1f}%")
        print(f"  Average rating: {cap.average_rating:.2f}/5.0")
        print(f"  Reputation: {cap.reputation:.1f}/100")

    # Registry statistics
    print_section("7. Registry Statistics")

    stats = registry.get_statistics()

    print("Providers:")
    print(f"  Total: {stats['providers']['total']}")
    print(f"  Average trust score: {stats['providers']['average_trust_score']:.1f}")
    print(f"  Total operations: {stats['providers']['total_operations']}")

    print("\nCapabilities:")
    print(f"  Total: {stats['capabilities']['total']}")
    print(f"  Average reputation: {stats['capabilities']['average_reputation']:.1f}")
    print(f"  Total invocations: {stats['capabilities']['total_invocations']}")
    print(f"  By status:")
    for status, count in stats['capabilities'].items():
        if status not in ['total', 'average_reputation', 'total_invocations']:
            print(f"    - {status}: {count}")

    print("\nInvocations:")
    for status, count in stats['invocations'].items():
        print(f"  - {status}: {count}")

    # Test capability discovery with different filters
    print_section("8. Advanced Discovery Tests")

    print("Find cheap capabilities (price <= $5):")
    all_caps = registry.discover_capabilities(limit=100)
    cheap_caps = [(c, p) for c, p in all_caps if c.price <= 5.0]

    for cap, provider in cheap_caps[:5]:
        print(f"  • {cap.name} - ${cap.price:.2f}")

    print(f"\nFind free capabilities:")
    free_caps = [(c, p) for c, p in all_caps if c.price == 0.0]

    for cap, provider in free_caps:
        print(f"  • {cap.name} (provider: {provider.provider_id})")

    # Final summary
    print_section("✅ Demonstration Complete")

    print("Capability Registry Features Validated:")
    print("  ✓ Provider registration with trust score integration")
    print("  ✓ Capability publishing with rich metadata")
    print("  ✓ Capability discovery with filtering")
    print("  ✓ Intelligent capability matching with weighted scoring")
    print("  ✓ Invocation tracking and reputation updates")
    print("  ✓ Statistics and reporting")
    print()
    print("The capability registry is ready for A2A integration!")
    print()


if __name__ == "__main__":
    main()
