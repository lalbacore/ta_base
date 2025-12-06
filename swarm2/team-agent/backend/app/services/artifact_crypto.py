"""
Artifact Cryptography - Encryption and Signing for Artifacts.

Provides encryption (AES-256-GCM) and signing (RSA-PSS with SHA-256) for artifacts.
Integrates with existing PKI infrastructure.
"""
import sys
import os
import base64
import hashlib
from typing import Dict, Any, Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

# Add parent directory to path for PKI imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from swarms.team_agent.crypto import Signer, Verifier, TrustDomain, PKIManager


class ArtifactCrypto:
    """
    Handles encryption and signing of artifacts.

    Uses AES-256-GCM for encryption and RSA-PSS for signing (via PKI).
    """

    def __init__(self, trust_domain: TrustDomain = TrustDomain.LOGGING):
        """
        Initialize artifact crypto with PKI trust domain.

        Args:
            trust_domain: PKI trust domain for signing (default: LOGGING)
        """
        self.trust_domain = trust_domain

        # Get certificate and private key from PKI manager
        pki = PKIManager()
        cert_data = pki.get_certificate_chain(trust_domain)

        # Initialize signer with certificate materials
        self.signer = Signer(
            private_key_pem=cert_data['key'],
            certificate_pem=cert_data['cert'],
            signer_id=f"artifact_crypto_{trust_domain.value}"
        )

    def encrypt(
        self,
        content: bytes,
        encryption_key: Optional[bytes] = None,
        associated_data: Optional[bytes] = None
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Encrypt artifact content using AES-256-GCM.

        Args:
            content: Binary content to encrypt
            encryption_key: Optional 32-byte key (auto-generated if not provided)
            associated_data: Optional authenticated associated data (AAD)

        Returns:
            Tuple of (encrypted_content, encryption_metadata)
        """
        # Generate key if not provided
        if encryption_key is None:
            encryption_key = AESGCM.generate_key(bit_length=256)

        # Generate random 96-bit nonce (12 bytes)
        nonce = secrets.token_bytes(12)

        # Encrypt using AES-256-GCM
        aesgcm = AESGCM(encryption_key)
        ciphertext = aesgcm.encrypt(nonce, content, associated_data)

        # Return encrypted content and metadata
        metadata = {
            'algorithm': 'AES-256-GCM',
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'key_id': hashlib.sha256(encryption_key).hexdigest()[:16],
            'encrypted_size': len(ciphertext)
        }

        # If AAD was used, store its hash
        if associated_data:
            metadata['aad_hash'] = hashlib.sha256(associated_data).hexdigest()

        return ciphertext, metadata

    def decrypt(
        self,
        encrypted_content: bytes,
        encryption_key: bytes,
        nonce: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt artifact content using AES-256-GCM.

        Args:
            encrypted_content: Encrypted binary content
            encryption_key: 32-byte decryption key
            nonce: 12-byte nonce used for encryption
            associated_data: Optional AAD used during encryption

        Returns:
            Decrypted binary content

        Raises:
            ValueError: If decryption fails (wrong key, corrupted data, etc.)
        """
        try:
            aesgcm = AESGCM(encryption_key)
            plaintext = aesgcm.decrypt(nonce, encrypted_content, associated_data)
            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def sign(
        self,
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Sign artifact content using PKI.

        Args:
            content: Binary content to sign
            metadata: Optional metadata to include in signature

        Returns:
            Base64-encoded signature
        """
        # Calculate SHA-256 hash of content
        content_hash = hashlib.sha256(content).hexdigest()

        # Build signature payload
        payload = {
            'content_hash': content_hash,
            'size': len(content),
            'trust_domain': self.trust_domain.value
        }

        # Add metadata if provided
        if metadata:
            payload['metadata'] = metadata

        # Sign using PKI
        signature = self.signer.sign(payload)

        return signature

    def verify(
        self,
        content: bytes,
        signature: str,
        chain_pem: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify artifact signature using PKI.

        Args:
            content: Binary content to verify
            signature: Base64-encoded signature
            chain_pem: Certificate chain PEM for verification

        Returns:
            Tuple of (is_valid, payload_dict)
        """
        # Create verifier
        verifier = Verifier(chain_pem=chain_pem)

        # Verify signature
        payload = verifier.verify(signature)

        if not payload:
            return False, None

        # Verify content hash matches
        actual_hash = hashlib.sha256(content).hexdigest()
        expected_hash = payload.get('content_hash')

        if actual_hash != expected_hash:
            return False, None

        return True, payload

    def derive_key_from_password(
        self,
        password: str,
        salt: Optional[bytes] = None,
        iterations: int = 100000
    ) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2.

        Args:
            password: User password
            salt: Optional salt (generated if not provided)
            iterations: PBKDF2 iterations (default: 100,000)

        Returns:
            Tuple of (32-byte key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations
        )

        key = kdf.derive(password.encode('utf-8'))

        return key, salt

    def generate_encryption_key(self) -> bytes:
        """
        Generate a random 256-bit encryption key.

        Returns:
            32-byte key
        """
        return AESGCM.generate_key(bit_length=256)

    def export_key(self, key: bytes) -> str:
        """
        Export encryption key as base64 string.

        Args:
            key: Binary key

        Returns:
            Base64-encoded key string
        """
        return base64.b64encode(key).decode('utf-8')

    def import_key(self, key_str: str) -> bytes:
        """
        Import encryption key from base64 string.

        Args:
            key_str: Base64-encoded key string

        Returns:
            Binary key

        Raises:
            ValueError: If key string is invalid
        """
        try:
            return base64.b64decode(key_str)
        except Exception as e:
            raise ValueError(f"Invalid key format: {e}")


# Convenience functions for common operations

def encrypt_and_sign(
    content: bytes,
    encryption_key: Optional[bytes] = None,
    trust_domain: TrustDomain = TrustDomain.LOGGING,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Encrypt and sign artifact content.

    Args:
        content: Binary content
        encryption_key: Optional encryption key (generated if not provided)
        trust_domain: PKI trust domain
        metadata: Optional metadata for signature

    Returns:
        Dictionary with encrypted content and crypto metadata
    """
    crypto = ArtifactCrypto(trust_domain=trust_domain)

    # Encrypt
    encrypted_content, encryption_metadata = crypto.encrypt(content, encryption_key)

    # Sign the encrypted content
    signature = crypto.sign(encrypted_content, metadata)

    return {
        'encrypted_content': encrypted_content,
        'encryption_metadata': encryption_metadata,
        'signature': signature,
        'trust_domain': trust_domain.value
    }


def verify_and_decrypt(
    encrypted_content: bytes,
    encryption_key: bytes,
    nonce: bytes,
    signature: str,
    chain_pem: str,
    trust_domain: TrustDomain = TrustDomain.LOGGING
) -> Tuple[bool, Optional[bytes]]:
    """
    Verify signature and decrypt artifact content.

    Args:
        encrypted_content: Encrypted binary content
        encryption_key: Decryption key
        nonce: Nonce used for encryption
        signature: Signature to verify
        chain_pem: Certificate chain PEM
        trust_domain: PKI trust domain

    Returns:
        Tuple of (is_valid, decrypted_content)
    """
    crypto = ArtifactCrypto(trust_domain=trust_domain)

    # Verify signature on encrypted content
    is_valid, payload = crypto.verify(encrypted_content, signature, chain_pem)

    if not is_valid:
        return False, None

    # Decrypt content
    try:
        decrypted_content = crypto.decrypt(encrypted_content, encryption_key, nonce)
        return True, decrypted_content
    except ValueError:
        return False, None
