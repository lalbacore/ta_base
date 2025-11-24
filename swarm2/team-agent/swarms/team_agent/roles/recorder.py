"""
Recorder Agent - Publishes artifacts and final record.
"""

import json
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
    
    def run(self, context):
        """Record workflow data."""
        # Normalize to dict
        if not isinstance(context, dict):
            try:
                context = json.loads(context) if isinstance(context, str) else {"data": context}
            except Exception:
                context = {"data": str(context)}
        
        # Extract fields safely
        mission = context.get("mission", context.get("input", ""))
        architecture = context.get("architecture", {})
        implementation = context.get("implementation", {})
        review = context.get("review", {})
        artifacts = context.get("artifacts", {})
        
        # Build record
        record_data = {
            "mission": mission,
            "architecture": architecture,
            "implementation": implementation,
            "review": review,
            "artifacts": artifacts,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        output_file = self.output_dir / f"{self.workflow_id}_record.json"
        output_file.write_text(json.dumps(record_data, indent=2, default=str))
        
        return record_data
    
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