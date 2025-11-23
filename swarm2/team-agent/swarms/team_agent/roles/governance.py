"""
Governance Agent - Ensures compliance and approval decisions.
"""

from typing import Dict, Any, List
from datetime import datetime

from .base import BaseRole


class Governance(BaseRole):
    """Governance role implementation."""
    
    def __init__(self, workflow_id: str):
        """Initialize governance with workflow ID."""
        super().__init__(workflow_id)
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make governance decision based on review."""
        review = context.get("input", {})
        quality_score = review.get("quality_score", 0)
        issues = review.get("issues", [])
        
        self.logger.info("Starting stage: governance", extra={
            "stage": "governance",
            "event": "stage_start",
            "input_size": len(str(review)),
        })
        
        decision = {
            "approved": self._make_decision(quality_score, issues),
            "compliance_score": self._calculate_compliance_score(quality_score, issues),
            "risk_level": self._assess_risk(issues),
            "rationale": self._generate_rationale(quality_score, issues),
            "conditions": self._generate_conditions(issues),
            "review_reference": review,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.logger.info("Completed stage: governance", extra={
            "stage": "governance",
            "event": "stage_complete",
            "output_size": len(str(decision)),
            "duration_seconds": 0,
        })
        
        return decision
    
    def _make_decision(self, quality_score: float, issues: List[Dict]) -> bool:
        """Make approval decision."""
        has_critical = any(i.get("severity") == "error" for i in issues)
        return quality_score >= 70 and not has_critical
    
    def _calculate_compliance_score(self, quality_score: float, issues: List[Dict]) -> float:
        """Calculate compliance score."""
        compliance = quality_score
        
        critical_issues = sum(1 for i in issues if i.get("severity") == "error")
        compliance -= critical_issues * 15
        
        return max(0, min(100, compliance))
    
    def _assess_risk(self, issues: List[Dict]) -> str:
        """Assess risk level."""
        critical = sum(1 for i in issues if i.get("severity") == "error")
        warnings = sum(1 for i in issues if i.get("severity") == "warning")
        
        if critical > 0:
            return "high"
        elif warnings > 2:
            return "medium"
        else:
            return "low"
    
    def _generate_rationale(self, quality_score: float, issues: List[Dict]) -> str:
        """Generate decision rationale."""
        if quality_score >= 90:
            return "High quality implementation with minimal issues"
        elif quality_score >= 70:
            return "Acceptable quality with some minor issues to address"
        else:
            return "Quality improvements needed before approval"
    
    def _generate_conditions(self, issues: List[Dict]) -> List[str]:
        """Generate approval conditions."""
        conditions = []
        
        for issue in issues:
            if issue["severity"] in ["error", "warning"]:
                conditions.append(f"Resolve: {issue['message']}")
        
        return conditions