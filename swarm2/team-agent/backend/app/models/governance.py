"""
Governance models for policy configuration and decision tracking.

Models:
- GovernancePolicy: Global policy configuration
- GovernanceDecision: Historical governance decisions
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime, Text
from app.models.base import Base, TimestampMixin


class GovernancePolicy(Base, TimestampMixin):
    """
    Governance policy configuration.

    Stores policy settings that control:
    - Mission approval requirements
    - Trust score thresholds
    - Security and code review requirements
    - Allowed programming languages
    - Cost limits
    - Breakpoint and auto-approval settings

    Multiple policies can exist (templates, dev/staging/prod),
    but only one should be active at a time.
    """
    __tablename__ = 'governance_policies'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Policy metadata
    name = Column(String, nullable=False, unique=True)  # e.g. "Production", "Development", "Strict"
    description = Column(Text)  # Human-readable description
    is_active = Column(Boolean, default=False, nullable=False, index=True)  # Only one should be active

    # Trust and approval settings
    min_trust_score = Column(Float, nullable=False, default=75.0)
    auto_approve_threshold = Column(Float, nullable=False, default=90.0)

    # Review requirements
    require_security_review = Column(Boolean, default=True, nullable=False)
    require_code_review = Column(Boolean, default=True, nullable=False)

    # Language restrictions
    allowed_languages = Column(JSON, nullable=False)  # List of allowed language strings

    # Cost constraints
    max_cost_per_mission = Column(Float, default=500.0)

    # Workflow control
    enable_breakpoints = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return (f"<GovernancePolicy(id={self.id}, name='{self.name}', "
                f"active={self.is_active})>")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'min_trust_score': self.min_trust_score,
            'require_security_review': self.require_security_review,
            'allowed_languages': self.allowed_languages,
            'max_cost_per_mission': self.max_cost_per_mission,
            'require_code_review': self.require_code_review,
            'auto_approve_threshold': self.auto_approve_threshold,
            'enable_breakpoints': self.enable_breakpoints,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class GovernanceDecision(Base):
    """
    Historical record of governance decisions made during workflow execution.

    Tracks each approval/rejection decision with:
    - Which workflow was affected
    - What stage it was in
    - Why it was approved/rejected
    - Trust score at the time
    - Policy violations detected
    """
    __tablename__ = 'governance_decisions'

    decision_id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False, index=True)
    stage = Column(String, nullable=False)
    decision = Column(String, nullable=False)  # 'approved' or 'rejected'
    timestamp = Column(DateTime, nullable=False)
    trust_score = Column(Float, nullable=False)
    policy_violations = Column(Integer, default=0, nullable=False)
    reason = Column(Text)

    def __repr__(self):
        return (f"<GovernanceDecision(id={self.decision_id}, workflow={self.workflow_id}, "
                f"decision={self.decision})>")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'decision_id': self.decision_id,
            'workflow_id': self.workflow_id,
            'stage': self.stage,
            'decision': self.decision,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'trust_score': self.trust_score,
            'policy_violations': self.policy_violations,
            'reason': self.reason
        }
