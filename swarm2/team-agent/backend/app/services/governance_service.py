"""
Governance Service - Bridges Flask API to Governance role with SQLAlchemy persistence.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import Dict, Any, List, Optional
from app.database import get_backend_session
from app.models.governance import GovernancePolicy, GovernanceDecision


class GovernanceService:
    """
    Service layer for governance and policy management.

    Uses SQLAlchemy for persistent storage of policies and decisions.
    """

    def __init__(self):
        # TODO: Initialize governance role when ready
        # from swarms.team_agent.roles.governance import Governance
        # self.governance = Governance()
        pass

    def get_policy_config(self) -> Dict[str, Any]:
        """
        Get current active policy configuration from database.

        Returns the active policy record.
        If no active policy exists, returns the first policy or creates a default one.
        """
        with get_backend_session() as session:
            # Try to get active policy first
            policy = session.query(GovernancePolicy)\
                .filter(GovernancePolicy.is_active == True)\
                .first()

            # Fall back to first policy if no active one
            if not policy:
                policy = session.query(GovernancePolicy).first()

            if not policy:
                # Create default policy if none exists
                policy = GovernancePolicy(
                    name='Default Policy',
                    description='Default governance policy for Team Agent missions',
                    is_active=True,
                    min_trust_score=75.0,
                    require_security_review=True,
                    allowed_languages=['python', 'javascript', 'typescript', 'go', 'rust'],
                    max_cost_per_mission=500.0,
                    require_code_review=True,
                    auto_approve_threshold=90.0,
                    enable_breakpoints=True
                )
                session.add(policy)
                session.commit()

            return policy.to_dict()

    def update_policy_config(self, config: Dict[str, Any]) -> None:
        """
        Update policy configuration in database.

        Updates the first policy record or creates one if none exists.
        """
        with get_backend_session() as session:
            policy = session.query(GovernancePolicy).first()

            if not policy:
                # Create new policy
                policy = GovernancePolicy(**config)
                session.add(policy)
            else:
                # Update existing policy
                for key, value in config.items():
                    if hasattr(policy, key):
                        setattr(policy, key, value)

            session.commit()

    def get_decisions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get governance decision history from database.

        Returns most recent decisions, ordered by timestamp descending.
        """
        with get_backend_session() as session:
            decisions = session.query(GovernanceDecision)\
                .order_by(GovernanceDecision.timestamp.desc())\
                .limit(limit)\
                .all()

            return [decision.to_dict() for decision in decisions]

    # Policy CRUD Methods

    def get_all_policies(self) -> List[Dict[str, Any]]:
        """
        Get all governance policies from database.

        Returns all policies with their metadata (name, description, active status).
        """
        with get_backend_session() as session:
            policies = session.query(GovernancePolicy)\
                .order_by(GovernancePolicy.is_active.desc(), GovernancePolicy.name)\
                .all()

            return [policy.to_dict() for policy in policies]

    def get_active_policy(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently active policy.

        Returns None if no active policy exists.
        """
        with get_backend_session() as session:
            policy = session.query(GovernancePolicy)\
                .filter(GovernancePolicy.is_active == True)\
                .first()

            return policy.to_dict() if policy else None

    def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new governance policy.

        New policies are created as inactive by default.
        To activate, call activate_policy() separately.
        """
        with get_backend_session() as session:
            # Ensure new policies start as inactive
            policy_data['is_active'] = False

            policy = GovernancePolicy(**policy_data)
            session.add(policy)
            session.flush()  # Get the ID

            return policy.to_dict()

    def update_policy(self, policy_id: int, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing governance policy.

        Cannot change is_active via this method - use activate_policy() instead.
        """
        with get_backend_session() as session:
            policy = session.query(GovernancePolicy)\
                .filter(GovernancePolicy.id == policy_id)\
                .first()

            if not policy:
                raise ValueError(f"Policy {policy_id} not found")

            # Don't allow changing is_active via update
            if 'is_active' in policy_data:
                del policy_data['is_active']

            # Update fields
            for key, value in policy_data.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)

            session.flush()
            return policy.to_dict()

    def delete_policy(self, policy_id: int) -> None:
        """
        Delete a governance policy.

        Cannot delete the active policy - deactivate it first.
        """
        with get_backend_session() as session:
            policy = session.query(GovernancePolicy)\
                .filter(GovernancePolicy.id == policy_id)\
                .first()

            if not policy:
                raise ValueError(f"Policy {policy_id} not found")

            if policy.is_active:
                raise ValueError("Cannot delete active policy - activate another policy first")

            session.delete(policy)

    def activate_policy(self, policy_id: int) -> Dict[str, Any]:
        """
        Activate a governance policy.

        Automatically deactivates all other policies (only one can be active).
        """
        with get_backend_session() as session:
            # Deactivate all policies
            session.query(GovernancePolicy)\
                .update({GovernancePolicy.is_active: False})

            # Activate the selected policy
            policy = session.query(GovernancePolicy)\
                .filter(GovernancePolicy.id == policy_id)\
                .first()

            if not policy:
                raise ValueError(f"Policy {policy_id} not found")

            policy.is_active = True
            session.flush()

            return policy.to_dict()

    def get_pending_gates(self) -> List[Dict[str, Any]]:
        """Get pending approval gates."""
        # TODO: Get pending gates from workflow system
        return []

    def approve_gate(self, gate_id: str) -> None:
        """Approve an approval gate."""
        # TODO: Implement gate approval
        pass

    def reject_gate(self, gate_id: str, reason: Optional[str] = None) -> None:
        """Reject an approval gate."""
        # TODO: Implement gate rejection
        pass

    def check_mission_compliance(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check how a mission compares against current policies.
        This is the easter egg feature!

        Returns a compliance report showing which policies are satisfied/violated.
        """
        # Get current policy from database
        policy_config = self.get_policy_config()

        violations = []
        satisfied = []
        warnings = []

        # Check min trust score
        min_trust = mission_data.get('min_trust_score', 0)
        if min_trust < policy_config['min_trust_score']:
            violations.append({
                'policy': 'min_trust_score',
                'required': policy_config['min_trust_score'],
                'actual': min_trust,
                'message': f'Mission trust score ({min_trust}) below minimum required ({policy_config["min_trust_score"]})'
            })
        else:
            satisfied.append({
                'policy': 'min_trust_score',
                'message': f'Trust score requirement met ({min_trust} >= {policy_config["min_trust_score"]})'
            })

        # Check max cost
        max_cost = mission_data.get('max_cost', 0)
        if max_cost > policy_config['max_cost_per_mission']:
            violations.append({
                'policy': 'max_cost_per_mission',
                'required': policy_config['max_cost_per_mission'],
                'actual': max_cost,
                'message': f'Mission cost (${max_cost}) exceeds maximum (${policy_config["max_cost_per_mission"]})'
            })
        else:
            satisfied.append({
                'policy': 'max_cost_per_mission',
                'message': f'Cost within budget ({max_cost} tokens <= {policy_config["max_cost_per_mission"]} tokens)'
            })

        # Check if security review is required
        capabilities = mission_data.get('required_capabilities', [])
        needs_security = any(cap.get('capability_type') in ['deployment', 'security_audit']
                           for cap in capabilities)

        if policy_config['require_security_review'] and needs_security:
            has_security_cap = any(cap.get('capability_type') == 'security_audit'
                                 for cap in capabilities)
            if has_security_cap:
                satisfied.append({
                    'policy': 'require_security_review',
                    'message': 'Security audit capability included'
                })
            else:
                warnings.append({
                    'policy': 'require_security_review',
                    'message': 'Deployment detected but no security audit requested - consider adding one'
                })

        # Check if code review is required
        has_code_gen = any(cap.get('capability_type') == 'code_generation'
                          for cap in capabilities)
        if policy_config['require_code_review'] and has_code_gen:
            has_review_cap = any(cap.get('capability_type') == 'code_review'
                                for cap in capabilities)
            if has_review_cap:
                satisfied.append({
                    'policy': 'require_code_review',
                    'message': 'Code review capability included'
                })
            else:
                warnings.append({
                    'policy': 'require_code_review',
                    'message': 'Code generation detected but no code review requested - consider adding one'
                })

        # Calculate compliance score
        total_checks = len(violations) + len(satisfied) + len(warnings)
        compliance_score = (len(satisfied) / total_checks * 100) if total_checks > 0 else 100

        # Determine overall status
        if len(violations) > 0:
            status = 'non_compliant'
        elif len(warnings) > 0:
            status = 'compliant_with_warnings'
        else:
            status = 'fully_compliant'

        return {
            'status': status,
            'compliance_score': round(compliance_score, 1),
            'violations': violations,
            'satisfied': satisfied,
            'warnings': warnings,
            'summary': {
                'total_checks': total_checks,
                'violations_count': len(violations),
                'satisfied_count': len(satisfied),
                'warnings_count': len(warnings)
            }
        }


# Singleton instance
governance_service = GovernanceService()
