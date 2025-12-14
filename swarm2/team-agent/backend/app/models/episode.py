"""
Episode Model - Represents a complete workflow execution with token tracking
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class Episode:
    """
    An Episode represents a complete mission execution.
    
    Episode = Mission + Agent(s) + Execution Path + Artifact(s) + Rating + Tokens
    """
    
    # Core identifiers
    episode_id: str
    mission_id: str
    
    # Status tracking
    status: str = "created"  # created, running, completed, failed
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Execution tracking
    steps_count: int = 0
    agents_count: int = 0
    decisions_count: int = 0
    
    # Artifacts
    artifacts: List[Dict] = field(default_factory=list)
    
    # Rating & effectiveness
    effectiveness_score: float = 0.0
    rating_breakdown: Dict = field(default_factory=dict)
    
    # Token consumption tracking (NEW!)
    total_tokens_consumed: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    agent_token_breakdown: Dict[str, int] = field(default_factory=dict)
    
    # Estimation (for future use)
    estimated_tokens: int = 0
    token_variance: float = 0.0
    
    # Attestation
    attestation_chain: List[Dict] = field(default_factory=list)
    root_attestation_id: Optional[str] = None
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert episode to dictionary for API responses."""
        return {
            "episode_id": self.episode_id,
            "mission_id": self.mission_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "steps_count": self.steps_count,
            "agents_count": self.agents_count,
            "decisions_count": self.decisions_count,
            "artifacts": self.artifacts,
            "effectiveness_score": self.effectiveness_score,
            "rating_breakdown": self.rating_breakdown,
            "tokens": {
                "total": self.total_tokens_consumed,
                "prompt": self.prompt_tokens,
                "completion": self.completion_tokens,
                "by_agent": self.agent_token_breakdown,
                "estimated": self.estimated_tokens,
                "variance": self.token_variance
            },
            "attestation_chain": self.attestation_chain,
            "root_attestation_id": self.root_attestation_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Episode':
        """Create episode from dictionary."""
        # Extract token data if present
        tokens = data.get('tokens', {})
        
        return cls(
            episode_id=data['episode_id'],
            mission_id=data['mission_id'],
            status=data.get('status', 'created'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            steps_count=data.get('steps_count', 0),
            agents_count=data.get('agents_count', 0),
            decisions_count=data.get('decisions_count', 0),
            artifacts=data.get('artifacts', []),
            effectiveness_score=data.get('effectiveness_score', 0.0),
            rating_breakdown=data.get('rating_breakdown', {}),
            total_tokens_consumed=tokens.get('total', 0),
            prompt_tokens=tokens.get('prompt', 0),
            completion_tokens=tokens.get('completion', 0),
            agent_token_breakdown=tokens.get('by_agent', {}),
            estimated_tokens=tokens.get('estimated', 0),
            token_variance=tokens.get('variance', 0.0),
            attestation_chain=data.get('attestation_chain', []),
            root_attestation_id=data.get('root_attestation_id'),
            metadata=data.get('metadata', {})
        )
    
    def add_tokens(self, agent_id: str, prompt: int, completion: int):
        """Add token consumption for an agent."""
        total = prompt + completion
        
        # Update totals
        self.total_tokens_consumed += total
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        
        # Update per-agent breakdown
        if agent_id not in self.agent_token_breakdown:
            self.agent_token_breakdown[agent_id] = 0
        self.agent_token_breakdown[agent_id] += total
        
        # Calculate variance if we have an estimate
        if self.estimated_tokens > 0:
            self.token_variance = (
                (self.total_tokens_consumed - self.estimated_tokens) / 
                self.estimated_tokens
            )
    
    def add_artifact(self, artifact: Dict):
        """Add an artifact to the episode."""
        self.artifacts.append(artifact)
    
    def update_status(self, status: str):
        """Update episode status with timestamp."""
        self.status = status
        
        if status == "running" and not self.started_at:
            self.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            self.completed_at = datetime.utcnow()
    
    def increment_step(self):
        """Increment step counter."""
        self.steps_count += 1
    
    def set_effectiveness_score(self, score: float, breakdown: Dict = None):
        """Set effectiveness score and optional breakdown."""
        self.effectiveness_score = score
        if breakdown:
            self.rating_breakdown = breakdown
