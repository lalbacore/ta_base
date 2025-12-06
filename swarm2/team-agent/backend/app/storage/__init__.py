"""
Storage Module - Pluggable artifact storage backends.
"""
from .base import (
    StorageProvider,
    StorageType,
    StorageResult,
    ArtifactMetadata
)
from .local import LocalStorageProvider
from .ipfs import IPFSStorageProvider

__all__ = [
    'StorageProvider',
    'StorageType',
    'StorageResult',
    'ArtifactMetadata',
    'LocalStorageProvider',
    'IPFSStorageProvider'
]
