"""
.well-known endpoints for Agent2Agent (A2A) protocol compliance.

Provides:
- /.well-known/agent.json - Agent Card discovery endpoint
"""
from flask import Blueprint, jsonify, request
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.database import get_backend_session
from app.models.agent import AgentCard, AgentCapabilityMapping, CapabilityRegistry
from swarms.team_agent.crypto.signing import Signer
from swarms.team_agent.crypto.pki import PKIManager, TrustDomain

well_known_bp = Blueprint('well_known', __name__)


def _get_pki_signer():
    """Get PKI signer for signing agent cards."""
    try:
        pki_manager = PKIManager()
        # Use EXECUTION trust domain for agent cards
        cert_chain = pki_manager.get_certificate_chain(TrustDomain.EXECUTION)

        signer = Signer(
            private_key_pem=cert_chain['key'],
            certificate_pem=cert_chain['cert'],
            signer_id='team_agent_registry'
        )
        return signer
    except Exception as e:
        print(f"Warning: Could not initialize PKI signer: {e}")
        return None


@well_known_bp.route('/.well-known/agent.json', methods=['GET'])
def get_agent_card():
    """
    A2A Protocol - Agent Card Discovery Endpoint.

    Returns agent card with:
    - Agent identity and metadata
    - Available capabilities
    - Pricing information
    - Reputation/trust scores
    - Cryptographic signature (if PKI enabled)

    Spec: https://agent2agent.ai/spec/v1.0/agent-card
    """
    try:
        # Query all active agents and their capabilities
        with get_backend_session() as session:
            agents = session.query(AgentCard).filter_by(status='active').all()

            # Get capabilities registry
            capabilities = session.query(CapabilityRegistry).filter_by(status='active').all()

            # Build agent card data structure
            agent_cards = []

            for agent in agents:
                # Get agent's capabilities through mappings
                capability_mappings = session.query(AgentCapabilityMapping).filter_by(
                    agent_id=agent.agent_id
                ).all()

                agent_capabilities = []
                for mapping in capability_mappings:
                    cap = session.query(CapabilityRegistry).filter_by(
                        capability_id=mapping.capability_id
                    ).first()

                    if cap:
                        agent_capabilities.append({
                            'capability_id': cap.capability_id,
                            'capability_name': cap.capability_name,
                            'capability_type': cap.capability_type,
                            'description': cap.description,
                            'domains': cap.domains if isinstance(cap.domains, list) else [],
                            'version': cap.version,
                            'is_primary': mapping.is_primary,
                            'priority': mapping.priority,
                            'times_used': mapping.times_used,
                            'success_rate': mapping.success_rate
                        })

                # Build agent card
                agent_card = {
                    'agent_id': agent.agent_id,
                    'agent_name': agent.agent_name,
                    'agent_type': agent.agent_type,
                    'description': agent.description,
                    'version': agent.version,
                    'capabilities': agent_capabilities,
                    'specialties': agent.specialties if isinstance(agent.specialties, list) else [],
                    'supported_languages': agent.supported_languages if isinstance(agent.supported_languages, list) else [],
                    'trust_score': agent.trust_score,
                    'total_invocations': agent.total_invocations,
                    'success_rate': agent.success_rate,
                    'average_rating': agent.average_rating,
                    'status': agent.status,
                    'certificate_serial': agent.certificate_serial,
                    'trust_domain': agent.trust_domain,
                    'author': agent.author,
                    'homepage': agent.homepage,
                    'license': agent.license,
                    'tags': agent.tags if isinstance(agent.tags, list) else [],
                    'created_at': agent.created_at.isoformat() if agent.created_at else None,
                    'updated_at': agent.updated_at.isoformat() if agent.updated_at else None
                }

                agent_cards.append(agent_card)

            # Build complete agent discovery response
            response_data = {
                'protocol': 'A2A',
                'version': '1.0',
                'provider': {
                    'name': 'Team Agent',
                    'url': request.url_root.rstrip('/'),
                    'description': 'Capability-driven multi-agent orchestration framework'
                },
                'agents': agent_cards,
                'total_agents': len(agent_cards),
                'capabilities_available': len(capabilities),
                'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
            }

            # Add cryptographic signature if PKI is available
            signer = _get_pki_signer()
            if signer:
                signed_data = signer.sign(response_data)
                response_data['signature'] = {
                    'signature': signed_data.signature,
                    'signer': signed_data.signer,
                    'cert_subject': signed_data.cert_subject,
                    'timestamp': signed_data.timestamp
                }

            return jsonify(response_data), 200

    except Exception as e:
        import traceback
        print(f"Error generating agent card: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate agent card',
            'message': str(e)
        }), 500


@well_known_bp.route('/.well-known/capabilities.json', methods=['GET'])
def get_capabilities_manifest():
    """
    A2A Protocol - Capabilities Manifest Endpoint.

    Returns detailed capability catalog independent of agents.
    Useful for capability discovery and matching.
    """
    try:
        with get_backend_session() as session:
            capabilities = session.query(CapabilityRegistry).filter_by(status='active').all()

            capability_list = []
            for cap in capabilities:
                capability_list.append({
                    'capability_id': cap.capability_id,
                    'capability_name': cap.capability_name,
                    'capability_type': cap.capability_type,
                    'description': cap.description,
                    'version': cap.version,
                    'domains': cap.domains if isinstance(cap.domains, list) else [],
                    'keywords': cap.keywords if isinstance(cap.keywords, list) else [],
                    'tags': cap.tags if isinstance(cap.tags, list) else [],
                    'module_path': cap.module_path,
                    'class_name': cap.class_name,
                    'author': cap.author,
                    'license': cap.license,
                    'created_at': cap.created_at.isoformat() if cap.created_at else None
                })

            response_data = {
                'protocol': 'A2A',
                'version': '1.0',
                'capabilities': capability_list,
                'total_capabilities': len(capability_list),
                'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
            }

            # Add cryptographic signature if PKI is available
            signer = _get_pki_signer()
            if signer:
                signed_data = signer.sign(response_data)
                response_data['signature'] = {
                    'signature': signed_data.signature,
                    'signer': signed_data.signer,
                    'cert_subject': signed_data.cert_subject,
                    'timestamp': signed_data.timestamp
                }

            return jsonify(response_data), 200

    except Exception as e:
        import traceback
        print(f"Error generating capabilities manifest: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate capabilities manifest',
            'message': str(e)
        }), 500
