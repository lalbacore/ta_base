"""
Episode Service - Manages episode lifecycle and storage
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid
import logging

from app.models.episode import Episode

logger = logging.getLogger(__name__)


class EpisodeService:
    """Service for managing episodes (in-memory for now)."""
    
    def __init__(self):
        self.episodes: Dict[str, Episode] = {}
    
    def create_episode(self, mission_id: str, estimated_tokens: int = 0) -> Episode:
        """
        Create a new episode for a mission.
        
        Args:
            mission_id: ID of the mission
            estimated_tokens: Optional token consumption estimate
            
        Returns:
            Created episode
        """
        episode_id = f"episode_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        episode = Episode(
            episode_id=episode_id,
            mission_id=mission_id,
            estimated_tokens=estimated_tokens
        )
        
        self.episodes[episode_id] = episode
        logger.info(f"Created episode {episode_id} for mission {mission_id}")
        
        return episode
    
    def get_episode(self, episode_id: str) -> Optional[Episode]:
        """Get episode by ID."""
        return self.episodes.get(episode_id)
    
    def list_episodes(
        self,
        status: Optional[str] = None,
        mission_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Episode]:
        """
        List episodes with optional filtering.
        
        Args:
            status: Filter by status
            mission_id: Filter by mission ID
            limit: Maximum number of episodes to return
            offset: Offset for pagination
            
        Returns:
            List of episodes
        """
        episodes = list(self.episodes.values())
        
        # Filter by status
        if status:
            episodes = [e for e in episodes if e.status == status]
        
        # Filter by mission
        if mission_id:
            episodes = [e for e in episodes if e.mission_id == mission_id]
        
        # Sort by created_at (newest first)
        episodes.sort(key=lambda x: x.created_at, reverse=True)
        
        # Paginate
        return episodes[offset:offset + limit]
    
    def update_episode_status(self, episode_id: str, status: str) -> Optional[Episode]:
        """Update episode status."""
        episode = self.get_episode(episode_id)
        if episode:
            episode.update_status(status)
            logger.info(f"Updated episode {episode_id} status to {status}")
        return episode
    
    def add_artifact(self, episode_id: str, artifact: Dict) -> Optional[Episode]:
        """Add artifact to episode."""
        episode = self.get_episode(episode_id)
        if episode:
            episode.add_artifact(artifact)
            logger.info(f"Added artifact to episode {episode_id}")
        return episode
    
    def add_tokens(
        self,
        episode_id: str,
        agent_id: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Optional[Episode]:
        """
        Add token consumption for an agent.
        
        Args:
            episode_id: Episode ID
            agent_id: Agent ID
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            
        Returns:
            Updated episode or None if not found
        """
        episode = self.get_episode(episode_id)
        if episode:
            episode.add_tokens(agent_id, prompt_tokens, completion_tokens)
            logger.info(
                f"Added {prompt_tokens + completion_tokens} tokens "
                f"for agent {agent_id} in episode {episode_id}"
            )
        return episode
    
    def set_effectiveness_score(
        self,
        episode_id: str,
        score: float,
        breakdown: Dict = None
    ) -> Optional[Episode]:
        """Set effectiveness score for episode."""
        episode = self.get_episode(episode_id)
        if episode:
            episode.set_effectiveness_score(score, breakdown)
            logger.info(f"Set effectiveness score {score} for episode {episode_id}")
        return episode
    
    def increment_step(self, episode_id: str) -> Optional[Episode]:
        """Increment step counter."""
        episode = self.get_episode(episode_id)
        if episode:
            episode.increment_step()
        return episode
    
    def get_total_tokens_by_agent(self, episode_id: str) -> Dict[str, int]:
        """Get token breakdown by agent."""
        episode = self.get_episode(episode_id)
        if episode:
            return episode.agent_token_breakdown
        return {}
    
    def get_episode_stats(self) -> Dict:
        """Get overall episode statistics."""
        total = len(self.episodes)
        completed = len([e for e in self.episodes.values() if e.status == "completed"])
        failed = len([e for e in self.episodes.values() if e.status == "failed"])
        running = len([e for e in self.episodes.values() if e.status == "running"])
        
        # Token statistics
        total_tokens = sum(e.total_tokens_consumed for e in self.episodes.values())
        avg_tokens = total_tokens / total if total > 0 else 0
        
        return {
            "total_episodes": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "total_tokens_consumed": total_tokens,
            "average_tokens_per_episode": avg_tokens
        }


# Singleton instance
episode_service = EpisodeService()
