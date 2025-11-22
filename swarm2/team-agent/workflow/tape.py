"""
Turing Tape - Workflow state machine with checkpoint/resume capability.
Manages mission progress and enables workflow continuation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class StageStatus(Enum):
    """Status of a workflow stage."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageCheckpoint:
    """Checkpoint for a single workflow stage."""
    stage_name: str
    status: StageStatus
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StageCheckpoint':
        """Create from dictionary."""
        data['status'] = StageStatus(data['status'])
        return cls(**data)


@dataclass
class WorkflowTape:
    """
    Turing Tape - Complete workflow state with mission and progress.
    Enables checkpoint/resume functionality.
    """
    workflow_id: str
    mission: str  # The user's request
    team_id: str
    created_at: str
    updated_at: str
    status: str  # overall, in_progress, completed, failed
    current_stage: Optional[str] = None
    stages: Dict[str, StageCheckpoint] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize stages if not provided."""
        if self.stages is None:
            self.stages = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "workflow_id": self.workflow_id,
            "mission": self.mission,
            "team_id": self.team_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "current_stage": self.current_stage,
            "stages": {k: v.to_dict() for k, v in self.stages.items()},
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowTape':
        """Create from dictionary."""
        stages = {
            k: StageCheckpoint.from_dict(v) 
            for k, v in data.get('stages', {}).items()
        }
        data['stages'] = stages
        return cls(**data)
    
    def save(self, tape_dir: str = "data/tapes"):
        """Save tape to disk."""
        tape_path = Path(tape_dir)
        tape_path.mkdir(parents=True, exist_ok=True)
        
        file_path = tape_path / f"{self.workflow_id}.json"
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, workflow_id: str, tape_dir: str = "data/tapes") -> Optional['WorkflowTape']:
        """Load tape from disk."""
        file_path = Path(tape_dir) / f"{workflow_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def create_new(cls, mission: str, team_id: str, stages: List[str]) -> 'WorkflowTape':
        """Create a new workflow tape."""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.utcnow().isoformat() + "Z"
        
        # Initialize all stages as pending
        stage_checkpoints = {
            stage: StageCheckpoint(
                stage_name=stage,
                status=StageStatus.PENDING
            )
            for stage in stages
        }
        
        return cls(
            workflow_id=workflow_id,
            mission=mission,
            team_id=team_id,
            created_at=now,
            updated_at=now,
            status="pending",
            current_stage=stages[0] if stages else None,
            stages=stage_checkpoints,
            metadata={}
        )
    
    def start_stage(self, stage_name: str, input_data: Any = None):
        """Mark a stage as started."""
        if stage_name not in self.stages:
            self.stages[stage_name] = StageCheckpoint(stage_name=stage_name, status=StageStatus.PENDING)
        
        self.stages[stage_name].status = StageStatus.IN_PROGRESS
        self.stages[stage_name].started_at = datetime.utcnow().isoformat() + "Z"
        self.stages[stage_name].input_data = input_data
        self.current_stage = stage_name
        self.updated_at = datetime.utcnow().isoformat() + "Z"
        self.save()
    
    def complete_stage(self, stage_name: str, output_data: Any = None):
        """Mark a stage as completed."""
        if stage_name in self.stages:
            checkpoint = self.stages[stage_name]
            checkpoint.status = StageStatus.COMPLETED
            checkpoint.completed_at = datetime.utcnow().isoformat() + "Z"
            checkpoint.output_data = output_data
            
            # Calculate duration
            if checkpoint.started_at:
                start = datetime.fromisoformat(checkpoint.started_at.replace('Z', '+00:00'))
                end = datetime.fromisoformat(checkpoint.completed_at.replace('Z', '+00:00'))
                checkpoint.duration_seconds = (end - start).total_seconds()
        
        self.updated_at = datetime.utcnow().isoformat() + "Z"
        self.save()
    
    def fail_stage(self, stage_name: str, error: str):
        """Mark a stage as failed."""
        if stage_name in self.stages:
            self.stages[stage_name].status = StageStatus.FAILED
            self.stages[stage_name].error = error
            self.stages[stage_name].completed_at = datetime.utcnow().isoformat() + "Z"
        
        self.status = "failed"
        self.updated_at = datetime.utcnow().isoformat() + "Z"
        self.save()
    
    def get_next_pending_stage(self) -> Optional[str]:
        """Get the next pending stage to execute."""
        for stage_name, checkpoint in self.stages.items():
            if checkpoint.status == StageStatus.PENDING:
                return stage_name
        return None
    
    def is_complete(self) -> bool:
        """Check if all stages are completed."""
        return all(
            stage.status == StageStatus.COMPLETED 
            for stage in self.stages.values()
        )
    
    def get_progress(self) -> Dict[str, Any]:
        """Get workflow progress summary."""
        total = len(self.stages)
        completed = sum(1 for s in self.stages.values() if s.status == StageStatus.COMPLETED)
        failed = sum(1 for s in self.stages.values() if s.status == StageStatus.FAILED)
        
        return {
            "total_stages": total,
            "completed": completed,
            "failed": failed,
            "in_progress": 1 if self.current_stage else 0,
            "pending": total - completed - failed,
            "progress_percent": (completed / total * 100) if total > 0 else 0
        }