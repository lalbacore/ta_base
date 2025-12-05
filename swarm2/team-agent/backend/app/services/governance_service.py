"""
Governance Service - Bridges Flask API to Governance role.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import Dict, Any, List, Optional
from app.data.seed_data import GOVERNANCE_CONFIG, GOVERNANCE_DECISIONS


class GovernanceService:
    """
    Service layer for governance and policy management.
    Bridges Flask API to Governance role.
    """

    def __init__(self):
        # TODO: Initialize governance when ready
        # from swarms.team_agent.roles.governance import Governance
        # from storage.models import AgentConfig
        # self.governance = Governance()

        # Load seed data
        self.policy_config = GOVERNANCE_CONFIG.copy()
        self.decisions = GOVERNANCE_DECISIONS.copy()

    def get_policy_config(self) -> Dict[str, Any]:
        """Get current policy configuration."""
        # TODO: Get from governance.policy or storage.get_agent_config()
        return self.policy_config

    def update_policy_config(self, config: Dict[str, Any]) -> None:
        """Update policy configuration."""
        # TODO: Update governance.policy and persist to storage
        self.policy_config.update(config)

    def get_decisions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get governance decision history."""
        # TODO: Get from governance.decisions list
        return self.decisions[:limit]

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
        violations = []
        satisfied = []
        warnings = []

        # Check min trust score
        min_trust = mission_data.get('min_trust_score', 0)
        if min_trust < self.policy_config['min_trust_score']:
            violations.append({
                'policy': 'min_trust_score',
                'required': self.policy_config['min_trust_score'],
                'actual': min_trust,
                'message': f'Mission trust score ({min_trust}) below minimum required ({self.policy_config["min_trust_score"]})'
            })
        else:
            satisfied.append({
                'policy': 'min_trust_score',
                'message': f'Trust score requirement met ({min_trust} >= {self.policy_config["min_trust_score"]})'
            })

        # Check max cost
        max_cost = mission_data.get('max_cost', 0)
        if max_cost > self.policy_config['max_cost_per_mission']:
            violations.append({
                'policy': 'max_cost_per_mission',
                'required': self.policy_config['max_cost_per_mission'],
                'actual': max_cost,
                'message': f'Mission cost (${max_cost}) exceeds maximum (${self.policy_config["max_cost_per_mission"]})'
            })
        else:
            satisfied.append({
                'policy': 'max_cost_per_mission',
                'message': f'Cost within budget (${max_cost} <= ${self.policy_config["max_cost_per_mission"]})'
            })

        # Check if security review is required
        capabilities = mission_data.get('required_capabilities', [])
        needs_security = any(cap.get('capability_type') in ['deployment', 'security_audit']
                           for cap in capabilities)

        if self.policy_config['require_security_review'] and needs_security:
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
        if self.policy_config['require_code_review'] and has_code_gen:
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
