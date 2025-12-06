"""
Trust Management API - Agent reputation and trust scoring.
"""
from flask import Blueprint, request, jsonify
from app.services.trust_service import trust_service

trust_bp = Blueprint('trust', __name__)


@trust_bp.route('/agents', methods=['GET'])
def get_all_agents():
    """Get all agents with trust metrics."""
    try:
        agents = trust_service.get_all_agents()
        return jsonify(agents), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trust_bp.route('/agent/<agent_id>', methods=['GET'])
def get_agent_details(agent_id):
    """Get detailed trust metrics for an agent."""
    try:
        agent = trust_service.get_agent_details(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        return jsonify(agent), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trust_bp.route('/agent/<agent_id>/history', methods=['GET'])
def get_agent_history(agent_id):
    """Get trust score history for an agent."""
    try:
        history = trust_service.get_agent_history(agent_id)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trust_bp.route('/agent/<agent_id>/events', methods=['GET'])
def get_agent_events(agent_id):
    """Get trust events for an agent."""
    try:
        events = trust_service.get_agent_events(agent_id)
        return jsonify(events), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trust_bp.route('/agent/<agent_id>/event', methods=['POST'])
def record_event(agent_id):
    """Record a new trust event."""
    try:
        event_data = request.get_json()
        trust_service.record_event(agent_id, event_data)
        return jsonify({'status': 'recorded'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
