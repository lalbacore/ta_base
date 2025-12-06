"""
Authentication and authorization for Team Agent Backend.

Implements role-based access control with government agent verification.

Current: Header-based authentication for UI demo
Future: Full PKI certificate verification
"""
import sys
import os
from functools import wraps
from flask import request, jsonify
from typing import Optional, Callable

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def require_government_role(f: Callable) -> Callable:
    """
    Decorator to require government agent role for endpoint access.

    Current Implementation (UI Demo):
    - Checks for X-Agent-Role header with value 'government'
    - Simple header-based authentication for testing

    Future Implementation (Production):
    - Verify client certificate from government trust domain
    - Check certificate is not revoked via CRLManager
    - Validate certificate chain to root CA

    Usage:
        @governance_bp.route('/policies', methods=['POST'])
        @require_government_role
        def create_policy():
            # Only government agents can access
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Current: Simple header check for UI demo
        agent_role = request.headers.get('X-Agent-Role')

        if agent_role != 'government':
            return jsonify({
                'error': 'Forbidden',
                'message': 'Only government agents can modify policies',
                'required_role': 'government',
                'provided_role': agent_role
            }), 403

        # TODO: Production implementation
        # 1. Extract client certificate from request
        # 2. Verify certificate is from government domain
        # 3. Check certificate is not revoked
        # Example:
        # cert = request.environ.get('SSL_CLIENT_CERT')
        # if not verify_government_certificate(cert):
        #     return jsonify({'error': 'Invalid certificate'}), 403

        return f(*args, **kwargs)

    return decorated_function


def verify_government_certificate(cert_pem: str) -> bool:
    """
    Verify a certificate belongs to the government trust domain.

    TODO: Implement full PKI verification:
    1. Parse certificate from PEM format
    2. Verify certificate chain to government CA
    3. Check certificate is not expired
    4. Check certificate is not revoked (CRLManager)
    5. Verify certificate has government domain in subject

    Args:
        cert_pem: Certificate in PEM format

    Returns:
        bool: True if certificate is valid government cert
    """
    # TODO: Implement using PKIManager and CRLManager
    # from swarms.team_agent.crypto.pki import PKIManager, TrustDomain
    # from swarms.team_agent.crypto.crl import CRLManager
    #
    # pki_manager = PKIManager()
    # crl_manager = CRLManager()
    #
    # 1. Parse certificate
    # cert = x509.load_pem_x509_certificate(cert_pem.encode())
    #
    # 2. Verify it's from government domain
    # subject = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    # if 'government' not in subject.lower():
    #     return False
    #
    # 3. Check not revoked
    # serial = cert.serial_number
    # if crl_manager.is_revoked(serial):
    #     return False
    #
    # 4. Verify certificate chain
    # # TODO: Implement chain verification
    #
    # return True

    pass


def get_agent_role() -> Optional[str]:
    """
    Get the current agent role from the request.

    Returns:
        str: Agent role ('government', 'execution', 'logging', None)
    """
    return request.headers.get('X-Agent-Role')


def set_agent_context(role: str, agent_id: Optional[str] = None):
    """
    Set agent context for the current request.

    This is used for audit logging and tracking which agent
    performed an action.

    Args:
        role: Agent role ('government', 'execution', 'logging')
        agent_id: Optional agent identifier
    """
    # Store in Flask's g object for request context
    from flask import g
    g.agent_role = role
    g.agent_id = agent_id


# Export commonly used functions
__all__ = [
    'require_government_role',
    'verify_government_certificate',
    'get_agent_role',
    'set_agent_context'
]
