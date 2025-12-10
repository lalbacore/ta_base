#!/usr/bin/env python3
"""
Reset Agents Only Script

Surgical database cleanup that:
1. Deletes all AgentCard entries except base classes
2. Deletes associated AgentCapabilityMapping entries
3. Cleans up orphaned CapabilityRegistry entries
4. Clears logs directory
5. Clears team_output artifacts directory

Preserves:
- Database schema
- Base class agents (BaseRole, etc.)
- Governance policies and decisions
- Network providers
- PKI certificates

Usage:
    python scripts/reset_agents_only.py              # Interactive mode with confirmation
    python scripts/reset_agents_only.py --force      # Skip confirmation
    python scripts/reset_agents_only.py --dry-run    # Show what would be deleted
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import argparse

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.database import get_backend_session, init_backend_db
from app.models.agent import AgentCard, CapabilityRegistry, AgentCapabilityMapping

PROJECT_ROOT = Path(__file__).parent.parent


def get_agent_stats():
    """Get current agent statistics."""
    init_backend_db()
    
    with get_backend_session() as session:
        total_agents = session.query(AgentCard).count()
        base_agents = session.query(AgentCard).filter(
            AgentCard.base_class.in_(['BaseRole', 'BaseAgent', 'base'])
        ).count()
        specialist_agents = session.query(AgentCard).filter_by(
            agent_type='specialist'
        ).count()
        
        return {
            'total': total_agents,
            'base': base_agents,
            'specialists': specialist_agents,
            'other': total_agents - base_agents - specialist_agents
        }


def delete_non_base_agents(dry_run=False):
    """Delete all agents except base classes."""
    print("\n🗑️  Deleting non-base agents...")
    
    with get_backend_session() as session:
        # Find all non-base agents
        # We'll keep agents that are truly base classes
        # In this system, we want to delete ALL agents since they get re-registered
        # But let's be conservative and only delete specialists and role types
        
        agents_to_delete = session.query(AgentCard).filter(
            AgentCard.agent_type.in_(['specialist', 'role', 'tool'])
        ).all()
        
        if not agents_to_delete:
            print("   ℹ️  No agents to delete")
            return 0
        
        print(f"   Found {len(agents_to_delete)} agents to delete:")
        for agent in agents_to_delete:
            print(f"      - {agent.agent_name} ({agent.agent_id}) [{agent.agent_type}]")
        
        if dry_run:
            print(f"   [DRY RUN] Would delete {len(agents_to_delete)} agents")
            return len(agents_to_delete)
        
        # Delete capability mappings first
        deleted_mappings = 0
        for agent in agents_to_delete:
            count = session.query(AgentCapabilityMapping).filter_by(
                agent_id=agent.agent_id
            ).delete()
            deleted_mappings += count
        
        print(f"   ✓ Deleted {deleted_mappings} capability mappings")
        
        # Delete agents
        for agent in agents_to_delete:
            session.delete(agent)
        
        session.commit()
        print(f"   ✓ Deleted {len(agents_to_delete)} agents")
        
        return len(agents_to_delete)


def cleanup_orphaned_capabilities(dry_run=False):
    """Remove capability registry entries with no agent mappings."""
    print("\n🗑️  Cleaning up orphaned capabilities...")
    
    with get_backend_session() as session:
        capabilities = session.query(CapabilityRegistry).all()
        orphaned = []
        
        for cap in capabilities:
            mapping_count = session.query(AgentCapabilityMapping).filter_by(
                capability_id=cap.capability_id
            ).count()
            
            if mapping_count == 0:
                orphaned.append(cap)
        
        if not orphaned:
            print("   ℹ️  No orphaned capabilities found")
            return 0
        
        print(f"   Found {len(orphaned)} orphaned capabilities:")
        for cap in orphaned:
            print(f"      - {cap.capability_name} ({cap.capability_id})")
        
        if dry_run:
            print(f"   [DRY RUN] Would delete {len(orphaned)} capabilities")
            return len(orphaned)
        
        for cap in orphaned:
            session.delete(cap)
        
        session.commit()
        print(f"   ✓ Deleted {len(orphaned)} orphaned capabilities")
        
        return len(orphaned)


def clear_logs(dry_run=False):
    """Clear all log files."""
    print("\n🗑️  Clearing log files...")
    
    log_dirs = [
        PROJECT_ROOT / 'logs',
        PROJECT_ROOT / 'backend' / 'logs',
    ]
    
    # Also clear root-level log files
    root_log_patterns = ['*.log', '*.jsonl']
    
    deleted_count = 0
    
    # Clear log directories
    for log_dir in log_dirs:
        if not log_dir.exists():
            continue
        
        for log_file in log_dir.glob('*'):
            if log_file.is_file():
                if dry_run:
                    print(f"   [DRY RUN] Would delete {log_file}")
                else:
                    log_file.unlink()
                deleted_count += 1
    
    # Clear root-level logs
    for pattern in root_log_patterns:
        for log_file in PROJECT_ROOT.glob(pattern):
            if log_file.is_file():
                if dry_run:
                    print(f"   [DRY RUN] Would delete {log_file}")
                else:
                    log_file.unlink()
                deleted_count += 1
    
    if deleted_count == 0:
        print("   ℹ️  No log files found")
    elif dry_run:
        print(f"   [DRY RUN] Would delete {deleted_count} log files")
    else:
        print(f"   ✓ Deleted {deleted_count} log files")
    
    return deleted_count


def clear_artifacts(dry_run=False):
    """Clear team_output artifacts directory."""
    print("\n🗑️  Clearing artifacts...")
    
    artifacts_dir = PROJECT_ROOT / 'team_output'
    
    if not artifacts_dir.exists():
        print("   ℹ️  Artifacts directory does not exist")
        return 0
    
    # Count files
    file_count = sum(1 for _ in artifacts_dir.rglob('*') if _.is_file())
    
    if file_count == 0:
        print("   ℹ️  No artifacts found")
        return 0
    
    if dry_run:
        print(f"   [DRY RUN] Would delete {file_count} artifact files")
        return file_count
    
    # Remove all contents but keep the directory
    shutil.rmtree(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"   ✓ Cleared artifacts directory ({file_count} files)")
    
    return file_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Reset Team Agent database (agents only)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Team Agent Database Reset (Agents Only)")
    print("=" * 70)
    
    # Show current state
    print("\n📊 Current Database State:")
    stats = get_agent_stats()
    print(f"   Total agents: {stats['total']}")
    print(f"   Base class agents: {stats['base']}")
    print(f"   Specialist agents: {stats['specialists']}")
    print(f"   Other agents: {stats['other']}")
    
    # Confirm deletion unless force or dry-run
    if not args.force and not args.dry_run:
        print("\n⚠️  WARNING: This will DELETE all specialist and role agents!")
        print("   Base classes and governance data will be preserved.")
        confirm = input("\nType 'YES' to confirm deletion: ")
        
        if confirm != "YES":
            print("❌ Deletion cancelled")
            return
    
    # Perform cleanup
    deleted_agents = delete_non_base_agents(dry_run=args.dry_run)
    deleted_caps = cleanup_orphaned_capabilities(dry_run=args.dry_run)
    deleted_logs = clear_logs(dry_run=args.dry_run)
    deleted_artifacts = clear_artifacts(dry_run=args.dry_run)
    
    # Summary
    print("\n" + "=" * 70)
    if args.dry_run:
        print("✅ Dry run completed - no files were deleted")
        print(f"\nWould delete:")
        print(f"   - {deleted_agents} agents")
        print(f"   - {deleted_caps} capabilities")
        print(f"   - {deleted_logs} log files")
        print(f"   - {deleted_artifacts} artifact files")
    else:
        print("✅ Cleanup completed successfully!")
        print(f"\nDeleted:")
        print(f"   - {deleted_agents} agents")
        print(f"   - {deleted_caps} capabilities")
        print(f"   - {deleted_logs} log files")
        print(f"   - {deleted_artifacts} artifact files")
        
        # Show new state
        print("\n📊 New Database State:")
        new_stats = get_agent_stats()
        print(f"   Total agents: {new_stats['total']}")
        print(f"   Base class agents: {new_stats['base']}")
        print(f"   Specialist agents: {new_stats['specialists']}")
        
        print("\n💡 Next steps:")
        print("   1. Restart the backend to re-register agents")
        print("   2. Run: python -m pytest tests/test_hello_world_mission.py")
    
    print("=" * 70)


if __name__ == '__main__':
    main()
