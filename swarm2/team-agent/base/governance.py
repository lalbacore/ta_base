from typing import Optional, Dict, Any
import time

class Governance:
    def __init__(self, workflow_id: Optional[str] = None, policy: Optional[Dict[str, Any]] = None):
        # Default a stable-ish workflow id if not provided
        self.workflow_id = workflow_id or f"wf_{int(time.time())}"
        # Keep existing policy behavior if present, otherwise default to empty dict
        self.policy = policy or {}