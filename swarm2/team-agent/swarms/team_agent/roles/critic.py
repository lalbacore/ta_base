"""
Critic Agent - Reviews code quality.
"""

from typing import Dict, Any, List
from datetime import datetime
import re

from .base import BaseRole


class Critic(BaseRole):
    """Critic role implementation."""
    
    def __init__(self, workflow_id: str):
        """Initialize critic with workflow ID."""
        super().__init__(workflow_id)
    
    def run(self, context):
        if not isinstance(context, dict):
            context = {"input": str(context)}
    
        implementation = context.get("implementation", {})
        if isinstance(implementation, str):
            try:
                import json as _json
                implementation = _json.loads(implementation)
            except Exception:
                implementation = {}
    
        code = implementation.get("code", context.get("code", ""))
        
        self.logger.info("Starting stage: critic", extra={
            "stage": "critic",
            "event": "stage_start",
            "input_size": len(str(implementation)),
        })
        
        issues = self._identify_issues(code)
        metrics = self._calculate_metrics(code)
        
        review = {
            "quality_score": self._calculate_quality_score(issues, metrics),
            "issues": issues,
            "metrics": metrics,
            "recommendations": self._generate_recommendations(issues),
            "implementation_reference": implementation,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.logger.info("Completed stage: critic", extra={
            "stage": "critic",
            "event": "stage_complete",
            "output_size": len(str(review)),
            "duration_seconds": 0,
        })
        
        return review
    
    def _identify_issues(self, code: str) -> List[Dict[str, Any]]:
        """Identify potential issues in the code."""
        issues = []
        
        if "TODO" in code:
            issues.append({
                "severity": "info",
                "type": "incomplete",
                "message": "Code contains TODO comments",
            })
        
        if "FIXME" in code:
            issues.append({
                "severity": "warning",
                "type": "needs_fix",
                "message": "Code contains FIXME comments",
            })
        
        if len(code) < 100:
            issues.append({
                "severity": "warning",
                "type": "minimal_implementation",
                "message": "Implementation appears minimal",
            })
        
        if "def test_" not in code and "class Test" not in code:
            issues.append({
                "severity": "info",
                "type": "missing_tests",
                "message": "No test functions found in implementation",
            })
        
        return issues
    
    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate code metrics."""
        lines = code.split("\n")
        
        return {
            "lines_of_code": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
            "total_lines": len(lines),
            "functions": len(re.findall(r"def \w+\(", code)),
            "classes": len(re.findall(r"class \w+", code)),
            "docstrings": len(re.findall(r'"""', code)) // 2,
        }
    
    def _calculate_quality_score(self, issues: List[Dict], metrics: Dict) -> float:
        """Calculate overall quality score."""
        base_score = 100.0
        
        for issue in issues:
            if issue["severity"] == "error":
                base_score -= 20
            elif issue["severity"] == "warning":
                base_score -= 10
            elif issue["severity"] == "info":
                base_score -= 5
        
        if metrics.get("docstrings", 0) > 0:
            base_score += 5
        
        if metrics.get("functions", 0) > 0:
            base_score += 5
        
        return max(0, min(100, base_score))
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "missing_tests":
                recommendations.append("Add comprehensive unit tests")
            elif issue["type"] == "incomplete":
                recommendations.append("Complete TODO items before production")
            elif issue["type"] == "minimal_implementation":
                recommendations.append("Expand implementation with error handling and edge cases")
        
        if not recommendations:
            recommendations.append("Code quality is acceptable")
        
        return recommendations