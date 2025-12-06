"""
Local Filesystem Storage Provider.

Stores artifacts on the local filesystem in the team_output directory.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base import StorageProvider, StorageType, StorageResult, ArtifactMetadata


class LocalStorageProvider(StorageProvider):
    """
    Local filesystem storage provider.

    Stores artifacts in the team_output directory structure:
    team_output/{workflow_id}/{artifact_name}
    team_output/{workflow_id}/.metadata/{artifact_name}.json
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize local storage provider.

        Args:
            base_dir: Base directory for storage (defaults to team_output)
        """
        if base_dir is None:
            base_dir = Path(os.path.expanduser(
                "~/Dropbox/Team Agent/Projects/ta_base/swarm2/team-agent/team_output"
            ))
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @property
    def storage_type(self) -> StorageType:
        """Return LOCAL storage type."""
        return StorageType.LOCAL

    def store(
        self,
        content: bytes,
        metadata: ArtifactMetadata,
        **kwargs
    ) -> StorageResult:
        """
        Store artifact to local filesystem.

        Args:
            content: Binary content
            metadata: Artifact metadata
            **kwargs: Ignored for local storage

        Returns:
            StorageResult with file path
        """
        try:
            # Create workflow directory
            workflow_dir = self.base_dir / metadata.workflow_id
            workflow_dir.mkdir(parents=True, exist_ok=True)

            # Create metadata directory
            metadata_dir = workflow_dir / ".metadata"
            metadata_dir.mkdir(parents=True, exist_ok=True)

            # Write artifact file
            artifact_path = workflow_dir / metadata.artifact_name
            artifact_path.write_bytes(content)

            # Write metadata file
            metadata_path = metadata_dir / f"{metadata.artifact_name}.json"
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
                'storage_type': 'local',
                'file_path': str(artifact_path)
            }
            metadata_path.write_text(json.dumps(metadata_dict, indent=2))

            return StorageResult(
                success=True,
                storage_type=self.storage_type,
                identifier=str(artifact_path),
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
        Retrieve artifact from local filesystem.

        Args:
            identifier: File path
            **kwargs: Ignored for local storage

        Returns:
            Binary content or None if not found
        """
        try:
            path = Path(identifier)
            if not path.exists():
                return None
            return path.read_bytes()
        except Exception:
            return None

    def delete(
        self,
        identifier: str,
        **kwargs
    ) -> bool:
        """
        Delete artifact from local filesystem.

        Args:
            identifier: File path
            **kwargs: Ignored for local storage

        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(identifier)
            if path.exists():
                path.unlink()

                # Also delete metadata
                metadata_path = path.parent / ".metadata" / f"{path.name}.json"
                if metadata_path.exists():
                    metadata_path.unlink()

                return True
            return False
        except Exception:
            return False

    def exists(
        self,
        identifier: str,
        **kwargs
    ) -> bool:
        """
        Check if artifact exists on local filesystem.

        Args:
            identifier: File path
            **kwargs: Ignored for local storage

        Returns:
            True if exists, False otherwise
        """
        try:
            return Path(identifier).exists()
        except Exception:
            return False

    def list_artifacts(
        self,
        workflow_id: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        List stored artifacts.

        Args:
            workflow_id: Optional workflow filter
            **kwargs: Ignored for local storage

        Returns:
            List of artifact metadata dictionaries
        """
        artifacts = []

        if workflow_id:
            # List artifacts for specific workflow
            workflow_dir = self.base_dir / workflow_id
            if not workflow_dir.exists():
                return []

            metadata_dir = workflow_dir / ".metadata"
            if metadata_dir.exists():
                for metadata_file in metadata_dir.glob('*.json'):
                    try:
                        metadata = json.loads(metadata_file.read_text())
                        artifacts.append(metadata)
                    except Exception:
                        continue
        else:
            # List all artifacts
            for workflow_dir in self.base_dir.iterdir():
                if not workflow_dir.is_dir():
                    continue

                metadata_dir = workflow_dir / ".metadata"
                if metadata_dir.exists():
                    for metadata_file in metadata_dir.glob('*.json'):
                        try:
                            metadata = json.loads(metadata_file.read_text())
                            artifacts.append(metadata)
                        except Exception:
                            continue

        return artifacts

    def get_metadata(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an artifact.

        Args:
            identifier: File path

        Returns:
            Metadata dictionary or None
        """
        try:
            path = Path(identifier)
            metadata_path = path.parent / ".metadata" / f"{path.name}.json"

            if not metadata_path.exists():
                return None

            return json.loads(metadata_path.read_text())
        except Exception:
            return None
