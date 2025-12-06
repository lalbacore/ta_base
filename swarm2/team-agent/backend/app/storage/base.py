"""
Base Storage Provider Interface.

Defines the contract for all storage backends (local, IPFS, S3, etc.)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class StorageType(Enum):
    """Storage backend types."""
    LOCAL = "local"
    IPFS = "ipfs"
    FILECOIN = "filecoin"
    S3 = "s3"
    ARWEAVE = "arweave"


@dataclass
class StorageResult:
    """Result of storage operation."""
    success: bool
    storage_type: StorageType
    identifier: str  # File path, CID, URL, etc.
    metadata: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class ArtifactMetadata:
    """Metadata for stored artifacts."""
    workflow_id: str
    artifact_name: str
    content_type: str
    size: int
    sha256_checksum: str
    encrypted: bool = False
    signed: bool = False
    signature: Optional[str] = None
    encryption_key_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class StorageProvider(ABC):
    """
    Abstract base class for storage providers.

    All storage backends must implement this interface.
    """

    @property
    @abstractmethod
    def storage_type(self) -> StorageType:
        """Return the storage type."""
        pass

    @abstractmethod
    def store(
        self,
        content: bytes,
        metadata: ArtifactMetadata,
        **kwargs
    ) -> StorageResult:
        """
        Store artifact content.

        Args:
            content: Binary content to store
            metadata: Artifact metadata
            **kwargs: Provider-specific options

        Returns:
            StorageResult with identifier and metadata
        """
        pass

    @abstractmethod
    def retrieve(
        self,
        identifier: str,
        **kwargs
    ) -> Optional[bytes]:
        """
        Retrieve artifact content.

        Args:
            identifier: Storage identifier (path, CID, URL, etc.)
            **kwargs: Provider-specific options

        Returns:
            Binary content or None if not found
        """
        pass

    @abstractmethod
    def delete(
        self,
        identifier: str,
        **kwargs
    ) -> bool:
        """
        Delete artifact.

        Args:
            identifier: Storage identifier
            **kwargs: Provider-specific options

        Returns:
            True if deleted, False otherwise
        """
        pass

    @abstractmethod
    def exists(
        self,
        identifier: str,
        **kwargs
    ) -> bool:
        """
        Check if artifact exists.

        Args:
            identifier: Storage identifier
            **kwargs: Provider-specific options

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    def list_artifacts(
        self,
        workflow_id: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        List stored artifacts.

        Args:
            workflow_id: Optional workflow filter
            **kwargs: Provider-specific options

        Returns:
            List of artifact metadata dictionaries
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        Get provider information.

        Returns:
            Dictionary with provider details
        """
        return {
            'storage_type': self.storage_type.value,
            'name': self.__class__.__name__,
            'description': self.__class__.__doc__ or ''
        }
