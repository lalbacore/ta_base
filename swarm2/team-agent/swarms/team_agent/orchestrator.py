"""
Orchestrator - Coordinates the multi-agent workflow.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logging import get_logger
from swarms.team_agent.roles import (
    Architect,
    Builder,
    Critic,
    Governance,
    Recorder,
)


class Orchestrator:
    """
    Orchestrator coordinates the entire workflow through multiple agents.
    """
    
    def __init__(self, workflow_id: Optional[str] = None, output_dir: str = "output"):
        """Initialize orchestrator with workflow ID and output directory."""
        self.workflow_id = workflow_id or self._generate_workflow_id()
        self.output_dir = output_dir
        self.logger = get_logger("orchestrator")
        
        # Initialize agents
        self.architect = Architect(self.workflow_id)
        self.builder = Builder(self.workflow_id)
        self.critic = Critic(self.workflow_id)
        self.governance = Governance(self.workflow_id)
        self.recorder = Recorder(self.workflow_id, output_dir)
        
        self.logger.info(f"Created new workflow {self.workflow_id}")
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"wf_{timestamp}"
    
    def execute(self, mission: str, instructions: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute the complete workflow.
        
        Args:
            mission: The user's mission/request
            instructions: Optional stage-specific instructions
            
        Returns:
            Complete workflow results including all stage outputs
        """
        instructions = instructions or {}
        
        # Track all outputs
        all_outputs = {}
        
        # Stage 1: Architect
        self.logger.info("Executing stage: architect")
        architecture = self.architect.run({
            'input': mission,
            'instructions': instructions.get('architect', {})
        })
        all_outputs['architecture'] = architecture
        self.logger.info("Completed stage: architect")
        
        # Stage 2: Builder
        self.logger.info("Executing stage: builder")
        implementation = self.builder.run({
            'input': architecture,
            'instructions': instructions.get('builder', {})
        })
        all_outputs['implementation'] = implementation
        self.logger.info("Completed stage: builder")
        
        # Stage 3: Critic
        self.logger.info("Executing stage: critic")
        review = self.critic.run({
            'input': implementation,
            'instructions': instructions.get('critic', {})
        })
        all_outputs['review'] = review
        self.logger.info("Completed stage: critic")
        
        # Stage 4: Governance
        self.logger.info("Executing stage: governance")
        decision = self.governance.run({
            'input': review,
            'instructions': instructions.get('governance', {})
        })
        all_outputs['decision'] = decision
        self.logger.info("Completed stage: governance")
        
        # Stage 5: Recorder
        self.logger.info("Executing stage: recorder")
        final_record = self.recorder.run({
            'input': {
                'architecture': architecture,
                'implementation': implementation,
                'review': review,
                'decision': decision
            },
            'instructions': instructions.get('recorder', {})
        })
        self.logger.info("Completed stage: recorder")
        
        return {
            'workflow_id': self.workflow_id,
            'mission': mission,
            'stages': all_outputs,
            'final_record': final_record
        }
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current workflow progress."""
        return {
            'workflow_id': self.workflow_id,
            'status': 'running',
            'stages_completed': 0,
            'total_stages': 5
        }