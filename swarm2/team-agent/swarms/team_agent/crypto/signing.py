"""
Signing and verification utilities for Team Agent.

Provides data signing and verification using intermediate CA certificates.
"""

import base64
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


@dataclass
class SignedData:
    """Container for signed data with metadata."""
    data: Any
    signature: str
    signer: str
    timestamp: str
    cert_subject: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SignedData":
        """Create from dictionary."""
        return cls(**d)


class Signer:
    """
    Signs data using intermediate CA private key.

    Used by agents to sign their outputs (logs, artifacts, tape entries).
    """

    def __init__(
        self,
        private_key_pem: bytes,
        certificate_pem: bytes,
        signer_id: str
    ):
        """
        Initialize signer with certificate chain.

        Args:
            private_key_pem: Private key in PEM format
            certificate_pem: Certificate in PEM format
            signer_id: Identifier for this signer (e.g., "architect", "recorder")
        """
        self.private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        self.certificate = x509.load_pem_x509_certificate(
            certificate_pem,
            backend=default_backend()
        )
        self.signer_id = signer_id
        self.cert_subject = self.certificate.subject.rfc4514_string()

    def sign(self, data: Any) -> SignedData:
        """
        Sign arbitrary data.

        Args:
            data: Data to sign (will be JSON serialized)

        Returns:
            SignedData object with signature and metadata
        """
        # Serialize data to canonical JSON
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = str(data).encode('utf-8')

        # Sign the data
        signature = self.private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Base64 encode signature for storage
        signature_b64 = base64.b64encode(signature).decode('ascii')

        return SignedData(
            data=data,
            signature=signature_b64,
            signer=self.signer_id,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            cert_subject=self.cert_subject
        )

    def sign_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign data and return as dict with signature embedded.

        Args:
            data: Dictionary to sign

        Returns:
            Dict with original data plus signature metadata
        """
        signed = self.sign(data)
        result = data.copy()
        result['_signature'] = {
            'signature': signed.signature,
            'signer': signed.signer,
            'timestamp': signed.timestamp,
            'cert_subject': signed.cert_subject
        }
        return result


class Verifier:
    """
    Verifies signatures using certificate chain.

    Used to verify data signed by agents.
    """

    def __init__(self, chain_pem: bytes):
        """
        Initialize verifier with certificate chain.

        Args:
            chain_pem: Certificate chain in PEM format (intermediate + root)
        """
        # Load all certificates from chain
        self.certificates = []
        for cert_pem in chain_pem.split(b'-----END CERTIFICATE-----'):
            if b'-----BEGIN CERTIFICATE-----' in cert_pem:
                cert_pem = cert_pem + b'-----END CERTIFICATE-----\n'
                cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
                self.certificates.append(cert)

        if not self.certificates:
            raise ValueError("No certificates found in chain")

        # First cert is the signing cert
        self.signing_cert = self.certificates[0]

    def verify(self, signed_data: SignedData) -> bool:
        """
        Verify signed data.

        Args:
            signed_data: SignedData object to verify

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Serialize data to canonical JSON (same as signing)
            data = signed_data.data
            if isinstance(data, (dict, list)):
                data_bytes = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = str(data).encode('utf-8')

            # Decode signature
            signature = base64.b64decode(signed_data.signature)

            # Verify signature
            public_key = self.signing_cert.public_key()
            public_key.verify(
                signature,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True

        except InvalidSignature:
            return False
        except Exception:
            return False

    def verify_dict(self, data: Dict[str, Any]) -> bool:
        """
        Verify dictionary with embedded signature.

        Args:
            data: Dict with _signature metadata

        Returns:
            True if signature is valid, False otherwise
        """
        if '_signature' not in data:
            return False

        # Extract signature metadata
        sig_meta = data['_signature']

        # Create copy without signature for verification
        data_copy = {k: v for k, v in data.items() if k != '_signature'}

        # Create SignedData object
        signed = SignedData(
            data=data_copy,
            signature=sig_meta['signature'],
            signer=sig_meta['signer'],
            timestamp=sig_meta['timestamp'],
            cert_subject=sig_meta['cert_subject']
        )

        return self.verify(signed)

    def get_signer_info(self) -> Dict[str, str]:
        """Get information about the signing certificate."""
        return {
            "subject": self.signing_cert.subject.rfc4514_string(),
            "issuer": self.signing_cert.issuer.rfc4514_string(),
            "serial": str(self.signing_cert.serial_number),
            "not_before": self.signing_cert.not_valid_before.isoformat(),
            "not_after": self.signing_cert.not_valid_after.isoformat(),
        }
