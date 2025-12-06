"""
Logs API - Endpoints for retrieving workflow tape logs.
"""
from flask import Blueprint, jsonify, request
from app.services.logs_service import logs_service

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/logs', methods=['GET'])
def get_all_logs():
    """
    Get all workflow logs with optional filtering.

    Query Parameters:
        level: Minimum syslog level (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: INFO
        limit: Maximum number of entries - default: 1000
        workflow_id: Filter by specific workflow ID (optional)

    Returns:
        List of log entries with syslog levels
    """
    try:
        level = request.args.get('level', 'INFO').upper()
        limit = int(request.args.get('limit', 1000))
        workflow_id = request.args.get('workflow_id')

        # Validate level
        valid_levels = ['DEBUG', 'INFO', 'NOTICE', 'WARNING', 'ERROR', 'CRITICAL', 'ALERT', 'EMERGENCY']
        if level not in valid_levels:
            return jsonify({'error': f'Invalid level. Must be one of: {valid_levels}'}), 400

        # Get logs
        if workflow_id:
            logs = logs_service.get_workflow_logs(workflow_id)
        else:
            logs = logs_service.get_all_logs(level=level, limit=limit)

        return jsonify({
            'logs': logs,
            'count': len(logs),
            'level': level,
            'limit': limit
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logs_bp.route('/logs/workflow/<workflow_id>', methods=['GET'])
def get_workflow_logs(workflow_id):
    """
    Get logs for a specific workflow.

    Args:
        workflow_id: Workflow ID to get logs for

    Returns:
        List of log entries for the workflow
    """
    try:
        logs = logs_service.get_workflow_logs(workflow_id)

        return jsonify({
            'workflow_id': workflow_id,
            'logs': logs,
            'count': len(logs)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logs_bp.route('/logs/levels', methods=['GET'])
def get_log_levels():
    """
    Get available syslog levels.

    Returns:
        Dictionary of syslog levels with their numeric priorities
    """
    return jsonify({
        'levels': logs_service.SYSLOG_LEVELS,
        'description': {
            'DEBUG': 'Debug-level messages',
            'INFO': 'Informational messages',
            'NOTICE': 'Normal but significant condition',
            'WARNING': 'Warning conditions',
            'ERROR': 'Error conditions',
            'CRITICAL': 'Critical conditions',
            'ALERT': 'Action must be taken immediately',
            'EMERGENCY': 'System is unusable'
        }
    }), 200
