"""
Artifact Signing Utilities - Sign and verify individual artifacts.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, Union
import hashlib
import json
from pathlib import Path
from datetime import datetime

from .signing import Signer, Verifier


class ArtifactSigner:
    """
    Utilities for signing individual artifacts like files, logs, and policies.
    """

    def __init__(self, signer: Optional[Signer] = None):
        """
        Initialize artifact signer.

        Args:
            signer: Optional Signer instance for cryptographic signing
        """
        self.signer = signer

    def sign_file(
        self,
        file_path: Union[str, Path],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sign a file and return signed metadata.

        Args:
            file_path: Path to file to sign
            metadata: Optional additional metadata

        Returns:
            Signed artifact metadata with checksum and signature
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file and calculate checksum
        with open(file_path, "rb") as f:
            content = f.read()

        checksum = hashlib.sha256(content).hexdigest()

        artifact = {
            "type": "file",
            "path": str(file_path),
            "name": file_path.name,
            "size": len(content),
            "checksum": checksum,
            "checksum_algorithm": "SHA-256",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {},
        }

        # Sign if signer is available
        if self.signer:
            artifact = self.signer.sign_dict(artifact)

        return artifact

    def sign_log_entry(
        self,
        log_data: Dict[str, Any],
        log_type: str = "workflow"
    ) -> Dict[str, Any]:
        """
        Sign a log entry.

        Args:
            log_data: Log data to sign
            log_type: Type of log (workflow, audit, error, etc.)

        Returns:
            Signed log entry
        """
        log_entry = {
            "type": "log",
            "log_type": log_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": log_data,
        }

        # Calculate checksum of log data
        log_json = json.dumps(log_data, sort_keys=True)
        log_entry["checksum"] = hashlib.sha256(log_json.encode()).hexdigest()

        # Sign if signer is available
        if self.signer:
            log_entry = self.signer.sign_dict(log_entry)

        return log_entry

    def sign_policy(
        self,
        policy_data: Dict[str, Any],
        policy_name: str,
        version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        Sign a policy document.

        Args:
            policy_data: Policy data to sign
            policy_name: Name of the policy
            version: Policy version

        Returns:
            Signed policy document
        """
        policy = {
            "type": "policy",
            "name": policy_name,
            "version": version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "policy": policy_data,
        }

        # Calculate checksum of policy data
        policy_json = json.dumps(policy_data, sort_keys=True)
        policy["checksum"] = hashlib.sha256(policy_json.encode()).hexdigest()

        # Sign if signer is available
        if self.signer:
            policy = self.signer.sign_dict(policy)

        return policy

    def sign_artifact(
        self,
        artifact_data: Any,
        artifact_type: str,
        artifact_name: str = "unnamed",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sign any generic artifact.

        Args:
            artifact_data: Artifact data (dict, string, or bytes)
            artifact_type: Type of artifact
            artifact_name: Name of artifact
            metadata: Optional metadata

        Returns:
            Signed artifact
        """
        # Convert artifact data to bytes for checksumming
        if isinstance(artifact_data, bytes):
            data_bytes = artifact_data
        elif isinstance(artifact_data, str):
            data_bytes = artifact_data.encode()
        else:
            data_bytes = json.dumps(artifact_data, sort_keys=True).encode()

        checksum = hashlib.sha256(data_bytes).hexdigest()

        artifact = {
            "type": artifact_type,
            "name": artifact_name,
            "size": len(data_bytes),
            "checksum": checksum,
            "checksum_algorithm": "SHA-256",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {},
        }

        # Include data if it's a dict or small enough
        if isinstance(artifact_data, dict):
            artifact["data"] = artifact_data
        elif len(data_bytes) < 1024 * 1024:  # Less than 1MB
            if isinstance(artifact_data, str):
                artifact["data"] = artifact_data
            # Don't include raw bytes in the signed artifact

        # Sign if signer is available
        if self.signer:
            artifact = self.signer.sign_dict(artifact)

        return artifact

    def verify_artifact(
        self,
        signed_artifact: Dict[str, Any],
        verifier: Optional[Verifier] = None
    ) -> Dict[str, Any]:
        """
        Verify a signed artifact.

        Args:
            signed_artifact: Signed artifact to verify
            verifier: Optional Verifier instance

        Returns:
            Verification results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Check for required fields
        if "checksum" not in signed_artifact:
            results["valid"] = False
            results["errors"].append("Missing checksum")

        if "timestamp" not in signed_artifact:
            results["warnings"].append("Missing timestamp")

        # Verify signature if verifier is provided
        if verifier and "signature" in signed_artifact:
            try:
                # Extract signature components
                signature_b64 = signed_artifact.get("signature")
                signer_id = signed_artifact.get("signer_id")

                if not signature_b64:
                    results["valid"] = False
                    results["errors"].append("Invalid signature format")
                else:
                    # Verify would require the original data and public key
                    # For now, just check that signature fields are present
                    if not signer_id:
                        results["warnings"].append("Missing signer_id")
            except Exception as e:
                results["valid"] = False
                results["errors"].append(f"Signature verification failed: {str(e)}")
        elif "signature" not in signed_artifact:
            results["warnings"].append("Artifact is not signed")

        return results

    def batch_sign_artifacts(
        self,
        artifacts: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Sign multiple artifacts in batch.

        Args:
            artifacts: List of artifact dicts with 'data', 'type', and 'name'

        Returns:
            List of signed artifacts
        """
        signed_artifacts = []

        for artifact in artifacts:
            try:
                signed = self.sign_artifact(
                    artifact_data=artifact.get("data", {}),
                    artifact_type=artifact.get("type", "generic"),
                    artifact_name=artifact.get("name", "unnamed"),
                    metadata=artifact.get("metadata")
                )
                signed_artifacts.append(signed)
            except Exception as e:
                # Include error in the artifact
                error_artifact = artifact.copy()
                error_artifact["error"] = str(e)
                error_artifact["signed"] = False
                signed_artifacts.append(error_artifact)

        return signed_artifacts


def create_artifact_manifest(
    artifacts: list[Dict[str, Any]],
    workflow_id: str,
    signer: Optional[Signer] = None
) -> Dict[str, Any]:
    """
    Create a manifest for a collection of artifacts.

    Args:
        artifacts: List of signed artifacts
        workflow_id: Workflow identifier
        signer: Optional signer for the manifest itself

    Returns:
        Signed manifest of artifacts
    """
    manifest = {
        "type": "artifact_manifest",
        "workflow_id": workflow_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }

    # Calculate manifest checksum
    manifest_json = json.dumps(artifacts, sort_keys=True)
    manifest["manifest_checksum"] = hashlib.sha256(manifest_json.encode()).hexdigest()

    # Sign manifest if signer is available
    if signer:
        manifest = signer.sign_dict(manifest)

    return manifest
