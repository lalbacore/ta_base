"""
Missions API - Additional endpoints for frontend compatibility
"""
from flask import Blueprint, jsonify
from app.services.mission_service import mission_service
from app.services.episode_service import episode_service

missions_bp = Blueprint('missions', __name__, url_prefix='/api/missions')


@missions_bp.route('/workflows/<workflow_id>/status', methods=['GET'])
def get_workflow_status(workflow_id):
    """
    Get workflow status - compatible with frontend expectations.
    
    This endpoint provides workflow status by checking both:
    1. Mission service (for workflow data)
    2. Episode service (for episode tracking)
    """
    try:
        # Try to get workflow status from mission service
        status = mission_service.get_workflow_status(workflow_id)
        
        if not status:
            return jsonify({'error': 'Workflow not found'}), 404
        
        # Enhance with episode data if available
        mission_id = status.get('mission_id', workflow_id)
        episodes = episode_service.list_episodes(mission_id=mission_id, limit=1)
        
        if episodes:
            episode = episodes[0]
            status['episode'] = {
                'episode_id': episode.episode_id,
                'status': episode.status,
                'effectiveness_score': episode.effectiveness_score,
                'tokens': {
                    'total': episode.total_tokens_consumed,
                    'prompt': episode.prompt_tokens,
                    'completion': episode.completion_tokens
                },
                'steps_count': episode.steps_count
            }
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
