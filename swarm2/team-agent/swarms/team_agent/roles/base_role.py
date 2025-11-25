"""
Base Role - Abstract base class for all agent roles.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import time
from utils.logging import get_logger


class BaseRole(ABC):
    """Abstract base class for agent roles."""
    
    def __init__(self, workflow_id: str = "unknown"):
        """
        Initialize base role.
        
        Args:
            workflow_id: Current workflow identifier
        """
        self.workflow_id = workflow_id
        self.logger = get_logger(f"team_agent.{self.__class__.__name__.lower()}")
    
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the role's logic.
        
        Args:
            context: Input context dict
        
        Returns:
            Result dict
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    def _log_stage_start(self, stage: str, input_data: Any):
        """Log stage start."""
        self.logger.info(
            f"Starting stage: {stage}",
            extra={
                "stage": stage,
                "event": "stage_start",
                "input_size": len(str(input_data))
            }
        )
    
    def _log_stage_complete(self, stage: str, output: Any, start_time: float):
        """Log stage completion."""
        duration = time.time() - start_time
        self.logger.info(
            f"Completed stage: {stage}",
            extra={
                "stage": stage,
                "event": "stage_complete",
                "output_size": len(str(output)),
                "duration_seconds": round(duration, 2)
            }
        )
    
    def _extract_input(self, context: Dict[str, Any]) -> str:
        """Extract input string from context."""
        if isinstance(context, str):
            return context
        
        return context.get("input", context.get("mission", ""))