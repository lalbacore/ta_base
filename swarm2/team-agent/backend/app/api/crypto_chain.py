"""
Crypto Chain API - Visualize cryptographic provenance of artifacts and workflows.
"""
from flask import Blueprint, jsonify, Response
from app.services.crypto_chain_service import crypto_chain_service
from app.services.crypto_manifest_service import crypto_manifest_service

crypto_chain_bp = Blueprint('crypto_chain', __name__)


@crypto_chain_bp.route('/artifact/<workflow_id>/<artifact_name>', methods=['GET'])
def get_artifact_crypto_chain(workflow_id, artifact_name):
    """
    Get the complete cryptographic provenance chain for an artifact.

    Returns a graph showing:
    - Agent identity & trust score
    - Artifact creation & signing
    - Manifest generation
    - Registry publishing
    - Verification steps
    - Weak links & trust violations
    """
    try:
        chain = crypto_chain_service.trace_artifact_chain(workflow_id, artifact_name)
        return jsonify(chain), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@crypto_chain_bp.route('/simulate-break/<workflow_id>/<artifact_name>/<break_type>', methods=['POST'])
def simulate_chain_break(workflow_id, artifact_name, break_type):
    """
    Simulate different types of chain breaks for testing.

    Break types:
    - trust_violation: Low agent trust score
    - signature_invalid: Invalid artifact signature
    - checksum_mismatch: Corrupted artifact
    - unverified_registry: Registry entry not verified
    """
    try:
        # Get the normal chain
        chain = crypto_chain_service.trace_artifact_chain(workflow_id, artifact_name)

        # Simulate the break based on type
        if break_type == 'trust_violation':
            # Reduce agent trust score
            agent_node = next((n for n in chain['graph']['nodes'] if n['type'] == 'agent'), None)
            if agent_node:
                agent_node['trust_score'] = 45.0
                agent_node['status'] = 'untrusted'

                chain['trust_violations'].append({
                    'type': 'low_trust_score',
                    'severity': 'critical',
                    'message': 'Agent trust score below threshold (45 < 75)',
                    'node_id': agent_node['id']
                })

        elif break_type == 'signature_invalid':
            # Mark signature as invalid
            manifest_node = next((n for n in chain['graph']['nodes'] if n['type'] == 'manifest'), None)
            
            if manifest_node:
                manifest_node['verified'] = False
                manifest_node['signature'] = None

                # Mark signing edge as unverified
                for edge in chain['graph']['edges']:
                    if edge['type'] == 'signature':
                        edge['verified'] = False

                chain['weak_links'].append({
                    'type': 'invalid_signature',
                    'severity': 'critical',
                    'message': 'Artifact signature verification failed',
                    'node_id': manifest_node['id']
                })

        elif break_type == 'checksum_mismatch':
            # Corrupt checksum
            artifact_node = next((n for n in chain['graph']['nodes'] if n['type'] == 'artifact'), None)
            
            for node in chain['graph']['nodes']:
                if node['type'] == 'manifest':
                    node['checksum'] = 'CORRUPTED_' + (node['checksum'] or 'unknown')

                if node['type'] == 'verification':
                    for check in node['checks']:
                        if check['name'] == 'Checksum Integrity':
                            check['passed'] = False
                    node['all_checks_passed'] = False
            
            if artifact_node:
                chain['weak_links'].append({
                    'type': 'checksum_mismatch',
                    'severity': 'critical',
                    'message': 'Artifact checksum does not match manifest',
                    'node_id': artifact_node['id']
                })

        elif break_type == 'unverified_registry':
            # Mark registry as unverified
            registry_node = next((n for n in chain['graph']['nodes'] if n['type'] == 'registry'), None)
            
            if registry_node:
                registry_node['published'] = False
                registry_node['status'] = 'unverified'

                for edge in chain['graph']['edges']:
                    if edge['type'] == 'registry':
                        edge['verified'] = False

                chain['weak_links'].append({
                    'type': 'unverified_registry',
                    'severity': 'high',
                    'message': 'Registry entry not properly verified',
                    'node_id': registry_node['id']
                })

        # Recalculate chain integrity
        chain['chain_integrity'] = len(chain['trust_violations']) == 0 and len(chain['weak_links']) == 0
        chain['overall_trust_score'] = crypto_chain_service._calculate_chain_trust(
            chain['graph']['nodes'],
            chain['graph']['edges']
        )

        return jsonify(chain), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Workflow Crypto Manifest Endpoints - PKI Mesh Journey Tracking
# ============================================================================

@crypto_chain_bp.route('/workflow/<workflow_id>/manifest', methods=['GET'])
def get_workflow_crypto_manifest(workflow_id):
    """
    Get the complete cryptographic manifest for a workflow.

    Shows the PKI mesh journey through all stages:
    - Mission creation
    - Orchestrator (GOVERNMENT trust domain)
    - Architect (EXECUTION trust domain)
    - Builder (EXECUTION trust domain)
    - Critic (EXECUTION trust domain)
    - Recorder (LOGGING trust domain)
    - Artifact publishing (LOGGING trust domain)

    Returns:
        Crypto manifest with:
        - Timeline of all Turing Tape entries
        - Trust domain flow
        - PKI mesh topology
        - Signature verification status
        - Chain integrity analysis
        - Weak links identification
    """
    try:
        manifest = crypto_manifest_service.get_workflow_manifest(
            workflow_id=workflow_id,
            verify_signatures=True
        )
        return jsonify(manifest), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@crypto_chain_bp.route('/workflow/<workflow_id>/manifest/text', methods=['GET'])
def get_workflow_crypto_manifest_text(workflow_id):
    """
    Get displayable/loggable text format of crypto manifest.

    Returns plain text suitable for console or log output.
    """
    try:
        manifest = crypto_manifest_service.get_workflow_manifest(
            workflow_id=workflow_id,
            verify_signatures=True
        )

        displayable_chain = manifest.get('displayable_chain', [])
        text_output = '\n'.join(displayable_chain)

        return Response(text_output, mimetype='text/plain'), 200
    except Exception as e:
        return Response(f"Error: {str(e)}", mimetype='text/plain'), 500


@crypto_chain_bp.route('/workflow/<workflow_id>/trust-flow', methods=['GET'])
def get_workflow_trust_flow(workflow_id):
    """
    Get just the trust domain flow for a workflow.

    Returns simplified view showing which trust domains signed each stage.
    """
    try:
        manifest = crypto_manifest_service.get_workflow_manifest(
            workflow_id=workflow_id,
            verify_signatures=False  # Skip verification for faster response
        )

        return jsonify({
            'workflow_id': workflow_id,
            'trust_flow': manifest.get('trust_flow', []),
            'pki_mesh': manifest.get('pki_mesh', {})
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@crypto_chain_bp.route('/workflow/<workflow_id>/integrity', methods=['GET'])
def get_workflow_integrity(workflow_id):
    """
    Get cryptographic integrity status for a workflow.

    Returns:
        - Overall integrity score (0-100)
        - Chain completeness
        - Signature validity
        - Weak links
        - Missing stages
    """
    try:
        manifest = crypto_manifest_service.get_workflow_manifest(
            workflow_id=workflow_id,
            verify_signatures=True
        )

        return jsonify({
            'workflow_id': workflow_id,
            'integrity': manifest.get('integrity', {}),
            'weak_links': manifest.get('weak_links', [])
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
