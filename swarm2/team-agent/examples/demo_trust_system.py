#!/usr/bin/env python3
"""
Trust Scoring System Integration Demo

Demonstrates the complete PKI trust scoring system with realistic agent scenarios.
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from swarms.team_agent.crypto import (
    PKIManager,
    AgentReputationTracker,
    EventType,
    TrustDomain
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_agent_summary(tracker: AgentReputationTracker, agent_id: str):
    """Print a summary of an agent's metrics."""
    metrics = tracker.get_agent_metrics(agent_id)
    if not metrics:
        print(f"Agent {agent_id} not found")
        return

    # Color-code based on trust score
    if metrics.trust_score >= 80:
        color = "\033[92m"  # Green
        rating = "EXCELLENT"
    elif metrics.trust_score >= 60:
        color = "\033[93m"  # Yellow
        rating = "GOOD"
    else:
        color = "\033[91m"  # Red
        rating = "POOR"
    reset = "\033[0m"

    print(f"  {agent_id}:")
    print(f"    Trust Score: {color}{metrics.trust_score:.2f}{reset} ({rating})")
    print(f"    Operations: {metrics.total_operations} total, "
          f"{metrics.successful_operations} success ({metrics.success_rate:.1f}%), "
          f"{metrics.failed_operations} failures, {metrics.error_operations} errors")
    print(f"    Security: {metrics.security_incidents} incidents, "
          f"{metrics.certificate_revocations} revocations, "
          f"{metrics.policy_violations} policy violations")
    print(f"    Performance: {metrics.average_response_time:.3f}s avg response time")
    print()


def simulate_agent_operations(tracker: AgentReputationTracker, agent_id: str,
                              success: int, failures: int, errors: int,
                              incidents: int = 0):
    """Simulate agent operations."""
    print(f"  Simulating {agent_id} operations:")
    print(f"    - {success} successful operations")
    print(f"    - {failures} failed operations")
    print(f"    - {errors} error operations")
    if incidents > 0:
        print(f"    - {incidents} security incidents")

    # Register agent
    tracker.register_agent(agent_id)

    # Successful operations
    for i in range(success):
        tracker.record_event(
            agent_id=agent_id,
            event_type=EventType.OPERATION_SUCCESS,
            response_time=0.3 + (i % 10) * 0.05  # Vary response times
        )

    # Failed operations
    for i in range(failures):
        tracker.record_event(
            agent_id=agent_id,
            event_type=EventType.OPERATION_FAILURE,
            metadata={"reason": "timeout", "attempt": i+1}
        )

    # Error operations
    for i in range(errors):
        tracker.record_event(
            agent_id=agent_id,
            event_type=EventType.OPERATION_ERROR,
            metadata={"error": "RuntimeError", "attempt": i+1}
        )

    # Security incidents
    for i in range(incidents):
        tracker.record_event(
            agent_id=agent_id,
            event_type=EventType.SECURITY_INCIDENT,
            metadata={"type": "unauthorized_access", "severity": "high"}
        )

    print()


def main():
    """Run the trust scoring system demo."""
    print_section("PKI Trust Scoring System Integration Demo")

    print("This demo will:")
    print("  1. Initialize the PKI system")
    print("  2. Create a trust tracker")
    print("  3. Simulate various agent behaviors")
    print("  4. Show trust score calculations")
    print("  5. Demonstrate agent selection based on trust")

    # Initialize PKI
    print_section("Step 1: Initialize PKI System")
    pki = PKIManager()
    pki.initialize_pki()
    print("✓ PKI initialized with 3 trust domains")
    print("✓ Root CA and intermediate CAs generated")

    # Create trust tracker
    print_section("Step 2: Create Trust Tracker")
    tracker = AgentReputationTracker()
    print("✓ Trust tracker initialized")
    print(f"✓ Database: {tracker.db_path}")
    print(f"✓ Weights: {tracker.weights}")

    # Scenario 1: Excellent Agent
    print_section("Scenario 1: Excellent Agent (architect-agent)")
    simulate_agent_operations(
        tracker,
        "architect-agent",
        success=95,
        failures=3,
        errors=2,
        incidents=0
    )
    print_agent_summary(tracker, "architect-agent")

    # Scenario 2: Good Agent
    print_section("Scenario 2: Good Agent (builder-agent)")
    simulate_agent_operations(
        tracker,
        "builder-agent",
        success=80,
        failures=10,
        errors=10,
        incidents=1
    )
    print_agent_summary(tracker, "builder-agent")

    # Scenario 3: Fair Agent
    print_section("Scenario 3: Fair Agent (critic-agent)")
    simulate_agent_operations(
        tracker,
        "critic-agent",
        success=60,
        failures=20,
        errors=20,
        incidents=2
    )
    print_agent_summary(tracker, "critic-agent")

    # Scenario 4: Poor Agent
    print_section("Scenario 4: Poor Agent (problematic-agent)")
    simulate_agent_operations(
        tracker,
        "problematic-agent",
        success=30,
        failures=40,
        errors=30,
        incidents=5
    )
    print_agent_summary(tracker, "problematic-agent")

    # Show all agents
    print_section("All Agents Summary")
    agents = tracker.list_all_agents()
    print(f"Total agents registered: {len(agents)}\n")

    print(f"{'Agent ID':<25} {'Trust Score':<15} {'Operations':<12} {'Success Rate':<15} {'Incidents'}")
    print("-" * 85)
    for agent in agents:
        score_str = f"{agent.trust_score:.2f}"
        print(f"{agent.agent_id:<25} {score_str:<15} {agent.total_operations:<12} "
              f"{agent.success_rate:.1f}%{'':<10} {agent.security_incidents}")

    # System statistics
    print_section("System Statistics")
    stats = tracker.get_statistics()
    print(f"  Total Agents:          {stats['total_agents']}")
    print(f"  Average Trust Score:   {stats['average_trust_score']:.2f}")
    print(f"  Min Trust Score:       {stats['min_trust_score']:.2f}")
    print(f"  Max Trust Score:       {stats['max_trust_score']:.2f}")
    print(f"  Total Operations:      {stats['total_operations']}")
    print(f"  Security Incidents:    {stats['total_security_incidents']}")

    # Policy-based agent selection
    print_section("Policy-Based Agent Selection")

    # Critical task - need trust >= 90
    print("Task: Critical Infrastructure Change")
    print("  Required trust score: >= 90.0")
    critical_agents = [a for a in agents if a.trust_score >= 90.0]
    if critical_agents:
        best = max(critical_agents, key=lambda a: a.trust_score)
        print(f"  ✓ Selected: {best.agent_id} (trust: {best.trust_score:.2f})")
    else:
        print("  ✗ No agents meet trust requirement!")

    # Standard task - need trust >= 75
    print("\nTask: Standard Feature Implementation")
    print("  Required trust score: >= 75.0")
    standard_agents = [a for a in agents if a.trust_score >= 75.0]
    if standard_agents:
        best = max(standard_agents, key=lambda a: a.trust_score)
        print(f"  ✓ Selected: {best.agent_id} (trust: {best.trust_score:.2f})")
        print(f"  Available agents: {', '.join(a.agent_id for a in standard_agents)}")
    else:
        print("  ✗ No agents meet trust requirement!")

    # Low-risk task - need trust >= 60
    print("\nTask: Documentation Update")
    print("  Required trust score: >= 60.0")
    lowrisk_agents = [a for a in agents if a.trust_score >= 60.0]
    if lowrisk_agents:
        best = max(lowrisk_agents, key=lambda a: a.trust_score)
        print(f"  ✓ Selected: {best.agent_id} (trust: {best.trust_score:.2f})")
        print(f"  Available agents: {', '.join(a.agent_id for a in lowrisk_agents)}")

    # Security incident response
    print_section("Security Incident Response")
    print("Checking for agents requiring investigation (trust < 60)...")

    problematic = [a for a in agents if a.trust_score < 60.0]
    if problematic:
        print(f"\n⚠️  Found {len(problematic)} agent(s) requiring investigation:\n")
        for agent in problematic:
            print(f"  {agent.agent_id}:")
            print(f"    Trust Score: {agent.trust_score:.2f}")
            print(f"    Security Incidents: {agent.security_incidents}")
            print(f"    Success Rate: {agent.success_rate:.1f}%")

            # Get recent events
            events = tracker.get_recent_events(agent.agent_id, limit=5)
            print(f"    Recent events:")
            for event in events[:3]:
                print(f"      - {event['event_type']}: {event.get('metadata', {})}")
            print()
    else:
        print("✓ All agents have acceptable trust scores")

    # CLI tool demonstration
    print_section("CLI Tool Usage")
    print("The trust scoring system includes a CLI tool for management:\n")

    print("# List all agents")
    print("$ python scripts/pki_trust_cli.py list\n")

    print("# Show detailed metrics")
    print("$ python scripts/pki_trust_cli.py show architect-agent\n")

    print("# View trust history")
    print("$ python scripts/pki_trust_cli.py history architect-agent --limit 10\n")

    print("# Record new event")
    print("$ python scripts/pki_trust_cli.py record builder-agent operation-success --response-time 0.5\n")

    print("# System statistics")
    print("$ python scripts/pki_trust_cli.py stats\n")

    # Summary
    print_section("Demo Complete!")
    print("The trust scoring system successfully:")
    print("  ✓ Tracked behavior for 4 agents")
    print("  ✓ Calculated trust scores based on operations and incidents")
    print("  ✓ Enabled policy-based agent selection")
    print("  ✓ Identified problematic agents for investigation")
    print("  ✓ Provided CLI tools for management")
    print("\nNext steps:")
    print("  - Run: python scripts/pki_trust_cli.py list")
    print("  - Run all tests: python -m pytest utils/tests/test_trust.py -v")
    print("  - Integrate with orchestrator for automated trust-based decisions")
    print()


if __name__ == "__main__":
    main()
