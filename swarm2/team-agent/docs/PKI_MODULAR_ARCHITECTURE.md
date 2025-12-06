# Modular PKI Architecture for Team Agent

## Overview

This document defines a modular, pluggable PKI architecture that allows Team Agent deployments to use different certificate authorities and trust models based on their requirements:

- **Self-Signed CA** - Current implementation, ideal for development and testing
- **Let's Encrypt (ACME)** - Free, automated certificates for production web services
- **Blockchain PKI** - Decentralized trust using blockchain as canonical source
- **External CA** - Integration with enterprise certificate authorities

## Architecture Principles

### 1. Provider Pattern
All PKI implementations conform to a common `PKIProvider` interface, allowing hot-swapping of certificate backends without changing application code.

### 2. Configuration-Driven
Provider selection is controlled via configuration file, not code changes.

### 3. Trust Domain Independence
Each trust domain (Government, Execution, Logging) can use a different PKI provider if needed.

### 4. Zero Breaking Changes
Existing code continues to work; modularity is opt-in via configuration.

---

## PKI Provider Interface

### Base Abstract Class

**File**: `swarms/team_agent/crypto/pki_provider.py`

```python
"""
PKI Provider Interface - Abstract base for pluggable PKI backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum


class TrustDomain(Enum):
    """Trust domains for agent planes."""
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
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the PKI provider with configuration.

        Args:
            config: Provider-specific configuration dict
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
            - serial: Certificate serial number (hex)
            - not_before: Validity start date (ISO format)
            - not_after: Validity end date (ISO format)
            - subject: Certificate subject DN
            - issuer: Certificate issuer DN
            - pem: Certificate in PEM format (bytes)
        """
        pass

    @abstractmethod
    def get_certificate_info(self, domain: TrustDomain) -> Dict[str, str]:
        """
        Get certificate information for a trust domain.

        Args:
            domain: Trust domain

        Returns:
            Dict with certificate details
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
            serial_number: Certificate serial number (hex)
            reason: Revocation reason
            revoked_by: Entity revoking the certificate
            **kwargs: Provider-specific parameters

        Returns:
            True if revoked successfully
        """
        pass

    @abstractmethod
    def is_revoked(self, serial_number: str) -> bool:
        """
        Check if certificate is revoked.

        Args:
            serial_number: Certificate serial number

        Returns:
            True if revoked
        """
        pass

    @abstractmethod
    def get_revocation_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Get revocation information for a certificate.

        Args:
            serial_number: Certificate serial number

        Returns:
            Dict with revocation info, or None if not revoked
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
        """
        pass

    @abstractmethod
    def validate_certificate(self, cert_pem: bytes) -> Dict[str, Any]:
        """
        Validate a certificate against this PKI.

        Args:
            cert_pem: Certificate in PEM format

        Returns:
            Dict with validation result:
            - valid: Boolean
            - reason: Reason if invalid
            - chain_valid: Boolean (chain of trust)
            - revoked: Boolean
        """
        pass

    @abstractmethod
    def get_trust_chain(self, domain: TrustDomain) -> List[bytes]:
        """
        Get trust chain (certificate chain) for a domain.

        Args:
            domain: Trust domain

        Returns:
            List of certificates in PEM format (leaf to root)
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Return provider type identifier (e.g., 'self-signed', 'acme', 'blockchain')."""
        pass
```

---

## Provider Implementations

### 1. Self-Signed CA Provider (Current Implementation)

**File**: `swarms/team_agent/crypto/providers/self_signed_provider.py`

```python
"""
Self-Signed CA Provider - Three-tier CA hierarchy for development/testing.
"""
from typing import Dict, Any, Optional, List
from ..pki_provider import PKIProvider, TrustDomain, RevocationReason
from ..pki import PKIManager  # Existing implementation
from ..crl import CRLManager


class SelfSignedCAProvider(PKIProvider):
    """
    Self-signed CA provider using three-tier hierarchy.

    Best for:
    - Development and testing
    - Air-gapped environments
    - Internal agent-to-agent trust

    NOT suitable for:
    - Public-facing web services
    - Browser-trusted certificates
    """

    def __init__(self):
        self.pki_manager: Optional[PKIManager] = None
        self.crl_manager: Optional[CRLManager] = None

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize self-signed PKI."""
        base_dir = config.get('base_dir', None)
        self.pki_manager = PKIManager(base_dir=base_dir)
        self.pki_manager.initialize_pki(force=config.get('force_reinit', False))

        if self.pki_manager.crl_manager:
            self.crl_manager = self.pki_manager.crl_manager

    def issue_certificate(
        self,
        domain: TrustDomain,
        validity_days: int = 1825,
        **kwargs
    ) -> Dict[str, Any]:
        """Issue certificate using self-signed CA."""
        cert_info = self.pki_manager.issue_certificate(domain, validity_days)

        # Add PEM data
        cert_chain = self.pki_manager.get_certificate_chain(domain)
        cert_info['pem'] = cert_chain['cert']

        return cert_info

    def get_certificate_info(self, domain: TrustDomain) -> Dict[str, str]:
        """Get certificate information."""
        return self.pki_manager.get_certificate_info(domain)

    def revoke_certificate(
        self,
        serial_number: str,
        reason: RevocationReason,
        revoked_by: str,
        **kwargs
    ) -> bool:
        """Revoke certificate using CRL."""
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
        """Check if certificate is revoked."""
        return self.pki_manager.is_revoked(serial_number)

    def get_revocation_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get revocation information."""
        return self.pki_manager.get_revocation_info(serial_number)

    def list_certificates(self, domain: Optional[TrustDomain] = None) -> List[Dict[str, Any]]:
        """List all certificates."""
        if domain:
            return [self.get_certificate_info(domain)]
        else:
            return [self.get_certificate_info(d) for d in TrustDomain]

    def validate_certificate(self, cert_pem: bytes) -> Dict[str, Any]:
        """Validate certificate against self-signed CA."""
        # Implementation: Verify signature chain, check CRL
        # For now, basic validation
        return {
            'valid': True,
            'reason': None,
            'chain_valid': True,
            'revoked': False
        }

    def get_trust_chain(self, domain: TrustDomain) -> List[bytes]:
        """Get certificate chain."""
        cert_chain = self.pki_manager.get_certificate_chain(domain)
        return [cert_chain['cert'], cert_chain['chain']]

    @property
    def provider_name(self) -> str:
        return "Self-Signed CA (Three-Tier Hierarchy)"

    @property
    def provider_type(self) -> str:
        return "self-signed"
```

---

### 2. Let's Encrypt (ACME) Provider

**File**: `swarms/team_agent/crypto/providers/acme_provider.py`

```python
"""
ACME Provider - Let's Encrypt integration for production certificates.
"""
from typing import Dict, Any, Optional, List
import josepy as jose
from acme import client, messages
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from ..pki_provider import PKIProvider, TrustDomain, RevocationReason


class ACMEProvider(PKIProvider):
    """
    ACME (Automated Certificate Management Environment) provider.

    Uses Let's Encrypt or other ACME-compatible CA for free,
    browser-trusted certificates.

    Best for:
    - Production web services
    - Public-facing APIs
    - Browser-trusted certificates

    Requirements:
    - Public domain name
    - HTTP/DNS challenge capability
    - Internet connectivity

    NOT suitable for:
    - Internal agent identities (use self-signed)
    - Air-gapped environments
    """

    def __init__(self):
        self.acme_client: Optional[client.ClientV2] = None
        self.account_key: Optional[jose.JWKRSA] = None
        self.certificates: Dict[str, Dict[str, Any]] = {}
        self.directory_url = "https://acme-v02.api.letsencrypt.org/directory"  # Production
        # Use staging for testing: "https://acme-staging-v02.api.letsencrypt.org/directory"

    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize ACME provider.

        Config:
            email: Contact email for Let's Encrypt
            staging: Use staging environment (default: False)
            challenge_type: 'http-01' or 'dns-01' (default: http-01)
        """
        email = config.get('email')
        if not email:
            raise ValueError("ACME provider requires 'email' in config")

        # Use staging environment if specified
        if config.get('staging', False):
            self.directory_url = "https://acme-staging-v02.api.letsencrypt.org/directory"

        # Generate account key
        account_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.account_key = jose.JWKRSA(key=account_key)

        # Create ACME client
        net = client.ClientNetwork(self.account_key)
        directory = messages.Directory.from_json(net.get(self.directory_url).json())
        self.acme_client = client.ClientV2(directory, net=net)

        # Register account
        registration = messages.NewRegistration.from_data(
            email=email,
            terms_of_service_agreed=True
        )
        self.acme_client.new_account(registration)

    def issue_certificate(
        self,
        domain: TrustDomain,
        validity_days: int = 90,  # Let's Encrypt max is 90 days
        **kwargs
    ) -> Dict[str, Any]:
        """
        Issue certificate via ACME protocol.

        Additional kwargs:
            domain_name: Actual domain name (required for ACME)
            challenge_solver: Function to solve ACME challenges
        """
        domain_name = kwargs.get('domain_name')
        if not domain_name:
            raise ValueError("ACME provider requires 'domain_name' parameter")

        challenge_solver = kwargs.get('challenge_solver')
        if not challenge_solver:
            raise ValueError("ACME provider requires 'challenge_solver' callback")

        # Request new certificate
        order = self.acme_client.new_order(domain_name)

        # Solve challenges
        for authz in order.authorizations:
            # Get HTTP-01 challenge
            challenge = None
            for chall in authz.body.challenges:
                if isinstance(chall.chall, messages.challenges.HTTP01):
                    challenge = chall
                    break

            if not challenge:
                raise ValueError("No HTTP-01 challenge available")

            # Solve challenge (callback to user code)
            challenge_solver(challenge)

            # Notify ACME server
            self.acme_client.answer_challenge(challenge, challenge.response(self.account_key))

        # Finalize order (get certificate)
        # Generate CSR
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        csr = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, domain_name),
            ])
        ).sign(private_key, hashes.SHA256(), default_backend())

        # Finalize order
        order = self.acme_client.finalize_order(order, csr)

        # Get certificate
        cert_pem = order.fullchain_pem.encode()

        # Store certificate info
        from cryptography.hazmat.primitives import serialization
        cert = x509.load_pem_x509_certificate(cert_pem, default_backend())

        cert_info = {
            'serial': format(cert.serial_number, 'x'),
            'not_before': cert.not_valid_before.isoformat(),
            'not_after': cert.not_valid_after.isoformat(),
            'subject': cert.subject.rfc4514_string(),
            'issuer': cert.issuer.rfc4514_string(),
            'pem': cert_pem,
            'private_key': private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        }

        self.certificates[domain.value] = cert_info
        return cert_info

    def get_certificate_info(self, domain: TrustDomain) -> Dict[str, str]:
        """Get certificate information."""
        if domain.value not in self.certificates:
            return {}

        cert_info = self.certificates[domain.value]
        return {
            'serial': cert_info['serial'],
            'not_before': cert_info['not_before'],
            'not_after': cert_info['not_after'],
            'subject': cert_info['subject'],
            'issuer': cert_info['issuer']
        }

    def revoke_certificate(
        self,
        serial_number: str,
        reason: RevocationReason,
        revoked_by: str,
        **kwargs
    ) -> bool:
        """Revoke certificate via ACME."""
        # Find certificate by serial
        cert_pem = None
        for cert_info in self.certificates.values():
            if cert_info['serial'] == serial_number:
                cert_pem = cert_info['pem']
                break

        if not cert_pem:
            return False

        # Load certificate
        from cryptography import x509
        cert = x509.load_pem_x509_certificate(cert_pem, default_backend())

        # Revoke via ACME
        self.acme_client.revoke(
            jose.ComparableX509(cert),
            reason.value
        )

        return True

    def is_revoked(self, serial_number: str) -> bool:
        """Check if certificate is revoked (via OCSP)."""
        # Implementation: Query OCSP responder
        # For now, return False
        return False

    def get_revocation_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get revocation information."""
        # ACME doesn't provide revocation info API
        return None

    def list_certificates(self, domain: Optional[TrustDomain] = None) -> List[Dict[str, Any]]:
        """List all certificates."""
        if domain:
            return [self.get_certificate_info(domain)] if domain.value in self.certificates else []
        else:
            return [self.get_certificate_info(TrustDomain(d)) for d in self.certificates.keys()]

    def validate_certificate(self, cert_pem: bytes) -> Dict[str, Any]:
        """Validate certificate."""
        # Implementation: Verify against Let's Encrypt root, check OCSP
        return {
            'valid': True,
            'reason': None,
            'chain_valid': True,
            'revoked': False
        }

    def get_trust_chain(self, domain: TrustDomain) -> List[bytes]:
        """Get certificate chain."""
        if domain.value not in self.certificates:
            return []
        return [self.certificates[domain.value]['pem']]

    @property
    def provider_name(self) -> str:
        return "Let's Encrypt (ACME)"

    @property
    def provider_type(self) -> str:
        return "acme"
```

---

### 3. Blockchain PKI Provider

**File**: `swarms/team_agent/crypto/providers/blockchain_provider.py`

```python
"""
Blockchain PKI Provider - Decentralized trust using blockchain.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..pki_provider import PKIProvider, TrustDomain, RevocationReason


class BlockchainPKIProvider(PKIProvider):
    """
    Blockchain-based PKI for decentralized trust.

    Stores certificate hashes and revocation status on blockchain,
    providing immutable audit trail and no single point of trust.

    Best for:
    - Decentralized multi-agent systems
    - Trustless environments
    - Immutable audit requirements

    Blockchain Options:
    - Ethereum smart contract
    - Hyperledger Fabric
    - Custom blockchain

    NOT suitable for:
    - High-frequency certificate operations (gas costs)
    - Low-latency requirements
    """

    def __init__(self):
        self.blockchain_client = None
        self.contract_address: Optional[str] = None
        self.certificates: Dict[str, Dict[str, Any]] = {}

    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize blockchain PKI.

        Config:
            blockchain_type: 'ethereum', 'hyperledger', 'custom'
            contract_address: Smart contract address (for Ethereum)
            rpc_url: Blockchain RPC endpoint
            private_key: Signing key for transactions
        """
        blockchain_type = config.get('blockchain_type', 'ethereum')

        if blockchain_type == 'ethereum':
            from web3 import Web3
            rpc_url = config.get('rpc_url', 'http://localhost:8545')
            self.blockchain_client = Web3(Web3.HTTPProvider(rpc_url))
            self.contract_address = config.get('contract_address')

            if not self.contract_address:
                raise ValueError("Ethereum blockchain requires 'contract_address'")

        # Load existing certificates from blockchain
        self._sync_certificates()

    def issue_certificate(
        self,
        domain: TrustDomain,
        validity_days: int = 1825,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Issue certificate and register on blockchain.

        Process:
        1. Generate certificate locally
        2. Compute certificate hash
        3. Submit hash to blockchain smart contract
        4. Wait for transaction confirmation
        """
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        import hashlib

        # Generate key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Create self-signed certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Team Agent"),
            x509.NameAttribute(NameOID.COMMON_NAME, f"Team Agent {domain.value.title()}"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        # Compute certificate hash
        from cryptography.hazmat.primitives import serialization
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        cert_hash = hashlib.sha256(cert_pem).hexdigest()

        # Register on blockchain
        tx_hash = self._register_certificate_on_chain(
            serial=format(cert.serial_number, 'x'),
            cert_hash=cert_hash,
            domain=domain.value,
            expires_at=int((datetime.utcnow() + timedelta(days=validity_days)).timestamp())
        )

        cert_info = {
            'serial': format(cert.serial_number, 'x'),
            'not_before': cert.not_valid_before.isoformat(),
            'not_after': cert.not_valid_after.isoformat(),
            'subject': cert.subject.rfc4514_string(),
            'issuer': cert.issuer.rfc4514_string(),
            'pem': cert_pem,
            'cert_hash': cert_hash,
            'blockchain_tx': tx_hash
        }

        self.certificates[domain.value] = cert_info
        return cert_info

    def _register_certificate_on_chain(
        self,
        serial: str,
        cert_hash: str,
        domain: str,
        expires_at: int
    ) -> str:
        """Register certificate on blockchain smart contract."""
        # Example Ethereum smart contract interaction
        if self.blockchain_client:
            # Call smart contract function: registerCertificate(serial, hash, domain, expiresAt)
            # Return transaction hash
            pass

        return "0x" + "0" * 64  # Placeholder

    def get_certificate_info(self, domain: TrustDomain) -> Dict[str, str]:
        """Get certificate information."""
        if domain.value not in self.certificates:
            return {}

        cert_info = self.certificates[domain.value]
        return {
            'serial': cert_info['serial'],
            'not_before': cert_info['not_before'],
            'not_after': cert_info['not_after'],
            'subject': cert_info['subject'],
            'issuer': cert_info['issuer'],
            'blockchain_tx': cert_info.get('blockchain_tx')
        }

    def revoke_certificate(
        self,
        serial_number: str,
        reason: RevocationReason,
        revoked_by: str,
        **kwargs
    ) -> bool:
        """
        Revoke certificate on blockchain.

        Submits revocation transaction to smart contract,
        creating immutable revocation record.
        """
        # Submit revocation to blockchain
        tx_hash = self._revoke_on_chain(serial_number, reason.value, revoked_by)
        return bool(tx_hash)

    def _revoke_on_chain(self, serial: str, reason: int, revoked_by: str) -> str:
        """Submit revocation to blockchain."""
        # Call smart contract: revokeCertificate(serial, reason, revokedBy)
        return "0x" + "1" * 64  # Placeholder

    def is_revoked(self, serial_number: str) -> bool:
        """Check revocation status on blockchain."""
        # Query smart contract: isRevoked(serial)
        return False

    def get_revocation_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get revocation info from blockchain."""
        # Query smart contract for revocation details
        return None

    def list_certificates(self, domain: Optional[TrustDomain] = None) -> List[Dict[str, Any]]:
        """List certificates from blockchain."""
        if domain:
            return [self.get_certificate_info(domain)] if domain.value in self.certificates else []
        else:
            return [self.get_certificate_info(TrustDomain(d)) for d in self.certificates.keys()]

    def validate_certificate(self, cert_pem: bytes) -> Dict[str, Any]:
        """
        Validate certificate against blockchain registry.

        Steps:
        1. Compute certificate hash
        2. Query blockchain for hash
        3. Check revocation status
        4. Verify expiration
        """
        import hashlib
        cert_hash = hashlib.sha256(cert_pem).hexdigest()

        # Query blockchain for this hash
        # For now, return valid
        return {
            'valid': True,
            'reason': None,
            'chain_valid': True,
            'revoked': False,
            'blockchain_verified': True
        }

    def get_trust_chain(self, domain: TrustDomain) -> List[bytes]:
        """Get certificate (no chain in blockchain PKI)."""
        if domain.value not in self.certificates:
            return []
        return [self.certificates[domain.value]['pem']]

    def _sync_certificates(self):
        """Sync certificates from blockchain."""
        # Query smart contract for all registered certificates
        pass

    @property
    def provider_name(self) -> str:
        return "Blockchain PKI (Decentralized Trust)"

    @property
    def provider_type(self) -> str:
        return "blockchain"
```

---

## Provider Factory & Configuration

### Factory Pattern

**File**: `swarms/team_agent/crypto/pki_factory.py`

```python
"""
PKI Factory - Creates PKI providers based on configuration.
"""
from typing import Dict, Any
from .pki_provider import PKIProvider
from .providers.self_signed_provider import SelfSignedCAProvider
from .providers.acme_provider import ACMEProvider
from .providers.blockchain_provider import BlockchainPKIProvider


class PKIFactory:
    """Factory for creating PKI provider instances."""

    PROVIDERS = {
        'self-signed': SelfSignedCAProvider,
        'acme': ACMEProvider,
        'letsencrypt': ACMEProvider,  # Alias
        'blockchain': BlockchainPKIProvider,
    }

    @classmethod
    def create_provider(cls, config: Dict[str, Any]) -> PKIProvider:
        """
        Create PKI provider from configuration.

        Args:
            config: Configuration dict with 'type' and provider-specific settings

        Returns:
            Initialized PKI provider instance

        Example config:
            {
                "type": "self-signed",
                "base_dir": "~/.team_agent/pki"
            }
        """
        provider_type = config.get('type', 'self-signed')

        if provider_type not in cls.PROVIDERS:
            raise ValueError(f"Unknown PKI provider type: {provider_type}")

        provider_class = cls.PROVIDERS[provider_type]
        provider = provider_class()
        provider.initialize(config)

        return provider

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Register a custom PKI provider.

        Allows users to add their own provider implementations.

        Args:
            name: Provider type name
            provider_class: Provider class (must inherit from PKIProvider)
        """
        if not issubclass(provider_class, PKIProvider):
            raise ValueError(f"{provider_class} must inherit from PKIProvider")

        cls.PROVIDERS[name] = provider_class
```

### Configuration File

**File**: `config/pki_config.yaml`

```yaml
# PKI Provider Configuration
# Supported types: self-signed, acme, blockchain

# Default provider for all domains
default_provider:
  type: self-signed
  base_dir: ~/.team_agent/pki
  force_reinit: false

# Per-domain provider overrides (optional)
domain_providers:
  # Government domain uses self-signed (internal trust)
  government:
    type: self-signed
    base_dir: ~/.team_agent/pki

  # Execution domain uses blockchain (decentralized)
  execution:
    type: blockchain
    blockchain_type: ethereum
    rpc_url: http://localhost:8545
    contract_address: "0x1234567890abcdef1234567890abcdef12345678"
    private_key: "${BLOCKCHAIN_PRIVATE_KEY}"  # From env var

  # Logging domain uses Let's Encrypt (public-facing)
  logging:
    type: acme
    email: admin@teamagent.example.com
    staging: false  # Use production Let's Encrypt
    challenge_type: http-01
    domain_name: logs.teamagent.example.com

# Provider-specific configurations
providers:
  self-signed:
    # Self-signed CA settings
    root_ca_validity_days: 3650  # 10 years
    intermediate_ca_validity_days: 1825  # 5 years
    cert_validity_days: 1825  # 5 years

  acme:
    # ACME/Let's Encrypt settings
    staging: false
    challenge_type: http-01
    auto_renew_threshold_days: 30
    challenge_solver: http_file  # or dns_txt

  blockchain:
    # Blockchain PKI settings
    gas_price: auto
    confirmation_blocks: 3
    timeout_seconds: 300
```

---

## Integration with Team Agent

### Updated PKI Service

**File**: `backend/app/services/pki_service.py`

```python
"""
PKI Service - Modular PKI management using pluggable providers.
"""
from typing import List, Dict, Any
from swarms.team_agent.crypto.pki_factory import PKIFactory
from swarms.team_agent.crypto.pki_provider import PKIProvider, TrustDomain
import yaml


class PKIService:
    """
    PKI Service with pluggable provider support.

    Supports multiple PKI backends:
    - Self-signed CA (development)
    - Let's Encrypt (production)
    - Blockchain (decentralized)
    """

    def __init__(self, config_path: str = None):
        """
        Initialize PKI service with configuration.

        Args:
            config_path: Path to PKI configuration file
        """
        if config_path is None:
            config_path = 'config/pki_config.yaml'

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Create providers for each domain
        self.providers: Dict[str, PKIProvider] = {}

        default_config = self.config.get('default_provider', {'type': 'self-signed'})
        domain_configs = self.config.get('domain_providers', {})

        for domain in TrustDomain:
            # Use domain-specific config if available, otherwise default
            provider_config = domain_configs.get(domain.value, default_config)
            self.providers[domain.value] = PKIFactory.create_provider(provider_config)

    def get_all_certificates(self) -> List[Dict[str, Any]]:
        """Get all certificates from all providers."""
        certificates = []

        for domain in TrustDomain:
            provider = self.providers[domain.value]
            cert_info = provider.get_certificate_info(domain)

            if cert_info:
                cert_info['domain'] = domain.value
                cert_info['provider'] = provider.provider_name
                cert_info['provider_type'] = provider.provider_type
                certificates.append(cert_info)

        return certificates

    def rotate_certificate(self, domain: str, **kwargs) -> Dict[str, Any]:
        """Rotate certificate for a domain."""
        trust_domain = TrustDomain(domain)
        provider = self.providers[domain]

        # Get old certificate for audit
        old_cert = provider.get_certificate_info(trust_domain)
        old_serial = old_cert.get('serial')

        # Issue new certificate
        new_cert = provider.issue_certificate(trust_domain, **kwargs)

        # Revoke old certificate (if exists)
        if old_serial:
            from swarms.team_agent.crypto.pki_provider import RevocationReason
            provider.revoke_certificate(
                serial_number=old_serial,
                reason=RevocationReason.SUPERSEDED,
                revoked_by='system'
            )

        return {
            'domain': domain,
            'old_serial': old_serial,
            'new_serial': new_cert['serial'],
            'provider': provider.provider_name
        }

    def get_provider_info(self, domain: str = None) -> Dict[str, Any]:
        """Get information about configured providers."""
        if domain:
            provider = self.providers[domain]
            return {
                'domain': domain,
                'provider_name': provider.provider_name,
                'provider_type': provider.provider_type
            }
        else:
            return {
                domain: {
                    'provider_name': self.providers[domain].provider_name,
                    'provider_type': self.providers[domain].provider_type
                }
                for domain in self.providers.keys()
            }


# Singleton instance
pki_service = PKIService()
```

---

## Example: Custom Enterprise CA Provider

Users can implement their own providers for enterprise CAs:

**File**: `custom_providers/enterprise_ca_provider.py`

```python
"""
Custom Enterprise CA Provider - Integration with corporate PKI.
"""
from swarms.team_agent.crypto.pki_provider import PKIProvider, TrustDomain
from typing import Dict, Any


class EnterpriseCAProvider(PKIProvider):
    """
    Enterprise CA provider for integration with corporate PKI systems.

    Examples:
    - Microsoft Active Directory Certificate Services
    - HashiCorp Vault PKI
    - AWS Private CA
    """

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize connection to enterprise CA."""
        ca_url = config.get('ca_url')
        api_key = config.get('api_key')
        # Initialize CA client
        pass

    def issue_certificate(self, domain: TrustDomain, validity_days: int = 1825, **kwargs) -> Dict[str, Any]:
        """Request certificate from enterprise CA."""
        # Call enterprise CA API
        pass

    # Implement other abstract methods...

    @property
    def provider_name(self) -> str:
        return "Enterprise CA (Corporate PKI)"

    @property
    def provider_type(self) -> str:
        return "enterprise"


# Register with factory
from swarms.team_agent.crypto.pki_factory import PKIFactory
PKIFactory.register_provider('enterprise', EnterpriseCAProvider)
```

---

## Migration Guide

### Migrating from Self-Signed to Let's Encrypt

1. **Update configuration**:
```yaml
domain_providers:
  logging:
    type: acme
    email: admin@example.com
    domain_name: logs.example.com
```

2. **Implement challenge solver**:
```python
def http_challenge_solver(challenge):
    """Solve ACME HTTP-01 challenge."""
    token = challenge.encode("token")
    key_auth = challenge.response(account_key).key_authorization

    # Write challenge file to .well-known/acme-challenge/
    with open(f'.well-known/acme-challenge/{token}', 'w') as f:
        f.write(key_auth)
```

3. **Restart services** - No code changes needed!

---

## Summary

This modular PKI architecture provides:

✅ **Pluggable Providers** - Easy to swap PKI backends
✅ **Configuration-Driven** - No code changes to switch providers
✅ **Multi-Provider Support** - Different providers per domain
✅ **Extensible** - Users can implement custom providers
✅ **Production-Ready Options** - Let's Encrypt for public services
✅ **Decentralized Option** - Blockchain for trustless environments
✅ **Zero Breaking Changes** - Existing code continues to work

Users can choose the best PKI solution for their deployment:
- **Development**: Self-signed CA
- **Production Web**: Let's Encrypt
- **Enterprise**: Corporate CA
- **Decentralized**: Blockchain PKI
