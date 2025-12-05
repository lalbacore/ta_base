"""
PKI Service - Bridges Flask API to PKIManager and CRLManager.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import Dict, Any, List, Optional
from app.data.seed_data import SAMPLE_CERTIFICATES, REVOKED_CERTIFICATES


class PKIService:
    """
    Service layer for PKI management.
    Bridges Flask API to PKIManager and CRLManager.
    """

    def __init__(self):
        # TODO: Initialize PKI managers when ready
        # from swarms.team_agent.crypto.pki import PKIManager
        # from swarms.team_agent.crypto.crl import CRLManager
        # self.pki_manager = PKIManager()
        # self.crl_manager = CRLManager()

        # Load seed data - SAMPLE_CERTIFICATES is already a dict keyed by domain
        self.certificates = SAMPLE_CERTIFICATES.copy()
        self.revoked = REVOKED_CERTIFICATES.copy()

    def get_all_certificates(self) -> List[Dict[str, Any]]:
        """Get status of all certificates."""
        # TODO: Get from pki_manager.get_certificate_info() for each domain
        return list(self.certificates.values())

    def get_certificate(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get certificate details for a trust domain."""
        # TODO: Get from pki_manager.get_certificate_info(domain)
        return self.certificates.get(domain)

    def renew_certificate(self, domain: str) -> None:
        """Renew a certificate (same key)."""
        # TODO: Call pki_manager.renew_certificate(domain)
        pass

    def rotate_certificate(self, domain: str) -> None:
        """Rotate a certificate (new key)."""
        # TODO: Call pki_manager.rotate_certificate(domain)
        pass

    def revoke_certificate(self, serial_number: str, reason: str) -> None:
        """Revoke a certificate."""
        # TODO: Call crl_manager.revoke_certificate(serial_number, reason)
        pass

    def get_revoked_certificates(self) -> List[Dict[str, Any]]:
        """Get list of revoked certificates."""
        # TODO: Get from crl_manager.get_revocation_info()
        return self.revoked

    def get_crl(self) -> Dict[str, Any]:
        """Get Certificate Revocation List."""
        # TODO: Get CRL data from crl_manager
        return {
            'version': 2,
            'issuer': 'Root CA',
            'last_update': SAMPLE_CERTIFICATES[0]['issued_date'],
            'next_update': SAMPLE_CERTIFICATES[0]['expiry_date'],
            'revoked_certificates': self.revoked
        }

    def generate_certificate(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new certificate."""
        # TODO: Call pki_manager.generate_certificate(domain, subject, key_size, algorithm, validity_days)
        from datetime import datetime, timedelta
        import secrets

        domain = cert_data.get('domain')
        subject = cert_data.get('subject', f'Team Agent {domain.capitalize()}')
        key_size = cert_data.get('key_size', 2048)
        algorithm = cert_data.get('algorithm', 'SHA256-RSA')
        validity_days = cert_data.get('validity_days', 365)

        # Generate certificate data
        issued_date = datetime.now()
        expiry_date = issued_date + timedelta(days=validity_days)
        days_until_expiry = validity_days

        # Determine status based on days until expiry
        if days_until_expiry < 7:
            status = 'expiring_soon'
        elif days_until_expiry < 30:
            status = 'expiring_soon'
        else:
            status = 'valid'

        new_cert = {
            'domain': domain,
            'subject': subject,
            'issuer': 'Root CA',
            'serial_number': secrets.token_hex(16),
            'valid_from': issued_date.isoformat(),
            'valid_to': expiry_date.isoformat(),
            'status': status,
            'days_until_expiry': days_until_expiry,
            'key_size': key_size,
            'signature_algorithm': algorithm
        }

        # Add to certificates dict
        self.certificates[domain] = new_cert

        return new_cert


# Singleton instance
pki_service = PKIService()
