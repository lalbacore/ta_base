#!/usr/bin/env python3
"""
Clean up duplicate agents and bogus registry entries.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.database import get_backend_session, init_backend_db
from app.models.agent import AgentCard, CapabilityRegistry, AgentCapabilityMapping

def cleanup_duplicate_specialists():
    """Remove duplicate specialist agents, keep only the first one of each class."""
    init_backend_db()

    with get_backend_session() as session:
        # Get all specialist agents
        specialists = session.query(AgentCard).filter_by(
            agent_type="specialist"
        ).order_by(AgentCard.created_at.asc()).all()

        # Track seen class names
        seen_classes = set()
        to_delete = []

        for agent in specialists:
            if agent.class_name in seen_classes:
                # Duplicate - mark for deletion
                to_delete.append(agent)
                print(f"❌ Duplicate: {agent.agent_name} ({agent.agent_id}) - will delete")
            else:
                # First occurrence - keep it
                seen_classes.add(agent.class_name)
                print(f"✅ Keeping: {agent.agent_name} ({agent.agent_id})")

        # Delete duplicates
        for agent in to_delete:
            # Delete associated capability mappings first
            session.query(AgentCapabilityMapping).filter_by(
                agent_id=agent.agent_id
            ).delete()

            # Delete the agent
            session.delete(agent)

        session.commit()
        print(f"\n✅ Removed {len(to_delete)} duplicate specialists")

def cleanup_bogus_registry_entries():
    """Remove any orphaned or test entries from capability_registry."""
    with get_backend_session() as session:
        # Get all capabilities
        capabilities = session.query(CapabilityRegistry).all()

        print(f"\nFound {len(capabilities)} capability registry entries:")
        for cap in capabilities:
            # Count how many agents use this capability
            mappings = session.query(AgentCapabilityMapping).filter_by(
                capability_id=cap.capability_id
            ).count()

            print(f"  - {cap.capability_name} ({cap.capability_id}): {mappings} agent mappings")

        # No automatic deletion - just reporting
        print("\n✅ Registry entries reported above")

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE CLEANUP")
    print("=" * 60)
    print()

    cleanup_duplicate_specialists()
    cleanup_bogus_registry_entries()

    print()
    print("=" * 60)
    print("✅ CLEANUP COMPLETE")
    print("=" * 60)
