"""
Logs Service - Read and format Turing Tape entries as syslog-level logs.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class LogsService:
    """
    Service for reading workflow tape logs and formatting them with syslog levels.
    """

    # Syslog level mapping
    SYSLOG_LEVELS = {
        'DEBUG': 7,      # debug-level messages
        'INFO': 6,       # informational messages
        'NOTICE': 5,     # normal but significant condition
        'WARNING': 4,    # warning conditions
        'ERROR': 3,      # error conditions
        'CRITICAL': 2,   # critical conditions
        'ALERT': 1,      # action must be taken immediately
        'EMERGENCY': 0   # system is unusable
    }

    def __init__(self, tape_dir: str = None):
        """Initialize logs service."""
        if tape_dir is None:
            # Default to project tapes directory
            tape_dir = str(Path.home() / "Dropbox/Team Agent/Projects/ta_base/swarm2/team-agent/data/tapes")
        self.tape_dir = Path(tape_dir)

    def get_all_logs(self, level: str = 'INFO', limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all workflow tape logs formatted as syslog entries.

        Args:
            level: Minimum syslog level to include (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            limit: Maximum number of log entries to return

        Returns:
            List of log entries sorted by timestamp (newest first)
        """
        min_level = self.SYSLOG_LEVELS.get(level.upper(), 6)  # Default to INFO
        all_logs = []

        # Read all tape files
        if not self.tape_dir.exists():
            return []

        for tape_file in sorted(self.tape_dir.glob("*.json"), reverse=True):
            try:
                with open(tape_file, 'r') as f:
                    tape_data = json.load(f)

                # Convert tape to log entries
                logs = self._tape_to_logs(tape_data)

                # Filter by level
                logs = [log for log in logs if log['level_num'] <= min_level]
                all_logs.extend(logs)

                # Stop if we've hit the limit
                if len(all_logs) >= limit:
                    all_logs = all_logs[:limit]
                    break

            except Exception as e:
                print(f"Error reading tape {tape_file}: {e}")
                continue

        # Sort by timestamp (newest first), handle None timestamps
        all_logs.sort(key=lambda x: x['timestamp'] or '', reverse=True)

        return all_logs[:limit]

    def get_workflow_logs(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get logs for a specific workflow.

        Args:
            workflow_id: Workflow ID to get logs for

        Returns:
            List of log entries for the workflow
        """
        tape_file = self.tape_dir / f"{workflow_id}.json"

        if not tape_file.exists():
            return []

        try:
            with open(tape_file, 'r') as f:
                tape_data = json.load(f)

            return self._tape_to_logs(tape_data)
        except Exception as e:
            print(f"Error reading workflow tape {workflow_id}: {e}")
            return []

    def _tape_to_logs(self, tape_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert a workflow tape to syslog-formatted log entries.

        Args:
            tape_data: Workflow tape data

        Returns:
            List of log entries
        """
        logs = []
        workflow_id = tape_data.get('workflow_id', 'unknown')
        mission = tape_data.get('mission', 'unknown')

        # Add workflow start log
        logs.append({
            'timestamp': tape_data.get('created_at'),
            'level': 'INFO',
            'level_num': self.SYSLOG_LEVELS['INFO'],
            'workflow_id': workflow_id,
            'stage': 'workflow',
            'message': f"Workflow started: {mission}",
            'metadata': {
                'team_id': tape_data.get('team_id'),
                'mission': mission
            }
        })

        # Add stage logs
        stages = tape_data.get('stages', {})
        for stage_name, stage_data in stages.items():
            stage_logs = self._stage_to_logs(workflow_id, stage_name, stage_data)
            logs.extend(stage_logs)

        # Add workflow completion log
        final_status = tape_data.get('status', 'unknown')
        if final_status == 'completed':
            logs.append({
                'timestamp': tape_data.get('updated_at'),
                'level': 'INFO',
                'level_num': self.SYSLOG_LEVELS['INFO'],
                'workflow_id': workflow_id,
                'stage': 'workflow',
                'message': f"Workflow completed successfully",
                'metadata': {
                    'status': final_status
                }
            })
        elif final_status == 'failed':
            logs.append({
                'timestamp': tape_data.get('updated_at'),
                'level': 'ERROR',
                'level_num': self.SYSLOG_LEVELS['ERROR'],
                'workflow_id': workflow_id,
                'stage': 'workflow',
                'message': f"Workflow failed",
                'metadata': {
                    'status': final_status
                }
            })

        return logs

    def _stage_to_logs(self, workflow_id: str, stage_name: str, stage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert a stage checkpoint to log entries.

        Args:
            workflow_id: Workflow ID
            stage_name: Stage name
            stage_data: Stage checkpoint data

        Returns:
            List of log entries for the stage
        """
        logs = []
        status = stage_data.get('status', 'unknown')

        # Stage start log
        if stage_data.get('started_at'):
            logs.append({
                'timestamp': stage_data.get('started_at'),
                'level': 'DEBUG',
                'level_num': self.SYSLOG_LEVELS['DEBUG'],
                'workflow_id': workflow_id,
                'stage': stage_name,
                'message': f"Stage '{stage_name}' started",
                'metadata': {
                    'status': 'in_progress',
                    'input_keys': list(stage_data.get('input_data', {}).keys()) if isinstance(stage_data.get('input_data'), dict) else None
                }
            })

        # Stage completion/failure log
        if stage_data.get('completed_at'):
            if status == 'completed':
                level = 'INFO'
                message = f"Stage '{stage_name}' completed successfully"

                # Check for warnings in output
                output_data = stage_data.get('output_data', {})
                if isinstance(output_data, dict):
                    # Check for risks or warnings
                    risks = output_data.get('risks', [])
                    if risks:
                        level = 'WARNING'
                        message = f"Stage '{stage_name}' completed with {len(risks)} risk(s)"

                logs.append({
                    'timestamp': stage_data.get('completed_at'),
                    'level': level,
                    'level_num': self.SYSLOG_LEVELS[level],
                    'workflow_id': workflow_id,
                    'stage': stage_name,
                    'message': message,
                    'metadata': {
                        'status': status,
                        'duration_seconds': stage_data.get('duration_seconds'),
                        'output_keys': list(output_data.keys()) if isinstance(output_data, dict) else None
                    }
                })

            elif status == 'failed':
                error_msg = stage_data.get('error', 'Unknown error')
                logs.append({
                    'timestamp': stage_data.get('completed_at'),
                    'level': 'ERROR',
                    'level_num': self.SYSLOG_LEVELS['ERROR'],
                    'workflow_id': workflow_id,
                    'stage': stage_name,
                    'message': f"Stage '{stage_name}' failed: {error_msg}",
                    'metadata': {
                        'status': status,
                        'error': error_msg
                    }
                })

        return logs


# Singleton instance
logs_service = LogsService()
