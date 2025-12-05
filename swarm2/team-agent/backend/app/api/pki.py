"""
PKI Management API - Certificate lifecycle and CRL operations.
"""
from flask import Blueprint, request, jsonify
from app.services.pki_service import pki_service

pki_bp = Blueprint('pki', __name__)


@pki_bp.route('/status', methods=['GET'])
def get_all_certificates():
    """Get status of all certificates."""
    try:
        certificates = pki_service.get_all_certificates()
        return jsonify(certificates), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/certificate/<domain>', methods=['GET'])
def get_certificate(domain):
    """Get certificate details for a trust domain."""
    try:
        cert = pki_service.get_certificate(domain)
        if not cert:
            return jsonify({'error': 'Certificate not found'}), 404
        return jsonify(cert), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/renew/<domain>', methods=['POST'])
def renew_certificate(domain):
    """Renew a certificate (same key)."""
    try:
        pki_service.renew_certificate(domain)
        return jsonify({'status': 'renewed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/rotate/<domain>', methods=['POST'])
def rotate_certificate(domain):
    """Rotate a certificate (new key)."""
    try:
        pki_service.rotate_certificate(domain)
        return jsonify({'status': 'rotated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/revoke', methods=['POST'])
def revoke_certificate():
    """Revoke a certificate."""
    try:
        data = request.get_json()
        serial_number = data.get('serial_number')
        reason = data.get('reason', 'unspecified')
        pki_service.revoke_certificate(serial_number, reason)
        return jsonify({'status': 'revoked'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/revoked', methods=['GET'])
def get_revoked_certificates():
    """Get list of revoked certificates."""
    try:
        revoked = pki_service.get_revoked_certificates()
        return jsonify(revoked), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pki_bp.route('/crl', methods=['GET'])
def get_crl():
    """Get Certificate Revocation List."""
    try:
        crl = pki_service.get_crl()
        return jsonify(crl), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
