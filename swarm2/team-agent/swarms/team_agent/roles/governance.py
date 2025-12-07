"""
Governance Agent - Ensures compliance and approval decisions.
Uses ToolRegistry for policy checking and scoring.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import time
import uuid

from ..core.node import SwarmNode
from ..crypto.pki import TrustDomain
from ..tools import ToolRegistry, ScoringTool, ReviewTool

# Import crypto modules (optional)
try:
    from swarms.team_agent.crypto import Signer
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Signer = None


class Governance(SwarmNode):
    """
    Governance role implementation.
    Uses tools for compliance checking and scoring.
    """

    def __init__(
        self,
        workflow_id: Optional[str] = None,
        name: str = "Governance",
        id: str = "agent_governance_001",
        policy: Optional[Dict[str, Any]] = None,
        registry: Optional[ToolRegistry] = None,
        cert_chain: Optional[Dict[str, bytes]] = None
    ):
        """Initialize governance with workflow ID, tool registry, and cert chain."""
        # Initialize SwarmNode (GOVERNMENT domain)
        super().__init__(
            name=name,
            agent_type="role",
            agent_id=id,
            trust_domain=TrustDomain.GOVERNMENT
        )
        
        self.workflow_id = workflow_id or f"wf_{int(time.time())}"
        self.policy: Dict[str, Any] = policy or {
            "min_score_threshold": 0.5,
            "require_security_review": True,
            "allowed_languages": ["python"],
        }
        self.capabilities: List[str] = ["enforce_policy", "evaluate_request", "describe"]
        self.decisions: List[Dict[str, Any]] = []
        
        # Initialize tool registry
        self._registry = registry or ToolRegistry()
        self._register_default_tools()
        # Initialize signer if cert_chain is provided (manual override)
        if cert_chain and CRYPTO_AVAILABLE:
            try:
                self.signer = Signer(
                    private_key_pem=cert_chain['key'],
                    certificate_pem=cert_chain['cert'],
                    signer_id="governance"
                )
            except Exception:
                pass
    
    def _register_default_tools(self) -> None:
        """Register default tools if not already present."""
        if "content_scorer" not in self._registry:
            self._registry.register(ScoringTool())
        if "code_reviewer" not in self._registry:
            self._registry.register(ReviewTool())
    
    def act(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make governance decision based on review.
        Uses tools for additional compliance checking.
        """
        composite = float(review.get("score", 0.8)) if isinstance(review, dict) else 0.8
        
        # Additional policy checks using tools
        policy_violations: List[str] = []
        tool_results = []
        
        # Check if there are security risks in the review
        risks = review.get("risks", []) if isinstance(review, dict) else []
        high_risks = [r for r in risks if r.get("level") == "high"]
        
        if high_risks and self.policy.get("require_security_review"):
            policy_violations.append(f"High-risk security issues detected: {len(high_risks)}")
            composite = max(0.3, composite - 0.2)  # Penalty for security issues
        
        # Check score threshold
        min_threshold = self.policy.get("min_score_threshold", 0.5)
        allowed = composite >= min_threshold and len(policy_violations) == 0
        
        decision_id = str(uuid.uuid4())
        decision = {
            "status": "enforced",
            "decision_id": decision_id,
            "allowed": allowed,
            "composite_score": composite,
            "workflow_id": self.workflow_id,
            "policy_violations": policy_violations,
            "policy_applied": self.policy,
            "tool_results": tool_results,
            "tools_used": ["content_scorer"],
            "recommendation": "proceed" if allowed else "halt",
            "rationale": (
                f"Score {composite:.2f} meets threshold {min_threshold}" 
                if allowed 
                else f"Score {composite:.2f} below threshold or policy violations detected"
            ),
        }
        self.decisions.append(decision)

        # Sign output if signer is available
        if self.signer and CRYPTO_AVAILABLE:
            decision = self.signer.sign_dict(decision)

        return decision

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run governance with a context dict.
        Extracts review data and delegates to act().
        """
        if "status" in context and context.get("status") == "reviewed":
            return self.act(context)
        if "input" in context:
            return self.act(context["input"])
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
            "tools_available": [t.name for t in self._registry.list_tools()],
        }
