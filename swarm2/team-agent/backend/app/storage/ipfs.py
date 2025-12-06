"""
IPFS/Filecoin Storage Provider.

Stores artifacts on IPFS and optionally pins to Filecoin.
"""
import json
from typing import Dict, Any, Optional, List
import hashlib

from .base import StorageProvider, StorageType, StorageResult, ArtifactMetadata


class IPFSStorageProvider(StorageProvider):
    """
    IPFS storage provider.

    Stores artifacts on IPFS via HTTP API.
    Maintains local index of CIDs for querying.
    """

    def __init__(
        self,
        api_endpoint: str = "/ip4/127.0.0.1/tcp/5001",
        gateway_url: str = "http://127.0.0.1:8080/ipfs/",
        use_filecoin: bool = False
    ):
        """
        Initialize IPFS storage provider.

        Args:
            api_endpoint: IPFS API endpoint (multiaddr format)
            gateway_url: IPFS gateway URL for retrieval
            use_filecoin: Whether to pin to Filecoin (requires additional setup)
        """
        self.api_endpoint = api_endpoint
        self.gateway_url = gateway_url
        self.use_filecoin = use_filecoin

        # CID index (in-memory for now, could be persisted)
        self.cid_index: Dict[str, Dict[str, Any]] = {}

        # Try to connect to IPFS
        self.client = None
        self._connect()

    def _connect(self):
        """Connect to IPFS node."""
        try:
            import ipfshttpclient
            self.client = ipfshttpclient.connect(self.api_endpoint)
            print(f"✅ Connected to IPFS node at {self.api_endpoint}")
        except ImportError:
            print("⚠️  ipfshttpclient not installed. Install with: pip install ipfshttpclient")
            print("   IPFS storage will be unavailable")
        except Exception as e:
            print(f"⚠️  Could not connect to IPFS node: {e}")
            print("   Make sure IPFS daemon is running: ipfs daemon")

    @property
    def storage_type(self) -> StorageType:
        """Return IPFS storage type."""
        return StorageType.FILECOIN if self.use_filecoin else StorageType.IPFS

    def store(
        self,
        content: bytes,
        metadata: ArtifactMetadata,
        **kwargs
    ) -> StorageResult:
        """
        Store artifact to IPFS.

        Args:
            content: Binary content
            metadata: Artifact metadata
            **kwargs: pin=True to pin the file

        Returns:
            StorageResult with CID
        """
        if not self.client:
            return StorageResult(
                success=False,
                storage_type=self.storage_type,
                identifier='',
                metadata={},
                error='IPFS client not connected'
            )

        try:
            # Add file to IPFS
            result = self.client.add_bytes(content)
            cid = result  # CID string

            # Pin if requested
            pin = kwargs.get('pin', True)
            if pin:
                self.client.pin.add(cid)

            # Store metadata in index
            metadata_dict = {
                'workflow_id': metadata.workflow_id,
                'artifact_name': metadata.artifact_name,
                'content_type': metadata.content_type,
                'size': metadata.size,
                'sha256_checksum': metadata.sha256_checksum,
                'encrypted': metadata.encrypted,
                'signed': metadata.signed,
                'signature': metadata.signature,
                'encryption_key_id': metadata.encryption_key_id,
                'tags': metadata.tags or {},
                'storage_type': self.storage_type.value,
                'cid': cid,
                'gateway_url': f"{self.gateway_url}{cid}",
                'pinned': pin
            }

            # Index by both CID and artifact identifier
            index_key = f"{metadata.workflow_id}/{metadata.artifact_name}"
            self.cid_index[index_key] = metadata_dict
            self.cid_index[cid] = metadata_dict

            # If using Filecoin, initiate storage deal (requires lotus client)
            if self.use_filecoin:
                # This would integrate with Filecoin storage provider
                # For now, just mark as intended for Filecoin
                metadata_dict['filecoin_intended'] = True

            return StorageResult(
                success=True,
                storage_type=self.storage_type,
                identifier=cid,
                metadata=metadata_dict
            )

        except Exception as e:
            return StorageResult(
                success=False,
                storage_type=self.storage_type,
                identifier='',
                metadata={},
                error=str(e)
            )

    def retrieve(
        self,
        identifier: str,
        **kwargs
    ) -> Optional[bytes]:
        """
        Retrieve artifact from IPFS.

        Args:
            identifier: CID or workflow/artifact path
            **kwargs: timeout=30 for request timeout

        Returns:
            Binary content or None if not found
        """
        if not self.client:
            return None

        try:
            # If identifier is a path, lookup CID
            if '/' in identifier and identifier not in self.cid_index:
                # Check if it's in index by workflow/artifact path
                metadata = self.cid_index.get(identifier)
                if metadata:
                    identifier = metadata['cid']

            # Get content from IPFS
            timeout = kwargs.get('timeout', 30)
            content = self.client.cat(identifier, timeout=timeout)

            return content

        except Exception as e:
            print(f"Error retrieving from IPFS: {e}")
            return None

    def delete(
        self,
        identifier: str,
        **kwargs
    ) -> bool:
        """
        Unpin artifact from IPFS.

        Note: IPFS is content-addressed, so files aren't truly "deleted",
        just unpinned (allowing garbage collection).

        Args:
            identifier: CID
            **kwargs: Ignored for IPFS

        Returns:
            True if unpinned, False otherwise
        """
        if not self.client:
            return False

        try:
            self.client.pin.rm(identifier)

            # Remove from index
            if identifier in self.cid_index:
                del self.cid_index[identifier]

            return True
        except Exception:
            return False

    def exists(
        self,
        identifier: str,
        **kwargs
    ) -> bool:
        """
        Check if artifact exists on IPFS.

        Args:
            identifier: CID
            **kwargs: Ignored for IPFS

        Returns:
            True if exists, False otherwise
        """
        if not self.client:
            return False

        try:
            # Try to get object stats (doesn't download content)
            self.client.object.stat(identifier)
            return True
        except Exception:
            return False

    def list_artifacts(
        self,
        workflow_id: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        List stored artifacts from index.

        Args:
            workflow_id: Optional workflow filter
            **kwargs: Ignored for IPFS

        Returns:
            List of artifact metadata dictionaries
        """
        artifacts = []

        for key, metadata in self.cid_index.items():
            # Skip CID-only entries (duplicates)
            if '/' not in key:
                continue

            # Filter by workflow_id if provided
            if workflow_id and metadata.get('workflow_id') != workflow_id:
                continue

            artifacts.append(metadata)

        return artifacts

    def pin_to_filecoin(self, cid: str, **kwargs) -> Dict[str, Any]:
        """
        Pin CID to Filecoin network.

        Args:
            cid: IPFS CID to pin
            **kwargs: Filecoin-specific options (duration, price, etc.)

        Returns:
            Dictionary with deal information
        """
        # This would integrate with Filecoin storage provider (e.g., web3.storage, estuary)
        # For now, return placeholder
        return {
            'success': False,
            'error': 'Filecoin integration not yet implemented',
            'cid': cid
        }

    def get_info(self) -> Dict[str, Any]:
        """Get IPFS node information."""
        info = super().get_info()

        if self.client:
            try:
                ipfs_id = self.client.id()
                info['node_id'] = ipfs_id['ID']
                info['addresses'] = ipfs_id.get('Addresses', [])
                info['agent_version'] = ipfs_id.get('AgentVersion', 'unknown')
            except Exception:
                pass

        info['connected'] = self.client is not None
        info['api_endpoint'] = self.api_endpoint
        info['gateway_url'] = self.gateway_url
        info['filecoin_enabled'] = self.use_filecoin

        return info
