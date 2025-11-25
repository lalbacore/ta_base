"""
Governance Agent - Ensures compliance and approval decisions.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import time, uuid

from .base import BaseRole


class Governance(BaseRole):
    """Governance role implementation."""
    
    def __init__(self, name: str = "Governance", id: str = "agent_governance_001",
                 workflow_id: Optional[str] = None, policy: Optional[Dict[str, Any]] = None):
        """Initialize governance with workflow ID."""
        super().__init__(workflow_id)
        self.name = name
        self.id = id
        self.workflow_id = workflow_id or f"wf_{int(time.time())}"
        self.policy: Dict[str, Any] = policy or {}
        self.capabilities: List[str] = ["enforce_policy", "evaluate_request", "describe"]
        self.decisions: List[Dict[str, Any]] = []
    
    def act(self, review: Dict[str, Any]) -> Dict[str, Any]:
        # Simple composite score from review if provided, else default
        composite = float(review.get("score", 0.8)) if isinstance(review, dict) else 0.8
        allowed = composite >= 0.5
        decision_id = str(uuid.uuid4())
        decision = {
            "status": "enforced",
            "decision_id": decision_id,
            "allowed": allowed,
            "composite_score": composite,
            "workflow_id": self.workflow_id,
        }
        self.decisions.append(decision)
        return decision

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run governance with a context dict.
        Extracts review data and delegates to act().
        """
        # Handle various input formats
        if "status" in context and context.get("status") == "reviewed":
            return self.act(context)
        if "input" in context:
            return self.act(context["input"])
        # Fallback: treat as review
        return self.act(context)

    def describe(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": "role",
            "role": "governance",
            "workflow_id": self.workflow_id,
            "policy": self.policy,
            "capabilities": self.capabilities,
            "decisions_made": len(self.decisions),
        }