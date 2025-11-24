"""
Workflow Orchestrator - Manages execution of the five-agent workflow.
Uses the Turing Tape for checkpoint/resume capability.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union

sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow.tape import WorkflowTape, StageStatus
from swarms.team_agent.roles_v2 import Architect, Builder, Critic, Governance, Recorder
from utils.logging import get_logger


class Mission:
    """
    Mission definition - can be loaded from YAML or created programmatically.
    This will eventually be created by UI/form builder.
    """
    
    def __init__(self, mission_data: Dict[str, Any]):
        """Initialize from dictionary (loaded from YAML or API)."""
        self.data = mission_data
        self.mission_info = mission_data.get('mission', {})
        
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Mission':
        """Load mission from YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(data)
    
    @classmethod
    def from_simple_request(cls, request: str, user_id: str = "unknown") -> 'Mission':
        """Create a simple mission from a text request."""
        import datetime
        
        data = {
            'mission': {
                'id': f"mission_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'name': request[:50],
                'description': request,
                'created_at': datetime.datetime.utcnow().isoformat() + "Z",
                'created_by': user_id,
                'requirements': [request],
                'acceptance_criteria': {
                    'quality_score': ">= 70",
                    'compliance_score': ">= 80"
                },
                'stages': {
                    'architect': {'instructions': []},
                    'builder': {'instructions': []},
                    'critic': {'focus_areas': ['code_quality', 'security']},
                    'governance': {'policies': ['code_quality'], 'auto_approve': False}
                },
                'output': {'type': 'file'},
                'team': {'id': 'default_team', 'name': 'Default Team'}
            }
        }
        return cls(data)
    
    def get_stage_instructions(self, stage_name: str) -> Dict[str, Any]:
        """Get instructions for a specific stage."""
        return self.mission_info.get('stages', {}).get(stage_name, {})
    
    def get_acceptance_criteria(self) -> Dict[str, Any]:
        """Get acceptance criteria."""
        return self.mission_info.get('acceptance_criteria', {})
    
    def get_description(self) -> str:
        """Get mission description."""
        return self.mission_info.get('description', '')
    
    def get_requirements(self) -> list:
        """Get mission requirements."""
        return self.mission_info.get('requirements', [])


class WorkflowOrchestrator:
    """
    Orchestrates the five-agent workflow with checkpoint/resume capability.
    Now supports Mission files with stage-specific instructions.
    """
    
    STAGE_ORDER = ["architect", "builder", "critic", "governance", "recorder"]
    
    def __init__(self, team_id: str = "default_team"):
        """Initialize orchestrator."""
        self.team_id = team_id
        self.logger = get_logger("orchestrator")
    
    def execute_mission(self, 
                       mission: Union[str, Mission, Path],
                       resume_workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a mission (from YAML, Mission object, or simple string).
        
        Args:
            mission: Mission YAML path, Mission object, or simple string request
            resume_workflow_id: Optional workflow ID to resume
            
        Returns:
            Complete workflow results
        """
        # Parse mission
        if isinstance(mission, str):
            if Path(mission).exists() and mission.endswith('.yaml'):
                mission_obj = Mission.from_yaml(mission)
            else:
                # Simple text request
                mission_obj = Mission.from_simple_request(mission)
        elif isinstance(mission, Path):
            mission_obj = Mission.from_yaml(str(mission))
        else:
            mission_obj = mission
        
        # Execute workflow with mission context
        return self.execute_workflow(
            mission_obj.get_description(),
            mission_obj,
            resume_workflow_id
        )
    
    def execute_workflow(self, 
                        mission_text: str,
                        mission_obj: Optional[Mission] = None,
                        resume_workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a complete workflow or resume an existing one.
        
        Args:
            mission_text: The user's request/mission text
            mission_obj: Optional Mission object with stage instructions
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
            tape = WorkflowTape.create_new(mission_text, self.team_id, self.STAGE_ORDER)
            self.logger.info(f"Created new workflow {tape.workflow_id}")
            
            # Store mission metadata in tape
            if mission_obj:
                tape.metadata['mission'] = mission_obj.data
                tape.save()
        
        # Initialize agents with mission context
        agents = {
            "architect": Architect(tape.workflow_id),
            "builder": Builder(tape.workflow_id),
            "critic": Critic(tape.workflow_id),
            "governance": Governance(tape.workflow_id),
            "recorder": Recorder(tape.workflow_id)
        }
        
        # Execute workflow
        results = {}
        current_input = mission_text
        
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
                
                # Enhance input with stage-specific instructions from mission
                stage_input = current_input
                if mission_obj:
                    stage_instructions = mission_obj.get_stage_instructions(stage_name)
                    if stage_instructions:
                        # Wrap input with instructions
                        stage_input = {
                            "input": current_input,
                            "instructions": stage_instructions,
                            "requirements": mission_obj.get_requirements()
                        }
                
                tape.start_stage(stage_name, stage_input)
                
                agent = agents[stage_name]
                
                # Special handling for Recorder - give it full workflow context
                if stage_name == "recorder":
                    workflow_data = {
                        "mission": mission_text,
                        "architect": results.get("architect", {}),
                        "builder": results.get("builder", {}),
                        "critic": results.get("critic", {}),
                        "governance": results.get("governance", {})
                    }
                    output = agent.run(workflow_data)
                else:
                    output = agent.run(stage_input)
                
                tape.complete_stage(stage_name, output)
                results[stage_name] = output
                current_input = output
                
                self.logger.info(f"Completed stage: {stage_name}")
                
            except Exception as e:
                self.logger.error(f"Stage {stage_name} failed: {e}")
                tape.fail_stage(stage_name, str(e))
                raise
        
        # Check acceptance criteria if provided
        if mission_obj:
            acceptance_met = self._check_acceptance_criteria(
                results,
                mission_obj.get_acceptance_criteria()
            )
            tape.metadata['acceptance_met'] = acceptance_met
        
        # Mark workflow as complete
        tape.status = "completed"
        tape.save()
        
        # Return complete results
        return {
            "workflow_id": tape.workflow_id,
            "mission": mission_text,
            "results": results,
            "final_record": results.get("recorder", {}),
            "progress": tape.get_progress(),
            "acceptance_met": tape.metadata.get('acceptance_met', None)
        }
    
    def _check_acceptance_criteria(self, 
                                   results: Dict[str, Any],
                                   criteria: Dict[str, Any]) -> Dict[str, bool]:
        """Check if workflow results meet acceptance criteria."""
        checks = {}
        
        # Extract scores
        final_record = results.get('recorder', {})
        composite = final_record.get('composite_score', {})
        
        # Check quality score
        if 'quality_score' in criteria:
            threshold = int(criteria['quality_score'].replace('>=', '').strip())
            actual = composite.get('quality', 0)
            checks['quality_score'] = actual >= threshold
        
        # Check compliance score
        if 'compliance_score' in criteria:
            threshold = int(criteria['compliance_score'].replace('>=', '').strip())
            actual = composite.get('compliance', 0)
            checks['compliance_score'] = actual >= threshold
        
        # Future: Add test_coverage, security_scan, etc.
        
        return checks
    
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
            "stages": {k: v.to_dict() for k, v in tape.stages.items()},
            "acceptance_met": tape.metadata.get('acceptance_met')
        }