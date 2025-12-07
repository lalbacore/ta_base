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
            'status': 'pending',
            'submitted_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            **mission_data
        }

        # Execute mission in background thread
        def execute_mission():
            try:
                # Update status to running
                self.missions[mission_id]['status'] = 'running'
                self.missions[mission_id]['updated_at'] = datetime.now().isoformat()
                self.missions[mission_id]['started_at'] = datetime.now().isoformat()

                # Execute the mission
                results = self.orchestrator.execute(description)
                workflow_id = results.get('workflow_id')

                # Store workflow info
                self.active_workflows[workflow_id] = {
                    'workflow_id': workflow_id,
                    'mission_id': mission_id,
                    'status': 'completed',
                    'created_at': datetime.now().isoformat(),
                    'completed_at': datetime.now().isoformat()
                }

                # Update mission with workflow info
                self.missions[mission_id]['workflow_id'] = workflow_id
                self.missions[mission_id]['status'] = 'completed'
                self.missions[mission_id]['updated_at'] = datetime.now().isoformat()
                self.missions[mission_id]['completed_at'] = datetime.now().isoformat()

            except Exception as e:
                self.missions[mission_id]['status'] = 'failed'
                self.missions[mission_id]['error'] = str(e)
                self.missions[mission_id]['updated_at'] = datetime.now().isoformat()
                self.missions[mission_id]['failed_at'] = datetime.now().isoformat()

        thread = threading.Thread(target=execute_mission, daemon=True)
        thread.start()

        return {'mission_id': mission_id, 'status': 'pending'}

    def list_missions(self) -> List[Dict[str, Any]]:
        """List all missions."""
        return list(self.missions.values())

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission details."""
        return self.missions.get(mission_id)

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow status and progress by reading from filesystem and mission state.

        Args:
            workflow_id: Workflow identifier or mission identifier

        Returns:
            Workflow status dict or None
        """
        mission_id = workflow_id
        mission = None
        actual_workflow_id = workflow_id

        # If this is a mission_id, look up the associated workflow_id
        if workflow_id.startswith('mission_'):
            mission = self.missions.get(workflow_id)
            if not mission:
                return None

            mission_id = workflow_id
            # Check if workflow_id has been created yet
            if 'workflow_id' in mission:
                actual_workflow_id = mission['workflow_id']
        else:
            # This is a workflow_id, try to find the mission
            for mid, m in self.missions.items():
                if m.get('workflow_id') == workflow_id:
                    mission = m
                    mission_id = mid
                    break

        # Get mission status if available
        mission_status = mission.get('status', 'unknown') if mission else 'unknown'

        # If mission is still pending or running without a workflow_id yet
        if mission and mission_status in ['pending', 'running'] and 'workflow_id' not in mission:
            progress = 0
            current_stage = 'initializing'

            # If running, estimate progress
            if mission_status == 'running':
                # Check how long it's been running (rough estimate)
                started_at = mission.get('started_at')
                if started_at:
                    elapsed = (datetime.now() - datetime.fromisoformat(started_at)).total_seconds()
                    # Rough estimate: 30 seconds = 25% progress
                    progress = min(int((elapsed / 30) * 25), 25)
                current_stage = 'executing'

            return {
                'workflow_id': mission_id,
                'mission_id': mission_id,
                'status': mission_status,
                'progress': progress,
                'current_stage': current_stage,
                'artifacts_count': 0,
                'created_at': mission.get('submitted_at', datetime.now().isoformat()),
                'updated_at': mission.get('updated_at', datetime.now().isoformat()),
                'started_at': mission.get('started_at'),
                'stages': []
            }

        # If mission failed before creating workflow
        if mission and mission_status == 'failed':
            return {
                'workflow_id': mission_id,
                'mission_id': mission_id,
                'status': 'failed',
                'progress': 0,
                'current_stage': 'failed',
                'artifacts_count': 0,
                'error': mission.get('error'),
                'created_at': mission.get('submitted_at', datetime.now().isoformat()),
                'updated_at': mission.get('updated_at', datetime.now().isoformat()),
                'failed_at': mission.get('failed_at'),
                'stages': []
            }

        # Check filesystem for completed workflow
        workflow_dir = Path(self.orchestrator.output_dir) / actual_workflow_id

        if not workflow_dir.exists():
            # Workflow ID exists but no output directory yet
            if mission:
                return {
                    'workflow_id': actual_workflow_id,
                    'mission_id': mission_id,
                    'status': mission_status,
                    'progress': 50,
                    'current_stage': 'processing',
                    'artifacts_count': 0,
                    'created_at': mission.get('submitted_at', datetime.now().isoformat()),
                    'updated_at': mission.get('updated_at', datetime.now().isoformat()),
                    'stages': []
                }
            return None

        # Count artifacts
        artifacts = list(workflow_dir.glob('*.py'))

        # Read stages from turing tape, or fallback to workflow record
        stages = self._read_workflow_stages(actual_workflow_id)
        if not stages:
            stages = self._generate_stages_from_record(workflow_dir)

        return {
            'workflow_id': actual_workflow_id,
            'mission_id': mission_id if mission else actual_workflow_id,
            'status': mission_status if mission else 'completed',
            'progress': 100,
            'current_stage': 'completed',
            'artifacts_count': len(artifacts),
            'output_dir': str(workflow_dir),
            'created_at': mission.get('submitted_at') if mission else datetime.fromtimestamp(workflow_dir.stat().st_ctime).isoformat(),
            'updated_at': mission.get('updated_at') if mission else datetime.now().isoformat(),
            'completed_at': mission.get('completed_at') if mission else datetime.fromtimestamp(workflow_dir.stat().st_mtime).isoformat(),
            'stages': stages
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

    def get_governance_stats(self) -> Dict[str, Any]:
        """
        Get statistics on governance decisions (AI vs HITL).
        
        Returns:
            Dict with counts for ai_approved, human_approved, rejected, etc.
        """
        from app.database import get_backend_session
        from app.models.governance import GovernanceDecision
        
        stats = {
            'total_decisions': 0,
            'ai_approved': 0,
            'human_approved': 0,
            'rejected': 0,
            'autonomy_ratio': 0.0
        }
        
        try:
            with get_backend_session() as session:
                decisions = session.query(GovernanceDecision).all()
                stats['total_decisions'] = len(decisions)
                
                for d in decisions:
                    if d.decision == 'rejected':
                        stats['rejected'] += 1
                    elif 'Auto-approved' in (d.reason or ''):
                        stats['ai_approved'] += 1
                    elif 'Human' in (d.reason or ''):
                        stats['human_approved'] += 1
                    else:
                        # Fallback for legacy data
                        stats['ai_approved'] += 1

                total_approved = stats['ai_approved'] + stats['human_approved']
                if total_approved > 0:
                    stats['autonomy_ratio'] = stats['ai_approved'] / total_approved
                    
        except Exception as e:
            print(f"Error calculating governance stats: {e}")
            
        return stats

    def _read_workflow_stages(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Read workflow stages from turing tape.

        Args:
            workflow_id: Workflow identifier

        Returns:
            List of stage dictionaries
        """
        # Tape is in project directory, not home directory
        project_root = Path(__file__).parent.parent.parent
        tape_path = project_root / ".team_agent" / "tape" / f"{workflow_id}.jsonl"

        if not tape_path.exists():
            return []

        stages = []
        agent_entries = {}  # Group entries by agent

        try:
            with open(tape_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue

                    entry = json.loads(line)
                    agent = entry.get('agent', 'unknown')

                    if agent not in agent_entries:
                        agent_entries[agent] = []

                    agent_entries[agent].append(entry)

            # Convert agent entries to stages
            stage_order = ['orchestrator', 'architect', 'builder', 'critic', 'recorder']

            for agent in stage_order:
                if agent not in agent_entries:
                    continue

                entries = agent_entries[agent]
                if not entries:
                    continue

                # Get first and last entry for timing
                first_entry = entries[0]
                last_entry = entries[-1]

                # Determine status
                status = 'completed'
                output = {}

                # Try to extract meaningful output
                if 'state' in last_entry:
                    state = last_entry['state']
                    if isinstance(state, dict):
                        # Extract key information based on agent type
                        if agent == 'architect' and 'architecture' in state:
                            output = {'architecture': state['architecture']}
                        elif agent == 'builder' and 'artifacts' in state:
                            output = {'artifacts_count': len(state.get('artifacts', []))}
                        elif agent == 'critic' and 'review' in state:
                            output = {'score': state.get('review', {}).get('score')}
                        elif agent == 'recorder' and 'published' in state:
                            output = {'published': state['published']}
                        else:
                            output = {'completed': True}

                stages.append({
                    'stage_name': agent,
                    'status': status,
                    'started_at': first_entry.get('ts', datetime.now().isoformat()),
                    'completed_at': last_entry.get('ts', datetime.now().isoformat()),
                    'output': output
                })

        except Exception as e:
            print(f"Error reading turing tape for {workflow_id}: {e}")
            return []

        return stages

    def _generate_stages_from_record(self, workflow_dir: Path) -> List[Dict[str, Any]]:
        """
        Generate workflow stages from workflow record when turing tape doesn't exist.

        Args:
            workflow_dir: Path to workflow output directory

        Returns:
            List of stage dictionaries
        """
        stages = []

        # Find workflow record file
        record_files = list(workflow_dir.glob('*_record.json'))
        if not record_files:
            # No record file - generate basic stages from directory existence
            # If the workflow directory exists and has files, assume all phases completed
            files = list(workflow_dir.glob('*.py'))
            if files:
                # Use the earliest file timestamp as start time
                earliest_file = min(files, key=lambda f: f.stat().st_ctime)
                base_time = datetime.fromtimestamp(earliest_file.stat().st_ctime)

                # Generate basic stages for completed workflow
                stage_names = ['orchestrator', 'architect', 'builder', 'critic', 'recorder']
                for i, stage_name in enumerate(stage_names):
                    stages.append({
                        'stage_name': stage_name,
                        'status': 'completed',
                        'started_at': base_time.isoformat(),
                        'completed_at': base_time.isoformat(),
                        'output': {'completed': True}
                    })

                return stages
            return []

        try:
            with open(record_files[0], 'r') as f:
                record = json.load(f)

            # Use file modification time as fallback for timing
            record_mtime = datetime.fromtimestamp(record_files[0].stat().st_mtime)
            base_time = record_mtime

            # Generate orchestrator stage (always happens first)
            stages.append({
                'stage_name': 'orchestrator',
                'status': 'completed',
                'started_at': base_time.isoformat(),
                'completed_at': base_time.isoformat(),
                'output': {'mission': record.get('mission', '')}
            })

            # Generate architect stage if architecture exists
            if 'architecture' in record and record['architecture']:
                stages.append({
                    'stage_name': 'architect',
                    'status': 'completed',
                    'started_at': base_time.isoformat(),
                    'completed_at': base_time.isoformat(),
                    'output': {'architecture': record['architecture']}
                })

            # Generate builder stage if implementation exists
            if 'implementation' in record and record['implementation']:
                impl = record['implementation']
                output = {}
                if 'artifacts' in impl:
                    output['artifacts_count'] = len(impl['artifacts'])
                if 'capability_used' in impl:
                    output['capability_used'] = impl['capability_used']

                stages.append({
                    'stage_name': 'builder',
                    'status': 'completed',
                    'started_at': base_time.isoformat(),
                    'completed_at': base_time.isoformat(),
                    'output': output
                })

            # Generate critic stage if review exists
            if 'review' in record and record['review']:
                review = record['review']
                output = {}
                if 'score' in review:
                    output['score'] = review['score']
                if 'issues' in review:
                    output['issues_count'] = len(review['issues'])

                stages.append({
                    'stage_name': 'critic',
                    'status': 'completed',
                    'started_at': base_time.isoformat(),
                    'completed_at': base_time.isoformat(),
                    'output': output
                })

            # Generate recorder stage if artifacts exist
            if 'artifacts' in record and record['artifacts']:
                stages.append({
                    'stage_name': 'recorder',
                    'status': 'completed',
                    'started_at': base_time.isoformat(),
                    'completed_at': record.get('timestamp', base_time.isoformat()),
                    'output': {'published': True, 'artifacts': record['artifacts']}
                })

        except Exception as e:
            print(f"Error generating stages from record: {e}")
            return []

        return stages

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
