"""
Execution Tracker - Tracks agent actions and token consumption during episode execution
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from app.services.episode_service import episode_service

logger = logging.getLogger(__name__)


class ExecutionTracker:
    """Tracks execution steps and token consumption for episodes."""
    
    def track_action(
        self,
        episode_id: str,
        agent_id: str,
        action: str,
        input_data: Dict,
        output_data: Dict = None,
        tokens_used: Dict = None
    ):
        """
        Track an agent action in an episode.
        
        Args:
            episode_id: Episode ID
            agent_id: Agent performing the action
            action: Action name/type
            input_data: Input to the action
            output_data: Output from the action
            tokens_used: Token consumption dict with 'prompt' and 'completion' keys
        """
        try:
            # Increment step counter
            episode_service.increment_step(episode_id)
            
            # Track token consumption if provided
            if tokens_used:
                prompt_tokens = tokens_used.get('prompt', 0)
                completion_tokens = tokens_used.get('completion', 0)
                
                if prompt_tokens > 0 or completion_tokens > 0:
                    episode_service.add_tokens(
                        episode_id=episode_id,
                        agent_id=agent_id,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens
                    )
            
            logger.info(
                f"Tracked action '{action}' by {agent_id} in episode {episode_id}"
            )
            
        except Exception as e:
            logger.error(f"Error tracking action: {e}")
    
    def start_episode(self, episode_id: str):
        """Mark episode as started."""
        episode_service.update_episode_status(episode_id, "running")
    
    def complete_episode(self, episode_id: str, effectiveness_score: float = 80.0):
        """Mark episode as completed with effectiveness score."""
        episode_service.set_effectiveness_score(episode_id, effectiveness_score)
        episode_service.update_episode_status(episode_id, "completed")
    
    def fail_episode(self, episode_id: str, error: str = None):
        """Mark episode as failed."""
        episode_service.update_episode_status(episode_id, "failed")
        if error:
            logger.error(f"Episode {episode_id} failed: {error}")


# Singleton instance
execution_tracker = ExecutionTracker()
