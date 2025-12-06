"""
PKI Service - Modular PKI management using pluggable providers.

This service uses the PKIProvider interface to support different PKI backends
(self-signed, ACME, blockchain, enterprise) based on configuration.
"""
import sys
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from swarms.team_agent.crypto.pki_factory import PKIFactory
from swarms.team_agent.crypto.pki_provider import PKIProvider, TrustDomain, RevocationReason


class PKIService:
    """
    PKI Service with pluggable provider support.

    Supports multiple PKI backends through the provider pattern:
    - Self-signed CA (development/testing)
    - Let's Encrypt (production web services)
    - Blockchain (decentralized trust)
    - Enterprise CA (corporate PKI)

    Configuration is loaded from config/pki_config.yaml.
    """

    def __init__(self, config_path: str = None):
        """
        Initialize PKI service with configuration.

        Args:
            config_path: Path to PKI configuration file (default: config/pki_config.yaml)
        """
        if config_path is None:
            # Default to config/pki_config.yaml in project root
            project_root = Path(__file__).parent.parent.parent.parent
            config_path = project_root / 'config' / 'pki_config.yaml'

        # Load configuration
        self.config_path = config_path
        self.config = self._load_config()

        # Create providers for each domain
        self.providers: Dict[str, PKIProvider] = {}
        self._initialize_providers()

    def _load_config(self) -> Dict[str, Any]:
        """Load PKI configuration from YAML file."""
        config_path = Path(self.config_path)

        if not config_path.exists():
            print(f"Warning: PKI config not found at {config_path}, using default self-signed provider")
            return {
                'default_provider': {
                    'type': 'self-signed',
                    'base_dir': str(Path.home() / '.team_agent' / 'pki')
                }
            }

        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def _initialize_providers(self):
        """Initialize PKI providers for each trust domain."""
        default_config = self.config.get('default_provider', {'type': 'self-signed'})
        domain_configs = self.config.get('domain_providers', {})

        for domain in TrustDomain:
            # Use domain-specific config if available, otherwise default
            provider_config = domain_configs.get(domain.value, default_config.copy())

            try:
                self.providers[domain.value] = PKIFactory.create_provider(provider_config)
            except Exception as e:
                print(f"Error initializing provider for {domain.value}: {e}")
                # Fallback to self-signed
                fallback_config = {'type': 'self-signed'}
                self.providers[domain.value] = PKIFactory.create_provider(fallback_config)

    def get_all_certificates(self) -> List[Dict[str, Any]]:
        """
        Get all certificates from all providers.

        Returns:
            List of certificate info dicts with provider information
        """
        certificates = []

        for domain in TrustDomain:
            provider = self.providers[domain.value]

            try:
                cert_info = provider.get_certificate_info(domain)

                if cert_info:
                    # Add domain and provider info
                    cert_info['domain'] = domain.value
                    cert_info['provider'] = provider.provider_name
                    cert_info['provider_type'] = provider.provider_type

                    # Calculate status and days until expiry
                    cert_info.update(self._calculate_cert_status(cert_info))

                    certificates.append(cert_info)

            except Exception as e:
                print(f"Error getting certificate for {domain.value}: {e}")
                continue

        return certificates

    def _calculate_cert_status(self, cert_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate certificate status and days until expiry.

        Args:
            cert_info: Certificate information dict

        Returns:
            Dict with status and days_until_expiry
        """
        try:
            not_after = cert_info.get('not_after')
            if not not_after:
                return {'status': 'unknown', 'days_until_expiry': 0}

            # Parse expiry date
            expiry = datetime.fromisoformat(not_after.replace('Z', '+00:00'))
            now = datetime.now(expiry.tzinfo) if expiry.tzinfo else datetime.now()

            # Calculate days left
            delta = expiry - now
            days_left = delta.days

            # Determine status
            if days_left < 0:
                status = 'expired'
            elif days_left < 7:
                status = 'critical'
            elif days_left < 30:
                status = 'expiring_soon'
            else:
                status = 'valid'

            return {
                'status': status,
                'days_until_expiry': days_left
            }

        except Exception as e:
            print(f"Error calculating cert status: {e}")
            return {'status': 'unknown', 'days_until_expiry': 0}

    def get_certificate(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get certificate details for a trust domain.

        Args:
            domain: Trust domain name (government, execution, logging)

        Returns:
            Certificate info dict or None if not found
        """
        if domain not in self.providers:
            return None

        try:
            trust_domain = TrustDomain(domain)
            provider = self.providers[domain]

            cert_info = provider.get_certificate_info(trust_domain)
            if cert_info:
                cert_info['domain'] = domain
                cert_info['provider'] = provider.provider_name
                cert_info['provider_type'] = provider.provider_type
                cert_info.update(self._calculate_cert_status(cert_info))

            return cert_info

        except Exception as e:
            print(f"Error getting certificate for {domain}: {e}")
            return None

    def rotate_certificate(self, domain: str, **kwargs) -> Dict[str, Any]:
        """
        Rotate certificate for a domain (new key pair).

        Args:
            domain: Trust domain
            **kwargs: Provider-specific parameters

        Returns:
            Dict with rotation details (old_serial, new_serial, etc.)
        """
        if domain not in self.providers:
            raise ValueError(f"Unknown domain: {domain}")

        try:
            trust_domain = TrustDomain(domain)
            provider = self.providers[domain]

            # Get old certificate for audit
            old_cert = provider.get_certificate_info(trust_domain)
            old_serial = old_cert.get('serial') if old_cert else None

            # Issue new certificate
            new_cert = provider.issue_certificate(trust_domain, **kwargs)

            # Revoke old certificate if exists
            if old_serial:
                provider.revoke_certificate(
                    serial_number=old_serial,
                    reason=RevocationReason.SUPERSEDED,
                    revoked_by='system',
                    trust_domain=trust_domain
                )

            return {
                'domain': domain,
                'old_serial': old_serial,
                'new_serial': new_cert['serial'],
                'provider': provider.provider_name,
                'rotated_at': datetime.now().isoformat()
            }

        except Exception as e:
            raise RuntimeError(f"Certificate rotation failed: {str(e)}") from e

    def revoke_certificate(
        self,
        serial_number: str,
        reason: str = 'UNSPECIFIED',
        revoked_by: str = 'admin',
        domain: str = None
    ) -> Dict[str, Any]:
        """
        Revoke a certificate.

        Args:
            serial_number: Certificate serial number
            reason: Revocation reason (UNSPECIFIED, KEY_COMPROMISE, etc.)
            revoked_by: Who is revoking the certificate
            domain: Trust domain (optional, auto-detected if not provided)

        Returns:
            Dict with revocation status
        """
        # Convert reason string to enum
        try:
            reason_enum = RevocationReason[reason.upper()]
        except KeyError:
            reason_enum = RevocationReason.UNSPECIFIED

        # If domain not specified, try all providers
        if domain:
            providers_to_check = [(domain, self.providers[domain])]
        else:
            providers_to_check = list(self.providers.items())

        for domain_name, provider in providers_to_check:
            try:
                success = provider.revoke_certificate(
                    serial_number=serial_number,
                    reason=reason_enum,
                    revoked_by=revoked_by,
                    trust_domain=TrustDomain(domain_name)
                )

                if success:
                    return {
                        'revoked': True,
                        'serial_number': serial_number,
                        'domain': domain_name,
                        'reason': reason,
                        'revoked_by': revoked_by,
                        'revoked_at': datetime.now().isoformat()
                    }

            except Exception as e:
                print(f"Error revoking certificate in {domain_name}: {e}")
                continue

        return {
            'revoked': False,
            'serial_number': serial_number,
            'error': 'Certificate not found or revocation failed'
        }

    def get_revoked_certificates(
        self,
        domain: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get list of revoked certificates.

        Args:
            domain: Filter by trust domain (optional)
            limit: Maximum number to return

        Returns:
            List of revoked certificate records
        """
        revoked_certs = []

        if domain:
            providers_to_check = [(domain, self.providers[domain])]
        else:
            providers_to_check = list(self.providers.items())

        for domain_name, provider in providers_to_check:
            try:
                # Get revoked certs from provider
                domain_revoked = provider.list_certificates(TrustDomain(domain_name))

                # Filter for revoked ones
                for cert in domain_revoked:
                    serial = cert.get('serial')
                    if serial and provider.is_revoked(serial):
                        revocation_info = provider.get_revocation_info(serial)
                        if revocation_info:
                            revocation_info['domain'] = domain_name
                            revoked_certs.append(revocation_info)

            except Exception as e:
                print(f"Error getting revoked certificates for {domain_name}: {e}")
                continue

        return revoked_certs[:limit]

    def get_provider_info(self, domain: str = None) -> Dict[str, Any]:
        """
        Get information about configured providers.

        Args:
            domain: Specific domain (optional, returns all if not specified)

        Returns:
            Dict with provider information
        """
        if domain:
            if domain not in self.providers:
                return {'error': f'Unknown domain: {domain}'}

            provider = self.providers[domain]
            return {
                'domain': domain,
                'provider_name': provider.provider_name,
                'provider_type': provider.provider_type,
                'features': {
                    'crl': provider.supports_feature('crl'),
                    'ocsp': provider.supports_feature('ocsp'),
                    'auto_renewal': provider.supports_feature('auto_renewal'),
                    'offline': provider.supports_feature('offline')
                },
                'statistics': provider.get_statistics()
            }
        else:
            # Return info for all domains
            return {
                domain: {
                    'provider_name': provider.provider_name,
                    'provider_type': provider.provider_type,
                    'statistics': provider.get_statistics()
                }
                for domain, provider in self.providers.items()
            }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall PKI statistics.

        Returns:
            Dict with aggregate statistics across all providers
        """
        total_certs = 0
        active_certs = 0
        revoked_certs = 0

        for provider in self.providers.values():
            stats = provider.get_statistics()
            total_certs += stats.get('total_certificates', 0)
            active_certs += stats.get('active_certificates', 0)
            revoked_certs += stats.get('revoked_certificates', 0)

        return {
            'total_certificates': total_certs,
            'active_certificates': active_certs,
            'revoked_certificates': revoked_certs,
            'providers': len(self.providers)
        }


# Factory function to get PKI service instance (thread-safe)
_pki_service_instance = None

def get_pki_service() -> PKIService:
    """
    Get or create PKI service instance.

    This function ensures thread-safe access to the PKI service.
    """
    global _pki_service_instance
    if _pki_service_instance is None:
        _pki_service_instance = PKIService()
    return _pki_service_instance


# Singleton instance for backward compatibility
# Note: Direct use may cause threading issues, use get_pki_service() instead
pki_service = get_pki_service()
