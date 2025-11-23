"""
Base Role - Foundation for all agent roles.
"""

from typing import Dict, Any
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.logging import get_logger


class BaseRole:
    """Base class for all agent roles."""
    
    def __init__(self, workflow_id: str):
        """Initialize base role with workflow ID."""
        self.workflow_id = workflow_id
        self.role_name = self.__class__.__name__.lower()
        self.logger = get_logger(f"team_agent.{self.role_name}")
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the role's primary function."""
        raise NotImplementedError("Subclasses must implement run()")