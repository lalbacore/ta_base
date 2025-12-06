#!/usr/bin/env python3
"""
Fresh Mission Test Script

Tests the complete workflow with clean databases:
1. Create mission using legal capability
2. Run through orchestrator
3. Verify artifact generation
4. Check registry publishing
5. Analyze logs and trust scoring

This helps identify gaps in agent/team management.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.orchestrator import Orchestrator
from swarms.team_agent.capabilities.legal import LegalDocumentGenerator
import sqlite3


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_databases() -> None:
    """Check database states."""
    print_section("Database State Check")

    db_paths = {
        'Backend': Path.home() / '.team_agent' / 'backend.db',
        'Trust': Path.home() / '.team_agent' / 'trust.db',
        'Registry': Path.home() / '.team_agent' / 'registry.db',
        'CRL': Path.home() / '.team_agent' / 'pki' / 'crl.db',
    }

    for name, db_path in db_paths.items():
        if db_path.exists():
            size_kb = db_path.stat().st_size / 1024
            print(f"\n{name} Database: {size_kb:.1f} KB")

            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"  ✓ {table}: {count} rows")

                conn.close()
            except Exception as e:
                print(f"  Error reading {name}: {e}")
        else:
            print(f"\n{name} Database: Not created yet")


def check_logs() -> None:
    """Check log file states."""
    print_section("Log Files Check")

    log_dirs = [
        Path.cwd() / 'backend' / 'logs',
        Path.cwd() / 'logs',
    ]

    for log_dir in log_dirs:
        if log_dir.exists():
            log_files = list(log_dir.glob('*.jsonl'))
            if log_files:
                print(f"\n{log_dir}:")
                for log_file in log_files:
                    size_kb = log_file.stat().st_size / 1024
                    with open(log_file, 'r') as f:
                        lines = len(f.readlines())
                    print(f"  ✓ {log_file.name}: {lines} entries ({size_kb:.1f} KB)")


def check_artifacts(workflow_id: str) -> None:
    """Check generated artifacts."""
    print_section(f"Artifacts Check - {workflow_id}")

    output_dirs = [
        Path.cwd() / 'team_output',
        Path.cwd() / 'output',
    ]

    for output_dir in output_dirs:
        if output_dir.exists():
            workflow_dirs = [d for d in output_dir.iterdir() if d.is_dir() and workflow_id in d.name]
            for wf_dir in workflow_dirs:
                print(f"\nWorkflow Directory: {wf_dir}")
                for artifact in wf_dir.iterdir():
                    size_kb = artifact.stat().st_size / 1024
                    print(f"  ✓ {artifact.name}: {size_kb:.1f} KB")

                    # Show content preview for small files
                    if artifact.suffix in ['.md', '.txt', '.json'] and size_kb < 50:
                        with open(artifact, 'r') as f:
                            preview = f.read(200)
                        print(f"     Preview: {preview[:100]}...")


def analyze_trust_scoring() -> None:
    """Analyze trust scoring data."""
    print_section("Trust Scoring Analysis")

    trust_db = Path.home() / '.team_agent' / 'trust.db'

    if not trust_db.exists():
        print("  Trust database not created yet")
        return

    try:
        conn = sqlite3.connect(str(trust_db))
        cursor = conn.cursor()

        # Check agents table
        cursor.execute("SELECT COUNT(*) FROM agents")
        agent_count = cursor.fetchone()[0]
        print(f"\n Agents Registered: {agent_count}")

        if agent_count > 0:
            cursor.execute("SELECT agent_id, agent_name, trust_score, total_invocations FROM agents ORDER BY trust_score DESC LIMIT 10")
            agents = cursor.fetchall()
            print("\n  Top Agents by Trust Score:")
            for agent_id, name, score, invocations in agents:
                print(f"    - {name} (ID: {agent_id})")
                print(f"      Trust Score: {score:.2f}, Invocations: {invocations}")

        # Check events
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        print(f"\n  Trust Events: {event_count}")

        if event_count > 0:
            cursor.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type")
            event_types = cursor.fetchall()
            print("\n  Events by Type:")
            for event_type, count in event_types:
                print(f"    - {event_type}: {count}")

        conn.close()
    except Exception as e:
        print(f"  Error analyzing trust data: {e}")


def analyze_registry() -> None:
    """Analyze capability registry data."""
    print_section("Capability Registry Analysis")

    registry_db = Path.home() / '.team_agent' / 'registry.db'

    if not registry_db.exists():
        print("  Registry database not created yet")
        return

    try:
        conn = sqlite3.connect(str(registry_db))
        cursor = conn.cursor()

        # Check capabilities
        cursor.execute("SELECT COUNT(*) FROM capabilities")
        cap_count = cursor.fetchone()[0]
        print(f"\n  Capabilities Registered: {cap_count}")

        if cap_count > 0:
            cursor.execute("SELECT name, type, domain FROM capabilities LIMIT 10")
            caps = cursor.fetchall()
            print("\n  Registered Capabilities:")
            for name, cap_type, domain in caps:
                print(f"    - {name} (Type: {cap_type}, Domain: {domain})")

        # Check invocations
        cursor.execute("SELECT COUNT(*) FROM invocations")
        inv_count = cursor.fetchone()[0]
        print(f"\n  Capability Invocations: {inv_count}")

        if inv_count > 0:
            cursor.execute("""
                SELECT c.name, COUNT(*) as count
                FROM invocations i
                JOIN capabilities c ON i.capability_id = c.id
                GROUP BY c.name
                ORDER BY count DESC
                LIMIT 5
            """)
            top_caps = cursor.fetchall()
            print("\n  Most Used Capabilities:")
            for name, count in top_caps:
                print(f"    - {name}: {count} invocations")

        conn.close()
    except Exception as e:
        print(f"  Error analyzing registry: {e}")


def analyze_agent_cards() -> None:
    """Analyze agent card system."""
    print_section("Agent Card System Analysis")

    backend_db = Path.home() / '.team_agent' / 'backend.db'

    if not backend_db.exists():
        print("  Backend database not created yet")
        return

    try:
        conn = sqlite3.connect(str(backend_db))
        cursor = conn.cursor()

        # Check agent_cards
        cursor.execute("SELECT COUNT(*) FROM agent_cards")
        card_count = cursor.fetchone()[0]
        print(f"\n  Agent Cards Registered: {card_count}")

        if card_count > 0:
            cursor.execute("SELECT agent_id, agent_name, agent_type, trust_score, total_invocations FROM agent_cards")
            cards = cursor.fetchall()
            print("\n  Registered Agent Cards:")
            for agent_id, name, agent_type, score, invocations in cards:
                print(f"    - {name} (ID: {agent_id})")
                print(f"      Type: {agent_type}, Trust: {score:.2f}, Invocations: {invocations}")
        else:
            print("\n  ⚠️  No agent cards registered!")
            print("     This is a gap - orchestrator agents should be registered as agent cards")

        # Check agent_invocations
        cursor.execute("SELECT COUNT(*) FROM agent_invocations")
        inv_count = cursor.fetchone()[0]
        print(f"\n  Agent Invocations Recorded: {inv_count}")

        conn.close()
    except Exception as e:
        print(f"  Error analyzing agent cards: {e}")


def run_fresh_mission() -> dict:
    """Run a fresh mission using the legal capability."""
    print_section("Running Fresh Mission - Legal NDA Generation")

    # Create orchestrator
    print("\n1. Creating orchestrator...")
    orchestrator = Orchestrator(output_dir="./team_output")
    print("   ✓ Orchestrator initialized")
    print(f"   ✓ Capabilities registered: {len(orchestrator.capability_registry.list_capabilities())}")

    # Define mission
    mission = "Generate a non-disclosure agreement for a software development partnership"
    print(f"\n2. Mission: {mission}")

    # Execute mission
    print("\n3. Executing mission through orchestrator...")
    result = orchestrator.execute(mission)

    print(f"\n4. Mission completed!")
    print(f"   ✓ Workflow ID: {result['workflow_id']}")

    return result


def main():
    """Main test flow."""
    print("=" * 70)
    print("  Team Agent - Fresh Mission Test")
    print("  Testing: Legal Document Generator Capability")
    print("=" * 70)

    # Initial state check
    print("\n📋 BEFORE MISSION:")
    check_databases()
    check_logs()

    # Run mission
    print("\n\n🚀 EXECUTING MISSION:")
    result = run_fresh_mission()

    # Post-mission analysis
    print("\n\n📊 AFTER MISSION:")
    check_databases()
    check_logs()
    check_artifacts(result['workflow_id'])

    # Detailed analysis
    print("\n\n🔍 DETAILED ANALYSIS:")
    analyze_agent_cards()
    analyze_trust_scoring()
    analyze_registry()

    # Summary and findings
    print_section("Summary and Findings")
    print("""
Key Questions to Answer:

1. Agent Management:
   - Were Architect, Builder, Critic, Recorder registered as agent cards?
   - Is there a gap in automatic agent registration?

2. Trust Scoring:
   - Did trust scores get updated for the agents used?
   - Are agents being tracked properly?

3. Registry:
   - Was the legal capability registered and invoked?
   - Were artifacts published to the registry?

4. Workflow:
   - Were all artifacts generated correctly?
   - Are logs structured and complete?

5. Missing Components (from user feedback):
   - Agent Manager: System to register and track agents
   - Team Agent Manager: System to orchestrate agent groups
   - Mission Creation UX: Agent selection and registry integration

Next Steps:
   - Review the analysis output above
   - Identify which agents are missing from agent_cards
   - Design Agent Manager and Team Agent Manager systems
    """)

    print("=" * 70)
    print("✅ Fresh Mission Test Completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
