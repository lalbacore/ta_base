"""
Episodes API - REST endpoints for episode management
"""

from flask import Blueprint, jsonify, request
import logging

from app.services.episode_service import episode_service

logger = logging.getLogger(__name__)

episodes_bp = Blueprint('episodes', __name__, url_prefix='/api/episodes')


@episodes_bp.route('', methods=['GET'])
def list_episodes():
    """
    List all episodes with optional filtering.
    
    Query Parameters:
        status: Filter by status (created, running, completed, failed)
        mission_id: Filter by mission ID
        limit: Maximum number of results (default: 100)
        offset: Offset for pagination (default: 0)
    """
    try:
        status = request.args.get('status')
        mission_id = request.args.get('mission_id')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        episodes = episode_service.list_episodes(
            status=status,
            mission_id=mission_id,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'episodes': [e.to_dict() for e in episodes],
            'total': len(episode_service.episodes),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing episodes: {e}")
        return jsonify({'error': str(e)}), 500


@episodes_bp.route('/<episode_id>', methods=['GET'])
def get_episode(episode_id):
    """Get a specific episode by ID."""
    try:
        episode = episode_service.get_episode(episode_id)
        
        if not episode:
            return jsonify({'error': 'Episode not found'}), 404
        
        return jsonify(episode.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error getting episode {episode_id}: {e}")
        return jsonify({'error': str(e)}), 500


@episodes_bp.route('', methods=['POST'])
def create_episode():
    """
    Create a new episode.
    
    Request Body:
        mission_id: Mission ID (required)
        estimated_tokens: Estimated token consumption (optional)
    """
    try:
        data = request.json
        
        if not data or 'mission_id' not in data:
            return jsonify({'error': 'mission_id is required'}), 400
        
        mission_id = data['mission_id']
        estimated_tokens = data.get('estimated_tokens', 0)
        
        episode = episode_service.create_episode(
            mission_id=mission_id,
            estimated_tokens=estimated_tokens
        )
        
        return jsonify(episode.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating episode: {e}")
        return jsonify({'error': str(e)}), 500


@episodes_bp.route('/<episode_id>/status', methods=['PUT'])
def update_episode_status(episode_id):
    """
    Update episode status.
    
    Request Body:
        status: New status (created, running, completed, failed)
    """
    try:
        data = request.json
        
        if not data or 'status' not in data:
            return jsonify({'error': 'status is required'}), 400
        
        status = data['status']
        valid_statuses = ['created', 'running', 'completed', 'failed']
        
        if status not in valid_statuses:
            return jsonify({
                'error': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400
        
        episode = episode_service.update_episode_status(episode_id, status)
        
        if not episode:
            return jsonify({'error': 'Episode not found'}), 404
        
        return jsonify(episode.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error updating episode status: {e}")
        return jsonify({'error': str(e)}), 500


@episodes_bp.route('/<episode_id>/tokens', methods=['POST'])
def add_tokens(episode_id):
    """
    Add token consumption for an agent.
    
    Request Body:
        agent_id: Agent ID
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
    """
    try:
        data = request.json
        
        required_fields = ['agent_id', 'prompt_tokens', 'completion_tokens']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Required fields: {required_fields}'
            }), 400
        
        episode = episode_service.add_tokens(
            episode_id=episode_id,
            agent_id=data['agent_id'],
            prompt_tokens=data['prompt_tokens'],
            completion_tokens=data['completion_tokens']
        )
        
        if not episode:
            return jsonify({'error': 'Episode not found'}), 404
        
        return jsonify(episode.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error adding tokens: {e}")
        return jsonify({'error': str(e)}), 500


@episodes_bp.route('/<episode_id>/artifacts', methods=['POST'])
def add_artifact(episode_id):
    """
    Add an artifact to an episode.
    
    Request Body:
        artifact: Artifact data (dict)
    """
    try:
        data = request.json
        
        if not data or 'artifact' not in data:
            return jsonify({'error': 'artifact is required'}), 400
        
        episode = episode_service.add_artifact(episode_id, data['artifact'])
        
        if not episode:
            return jsonify({'error': 'Episode not found'}), 404
        
        return jsonify(episode.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error adding artifact: {e}")
        return jsonify({'error': str(e)}), 500


@episodes_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall episode statistics including token consumption."""
    try:
        stats = episode_service.get_episode_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500
