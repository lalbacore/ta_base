#!/usr/bin/env python3
"""
Reset Team Agent Databases Script

Cleans up all databases, logs, and state files to start fresh.
Optionally backs up data before deletion.

Databases:
- backend.db: Missions, agent cards, governance, PKI metadata
- trust.db: Agent reputation tracking
- registry.db: Capability registry
- crl.db: Certificate revocation list

Logs:
- *.jsonl files in backend/logs/ and logs/
- TuringTape files in .team_agent/tape/

Usage:
    python scripts/reset_databases.py              # Reset with backup
    python scripts/reset_databases.py --no-backup  # Reset without backup
    python scripts/reset_databases.py --dry-run    # Show what would be deleted
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import argparse


# Database file paths
HOME = Path.home()
TEAM_AGENT_DIR = HOME / '.team_agent'
BACKEND_DB = TEAM_AGENT_DIR / 'backend.db'
TRUST_DB = TEAM_AGENT_DIR / 'trust.db'
REGISTRY_DB = TEAM_AGENT_DIR / 'registry.db'
CRL_DB = TEAM_AGENT_DIR / 'pki' / 'crl.db'

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
PROJECT_ROOT = Path(__file__).parent.parent


def get_db_size(db_path: Path) -> int:
    """Get database file size in bytes."""
    if db_path.exists():
        return db_path.stat().st_size
    return 0


def get_db_table_counts(db_path: Path) -> dict:
    """Get row counts for all tables in database."""
    if not db_path.exists():
        return {}

    counts = {}
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]

        # Get row count for each table
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]

        conn.close()
    except Exception as e:
        counts['error'] = str(e)

    return counts


def backup_databases(backup_dir: Path) -> None:
    """Backup all databases to a timestamped directory."""
    print(f"\n📦 Backing up databases to: {backup_dir}")
    backup_dir.mkdir(parents=True, exist_ok=True)

    databases = [
        ('backend.db', BACKEND_DB),
        ('trust.db', TRUST_DB),
        ('registry.db', REGISTRY_DB),
        ('crl.db', CRL_DB)
    ]

    for name, db_path in databases:
        if db_path.exists():
            backup_path = backup_dir / name
            shutil.copy2(db_path, backup_path)
            size_kb = backup_path.stat().st_size / 1024
            print(f"   ✓ Backed up {name} ({size_kb:.1f} KB)")
        else:
            print(f"   - {name} does not exist, skipping")


def backup_logs(backup_dir: Path) -> None:
    """Backup all log files."""
    print(f"\n📦 Backing up logs to: {backup_dir / 'logs'}")
    log_dirs = [
        PROJECT_ROOT / 'backend' / 'logs',
        PROJECT_ROOT / 'logs',
    ]

    for log_dir in log_dirs:
        if log_dir.exists():
            dest_dir = backup_dir / 'logs' / log_dir.name
            shutil.copytree(log_dir, dest_dir, dirs_exist_ok=True)
            print(f"   ✓ Backed up {log_dir}")


def backup_tapes(backup_dir: Path) -> None:
    """Backup TuringTape files."""
    tape_dir = TEAM_AGENT_DIR / 'tape'
    if tape_dir.exists():
        print(f"\n📦 Backing up TuringTape files to: {backup_dir / 'tape'}")
        dest_dir = backup_dir / 'tape'
        shutil.copytree(tape_dir, dest_dir, dirs_exist_ok=True)
        print(f"   ✓ Backed up {tape_dir}")


def show_database_stats() -> None:
    """Display current database statistics."""
    print("\n📊 Current Database Statistics:")
    print("=" * 70)

    databases = [
        ('Backend', BACKEND_DB),
        ('Trust', TRUST_DB),
        ('Registry', REGISTRY_DB),
        ('CRL', CRL_DB)
    ]

    for name, db_path in databases:
        if db_path.exists():
            size_kb = get_db_size(db_path) / 1024
            print(f"\n{name} Database ({db_path.name}):")
            print(f"  Size: {size_kb:.1f} KB")

            counts = get_db_table_counts(db_path)
            if counts:
                print(f"  Tables:")
                for table, count in sorted(counts.items()):
                    print(f"    - {table}: {count:,} rows")
        else:
            print(f"\n{name} Database: Does not exist")


def delete_database(db_path: Path, name: str, dry_run: bool = False) -> None:
    """Delete a database file."""
    if db_path.exists():
        if dry_run:
            size_kb = get_db_size(db_path) / 1024
            print(f"   Would delete {name} ({size_kb:.1f} KB)")
        else:
            db_path.unlink()
            print(f"   ✓ Deleted {name}")
    else:
        print(f"   - {name} does not exist")


def delete_logs(dry_run: bool = False) -> None:
    """Delete all log files."""
    print("\n🗑️  Deleting logs...")

    log_patterns = [
        PROJECT_ROOT / 'backend' / 'logs' / '*.jsonl',
        PROJECT_ROOT / 'backend' / 'logs' / '*.log',
        PROJECT_ROOT / 'logs' / '*.jsonl',
        PROJECT_ROOT / 'logs' / '*.log',
    ]

    total_deleted = 0
    for pattern in log_patterns:
        for log_file in pattern.parent.glob(pattern.name):
            if dry_run:
                size_kb = log_file.stat().st_size / 1024
                print(f"   Would delete {log_file} ({size_kb:.1f} KB)")
            else:
                log_file.unlink()
                total_deleted += 1

    if not dry_run:
        print(f"   ✓ Deleted {total_deleted} log files")


def delete_tapes(dry_run: bool = False) -> None:
    """Delete TuringTape files."""
    tape_dir = TEAM_AGENT_DIR / 'tape'

    if tape_dir.exists():
        print("\n🗑️  Deleting TuringTape files...")

        tape_files = list(tape_dir.glob('*.jsonl'))
        if dry_run:
            for tape_file in tape_files:
                size_kb = tape_file.stat().st_size / 1024
                print(f"   Would delete {tape_file} ({size_kb:.1f} KB)")
        else:
            for tape_file in tape_files:
                tape_file.unlink()
            print(f"   ✓ Deleted {len(tape_files)} tape files")


def reset_databases(backup: bool = True, dry_run: bool = False) -> None:
    """Reset all databases, logs, and state files."""

    print("=" * 70)
    print("Team Agent Database Reset Utility")
    print("=" * 70)

    # Show current state
    show_database_stats()

    # Backup if requested
    if backup and not dry_run:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = PROJECT_ROOT / 'backups' / f'backup_{timestamp}'
        backup_databases(backup_dir)
        backup_logs(backup_dir)
        backup_tapes(backup_dir)
        print(f"\n✅ Backup completed: {backup_dir}")

    # Confirm deletion unless dry-run
    if not dry_run:
        print("\n⚠️  WARNING: This will DELETE all databases and logs!")
        if backup:
            print(f"   (Backup saved to backups/ directory)")
        confirm = input("\nType 'YES' to confirm deletion: ")

        if confirm != "YES":
            print("❌ Deletion cancelled")
            return

    # Delete databases
    print("\n🗑️  Deleting databases...")
    delete_database(BACKEND_DB, 'backend.db', dry_run)
    delete_database(TRUST_DB, 'trust.db', dry_run)
    delete_database(REGISTRY_DB, 'registry.db', dry_run)
    delete_database(CRL_DB, 'crl.db', dry_run)

    # Delete logs
    delete_logs(dry_run)

    # Delete tapes
    delete_tapes(dry_run)

    # Summary
    print("\n" + "=" * 70)
    if dry_run:
        print("✅ Dry run completed - no files were deleted")
    else:
        print("✅ Reset completed successfully!")
        print("\nAll databases, logs, and state files have been cleared.")
        print("The system is ready for a fresh start.")
        print("\nNote: PKI certificates (.team_agent/pki/) were preserved.")
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Reset Team Agent databases and logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip backup before deletion')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')

    args = parser.parse_args()

    reset_databases(backup=not args.no_backup, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
