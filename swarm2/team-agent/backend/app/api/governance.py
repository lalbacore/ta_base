"""
Governance API - Policy configuration and decision management.
"""
from flask import Blueprint, request, jsonify
from app.services.governance_service import governance_service
from app.auth import require_government_role

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


# Policy CRUD Endpoints

@governance_bp.route('/policies', methods=['GET'])
def get_all_policies():
    """Get all governance policies."""
    try:
        policies = governance_service.get_all_policies()
        return jsonify(policies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/policies', methods=['POST'])
@require_government_role
def create_policy():
    """Create a new governance policy (government only)."""
    try:
        policy_data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'min_trust_score', 'allowed_languages']
        for field in required_fields:
            if field not in policy_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        policy = governance_service.create_policy(policy_data)
        return jsonify(policy), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/policies/<int:policy_id>', methods=['GET'])
def get_policy(policy_id):
    """Get a specific governance policy."""
    try:
        policies = governance_service.get_all_policies()
        policy = next((p for p in policies if p['id'] == policy_id), None)

        if not policy:
            return jsonify({'error': 'Policy not found'}), 404

        return jsonify(policy), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/policies/<int:policy_id>', methods=['PUT'])
@require_government_role
def update_policy(policy_id):
    """Update a governance policy (government only)."""
    try:
        policy_data = request.get_json()
        policy = governance_service.update_policy(policy_id, policy_data)
        return jsonify(policy), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/policies/<int:policy_id>', methods=['DELETE'])
@require_government_role
def delete_policy(policy_id):
    """Delete a governance policy (government only)."""
    try:
        governance_service.delete_policy(policy_id)
        return jsonify({'status': 'deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@governance_bp.route('/policies/<int:policy_id>/activate', methods=['POST'])
@require_government_role
def activate_policy(policy_id):
    """Activate a governance policy (government only)."""
    try:
        policy = governance_service.activate_policy(policy_id)
        return jsonify(policy), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
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


@governance_bp.route('/check-compliance', methods=['POST'])
def check_compliance():
    """Check mission compliance against policies (Easter Egg!)."""
    try:
        mission_data = request.get_json()
        compliance_report = governance_service.check_mission_compliance(mission_data)
        return jsonify(compliance_report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
