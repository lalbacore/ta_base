#!/usr/bin/env python3
"""
Fresh Start Script

Resets the entire system to a clean state as requested by the user.
1. Deletes all databases (backend, trust, registry).
2. Deletes all logs and tapes.
3. Deletes team_output/ artifacts.
4. Re-initializes database schemas.
5. Seeds base data (Governance, Providers).
6. Re-registers all Agents (Specialists).

Usage:
    python scripts/fresh_start.py
"""
import sys
import os
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
# Add backend to path for app imports
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
# Add scripts dir to path
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import reset_databases as rd
from app.database import init_backend_db
from app.data.seed_loader import seed_database
from swarms.team_agent.orchestrator import Orchestrator

def clean_artifacts():
    """Delete team_output directory."""
    work_dir = Path(os.path.expanduser("~/Dropbox/Team Agent/Projects/ta_base/swarm2/team-agent/team_output"))
    if work_dir.exists():
        print(f"\n🗑️  Deleting artifacts in {work_dir}...")
        shutil.rmtree(work_dir)
        print("   ✓ Deleted artifacts directory")
        # Recreate empty dir
        work_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"\nℹ️  Artifacts directory {work_dir} not found")

def reseed_agents():
    """Re-register agents by instantiating Orchestrator."""
    print("\n🤖 Re-registering agents...")
    try:
        # Instantiating Orchestrator triggers _register_specialist_agents()
        # logging might be noisy, but that's fine
        orch = Orchestrator(output_dir="./team_output")
        print("   ✓ Agents re-registered successfully")
    except Exception as e:
        print(f"   ❌ Error registering agents: {e}")

def main():
    print("=" * 70)
    print("Team Agent Fresh Start")
    print("=" * 70)
    
    # 1. Reset Databases & Logs
    # Manually call delete functions to avoid input prompt
    print("\n🗑️  Deleting databases...")
    rd.delete_database(rd.BACKEND_DB, 'backend.db')
    rd.delete_database(rd.TRUST_DB, 'trust.db')
    rd.delete_database(rd.REGISTRY_DB, 'registry.db')
    rd.delete_database(rd.CRL_DB, 'crl.db')
    
    rd.delete_logs()
    rd.delete_tapes()
    
    # 2. Clean Artifacts
    clean_artifacts()
    
    # 3. Initialize Schema
    print("\n🔧 Re-initializing database schemas...")
    init_backend_db()
    
    # 4. Seed Data
    seed_database()
    
    # 5. Reseed Agents
    reseed_agents()
    
    print("\n" + "=" * 70)
    print("✅ Fresh start complete! You are ready to run missions.")
    print("=" * 70)

if __name__ == "__main__":
    main()
