"""
Workflow Orchestrator - Manages execution of the five-agent workflow.
Uses the Turing Tape for checkpoint/resume capability.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow.tape import WorkflowTape, StageStatus
from swarms.team_agent.roles_v2 import Architect, Builder, Critic, Governance, Recorder
from utils.logging import get_logger


class WorkflowOrchestrator:
    """
    Orchestrates the five-agent workflow with checkpoint/resume capability.
    """
    
    STAGE_ORDER = ["architect", "builder", "critic", "governance", "recorder"]
    
    def __init__(self, team_id: str = "default_team"):
        """Initialize orchestrator."""
        self.team_id = team_id
        self.logger = get_logger("orchestrator")
    
    def execute_workflow(self, mission: str, resume_workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a complete workflow or resume an existing one.
        
        Args:
            mission: The user's request/mission
            resume_workflow_id: Optional workflow ID to resume
            
        Returns:
            Complete workflow results
        """
        # Load or create tape
        if resume_workflow_id:
            tape = WorkflowTape.load(resume_workflow_id)
            if not tape:
                raise ValueError(f"Workflow {resume_workflow_id} not found")
            self.logger.info(f"Resuming workflow {resume_workflow_id}")
        else:
            tape = WorkflowTape.create_new(mission, self.team_id, self.STAGE_ORDER)
            self.logger.info(f"Created new workflow {tape.workflow_id}")
        
        # Initialize agents
        agents = {
            "architect": Architect(tape.workflow_id),
            "builder": Builder(tape.workflow_id),
            "critic": Critic(tape.workflow_id),
            "governance": Governance(tape.workflow_id),
            "recorder": Recorder(tape.workflow_id)
        }
        
        # Execute workflow
        results = {}
        current_input = mission
        
        for stage_name in self.STAGE_ORDER:
            # Skip if already completed
            if tape.stages[stage_name].status == StageStatus.COMPLETED:
                self.logger.info(f"Stage {stage_name} already completed, skipping")
                current_input = tape.stages[stage_name].output_data
                results[stage_name] = current_input
                continue
            
            # Execute stage
            try:
                self.logger.info(f"Executing stage: {stage_name}")
                tape.start_stage(stage_name, current_input)
                
                agent = agents[stage_name]
                
                # Special handling for Recorder - give it full workflow context
                if stage_name == "recorder":
                    workflow_data = {
                        "mission": mission,
                        "architect": results.get("architect", {}),
                        "builder": results.get("builder", {}),
                        "critic": results.get("critic", {}),
                        "governance": results.get("governance", {})
                    }
                    output = agent.run(workflow_data)
                else:
                    output = agent.run(current_input)
                
                tape.complete_stage(stage_name, output)
                results[stage_name] = output
                current_input = output
                
                self.logger.info(f"Completed stage: {stage_name}")
                
            except Exception as e:
                self.logger.error(f"Stage {stage_name} failed: {e}")
                tape.fail_stage(stage_name, str(e))
                raise
        
        # Mark workflow as complete
        tape.status = "completed"
        tape.save()
        
        # Return complete results
        return {
            "workflow_id": tape.workflow_id,
            "mission": mission,
            "results": results,
            "final_record": results.get("recorder", {}),
            "progress": tape.get_progress()
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow."""
        tape = WorkflowTape.load(workflow_id)
        if not tape:
            return None
        
        return {
            "workflow_id": tape.workflow_id,
            "mission": tape.mission,
            "status": tape.status,
            "current_stage": tape.current_stage,
            "progress": tape.get_progress(),
            "stages": {k: v.to_dict() for k, v in tape.stages.items()}
        }