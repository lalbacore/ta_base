#!/usr/bin/env python3
"""
Cleanup Duplicate Agents Script

Removes duplicate specialist agents created from multiple backend restarts.
Keeps the most recently created instance of each specialist type.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.database import get_backend_session
from app.models.agent import AgentCard
from sqlalchemy import func
from datetime import datetime


def cleanup_duplicate_agents():
    """Remove duplicate specialist agents, keeping most recent."""

    with get_backend_session() as session:
        # Get all agent cards
        all_agents = session.query(AgentCard).all()

        print(f"\n{'='*60}")
        print(f"Agent Cleanup Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        print(f"Total agents before cleanup: {len(all_agents)}\n")

        # Group agents by type and name
        agent_groups = {}
        for agent in all_agents:
            key = (agent.agent_type, agent.agent_name)
            if key not in agent_groups:
                agent_groups[key] = []
            agent_groups[key].append(agent)

        # Find duplicates
        duplicates_to_remove = []

        print("Agent Groups Analysis:")
        print(f"{'Type':<15} {'Name':<30} {'Count':<10} {'Action'}")
        print("-" * 80)

        for (agent_type, agent_name), agents in agent_groups.items():
            count = len(agents)

            if count > 1:
                # Sort by created_at descending (most recent first)
                agents_sorted = sorted(agents, key=lambda a: a.created_at or datetime.min, reverse=True)

                # Keep the most recent, mark others for deletion
                keep = agents_sorted[0]
                remove = agents_sorted[1:]

                duplicates_to_remove.extend(remove)

                print(f"{agent_type:<15} {agent_name:<30} {count:<10} Keep 1, Remove {len(remove)}")

                # Show details of what we're keeping vs removing
                print(f"  → Keeping:  {keep.agent_id[:16]}... (created: {keep.created_at})")
                for dup in remove:
                    print(f"  → Removing: {dup.agent_id[:16]}... (created: {dup.created_at})")
            else:
                print(f"{agent_type:<15} {agent_name:<30} {count:<10} OK (no duplicates)")

        print("-" * 80)
        print(f"\nTotal duplicates to remove: {len(duplicates_to_remove)}\n")

        if duplicates_to_remove:
            # Delete duplicates
            for agent in duplicates_to_remove:
                print(f"Deleting: {agent.agent_name} ({agent.agent_id[:16]}...)")
                session.delete(agent)

            session.commit()
            print(f"\n✓ Successfully removed {len(duplicates_to_remove)} duplicate agents")
        else:
            print("✓ No duplicates found - database is clean!")

        # Final count
        remaining = session.query(func.count(AgentCard.agent_id)).scalar()
        print(f"\nTotal agents after cleanup: {remaining}")

        # Show summary by type
        print("\nFinal Agent Summary by Type:")
        type_counts = session.query(
            AgentCard.agent_type,
            func.count(AgentCard.agent_id)
        ).group_by(AgentCard.agent_type).all()

        for agent_type, count in type_counts:
            print(f"  {agent_type}: {count}")

        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    try:
        cleanup_duplicate_agents()
    except Exception as e:
        print(f"Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
