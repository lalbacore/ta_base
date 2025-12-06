"""
Crypto Chain API - Visualize cryptographic provenance of artifacts.
"""
from flask import Blueprint, jsonify
from app.services.crypto_chain_service import crypto_chain_service

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
            for node in chain['graph']['nodes']:
                if node['type'] == 'agent':
                    node['trust_score'] = 45.0
                    node['status'] = 'untrusted'

            chain['trust_violations'].append({
                'type': 'low_trust_score',
                'severity': 'critical',
                'message': 'Agent trust score below threshold (45 < 75)',
                'node_id': next(n['id'] for n in chain['graph']['nodes'] if n['type'] == 'agent')
            })

        elif break_type == 'signature_invalid':
            # Mark signature as invalid
            for node in chain['graph']['nodes']:
                if node['type'] == 'manifest':
                    node['verified'] = False
                    node['signature'] = None

            # Mark signing edge as unverified
            for edge in chain['graph']['edges']:
                if edge['type'] == 'signature':
                    edge['verified'] = False

            chain['weak_links'].append({
                'type': 'invalid_signature',
                'severity': 'critical',
                'message': 'Artifact signature verification failed',
                'node_id': next(n['id'] for n in chain['graph']['nodes'] if n['type'] == 'manifest')
            })

        elif break_type == 'checksum_mismatch':
            # Corrupt checksum
            for node in chain['graph']['nodes']:
                if node['type'] == 'manifest':
                    node['checksum'] = 'CORRUPTED_' + (node['checksum'] or 'unknown')

                if node['type'] == 'verification':
                    for check in node['checks']:
                        if check['name'] == 'Checksum Integrity':
                            check['passed'] = False
                    node['all_checks_passed'] = False

            chain['weak_links'].append({
                'type': 'checksum_mismatch',
                'severity': 'critical',
                'message': 'Artifact checksum does not match manifest',
                'node_id': next(n['id'] for n in chain['graph']['nodes'] if n['type'] == 'artifact')
            })

        elif break_type == 'unverified_registry':
            # Mark registry as unverified
            for node in chain['graph']['nodes']:
                if node['type'] == 'registry':
                    node['published'] = False
                    node['status'] = 'unverified'

            for edge in chain['graph']['edges']:
                if edge['type'] == 'registry':
                    edge['verified'] = False

            chain['weak_links'].append({
                'type': 'unverified_registry',
                'severity': 'high',
                'message': 'Registry entry not properly verified',
                'node_id': next(n['id'] for n in chain['graph']['nodes'] if n['type'] == 'registry')
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
