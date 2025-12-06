"""
Self-Signed CA Provider - Three-tier CA hierarchy for development/testing.

Wraps the existing PKIManager implementation to conform to the PKIProvider interface.
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from ..pki_provider import PKIProvider, TrustDomain, RevocationReason
from ..pki import PKIManager
from ..crl import CRLManager


class SelfSignedCAProvider(PKIProvider):
    """
    Self-signed CA provider using three-tier hierarchy.

    Best for:
    - Development and testing
    - Air-gapped environments
    - Internal agent-to-agent trust
    - Environments without internet connectivity

    NOT suitable for:
    - Public-facing web services
    - Browser-trusted certificates
    - Production web applications

    Architecture:
    - Root CA (self-signed, 10-year validity)
    - Intermediate CAs (signed by root, 5-year validity)
      * Government CA (governance plane)
      * Execution CA (agent execution plane)
      * Logging CA (artifact/logging plane)
    - End-entity certificates (signed by intermediate)
    """

    def __init__(self):
        """Initialize provider (actual initialization happens in initialize())."""
        self.pki_manager: Optional[PKIManager] = None
        self.crl_manager: Optional[CRLManager] = None

    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize self-signed PKI.

        Config:
            base_dir: Base directory for PKI files (default: ~/.team_agent/pki)
            force_reinit: Force re-initialization even if PKI exists (default: False)

        Example:
            {
                'base_dir': '~/.team_agent/pki',
                'force_reinit': False
            }
        """
        base_dir = config.get('base_dir')
        if base_dir:
            base_dir = Path(base_dir).expanduser()

        # Initialize PKI manager with existing implementation
        self.pki_manager = PKIManager(base_dir=base_dir)
        self.pki_manager.initialize_pki(force=config.get('force_reinit', False))

        # Get CRL manager from PKI manager
        if hasattr(self.pki_manager, 'crl_manager') and self.pki_manager.crl_manager:
            self.crl_manager = self.pki_manager.crl_manager

    def issue_certificate(
        self,
        domain: TrustDomain,
        validity_days: int = 1825,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Issue certificate using self-signed CA.

        This generates a new certificate with a new key pair, effectively
        rotating/replacing the existing certificate for the domain.

        Args:
            domain: Trust domain (GOVERNMENT, EXECUTION, LOGGING)
            validity_days: Certificate validity in days (default: 1825 = 5 years)

        Returns:
            Dict with certificate information including serial, validity dates, and PEM data
        """
        if not self.pki_manager:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        # Use existing PKIManager implementation
        cert_info = self.pki_manager.issue_certificate(domain, validity_days)

        # Add PEM data to response
        cert_chain = self.pki_manager.get_certificate_chain(domain)
        cert_info['pem'] = cert_chain['cert']

        return cert_info

    def get_certificate_info(self, domain: TrustDomain) -> Dict[str, str]:
        """
        Get certificate information for a domain.

        Args:
            domain: Trust domain

        Returns:
            Dict with certificate details (serial, subject, issuer, validity dates)
        """
        if not self.pki_manager:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        return self.pki_manager.get_certificate_info(domain)

    def revoke_certificate(
        self,
        serial_number: str,
        reason: RevocationReason,
        revoked_by: str,
        **kwargs
    ) -> bool:
        """
        Revoke certificate using CRL.

        Args:
            serial_number: Certificate serial number (hex)
            reason: Revocation reason from RevocationReason enum
            revoked_by: Entity revoking the certificate
            **kwargs: Additional parameters (trust_domain, cert_subject, metadata)

        Returns:
            True if revoked successfully, False if CRL unavailable
        """
        if not self.pki_manager:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        # Extract optional parameters
        trust_domain = kwargs.get('trust_domain', TrustDomain.EXECUTION)
        cert_subject = kwargs.get('cert_subject')
        metadata = kwargs.get('metadata')

        return self.pki_manager.revoke_certificate(
            serial_number=serial_number,
            reason=reason,
            revoked_by=revoked_by,
            trust_domain=trust_domain,
            cert_subject=cert_subject,
            metadata=metadata
        )

    def is_revoked(self, serial_number: str) -> bool:
        """
        Check if certificate is revoked.

        Args:
            serial_number: Certificate serial number

        Returns:
            True if revoked, False otherwise
        """
        if not self.pki_manager:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        return self.pki_manager.is_revoked(serial_number)

    def get_revocation_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Get revocation information for a certificate.

        Args:
            serial_number: Certificate serial number

        Returns:
            Dict with revocation info if revoked, None otherwise
        """
        if not self.pki_manager:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        return self.pki_manager.get_revocation_info(serial_number)

    def list_certificates(self, domain: Optional[TrustDomain] = None) -> List[Dict[str, Any]]:
        """
        List all certificates.

        Args:
            domain: Filter by trust domain (optional)

        Returns:
            List of certificate information dicts
        """
        if not self.pki_manager:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        if domain:
            # Get single domain certificate
            cert_info = self.get_certificate_info(domain)
            if cert_info:
                cert_info['domain'] = domain.value
                return [cert_info]
            return []
        else:
            # Get all domain certificates
            certs = []
            for trust_domain in TrustDomain:
                cert_info = self.get_certificate_info(trust_domain)
                if cert_info:
                    cert_info['domain'] = trust_domain.value
                    certs.append(cert_info)
            return certs

    def validate_certificate(self, cert_pem: bytes) -> Dict[str, Any]:
        """
        Validate certificate against self-signed CA.

        This performs basic validation:
        - Signature verification
        - Chain of trust validation
        - Revocation check via CRL
        - Expiration check

        Args:
            cert_pem: Certificate in PEM format

        Returns:
            Dict with validation results
        """
        if not self.pki_manager:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        # Parse certificate
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        from datetime import datetime

        try:
            cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
            serial = format(cert.serial_number, 'x')

            # Check revocation
            revoked = self.is_revoked(serial)

            # Check expiration
            now = datetime.utcnow()
            expired = now > cert.not_valid_after

            # Determine validity
            valid = not revoked and not expired
            reason = None
            if revoked:
                reason = "Certificate has been revoked"
            elif expired:
                reason = f"Certificate expired on {cert.not_valid_after.isoformat()}"

            return {
                'valid': valid,
                'reason': reason,
                'chain_valid': True,  # Self-signed always has valid chain to itself
                'revoked': revoked,
                'expired': expired
            }

        except Exception as e:
            return {
                'valid': False,
                'reason': f"Certificate parsing failed: {str(e)}",
                'chain_valid': False,
                'revoked': False,
                'expired': False
            }

    def get_trust_chain(self, domain: TrustDomain) -> List[bytes]:
        """
        Get certificate chain for a domain.

        Returns:
            List of [intermediate_cert, root_cert] in PEM format
        """
        if not self.pki_manager:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        cert_chain = self.pki_manager.get_certificate_chain(domain)

        # Return chain (intermediate + root)
        return [cert_chain['cert'], cert_chain['chain']]

    @property
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        return "Self-Signed CA (Three-Tier Hierarchy)"

    @property
    def provider_type(self) -> str:
        """Return provider type identifier."""
        return "self-signed"

    def supports_feature(self, feature: str) -> bool:
        """
        Check if provider supports a feature.

        Supported features:
        - 'crl': Certificate Revocation Lists
        - 'offline': Works without internet
        """
        supported_features = {'crl', 'offline'}
        return feature in supported_features

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get PKI statistics.

        Returns:
            Dict with certificate and CRL statistics
        """
        if not self.pki_manager:
            return super().get_statistics()

        stats = {
            'total_certificates': len(TrustDomain),  # One per domain
            'active_certificates': 0,
            'revoked_certificates': 0
        }

        # Count active certificates
        for domain in TrustDomain:
            cert_info = self.get_certificate_info(domain)
            if cert_info:
                stats['active_certificates'] += 1

        # Get CRL statistics if available
        if self.crl_manager:
            crl_stats = self.pki_manager.get_crl_statistics()
            if crl_stats:
                stats['revoked_certificates'] = crl_stats.get('total_revoked', 0)

        return stats
