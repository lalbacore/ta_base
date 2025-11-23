"""
Recorder Agent - Publishes artifacts and final record.
"""

from typing import Dict, Any
from datetime import datetime
from pathlib import Path

from .base import BaseRole


class Recorder(BaseRole):
    """Recorder role implementation."""
    
    def __init__(self, workflow_id: str, output_dir: str = "output"):
        """Initialize recorder with workflow ID and output directory."""
        super().__init__(workflow_id)
        self.output_dir = Path(output_dir)
        self.workflow_dir = self.output_dir / workflow_id
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create final record and publish artifacts."""
        all_data = context.get("input", {})
        architecture = all_data.get("architecture", {})
        implementation = all_data.get("implementation", {})
        review = all_data.get("review", {})
        decision = all_data.get("decision", {})
        
        self.logger.info("Starting stage: recorder", extra={
            "stage": "recorder",
            "event": "stage_start",
            "input_size": len(str(all_data)),
        })
        
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        artifacts = self._publish_artifacts(implementation)
        
        record = {
            "workflow_id": self.workflow_id,
            "status": "approved" if decision.get("approved") else "rejected",
            "composite_score": (
                review.get("quality_score", 0) * 0.5 +
                decision.get("compliance_score", 0) * 0.5
            ),
            "quality_score": review.get("quality_score", 0),
            "compliance_score": decision.get("compliance_score", 0),
            "published_artifacts": artifacts,
            "requires_remediation": not decision.get("approved"),
            "metadata": {
                "architecture": architecture,
                "implementation_metrics": review.get("metrics", {}),
                "review_issues_count": len(review.get("issues", [])),
                "risk_level": decision.get("risk_level", "unknown"),
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        self.logger.info("Completed stage: recorder", extra={
            "stage": "recorder",
            "event": "stage_complete",
            "output_size": len(str(record)),
            "duration_seconds": 0,
        })
        
        return record
    
    def _publish_artifacts(self, implementation: Dict[str, Any]) -> Dict[str, str]:
        """Publish code and documentation artifacts."""
        artifacts = {}
        
        code = implementation.get("code", "")
        if code:
            filename = implementation.get("filename", "main.py")
            code_path = self.workflow_dir / filename
            code_path.write_text(code)
            artifacts["primary_code"] = str(code_path)
            self.logger.info(f"Published code to: {code_path}")
        else:
            self.logger.warning("No code to publish")
        
        docs = implementation.get("documentation", "")
        if docs:
            readme_path = self.workflow_dir / "README.md"
            readme_path.write_text(docs)
            artifacts["readme"] = str(readme_path)
        
        if code:
            filename = implementation.get("filename", "main.py")
            run_script = self.workflow_dir / "run.sh"
            run_script.write_text(f'''#!/bin/bash
# Auto-generated run script

python3 {filename}
''')
            run_script.chmod(0o755)
            artifacts["run_script"] = str(run_script)
        
        return artifacts