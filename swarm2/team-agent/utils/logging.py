"""
Centralized logging for Team Agent system.
Provides normalized, structured logging across all components.
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class TeamAgentLogger:
    """
    Normalized logger for Team Agent workflows.
    Logs to both file and console with structured JSON format.
    """
    
    def __init__(self, 
                 agent_name: str,
                 workflow_id: Optional[str] = None,
                 log_dir: str = "logs"):
        """
        Initialize logger for an agent.
        
        Args:
            agent_name: Name of the agent (architect, builder, etc.)
            workflow_id: Optional workflow ID for correlation
            log_dir: Directory for log files
        """
        self.agent_name = agent_name
        self.workflow_id = workflow_id or "unknown"
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(f"team_agent.{agent_name}")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers and close them properly
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
        
        # Console handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (DEBUG and above) - JSON format
        log_file = self.log_dir / f"{agent_name}.jsonl"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        
        # Workflow-specific file
        if workflow_id and workflow_id != "unknown":
            workflow_file = self.log_dir / f"workflow_{workflow_id}.jsonl"
            workflow_handler = logging.FileHandler(workflow_file)
            workflow_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(workflow_handler)
    
    def close(self):
        """Close all handlers properly."""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
    
    def _format_log(self, level: str, message: str, **kwargs) -> str:
        """Format log entry as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "agent": self.agent_name,
            "workflow_id": self.workflow_id,
            "message": message,
            **kwargs
        }
        return json.dumps(log_entry)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(self._format_log("DEBUG", message, **kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(self._format_log("INFO", message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(self._format_log("WARNING", message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(self._format_log("ERROR", message, **kwargs))
    
    def stage_start(self, stage: str, input_data: Any = None):
        """Log the start of an agent stage."""
        self.info(
            f"Starting stage: {stage}",
            stage=stage,
            event="stage_start",
            input_size=len(str(input_data)) if input_data else 0
        )
    
    def stage_complete(self, stage: str, output_data: Any = None, duration: float = 0):
        """Log the completion of an agent stage."""
        self.info(
            f"Completed stage: {stage}",
            stage=stage,
            event="stage_complete",
            output_size=len(str(output_data)) if output_data else 0,
            duration_seconds=duration
        )
    
    def stage_error(self, stage: str, error: Exception):
        """Log an error during a stage."""
        self.error(
            f"Error in stage: {stage}",
            stage=stage,
            event="stage_error",
            error_type=type(error).__name__,
            error_message=str(error)
        )


def get_logger(agent_name: str, workflow_id: Optional[str] = None) -> TeamAgentLogger:
    """
    Get or create a logger for an agent.
    
    Args:
        agent_name: Name of the agent
        workflow_id: Optional workflow ID
        
    Returns:
        TeamAgentLogger instance
    """
    return TeamAgentLogger(agent_name, workflow_id)