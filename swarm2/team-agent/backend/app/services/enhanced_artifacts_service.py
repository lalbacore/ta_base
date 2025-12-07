"""
Enhanced Artifacts Service - Storage abstraction with encryption and signing.

Extends the basic artifacts service with:
- Pluggable storage backends (Local, IPFS, Filecoin, etc.)
- Encryption (AES-256-GCM) with optional password protection
- PKI-based signing and verification
- Multi-backend artifact publishing
"""
import sys
import os
import json
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.storage import (
    StorageProvider,
    StorageType,
    StorageResult,
    ArtifactMetadata,
    LocalStorageProvider,
    IPFSStorageProvider
)
from app.services.artifact_crypto import ArtifactCrypto, encrypt_and_sign, verify_and_decrypt
from swarms.team_agent.crypto import TrustDomain, Signer, Verifier


class PublishOptions(Enum):
    """Options for artifact publishing."""
    ENCRYPT = "encrypt"
    SIGN = "sign"
    ENCRYPT_AND_SIGN = "encrypt_and_sign"
    NONE = "none"


class EnhancedArtifactsService:
    """
    Enhanced artifacts service with encryption, signing, and multi-backend storage.

    Supports:
    - Local filesystem storage (default)
    - IPFS distributed storage
    - Filecoin archival storage
    - Optional encryption (AES-256-GCM)
    - PKI-based signing (RSA-PSS)
    """

    def __init__(self):
        """Initialize enhanced artifacts service with storage providers."""
        # Initialize storage providers
        self.providers: Dict[StorageType, StorageProvider] = {}

        # Local storage (always available)
        self.providers[StorageType.LOCAL] = LocalStorageProvider()

        # IPFS storage (optional, requires IPFS daemon)
        try:
            ipfs_provider = IPFSStorageProvider()
            if ipfs_provider.client:
                self.providers[StorageType.IPFS] = ipfs_provider
        except Exception as e:
            print(f"⚠️  IPFS provider unavailable: {e}")

        # Filecoin storage (optional, requires Filecoin setup)
        try:
            filecoin_provider = IPFSStorageProvider(use_filecoin=True)
            if filecoin_provider.client:
                self.providers[StorageType.FILECOIN] = filecoin_provider
        except Exception as e:
            print(f"⚠️  Filecoin provider unavailable: {e}")

        # Crypto utilities
        self.crypto = ArtifactCrypto(trust_domain=TrustDomain.LOGGING)

        # Default output directory (for backward compatibility)
        self.output_dir = Path(os.path.expanduser(
            "~/Dropbox/Team Agent/Projects/ta_base/swarm2/team-agent/team_output"
        ))

    def list_available_backends(self) -> List[Dict[str, Any]]:
        """List all available storage backends."""
        backends = []
        for storage_type, provider in self.providers.items():
            info = provider.get_info()
            backends.append({
                'storage_type': storage_type.value,
                'available': True,
                'info': info
            })
        return backends

    def publish_artifact(
        self,
        workflow_id: str,
        artifact_name: str,
        content: bytes,
        storage_backend: str = "local",
        options: PublishOptions = PublishOptions.SIGN,
        encryption_password: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Publish artifact with encryption and signing to specified backend.

        Args:
            workflow_id: Workflow identifier
            artifact_name: Name of the artifact
            content: Binary content to store
            storage_backend: Backend to use ('local', 'ipfs', 'filecoin')
            options: Publishing options (encrypt, sign, both, or none)
            encryption_password: Optional password for key derivation
            metadata: Additional metadata tags

        Returns:
            Dictionary with publish result, storage location, and crypto metadata
        """
        try:
            # Validate storage backend
            storage_type = StorageType(storage_backend.lower())
            if storage_type not in self.providers:
                return {
                    'success': False,
                    'error': f'Storage backend {storage_backend} not available'
                }

            provider = self.providers[storage_type]

            # Prepare content based on options
            final_content = content
            crypto_metadata = {}
            signature = None
            encryption_key_b64 = None

            if options == PublishOptions.ENCRYPT or options == PublishOptions.ENCRYPT_AND_SIGN:
                # Derive or generate encryption key
                if encryption_password:
                    encryption_key, salt = self.crypto.derive_key_from_password(encryption_password)
                    crypto_metadata['key_derivation'] = {
                        'algorithm': 'PBKDF2-SHA256',
                        'salt': base64.b64encode(salt).decode('utf-8'),
                        'iterations': 100000
                    }
                else:
                    encryption_key = self.crypto.generate_encryption_key()

                # Encrypt content
                encrypted_content, enc_metadata = self.crypto.encrypt(content)
                final_content = encrypted_content
                crypto_metadata['encryption'] = enc_metadata

                # Export key for user (they'll need this to decrypt)
                encryption_key_b64 = self.crypto.export_key(encryption_key)

            if options == PublishOptions.SIGN or options == PublishOptions.ENCRYPT_AND_SIGN:
                # Sign the content (encrypted or plaintext)
                sign_metadata = metadata or {}
                sign_metadata['workflow_id'] = workflow_id
                sign_metadata['artifact_name'] = artifact_name
                signature = self.crypto.sign(final_content, sign_metadata)
                crypto_metadata['signature'] = {
                    'algorithm': 'RSA-PSS-SHA256',
                    'trust_domain': TrustDomain.LOGGING.value,
                    'signature': signature
                }

            # Calculate final checksum
            import hashlib
            sha256_checksum = hashlib.sha256(final_content).hexdigest()

            # Create artifact metadata
            artifact_metadata = ArtifactMetadata(
                workflow_id=workflow_id,
                artifact_name=artifact_name,
                content_type=self._guess_content_type(artifact_name),
                size=len(final_content),
                sha256_checksum=sha256_checksum,
                encrypted=(options == PublishOptions.ENCRYPT or options == PublishOptions.ENCRYPT_AND_SIGN),
                signed=(options == PublishOptions.SIGN or options == PublishOptions.ENCRYPT_AND_SIGN),
                signature=signature,
                encryption_key_id=crypto_metadata.get('encryption', {}).get('key_id'),
                tags=metadata
            )

            # Store to backend
            storage_result = provider.store(final_content, artifact_metadata)

            if not storage_result.success:
                return {
                    'success': False,
                    'error': storage_result.error
                }

            # Build response
            result = {
                'success': True,
                'workflow_id': workflow_id,
                'artifact_name': artifact_name,
                'storage_backend': storage_backend,
                'storage_identifier': storage_result.identifier,
                'size': len(final_content),
                'sha256_checksum': sha256_checksum,
                'encrypted': artifact_metadata.encrypted,
                'signed': artifact_metadata.signed,
                'crypto_metadata': crypto_metadata,
                'storage_metadata': storage_result.metadata
            }

            # Include encryption key if encrypted (user must save this!)
            if encryption_key_b64:
                result['encryption_key'] = encryption_key_b64
                result['warning'] = '⚠️  SAVE THIS ENCRYPTION KEY! It cannot be recovered if lost.'

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def retrieve_artifact(
        self,
        storage_identifier: str,
        storage_backend: str = "local",
        encryption_key: Optional[str] = None,
        verify_signature: bool = True,
        chain_pem: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve artifact with optional decryption and signature verification.

        Args:
            storage_identifier: Storage-specific identifier (file path, CID, etc.)
            storage_backend: Backend to retrieve from
            encryption_key: Base64-encoded encryption key (if encrypted)
            verify_signature: Whether to verify signature
            chain_pem: Certificate chain PEM for verification

        Returns:
            Dictionary with content and verification results
        """
        try:
            # Validate storage backend
            storage_type = StorageType(storage_backend.lower())
            if storage_type not in self.providers:
                return {
                    'success': False,
                    'error': f'Storage backend {storage_backend} not available'
                }

            provider = self.providers[storage_type]

            # Retrieve content
            content = provider.retrieve(storage_identifier)
            if content is None:
                return {
                    'success': False,
                    'error': f'Artifact not found: {storage_identifier}'
                }

            # Get metadata if available
            metadata = None
            if hasattr(provider, 'get_metadata'):
                metadata = provider.get_metadata(storage_identifier)

            result = {
                'success': True,
                'storage_identifier': storage_identifier,
                'storage_backend': storage_backend,
                'size': len(content),
                'encrypted': False,
                'signed': False,
                'signature_valid': None,
                'metadata': metadata
            }

            # Verify signature if requested
            if verify_signature and metadata and metadata.get('signed'):
                signature = metadata.get('signature')
                if signature and chain_pem:
                    is_valid, payload = self.crypto.verify(content, signature, chain_pem)
                    result['signature_valid'] = is_valid
                    result['signature_payload'] = payload
                    result['signed'] = True

                    if not is_valid:
                        result['warning'] = '⚠️  Signature verification failed!'

            # Decrypt if encrypted
            if metadata and metadata.get('encrypted'):
                result['encrypted'] = True

                if not encryption_key:
                    return {
                        'success': False,
                        'error': 'Artifact is encrypted but no encryption key provided'
                    }

                try:
                    # Import encryption key
                    key_bytes = self.crypto.import_key(encryption_key)

                    # Get nonce from metadata
                    enc_metadata = metadata.get('encryption_metadata', {})
                    nonce_b64 = enc_metadata.get('nonce')
                    if not nonce_b64:
                        return {
                            'success': False,
                            'error': 'Missing encryption nonce in metadata'
                        }

                    nonce = base64.b64decode(nonce_b64)

                    # Decrypt
                    decrypted_content = self.crypto.decrypt(content, key_bytes, nonce)
                    content = decrypted_content
                    result['size'] = len(content)
                    result['decrypted'] = True

                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Decryption failed: {e}'
                    }

            # Return content
            result['content'] = content

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def publish_workflow_artifacts(
        self,
        workflow_id: str,
        storage_backend: str = "local",
        options: PublishOptions = PublishOptions.SIGN,
        encryption_password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish all artifacts from a workflow to specified backend.

        Args:
            workflow_id: Workflow identifier
            storage_backend: Backend to use
            options: Publishing options
            encryption_password: Optional password for encryption

        Returns:
            Dictionary with results for each artifact
        """
        workflow_dir = self.output_dir / workflow_id

        if not workflow_dir.exists():
            return {
                'success': False,
                'error': f'Workflow {workflow_id} not found'
            }

        results = []
        errors = []

        for artifact_path in workflow_dir.glob('*'):
            if artifact_path.is_file() and not artifact_path.name.startswith('.'):
                content = artifact_path.read_bytes()

                result = self.publish_artifact(
                    workflow_id=workflow_id,
                    artifact_name=artifact_path.name,
                    content=content,
                    storage_backend=storage_backend,
                    options=options,
                    encryption_password=encryption_password
                )

                if result['success']:
                    results.append(result)
                else:
                    errors.append({
                        'artifact': artifact_path.name,
                        'error': result['error']
                    })

        return {
            'success': len(errors) == 0,
            'workflow_id': workflow_id,
            'storage_backend': storage_backend,
            'artifacts_published': len(results),
            'results': results,
            'errors': errors
        }

    def list_workflow_artifacts(
        self,
        workflow_id: str,
        storage_backend: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List artifacts for a workflow across all or specific backend.

        Args:
            workflow_id: Workflow identifier
            storage_backend: Optional backend filter

        Returns:
            List of artifact metadata
        """
        artifacts = []

        if storage_backend:
            # Query specific backend
            storage_type = StorageType(storage_backend.lower())
            if storage_type in self.providers:
                provider = self.providers[storage_type]
                artifacts = provider.list_artifacts(workflow_id=workflow_id)
        else:
            # Query all backends
            for provider in self.providers.values():
                backend_artifacts = provider.list_artifacts(workflow_id=workflow_id)
                artifacts.extend(backend_artifacts)

        return artifacts

    def _guess_content_type(self, filename: str) -> str:
        """Guess content type from filename extension."""
        ext = Path(filename).suffix.lower()

        content_types = {
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.ts': 'text/typescript',
            '.json': 'application/json',
            '.yaml': 'application/x-yaml',
            '.yml': 'application/x-yaml',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.css': 'text/css',
            '.xml': 'application/xml',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip'
        }

        return content_types.get(ext, 'application/octet-stream')


# Singleton instance
enhanced_artifacts_service = EnhancedArtifactsService()
