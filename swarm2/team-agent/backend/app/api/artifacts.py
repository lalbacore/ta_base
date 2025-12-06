"""
Artifacts API - Manifest and signature verification.
"""
from flask import Blueprint, request, jsonify
from app.services.artifacts_service import artifacts_service

artifacts_bp = Blueprint('artifacts', __name__)


@artifacts_bp.route('/workflow/<workflow_id>/manifest', methods=['GET'])
def get_workflow_manifest(workflow_id):
    """Get workflow manifest."""
    try:
        manifest = artifacts_service.get_workflow_manifest(workflow_id)
        if not manifest:
            return jsonify({'error': 'Manifest not found'}), 404
        return jsonify(manifest), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@artifacts_bp.route('/workflow/<workflow_id>/artifacts', methods=['GET'])
def get_workflow_artifacts(workflow_id):
    """Get workflow artifacts."""
    try:
        artifacts = artifacts_service.get_workflow_artifacts(workflow_id)
        return jsonify(artifacts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@artifacts_bp.route('/artifact/verify', methods=['POST'])
def verify_artifact():
    """Verify artifact signature."""
    try:
        artifact_data = request.get_json()
        result = artifacts_service.verify_artifact(artifact_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@artifacts_bp.route('/manifest/verify', methods=['POST'])
def verify_manifest():
    """Verify manifest integrity."""
    try:
        manifest_data = request.get_json()
        result = artifacts_service.verify_manifest(manifest_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@artifacts_bp.route('/workflow/<workflow_id>/manifest/export', methods=['GET'])
def export_manifest(workflow_id):
    """Export manifest in specified format."""
    try:
        format_type = request.args.get('format', 'json')
        manifest_text = artifacts_service.export_manifest(workflow_id, format_type)
        return jsonify(manifest_text), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@artifacts_bp.route('/workflow/<workflow_id>/artifact/<artifact_name>/publish', methods=['POST'])
def publish_artifact(workflow_id, artifact_name):
    """Publish artifact to capability registry."""
    try:
        publish_data = request.get_json() or {}
        result = artifacts_service.publish_to_registry(workflow_id, artifact_name, publish_data)

        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
