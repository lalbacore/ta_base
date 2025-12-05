"""
Automatic seed data loader for Team Agent Backend.

Loads initial data into the database on first run, including:
- Default governance policy
- Sample governance decisions
- Sample missions (future)
- Sample certificates (future)

This module provides idempotent seeding - safe to run multiple times.
"""
from datetime import datetime
from app.database import get_backend_session
from app.models.governance import GovernancePolicy, GovernanceDecision
from app.data.seed_data import GOVERNANCE_DECISIONS


def seed_governance_policy():
    """
    Create default governance policy if none exists.

    Returns:
        bool: True if policy was created, False if already exists
    """
    with get_backend_session() as session:
        # Check if policy already exists
        existing_policy = session.query(GovernancePolicy).first()
        if existing_policy:
            print("ℹ️  Governance policy already exists, skipping seed")
            return False

        # Create default policy
        policy = GovernancePolicy(
            min_trust_score=75.0,
            require_security_review=True,
            allowed_languages=['python', 'javascript', 'typescript', 'go', 'rust'],
            max_cost_per_mission=500.0,
            require_code_review=True,
            auto_approve_threshold=90.0,
            enable_breakpoints=True
        )

        session.add(policy)
        session.flush()  # Ensure it's saved

        print(f"✅ Created default governance policy (ID: {policy.id})")
        return True


def seed_governance_decisions():
    """
    Load sample governance decisions if none exist.

    Returns:
        int: Number of decisions created
    """
    with get_backend_session() as session:
        # Check if decisions already exist
        existing_count = session.query(GovernanceDecision).count()
        if existing_count > 0:
            print(f"ℹ️  {existing_count} governance decisions already exist, skipping seed")
            return 0

        # Create sample decisions
        created = 0
        for decision_data in GOVERNANCE_DECISIONS:
            decision = GovernanceDecision(
                decision_id=decision_data['decision_id'],
                workflow_id=decision_data['workflow_id'],
                stage=decision_data['stage'],
                decision=decision_data['decision'],
                timestamp=datetime.fromisoformat(decision_data['timestamp']),
                trust_score=decision_data['trust_score'],
                policy_violations=decision_data.get('policy_violations', 0),
                reason=decision_data.get('reason', '')
            )
            session.add(decision)
            created += 1

        session.flush()
        print(f"✅ Created {created} sample governance decisions")
        return created


def seed_database():
    """
    Main seed function - loads all seed data if database is empty.

    This function is idempotent and safe to call multiple times.
    It will only load data that doesn't already exist.

    Returns:
        dict: Summary of what was seeded
    """
    print("🌱 Checking if database needs seeding...")

    summary = {
        'policy_created': False,
        'decisions_created': 0
    }

    try:
        # Seed governance data
        summary['policy_created'] = seed_governance_policy()
        summary['decisions_created'] = seed_governance_decisions()

        # Future: seed missions, certificates, etc.

        if summary['policy_created'] or summary['decisions_created'] > 0:
            print("✅ Database seeding complete!")
        else:
            print("ℹ️  Database already seeded, no changes made")

        return summary

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise


if __name__ == '__main__':
    # Allow running directly for testing
    seed_database()
