"""
PKI Provider Interface - Abstract base for pluggable PKI backends.

This module defines the interface that all PKI providers must implement,
enabling Team Agent to use different certificate authorities and trust models.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum


class TrustDomain(Enum):
    """Trust domains corresponding to agent planes."""
    GOVERNMENT = "government"
    EXECUTION = "execution"
    LOGGING = "logging"


class RevocationReason(Enum):
    """Certificate revocation reasons (RFC 5280)."""
    UNSPECIFIED = 0
    KEY_COMPROMISE = 1
    CA_COMPROMISE = 2
    AFFILIATION_CHANGED = 3
    SUPERSEDED = 4
    CESSATION_OF_OPERATION = 5
    CERTIFICATE_HOLD = 6
    REMOVE_FROM_CRL = 8
    PRIVILEGE_WITHDRAWN = 9
    AA_COMPROMISE = 10


class PKIProvider(ABC):
    """
    Abstract base class for PKI providers.

    All PKI implementations (self-signed, Let's Encrypt, blockchain, etc.)
    must implement this interface to ensure compatibility with Team Agent.

    Example implementations:
    - SelfSignedCAProvider: Three-tier self-signed CA (current)
    - ACMEProvider: Let's Encrypt / ACME protocol
    - BlockchainPKIProvider: Decentralized trust via blockchain
    - EnterpriseCAProvider: Integration with corporate PKI
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the PKI provider with configuration.

        Args:
            config: Provider-specific configuration dict

        Example config for self-signed:
            {
                'base_dir': '~/.team_agent/pki',
                'force_reinit': False
            }

        Example config for ACME:
            {
                'email': 'admin@example.com',
                'staging': False,
                'domain_name': 'example.com'
            }
        """
        pass

    @abstractmethod
    def issue_certificate(
        self,
        domain: TrustDomain,
        validity_days: int = 1825,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Issue a new certificate for a trust domain.

        Args:
            domain: Trust domain (GOVERNMENT, EXECUTION, LOGGING)
            validity_days: Certificate validity period in days
            **kwargs: Provider-specific parameters

        Returns:
            Dict with certificate information:
            - serial: Certificate serial number (hex string)
            - not_before: Validity start date (ISO format string)
            - not_after: Validity end date (ISO format string)
            - subject: Certificate subject DN
            - issuer: Certificate issuer DN
            - pem: Certificate in PEM format (bytes) - optional

        Raises:
            ValueError: If domain is invalid or certificate issuance fails
        """
        pass

    @abstractmethod
    def get_certificate_info(self, domain: TrustDomain) -> Dict[str, str]:
        """
        Get certificate information for a trust domain.

        Args:
            domain: Trust domain

        Returns:
            Dict with certificate details:
            - serial: Certificate serial number
            - subject: Certificate subject DN
            - issuer: Certificate issuer DN
            - not_before: Validity start date
            - not_after: Validity end date

        Returns empty dict if no certificate exists for domain.
        """
        pass

    @abstractmethod
    def revoke_certificate(
        self,
        serial_number: str,
        reason: RevocationReason,
        revoked_by: str,
        **kwargs
    ) -> bool:
        """
        Revoke a certificate.

        Args:
            serial_number: Certificate serial number (hex string)
            reason: Revocation reason (from RevocationReason enum)
            revoked_by: Entity revoking the certificate (username/agent)
            **kwargs: Provider-specific parameters

        Returns:
            True if revoked successfully, False otherwise

        Raises:
            ValueError: If serial_number is invalid
        """
        pass

    @abstractmethod
    def is_revoked(self, serial_number: str) -> bool:
        """
        Check if certificate is revoked.

        Args:
            serial_number: Certificate serial number (hex string)

        Returns:
            True if revoked, False otherwise
        """
        pass

    @abstractmethod
    def get_revocation_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Get revocation information for a certificate.

        Args:
            serial_number: Certificate serial number

        Returns:
            Dict with revocation info if revoked:
            - serial_number: Certificate serial
            - revocation_date: When certificate was revoked
            - reason: Revocation reason
            - revoked_by: Who revoked it

            None if certificate is not revoked
        """
        pass

    @abstractmethod
    def list_certificates(self, domain: Optional[TrustDomain] = None) -> List[Dict[str, Any]]:
        """
        List all certificates.

        Args:
            domain: Filter by trust domain (optional)

        Returns:
            List of certificate information dicts

        Example:
            [
                {
                    'domain': 'government',
                    'serial': 'abc123',
                    'subject': 'CN=Team Agent Government CA',
                    'not_after': '2029-01-01T00:00:00'
                }
            ]
        """
        pass

    @abstractmethod
    def validate_certificate(self, cert_pem: bytes) -> Dict[str, Any]:
        """
        Validate a certificate against this PKI.

        Args:
            cert_pem: Certificate in PEM format (bytes)

        Returns:
            Dict with validation result:
            - valid: Boolean - overall validity
            - reason: String - reason if invalid (None if valid)
            - chain_valid: Boolean - chain of trust valid
            - revoked: Boolean - certificate revoked
            - expired: Boolean - certificate expired

        Example:
            {
                'valid': False,
                'reason': 'Certificate has been revoked',
                'chain_valid': True,
                'revoked': True,
                'expired': False
            }
        """
        pass

    @abstractmethod
    def get_trust_chain(self, domain: TrustDomain) -> List[bytes]:
        """
        Get trust chain (certificate chain) for a domain.

        Args:
            domain: Trust domain

        Returns:
            List of certificates in PEM format (bytes), ordered from
            leaf certificate to root CA

        Example:
            [
                b'-----BEGIN CERTIFICATE-----\n...',  # Leaf cert
                b'-----BEGIN CERTIFICATE-----\n...',  # Intermediate CA
                b'-----BEGIN CERTIFICATE-----\n...'   # Root CA
            ]
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return human-readable provider name.

        Example: "Self-Signed CA (Three-Tier Hierarchy)"
        """
        pass

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """
        Return provider type identifier.

        Used in configuration files and factory.

        Example: 'self-signed', 'acme', 'blockchain', 'enterprise'
        """
        pass

    # Optional helper methods (with default implementations)

    def supports_feature(self, feature: str) -> bool:
        """
        Check if provider supports a specific feature.

        Args:
            feature: Feature name (e.g., 'ocsp', 'crl', 'auto_renewal')

        Returns:
            True if feature is supported, False otherwise

        Override this method to advertise provider capabilities.
        """
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get provider statistics.

        Returns:
            Dict with statistics:
            - total_certificates: Total certificates issued
            - revoked_certificates: Total revoked
            - active_certificates: Currently valid certificates

        Override this method to provide provider-specific stats.
        """
        return {
            'total_certificates': 0,
            'revoked_certificates': 0,
            'active_certificates': 0
        }
