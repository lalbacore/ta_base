"""
Governance API - Policy configuration and decision management.
"""
from flask import Blueprint, request, jsonify
from app.services.governance_service import governance_service

governance_bp = Blueprint('governance', __name__)


@governance_bp.route('/config', methods=['GET'])
def get_policy_config():
    """Get current policy configuration."""
    try:
        config = governance_service.get_policy_config()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/config', methods=['PUT'])
def update_policy_config():
    """Update policy configuration."""
    try:
        config = request.get_json()
        governance_service.update_policy_config(config)
        return jsonify({'status': 'updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/governance/decisions', methods=['GET'])
def get_decisions():
    """Get governance decision history."""
    try:
        limit = request.args.get('limit', type=int, default=50)
        decisions = governance_service.get_decisions(limit)
        return jsonify(decisions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/approval/pending', methods=['GET'])
def get_pending_gates():
    """Get pending approval gates."""
    try:
        gates = governance_service.get_pending_gates()
        return jsonify(gates), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/approval/<gate_id>/action', methods=['POST'])
def handle_approval_gate(gate_id):
    """Approve or reject an approval gate."""
    try:
        data = request.get_json()
        action = data.get('action')  # 'approve' or 'reject'
        reason = data.get('reason')

        if action == 'approve':
            governance_service.approve_gate(gate_id)
        elif action == 'reject':
            governance_service.reject_gate(gate_id, reason)
        else:
            return jsonify({'error': 'Invalid action'}), 400

        return jsonify({'status': action}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
