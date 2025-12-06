"""
Mission Management API - Handles mission submission and workflow status.
"""
from flask import Blueprint, request, jsonify
from app.services.mission_service import mission_service

mission_bp = Blueprint('mission', __name__)


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
