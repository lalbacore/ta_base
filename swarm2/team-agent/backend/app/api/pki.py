"""
PKI Management API - Certificate lifecycle, rotation, revocation, and CRL operations.
"""
from flask import Blueprint, request, jsonify
from app.services.pki_service import pki_service
from app.services.cert_lifecycle_service import cert_lifecycle_service

pki_bp = Blueprint('pki', __name__)


# ============================================================================
# Certificate Status & Information
# ============================================================================

@pki_bp.route('/status', methods=['GET'])
def get_all_certificates():
    """
    Get status of all certificates across all trust domains.

    Returns:
        List of certificate details with expiration status
    """
    try:
        certificates = pki_service.get_all_certificates()
        return jsonify({
            'certificates': certificates,
            'count': len(certificates)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/certificate/<domain>', methods=['GET'])
def get_certificate(domain):
    """
    Get certificate details for a specific trust domain.

    Args:
        domain: Trust domain (government, execution, logging)

    Returns:
        Certificate details
    """
    try:
        cert = pki_service.get_certificate(domain)
        if not cert:
            return jsonify({'error': f'Certificate not found for domain: {domain}'}), 404
        return jsonify(cert), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Certificate Rotation & Renewal
# ============================================================================

@pki_bp.route('/certificate/<domain>/rotate', methods=['POST'])
def rotate_certificate(domain):
    """
    Rotate certificate with new key pair (recommended for security).

    This generates a completely new certificate with a new key pair
    and revokes the old certificate.

    Args:
        domain: Trust domain to rotate

    Returns:
        Rotation details including old and new serial numbers
    """
    try:
        result = pki_service.rotate_certificate(domain)
        return jsonify({
            'success': True,
            'message': f'Certificate rotated successfully for {domain}',
            'rotation': result
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Certificate Revocation
# ============================================================================

@pki_bp.route('/certificate/<serial>/revoke', methods=['POST'])
def revoke_certificate_by_serial(serial):
    """
    Revoke a certificate by serial number.

    Request body:
        {
            "reason": "KEY_COMPROMISE" | "SUPERSEDED" | "CESSATION_OF_OPERATION" | etc.
            "revoked_by": "admin" (optional)
            "domain": "execution" (optional, for faster lookup)
        }

    Returns:
        Revocation status
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'UNSPECIFIED')
        revoked_by = data.get('revoked_by', 'admin')
        domain = data.get('domain')

        result = pki_service.revoke_certificate(
            serial_number=serial,
            reason=reason,
            revoked_by=revoked_by,
            domain=domain
        )

        if result.get('revoked'):
            return jsonify({
                'success': True,
                'message': 'Certificate revoked successfully',
                'revocation': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Revocation failed')
            }), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/revoked', methods=['GET'])
def get_revoked_certificates():
    """
    Get list of revoked certificates.

    Query parameters:
        domain: Filter by trust domain (optional)
        limit: Maximum number to return (default: 100)

    Returns:
        List of revoked certificate records
    """
    try:
        domain = request.args.get('domain')
        limit = int(request.args.get('limit', 100))

        revoked = pki_service.get_revoked_certificates(domain=domain, limit=limit)

        return jsonify({
            'revoked_certificates': revoked,
            'count': len(revoked),
            'domain': domain if domain else 'all'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Certificate Lifecycle Management
# ============================================================================

@pki_bp.route('/lifecycle/status', methods=['GET'])
def get_lifecycle_status():
    """
    Get certificate lifecycle status with expiration warnings.

    Returns:
        {
            "summary": {
                "expired": 0,
                "critical": 1,
                "expiring_soon": 0,
                "warning": 1,
                "valid": 1
            },
            "alerts": [...],
            "certificates_by_status": {...},
            "requires_action": 1
        }
    """
    try:
        status = cert_lifecycle_service.get_lifecycle_summary()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/lifecycle/auto-renew', methods=['POST'])
def auto_renew_certificates():
    """
    Automatically renew expiring certificates.

    This will rotate certificates that are:
    - Expired
    - Critical (< 7 days)
    - Expiring soon (< 30 days)

    Request body (optional):
        {
            "dry_run": true  // Simulate without making changes
        }

    Returns:
        List of renewal results
    """
    try:
        data = request.get_json() or {}
        dry_run = data.get('dry_run', False)

        if dry_run:
            # Simulation mode
            result = cert_lifecycle_service.simulate_renewal()
            return jsonify(result), 200
        else:
            # Actually renew
            results = cert_lifecycle_service.auto_renew_expiring(dry_run=False)

            successful = len([r for r in results if r.get('status') == 'success'])
            failed = len([r for r in results if r.get('status') == 'failed'])

            return jsonify({
                'success': True,
                'message': f'Renewed {successful} certificate(s), {failed} failed',
                'results': results,
                'summary': {
                    'total': len(results),
                    'successful': successful,
                    'failed': failed
                }
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/lifecycle/simulate', methods=['GET'])
def simulate_renewal():
    """
    Simulate auto-renewal without making changes.

    Returns what would happen if auto-renewal was triggered.

    Returns:
        Simulation results showing which certificates would be renewed
    """
    try:
        result = cert_lifecycle_service.simulate_renewal()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Provider Information
# ============================================================================

@pki_bp.route('/providers', methods=['GET'])
def get_provider_info():
    """
    Get information about configured PKI providers.

    Query parameters:
        domain: Specific domain (optional, returns all if not specified)

    Returns:
        Provider information including type, features, and statistics
    """
    try:
        domain = request.args.get('domain')
        info = pki_service.get_provider_info(domain)
        return jsonify(info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get overall PKI statistics.

    Returns:
        Aggregate statistics across all providers
    """
    try:
        stats = pki_service.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Legacy/Compatibility Endpoints
# ============================================================================

@pki_bp.route('/renew/<domain>', methods=['POST'])
def renew_certificate(domain):
    """
    DEPRECATED: Use /certificate/<domain>/rotate instead.

    Rotate a certificate (new key).
    """
    try:
        result = pki_service.rotate_certificate(domain)
        return jsonify({
            'status': 'rotated',
            'message': 'This endpoint is deprecated. Use /certificate/<domain>/rotate instead.',
            'result': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/rotate/<domain>', methods=['POST'])
def rotate_certificate_legacy(domain):
    """
    DEPRECATED: Use /certificate/<domain>/rotate instead.

    Rotate a certificate (new key).
    """
    try:
        result = pki_service.rotate_certificate(domain)
        return jsonify({
            'status': 'rotated',
            'message': 'This endpoint is deprecated. Use /certificate/<domain>/rotate instead.',
            'result': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/revoke', methods=['POST'])
def revoke_certificate_legacy():
    """
    DEPRECATED: Use /certificate/<serial>/revoke instead.

    Revoke a certificate.
    """
    try:
        data = request.get_json() or {}
        serial_number = data.get('serial_number')
        reason = data.get('reason', 'UNSPECIFIED')
        revoked_by = data.get('revoked_by', 'admin')
        domain = data.get('domain')

        if not serial_number:
            return jsonify({'error': 'serial_number is required'}), 400

        result = pki_service.revoke_certificate(
            serial_number=serial_number,
            reason=reason,
            revoked_by=revoked_by,
            domain=domain
        )

        return jsonify({
            'status': 'revoked' if result.get('revoked') else 'failed',
            'message': 'This endpoint is deprecated. Use /certificate/<serial>/revoke instead.',
            'result': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
