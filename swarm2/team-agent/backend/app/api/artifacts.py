"""
Artifacts API - Manifest and signature verification.
"""
from flask import Blueprint, request, jsonify
from app.services.artifacts_service import artifacts_service
from app.services.enhanced_artifacts_service import enhanced_artifacts_service, PublishOptions

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


# ============================================================================
# Enhanced Artifact Publishing Endpoints (Encryption, Signing, Multi-Backend)
# ============================================================================

@artifacts_bp.route('/storage/backends', methods=['GET'])
def list_storage_backends():
    """List all available storage backends."""
    try:
        backends = enhanced_artifacts_service.list_available_backends()
        return jsonify(backends), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@artifacts_bp.route('/workflow/<workflow_id>/artifact/<artifact_name>/publish-enhanced', methods=['POST'])
def publish_artifact_enhanced(workflow_id, artifact_name):
    """
    Publish artifact with encryption and signing to specified backend.

    Request body:
    {
        "storage_backend": "local" | "ipfs" | "filecoin",
        "options": "none" | "sign" | "encrypt" | "encrypt_and_sign",
        "encryption_password": "optional password for key derivation",
        "metadata": {"key": "value"}
    }

    Response:
    {
        "success": true,
        "storage_identifier": "path/cid/url",
        "encryption_key": "base64_key (if encrypted)",
        "crypto_metadata": {...},
        "storage_metadata": {...}
    }
    """
    try:
        publish_data = request.get_json() or {}

        # Get artifact content from workflow directory
        workflow_dir = enhanced_artifacts_service.output_dir / workflow_id
        artifact_path = workflow_dir / artifact_name

        if not artifact_path.exists():
            return jsonify({
                'success': False,
                'error': f'Artifact {artifact_name} not found in workflow {workflow_id}'
            }), 404

        content = artifact_path.read_bytes()

        # Parse options
        storage_backend = publish_data.get('storage_backend', 'local')
        options_str = publish_data.get('options', 'sign')

        # Map string to enum
        options_map = {
            'none': PublishOptions.NONE,
            'sign': PublishOptions.SIGN,
            'encrypt': PublishOptions.ENCRYPT,
            'encrypt_and_sign': PublishOptions.ENCRYPT_AND_SIGN
        }
        options = options_map.get(options_str.lower(), PublishOptions.SIGN)

        # Publish
        result = enhanced_artifacts_service.publish_artifact(
            workflow_id=workflow_id,
            artifact_name=artifact_name,
            content=content,
            storage_backend=storage_backend,
            options=options,
            encryption_password=publish_data.get('encryption_password'),
            metadata=publish_data.get('metadata')
        )

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@artifacts_bp.route('/workflow/<workflow_id>/publish-all', methods=['POST'])
def publish_all_workflow_artifacts(workflow_id):
    """
    Publish all artifacts from a workflow.

    Request body:
    {
        "storage_backend": "local" | "ipfs" | "filecoin",
        "options": "none" | "sign" | "encrypt" | "encrypt_and_sign",
        "encryption_password": "optional password for key derivation"
    }

    Response:
    {
        "success": true,
        "artifacts_published": 3,
        "results": [...],
        "errors": [...]
    }
    """
    try:
        publish_data = request.get_json() or {}

        storage_backend = publish_data.get('storage_backend', 'local')
        options_str = publish_data.get('options', 'sign')

        options_map = {
            'none': PublishOptions.NONE,
            'sign': PublishOptions.SIGN,
            'encrypt': PublishOptions.ENCRYPT,
            'encrypt_and_sign': PublishOptions.ENCRYPT_AND_SIGN
        }
        options = options_map.get(options_str.lower(), PublishOptions.SIGN)

        result = enhanced_artifacts_service.publish_workflow_artifacts(
            workflow_id=workflow_id,
            storage_backend=storage_backend,
            options=options,
            encryption_password=publish_data.get('encryption_password')
        )

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@artifacts_bp.route('/artifact/retrieve', methods=['POST'])
def retrieve_artifact_enhanced():
    """
    Retrieve artifact with decryption and signature verification.

    Request body:
    {
        "storage_identifier": "path/cid/url",
        "storage_backend": "local" | "ipfs" | "filecoin",
        "encryption_key": "base64_key (if encrypted)",
        "verify_signature": true/false,
        "chain_pem": "certificate chain PEM for verification"
    }

    Response:
    {
        "success": true,
        "content": "binary content (base64 if binary)",
        "signature_valid": true/false,
        "metadata": {...}
    }
    """
    try:
        retrieve_data = request.get_json()

        if not retrieve_data or 'storage_identifier' not in retrieve_data:
            return jsonify({
                'success': False,
                'error': 'Missing storage_identifier'
            }), 400

        result = enhanced_artifacts_service.retrieve_artifact(
            storage_identifier=retrieve_data['storage_identifier'],
            storage_backend=retrieve_data.get('storage_backend', 'local'),
            encryption_key=retrieve_data.get('encryption_key'),
            verify_signature=retrieve_data.get('verify_signature', True),
            chain_pem=retrieve_data.get('chain_pem')
        )

        if result['success']:
            # Convert binary content to base64 for JSON response
            import base64
            content = result.pop('content')
            try:
                # Try to decode as UTF-8 text
                result['content'] = content.decode('utf-8')
                result['content_encoding'] = 'utf-8'
            except UnicodeDecodeError:
                # Binary content - encode as base64
                result['content'] = base64.b64encode(content).decode('utf-8')
                result['content_encoding'] = 'base64'

            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@artifacts_bp.route('/workflow/<workflow_id>/artifacts-enhanced', methods=['GET'])
def list_workflow_artifacts_enhanced(workflow_id):
    """
    List workflow artifacts from all or specific storage backend.

    Query params:
    - storage_backend: optional backend filter (local, ipfs, filecoin)

    Response:
    [
        {
            "artifact_name": "file.py",
            "storage_type": "ipfs",
            "cid": "Qm...",
            "encrypted": true,
            "signed": true,
            ...
        }
    ]
    """
    try:
        storage_backend = request.args.get('storage_backend')

        artifacts = enhanced_artifacts_service.list_workflow_artifacts(
            workflow_id=workflow_id,
            storage_backend=storage_backend
        )

        return jsonify(artifacts), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
