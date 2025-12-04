"""
PKI (Public Key Infrastructure) management for Team Agent.

Implements a three-tier CA hierarchy:
- Root CA (self-signed)
- Intermediate CAs for each trust domain:
  * Government/Control Plane (governance.py)
  * Execution Plane (architect.py, builder.py, critic.py)
  * Logging/Artifact Plane (recorder.py)
"""

import os
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Import CRL manager
try:
    from .crl import CRLManager, RevocationReason
    CRL_AVAILABLE = True
except ImportError:
    CRLManager = None
    RevocationReason = None
    CRL_AVAILABLE = False


class TrustDomain(Enum):
    """Trust domains corresponding to agent planes."""
    GOVERNMENT = "government"
    EXECUTION = "execution"
    LOGGING = "logging"


class PKIManager:
    """
    Manages PKI infrastructure with root CA and intermediate CAs.

    Directory structure:
    .team_agent/pki/
    ├── root/
    │   ├── root-ca.key
    │   └── root-ca.crt
    ├── government/
    │   ├── government-ca.key
    │   ├── government-ca.crt
    │   └── chain.pem
    ├── execution/
    │   ├── execution-ca.key
    │   ├── execution-ca.crt
    │   └── chain.pem
    └── logging/
        ├── logging-ca.key
        ├── logging-ca.crt
        └── chain.pem
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize PKI manager.

        Args:
            base_dir: Base directory for PKI files (default: .team_agent/pki)
        """
        self.base_dir = base_dir or Path(".team_agent") / "pki"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.root_dir = self.base_dir / "root"
        self.government_dir = self.base_dir / "government"
        self.execution_dir = self.base_dir / "execution"
        self.logging_dir = self.base_dir / "logging"

        for dir_path in [self.root_dir, self.government_dir,
                         self.execution_dir, self.logging_dir]:
            dir_path.mkdir(exist_ok=True)

        # Initialize CRL manager
        if CRL_AVAILABLE:
            crl_db_path = self.base_dir / "crl.db"
            self.crl_manager = CRLManager(db_path=crl_db_path)
        else:
            self.crl_manager = None

    def initialize_pki(self, force: bool = False) -> None:
        """
        Initialize complete PKI hierarchy.

        Args:
            force: If True, regenerate even if certificates exist
        """
        # Generate root CA
        if force or not self._root_ca_exists():
            self._generate_root_ca()

        # Generate intermediate CAs
        root_key, root_cert = self._load_root_ca()

        for domain in TrustDomain:
            if force or not self._intermediate_ca_exists(domain):
                self._generate_intermediate_ca(domain, root_key, root_cert)

    def _generate_root_ca(self) -> None:
        """Generate self-signed root CA."""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

        # Create self-signed certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Team Agent"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"Team Agent Root CA"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=3650))  # 10 years
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=1),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                critical=False,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        # Save private key
        key_path = self.root_dir / "root-ca.key"
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        os.chmod(key_path, 0o600)

        # Save certificate
        cert_path = self.root_dir / "root-ca.crt"
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    def _generate_intermediate_ca(
        self,
        domain: TrustDomain,
        root_key,
        root_cert
    ) -> None:
        """
        Generate intermediate CA signed by root CA.

        Args:
            domain: Trust domain for this intermediate CA
            root_key: Root CA private key
            root_cert: Root CA certificate
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Create certificate signed by root CA
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Team Agent"),
            x509.NameAttribute(
                NameOID.COMMON_NAME,
                f"Team Agent {domain.value.title()} CA"
            ),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(root_cert.subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=1825))  # 5 years
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=0),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(
                    root_cert.public_key()
                ),
                critical=False,
            )
            .sign(root_key, hashes.SHA256(), default_backend())
        )

        # Determine directory for this domain
        domain_dir = getattr(self, f"{domain.value}_dir")

        # Save private key
        key_path = domain_dir / f"{domain.value}-ca.key"
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        os.chmod(key_path, 0o600)

        # Save certificate
        cert_path = domain_dir / f"{domain.value}-ca.crt"
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Create chain file (intermediate + root)
        chain_path = domain_dir / "chain.pem"
        with open(chain_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            f.write(root_cert.public_bytes(serialization.Encoding.PEM))

    def _root_ca_exists(self) -> bool:
        """Check if root CA already exists."""
        return (
            (self.root_dir / "root-ca.key").exists() and
            (self.root_dir / "root-ca.crt").exists()
        )

    def _intermediate_ca_exists(self, domain: TrustDomain) -> bool:
        """Check if intermediate CA exists for given domain."""
        domain_dir = getattr(self, f"{domain.value}_dir")
        return (
            (domain_dir / f"{domain.value}-ca.key").exists() and
            (domain_dir / f"{domain.value}-ca.crt").exists() and
            (domain_dir / "chain.pem").exists()
        )

    def _load_root_ca(self) -> Tuple:
        """Load root CA private key and certificate."""
        with open(self.root_dir / "root-ca.key", "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )

        with open(self.root_dir / "root-ca.crt", "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())

        return private_key, cert

    def get_certificate_chain(self, domain: TrustDomain) -> Dict[str, bytes]:
        """
        Get certificate chain for a trust domain.

        Args:
            domain: Trust domain

        Returns:
            Dict with 'key', 'cert', and 'chain' as PEM bytes
        """
        domain_dir = getattr(self, f"{domain.value}_dir")

        with open(domain_dir / f"{domain.value}-ca.key", "rb") as f:
            key = f.read()

        with open(domain_dir / f"{domain.value}-ca.crt", "rb") as f:
            cert = f.read()

        with open(domain_dir / "chain.pem", "rb") as f:
            chain = f.read()

        return {
            "key": key,
            "cert": cert,
            "chain": chain,
        }

    def get_certificate_info(self, domain: TrustDomain) -> Dict[str, str]:
        """
        Get human-readable certificate information.

        Args:
            domain: Trust domain

        Returns:
            Dict with certificate details (serial in hex format)
        """
        domain_dir = getattr(self, f"{domain.value}_dir")

        with open(domain_dir / f"{domain.value}-ca.crt", "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())

        return {
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "serial": format(cert.serial_number, 'x'),  # Hex format for consistency
            "not_before": cert.not_valid_before.isoformat(),
            "not_after": cert.not_valid_after.isoformat(),
        }

    # Certificate Revocation Methods

    def revoke_certificate(
        self,
        serial_number: str,
        reason: 'RevocationReason',
        revoked_by: str,
        trust_domain: TrustDomain,
        cert_subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Revoke a certificate.

        Args:
            serial_number: Certificate serial number (hex string)
            reason: Revocation reason (from RevocationReason enum)
            revoked_by: Who revoked the certificate
            trust_domain: Trust domain (government, execution, logging)
            cert_subject: Certificate subject (optional)
            metadata: Additional metadata (optional)

        Returns:
            True if revoked, False if already revoked or CRL unavailable
        """
        if not self.crl_manager:
            return False

        return self.crl_manager.revoke_certificate(
            serial_number=serial_number,
            reason=reason,
            revoked_by=revoked_by,
            trust_domain=trust_domain.value,
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
        if not self.crl_manager:
            return False

        return self.crl_manager.is_revoked(serial_number)

    def get_revocation_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Get revocation information for a certificate.

        Args:
            serial_number: Certificate serial number

        Returns:
            Dict with revocation info, or None if not revoked
        """
        if not self.crl_manager:
            return None

        return self.crl_manager.get_revocation_info(serial_number)

    def generate_crl(
        self,
        domain: TrustDomain,
        validity_days: int = 7
    ) -> Optional[bytes]:
        """
        Generate CRL for a trust domain.

        Args:
            domain: Trust domain to generate CRL for
            validity_days: CRL validity period in days (default: 7)

        Returns:
            CRL in PEM format, or None if CRL unavailable
        """
        if not self.crl_manager:
            return None

        # Get certificate chain for the domain
        cert_chain = self.get_certificate_chain(domain)

        # Generate CRL
        crl_pem = self.crl_manager.generate_crl(
            issuer_key_pem=cert_chain['key'],
            issuer_cert_pem=cert_chain['cert'],
            validity_days=validity_days
        )

        # Save CRL to file
        domain_dir = getattr(self, f"{domain.value}_dir")
        crl_path = domain_dir / "crl.pem"
        with open(crl_path, "wb") as f:
            f.write(crl_pem)

        return crl_pem

    def generate_all_crls(self, validity_days: int = 7) -> Dict[str, bytes]:
        """
        Generate CRLs for all trust domains.

        Args:
            validity_days: CRL validity period in days (default: 7)

        Returns:
            Dict mapping trust domain to CRL PEM bytes
        """
        crls = {}
        for domain in TrustDomain:
            crl = self.generate_crl(domain, validity_days)
            if crl:
                crls[domain.value] = crl
        return crls

    def get_crl_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Get CRL statistics.

        Returns:
            Dict with statistics, or None if CRL unavailable
        """
        if not self.crl_manager:
            return None

        return self.crl_manager.get_statistics()

    def list_revoked_certificates(
        self,
        trust_domain: Optional[TrustDomain] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List revoked certificates.

        Args:
            trust_domain: Filter by trust domain (optional)
            limit: Maximum number to return

        Returns:
            List of revoked certificate records
        """
        if not self.crl_manager:
            return []

        domain_str = trust_domain.value if trust_domain else None
        return self.crl_manager.list_revoked_certificates(
            trust_domain=domain_str,
            limit=limit
        )
