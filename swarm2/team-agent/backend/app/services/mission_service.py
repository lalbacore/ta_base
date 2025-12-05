"""
Mission Service - Bridges Flask API to Team Agent orchestrator.
"""
import sys
import os

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import Dict, Any, List, Optional
from app.data.seed_data import SAMPLE_MISSIONS, SAMPLE_WORKFLOWS, SAMPLE_BREAKPOINTS


class MissionService:
    """
    Service layer for mission management.
    Bridges Flask API to OrchestratorA2A.
    """

    def __init__(self):
        # TODO: Initialize orchestrator when ready
        # from swarms.team_agent.orchestrator_a2a import OrchestratorA2A
        # self.orchestrator = OrchestratorA2A(enable_a2a=True, enable_breakpoints=True)

        # Load seed data
        self.missions = {m['mission_id']: m for m in SAMPLE_MISSIONS}
        self.workflows = {w['workflow_id']: w for w in SAMPLE_WORKFLOWS}
        self.breakpoints = {bp['breakpoint_id']: bp for bp in SAMPLE_BREAKPOINTS}

    def submit_mission(self, mission_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Submit a new mission for execution.

        Args:
            mission_data: Mission specification

        Returns:
            Dictionary with mission_id
        """
        # TODO: Parse mission_data into MissionSpec and submit to orchestrator
        # mission_spec = self._parse_mission_spec(mission_data)
        # asyncio.create_task(self.orchestrator.execute_mission(mission_spec))

        mission_id = mission_data.get('mission_id', 'mock_mission_001')
        self.missions[mission_id] = mission_data
        return {'mission_id': mission_id}

    def list_missions(self) -> List[Dict[str, Any]]:
        """List all missions."""
        return list(self.missions.values())

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission details."""
        return self.missions.get(mission_id)

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow status and progress.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow status dict or None
        """
        # TODO: Load from WorkflowTape
        # from workflow.tape import WorkflowTape
        # tape = WorkflowTape.load(workflow_id)
        # return tape.to_dict() with progress calculation

        return self.workflows.get(workflow_id, {
            'workflow_id': workflow_id,
            'status': 'pending',
            'progress': 0,
            'current_stage': 'none',
            'stages': []
        })

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        return list(self.workflows.values())

    def resume_workflow(self, workflow_id: str) -> None:
        """Resume a paused workflow."""
        # TODO: Implement resume logic with WorkflowTape
        pass

    def approve_breakpoint(self, breakpoint_id: str, option_index: int) -> None:
        """Approve a breakpoint with selected capability."""
        # TODO: Implement breakpoint approval
        pass

    def reject_breakpoint(self, breakpoint_id: str) -> None:
        """Reject a breakpoint."""
        # TODO: Implement breakpoint rejection
        pass

    def list_breakpoints(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all breakpoints, optionally filtered by workflow_id."""
        if workflow_id:
            return [bp for bp in self.breakpoints.values() if bp['workflow_id'] == workflow_id]
        return list(self.breakpoints.values())

    def get_breakpoint(self, breakpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get breakpoint details."""
        return self.breakpoints.get(breakpoint_id)


# Singleton instance
mission_service = MissionService()
