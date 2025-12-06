"""
Mission Service - Bridges Flask API to Team Agent orchestrator.
"""
import sys
import os
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from swarms.team_agent.orchestrator import Orchestrator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MissionService:
    """
    Service layer for mission management.
    Bridges Flask API to Orchestrator.
    """

    def __init__(self):
        # Initialize orchestrator
        self.orchestrator = Orchestrator(
            output_dir=os.path.expanduser("~/Dropbox/Team Agent/Projects/ta_base/swarm2/team-agent/team_output")
        )

        # Track missions in memory (could be moved to database)
        self.missions: Dict[str, Dict[str, Any]] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

        # Load seed data on initialization
        self._load_seed_missions()

    def submit_mission(self, mission_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Submit a new mission for execution.

        Args:
            mission_data: Mission specification with 'description' field

        Returns:
            Dictionary with mission_id and workflow_id
        """
        description = mission_data.get('description', '')
        mission_id = f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Store mission
        self.missions[mission_id] = {
            'mission_id': mission_id,
            'description': description,
            'status': 'submitted',
            'submitted_at': datetime.now().isoformat(),
            **mission_data
        }

        # Execute mission in background thread
        def execute_mission():
            try:
                self.missions[mission_id]['status'] = 'running'
                results = self.orchestrator.execute(description)
                workflow_id = results.get('workflow_id')

                # Store workflow info
                self.active_workflows[workflow_id] = {
                    'workflow_id': workflow_id,
                    'mission_id': mission_id,
                    'status': 'completed',
                    'completed_at': datetime.now().isoformat()
                }

                self.missions[mission_id]['workflow_id'] = workflow_id
                self.missions[mission_id]['status'] = 'completed'
            except Exception as e:
                self.missions[mission_id]['status'] = 'failed'
                self.missions[mission_id]['error'] = str(e)

        thread = threading.Thread(target=execute_mission, daemon=True)
        thread.start()

        return {'mission_id': mission_id, 'status': 'submitted'}

    def list_missions(self) -> List[Dict[str, Any]]:
        """List all missions."""
        return list(self.missions.values())

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission details."""
        return self.missions.get(mission_id)

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow status and progress by reading from filesystem.

        Args:
            workflow_id: Workflow identifier or mission identifier

        Returns:
            Workflow status dict or None
        """
        # If this is a mission_id, look up the associated workflow_id
        if workflow_id.startswith('mission_'):
            mission = self.missions.get(workflow_id)
            if not mission:
                return None

            # Check if workflow_id has been created yet
            if 'workflow_id' in mission:
                workflow_id = mission['workflow_id']
            else:
                # Mission is still running, return pending status
                return {
                    'workflow_id': workflow_id,
                    'mission_id': workflow_id,
                    'status': mission.get('status', 'pending'),
                    'progress': 0,
                    'current_stage': 'initializing',
                    'artifacts_count': 0,
                    'created_at': mission.get('submitted_at', datetime.now().isoformat())
                }

        workflow_dir = Path(self.orchestrator.output_dir) / workflow_id

        if not workflow_dir.exists():
            return None

        # Count artifacts
        artifacts = list(workflow_dir.glob('*.py'))

        return {
            'workflow_id': workflow_id,
            'status': 'completed',
            'progress': 100,
            'current_stage': 'completed',
            'artifacts_count': len(artifacts),
            'output_dir': str(workflow_dir),
            'created_at': datetime.fromtimestamp(workflow_dir.stat().st_ctime).isoformat()
        }

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows by scanning output directory."""
        workflows = []
        output_dir = Path(self.orchestrator.output_dir)

        if not output_dir.exists():
            return workflows

        # Scan for workflow directories
        for workflow_dir in output_dir.iterdir():
            if workflow_dir.is_dir() and workflow_dir.name.startswith('wf_'):
                workflow_id = workflow_dir.name

                # Count artifacts
                artifacts = list(workflow_dir.glob('*.py'))

                workflows.append({
                    'workflow_id': workflow_id,
                    'status': 'completed',
                    'artifacts_count': len(artifacts),
                    'output_dir': str(workflow_dir),
                    'created_at': datetime.fromtimestamp(workflow_dir.stat().st_ctime).isoformat()
                })

        # Sort by creation time (newest first)
        workflows.sort(key=lambda w: w['created_at'], reverse=True)

        return workflows

    def resume_workflow(self, workflow_id: str) -> None:
        """Resume a paused workflow."""
        # Not implemented yet - would require workflow tape support
        pass

    def approve_breakpoint(self, breakpoint_id: str, option_index: int) -> None:
        """Approve a breakpoint with selected capability."""
        # Not implemented yet - would require breakpoint support
        pass

    def reject_breakpoint(self, breakpoint_id: str) -> None:
        """Reject a breakpoint."""
        # Not implemented yet - would require breakpoint support
        pass

    def list_breakpoints(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all breakpoints, optionally filtered by workflow_id."""
        # Not implemented yet - would require breakpoint support
        return []

    def get_breakpoint(self, breakpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get breakpoint details."""
        # Not implemented yet - would require breakpoint support
        return None

    def _load_seed_missions(self):
        """Load sample missions from seed data for demo purposes."""
        try:
            from app.data.seed_data import SAMPLE_MISSIONS, SAMPLE_WORKFLOWS

            # Load sample missions
            for mission_data in SAMPLE_MISSIONS:
                self.missions[mission_data['mission_id']] = mission_data

            # Load sample workflows (simulating completed missions)
            for workflow_data in SAMPLE_WORKFLOWS:
                workflow_id = workflow_data['workflow_id']
                mission_id = workflow_data['mission_id']

                # Link workflow to mission
                if mission_id in self.missions:
                    self.missions[mission_id]['workflow_id'] = workflow_id
                    self.missions[mission_id]['status'] = workflow_data['status']

                # Store workflow info
                self.active_workflows[workflow_id] = workflow_data

            print(f"✅ Loaded {len(self.missions)} sample missions and {len(self.active_workflows)} workflows")
        except ImportError:
            print("⚠️  Could not load seed data - seed_data.py not found")
        except Exception as e:
            print(f"⚠️  Error loading seed missions: {e}")


# Singleton instance
mission_service = MissionService()
