"""
Mission Management API - Handles mission submission and workflow status.

Now includes A2A agent discovery for mission building.
"""
from flask import Blueprint, request, jsonify
from app.services.mission_service import mission_service
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from swarms.team_agent.a2a import AgentDiscovery, AgentMatcher, MatchCriteria, DiscoveryConfig

mission_bp = Blueprint('mission', __name__)

# Initialize A2A discovery (singleton)
_agent_discovery = None

def get_agent_discovery():
    """Get or create agent discovery instance."""
    global _agent_discovery
    if _agent_discovery is None:
        _agent_discovery = AgentDiscovery()
    return _agent_discovery


@mission_bp.route('/submit', methods=['POST'])
def submit_mission():
    """Submit a new mission for execution."""
    try:
        mission_data = request.get_json()
        result = mission_service.submit_mission(mission_data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@mission_bp.route('/list', methods=['GET'])
def list_missions():
    """List all missions."""
    try:
        missions = mission_service.list_missions()
        return jsonify(missions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/<mission_id>', methods=['GET'])
def get_mission(mission_id):
    """Get mission details."""
    try:
        mission = mission_service.get_mission(mission_id)
        if not mission:
            return jsonify({'error': 'Mission not found'}), 404
        return jsonify(mission), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/workflow/<workflow_id>/status', methods=['GET'])
def get_workflow_status(workflow_id):
    """Get workflow status and progress."""
    try:
        status = mission_service.get_workflow_status(workflow_id)
        if not status:
            return jsonify({'error': 'Workflow not found'}), 404
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/workflow/<workflow_id>/resume', methods=['POST'])
def resume_workflow(workflow_id):
    """Resume a paused workflow."""
    try:
        mission_service.resume_workflow(workflow_id)
        return jsonify({'status': 'resumed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/workflow/list', methods=['GET'])
def list_workflows():
    """List all workflows."""
    try:
        workflows = mission_service.list_workflows()
        return jsonify(workflows), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/breakpoint/<breakpoint_id>/approve', methods=['POST'])
def approve_breakpoint(breakpoint_id):
    """Approve a breakpoint with selected option."""
    try:
        data = request.get_json()
        option_index = data.get('option_index', 0)
        mission_service.approve_breakpoint(breakpoint_id, option_index)
        return jsonify({'status': 'approved'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/breakpoint/<breakpoint_id>/reject', methods=['POST'])
def reject_breakpoint(breakpoint_id):
    """Reject a breakpoint."""
    try:
        mission_service.reject_breakpoint(breakpoint_id)
        return jsonify({'status': 'rejected'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# A2A Agent Discovery Endpoints for Mission Building
# ============================================================================

@mission_bp.route('/discover-agents', methods=['GET'])
def discover_agents():
    """
    Discover available agents from local and remote registries.

    Query Parameters:
    - agent_type: Filter by type (role, specialist, tool)
    - min_trust_score: Minimum trust score (0-100)
    - min_success_rate: Minimum success rate (0-1.0)
    - use_cache: Use cached results (default: true)

    Returns:
    - List of agent cards with capabilities and metadata
    """
    try:
        # Get query parameters
        agent_type = request.args.get('agent_type')
        min_trust_score = float(request.args.get('min_trust_score', 0.0))
        min_success_rate = float(request.args.get('min_success_rate', 0.0))
        use_cache = request.args.get('use_cache', 'true').lower() == 'true'

        # Discover agents
        discovery = get_agent_discovery()

        if agent_type or min_trust_score > 0 or min_success_rate > 0:
            # Use filtered discovery
            agents = discovery.find_agents(
                agent_type=agent_type,
                min_trust_score=min_trust_score,
                min_success_rate=min_success_rate,
                use_cache=use_cache
            )
        else:
            # Get all agents
            agents = discovery.discover_all(use_cache=use_cache)

        # Convert to dict
        agent_dicts = [agent.to_dict() for agent in agents]

        return jsonify({
            'agents': agent_dicts,
            'total': len(agent_dicts),
            'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/match-agents', methods=['POST'])
def match_agents():
    """
    Match agents to mission requirements using weighted scoring.

    Request body:
    {
        "agent_type": "specialist",  // Optional
        "capability_type": "cloud_infrastructure",  // Optional
        "required_specialties": ["aws", "terraform"],  // Optional
        "required_tags": ["devops"],  // Optional
        "required_languages": ["python"],  // Optional
        "min_trust_score": 85.0,  // Optional (0-100)
        "min_success_rate": 0.9,  // Optional (0-1.0)
        "min_total_invocations": 10,  // Optional
        "min_average_rating": 4.0,  // Optional (0-5.0)
        "trust_score_weight": 0.4,  // Optional (default 0.4)
        "success_rate_weight": 0.3,  // Optional (default 0.3)
        "experience_weight": 0.2,  // Optional (default 0.2)
        "rating_weight": 0.1  // Optional (default 0.1)
    }

    Returns:
    - Ranked list of matching agents with scores and reasons
    """
    try:
        requirements = request.get_json()

        # Discover all agents
        discovery = get_agent_discovery()
        agents = discovery.discover_all()

        # Create match criteria
        criteria = MatchCriteria(
            agent_type=requirements.get('agent_type'),
            capability_type=requirements.get('capability_type'),
            required_specialties=requirements.get('required_specialties', []),
            required_tags=requirements.get('required_tags', []),
            required_languages=requirements.get('required_languages', []),
            min_trust_score=requirements.get('min_trust_score', 0.0),
            min_success_rate=requirements.get('min_success_rate', 0.0),
            min_total_invocations=requirements.get('min_total_invocations', 0),
            min_average_rating=requirements.get('min_average_rating', 0.0),
            trust_score_weight=requirements.get('trust_score_weight', 0.4),
            success_rate_weight=requirements.get('success_rate_weight', 0.3),
            experience_weight=requirements.get('experience_weight', 0.2),
            rating_weight=requirements.get('rating_weight', 0.1)
        )

        # Match agents
        matcher = AgentMatcher()
        matches = matcher.match_agents(agents, criteria)

        # Convert to dict
        match_dicts = [match.to_dict() for match in matches]

        return jsonify({
            'matches': match_dicts,
            'total': len(match_dicts),
            'best_match': match_dicts[0] if match_dicts else None,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid criteria: {str(e)}'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/agent/<agent_id>', methods=['GET'])
def get_agent_details(agent_id):
    """
    Get detailed information about a specific agent.

    Returns:
    - Agent card with full metadata, capabilities, and trust info
    """
    try:
        discovery = get_agent_discovery()
        agent = discovery.get_agent_by_id(agent_id, use_cache=True)

        if not agent:
            return jsonify({'error': 'Agent not found'}), 404

        return jsonify(agent.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/agents/specialists', methods=['GET'])
def get_specialists():
    """Get all specialist agents."""
    try:
        discovery = get_agent_discovery()
        specialists = discovery.get_agents_by_type('specialist')

        return jsonify({
            'agents': [agent.to_dict() for agent in specialists],
            'total': len(specialists)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/agents/roles', methods=['GET'])
def get_roles():
    """Get all role agents (Architect, Builder, Critic, etc.)."""
    try:
        discovery = get_agent_discovery()
        roles = discovery.get_agents_by_type('role')

        return jsonify({
            'agents': [agent.to_dict() for agent in roles],
            'total': len(roles)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mission_bp.route('/agents/clear-cache', methods=['POST'])
def clear_agent_cache():
    """Clear agent discovery cache (for development/testing)."""
    try:
        discovery = get_agent_discovery()
        discovery.clear_cache()

        return jsonify({'status': 'cache cleared'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
