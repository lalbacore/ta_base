"""
Script to update the existing default policy to the new Global Standard Protocol.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.database import get_backend_session
from app.models.governance import GovernancePolicy

def update_policy():
    print("🔄 Updating governance policy...")
    with get_backend_session() as session:
        # Find the default policy (or just the first one)
        policy = session.query(GovernancePolicy).first()
        if not policy:
            print("❌ No policy found!")
            return

        print(f"found policy: {policy.name}")
        
        # Update fields
        policy.name = 'Global Standard Protocol'
        policy.description = 'Universal baseline safety and compliance standards for all autonomous agent operations.'
        policy.min_trust_score = 80.0
        policy.max_cost_per_mission = 1000.0
        policy.auto_approve_threshold = 95.0
        # SQLAlchemy stores JSON for lists, but the model might handle it. 
        # Safest to just set it if the model supports it, or let's assume it does based on seed_loader.
        policy.allowed_languages = ['python', 'javascript', 'typescript', 'go', 'rust', 'solidity']
        
        session.commit()
        print("✅ Policy updated to 'Global Standard Protocol'")

if __name__ == "__main__":
    update_policy()
