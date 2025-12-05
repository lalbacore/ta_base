"""
Capability Registry API - A2A capability discovery and matching.
"""
from flask import Blueprint, request, jsonify
from app.services.registry_service import registry_service

registry_bp = Blueprint('registry', __name__)


@registry_bp.route('/capabilities', methods=['GET'])
def get_capabilities():
    """List/search capabilities with optional filters."""
    try:
        filters = request.args.to_dict()
        capabilities = registry_service.get_capabilities(filters)
        return jsonify(capabilities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@registry_bp.route('/capability/<capability_id>', methods=['GET'])
def get_capability(capability_id):
    """Get capability details."""
    try:
        capability = registry_service.get_capability(capability_id)
        if not capability:
            return jsonify({'error': 'Capability not found'}), 404
        return jsonify(capability), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@registry_bp.route('/providers', methods=['GET'])
def get_providers():
    """List all capability providers."""
    try:
        providers = registry_service.get_providers()
        return jsonify(providers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@registry_bp.route('/provider/<provider_id>', methods=['GET'])
def get_provider(provider_id):
    """Get provider details."""
    try:
        provider = registry_service.get_provider(provider_id)
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        return jsonify(provider), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@registry_bp.route('/discover', methods=['POST'])
def discover_capabilities():
    """Discover capabilities based on requirements."""
    try:
        requirements = request.get_json()
        capabilities = registry_service.discover_capabilities(requirements)
        return jsonify(capabilities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@registry_bp.route('/match', methods=['POST'])
def match_capabilities():
    """Match and score capabilities against requirements."""
    try:
        requirements = request.get_json()
        matches = registry_service.match_capabilities(requirements)
        return jsonify(matches), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@registry_bp.route('/capability/<capability_id>/revoke', methods=['POST'])
def revoke_capability(capability_id):
    """Revoke a capability."""
    try:
        registry_service.revoke_capability(capability_id)
        return jsonify({'status': 'revoked'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
