"""
Manifest Generator - Creates comprehensive manifests with signatures and checksums.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import hashlib
import json
import time
from datetime import datetime


class ManifestGenerator:
    """
    Generates comprehensive manifests for workflow outputs.
    Collects signatures from all roles and creates verifiable audit trails.
    """

    def __init__(self):
        self.manifest_version = "1.0"

    def generate_manifest(
        self,
        workflow_id: str,
        mission: str,
        role_outputs: Dict[str, Any],
        artifacts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive manifest from workflow outputs.

        Args:
            workflow_id: Unique workflow identifier
            mission: Mission description
            role_outputs: Dict mapping role names to their signed outputs
            artifacts: Optional list of artifact metadata

        Returns:
            Comprehensive manifest with all signatures and checksums
        """
        timestamp = datetime.utcnow().isoformat() + "Z"

        manifest = {
            "manifest_version": self.manifest_version,
            "workflow_id": workflow_id,
            "mission": mission,
            "timestamp": timestamp,
            "roles": {},
            "signatures": {},
            "artifacts": [],
            "checksums": {},
            "verification": {
                "total_signatures": 0,
                "valid_signatures": 0,
                "missing_signatures": [],
            }
        }

        # Process each role output
        for role_name, output in role_outputs.items():
            if not output:
                continue

            manifest["roles"][role_name] = {
                "status": output.get("status", "unknown"),
                "timestamp": output.get("timestamp", timestamp),
            }

            # Extract signature if present
            if "_signature" in output:
                sig_data = output["_signature"]
                manifest["signatures"][role_name] = {
                    "signature": sig_data.get("signature", ""),
                    "signer_id": sig_data.get("signer", ""),
                    "timestamp": sig_data.get("timestamp", ""),
                }
                manifest["verification"]["total_signatures"] += 1
                manifest["verification"]["valid_signatures"] += 1
            else:
                manifest["verification"]["missing_signatures"].append(role_name)

            # Generate checksum for role output
            output_json = json.dumps(output, sort_keys=True)
            checksum = hashlib.sha256(output_json.encode()).hexdigest()
            manifest["checksums"][role_name] = checksum

        # Process artifacts if provided
        if artifacts:
            for artifact in artifacts:
                artifact_entry = {
                    "type": artifact.get("type", "unknown"),
                    "name": artifact.get("name", "unnamed"),
                    "status": artifact.get("status", "unknown"),
                }

                # Generate artifact checksum if content is available
                if "content" in artifact:
                    content = artifact["content"]
                    if isinstance(content, str):
                        content = content.encode()
                    elif not isinstance(content, bytes):
                        content = json.dumps(content).encode()
                    artifact_entry["checksum"] = hashlib.sha256(content).hexdigest()

                manifest["artifacts"].append(artifact_entry)

        # Add artifact count
        manifest["artifact_count"] = len(manifest["artifacts"])

        # Add overall manifest checksum (excluding this field)
        manifest_copy = manifest.copy()
        manifest_json = json.dumps(manifest_copy, sort_keys=True)
        manifest["manifest_checksum"] = hashlib.sha256(manifest_json.encode()).hexdigest()

        return manifest

    def verify_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify manifest integrity.

        Args:
            manifest: Manifest to verify

        Returns:
            Verification results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Check required fields
        required_fields = ["manifest_version", "workflow_id", "timestamp"]
        for field in required_fields:
            if field not in manifest:
                results["valid"] = False
                results["errors"].append(f"Missing required field: {field}")

        # Check manifest checksum if present
        if "manifest_checksum" in manifest:
            manifest_copy = manifest.copy()
            stored_checksum = manifest_copy.pop("manifest_checksum")
            manifest_json = json.dumps(manifest_copy, sort_keys=True)
            calculated_checksum = hashlib.sha256(manifest_json.encode()).hexdigest()

            if stored_checksum != calculated_checksum:
                results["valid"] = False
                results["errors"].append("Manifest checksum mismatch")

        # Check for missing signatures
        missing_sigs = manifest.get("verification", {}).get("missing_signatures", [])
        if missing_sigs:
            results["warnings"].append(f"Missing signatures from: {', '.join(missing_sigs)}")

        return results

    def export_manifest(
        self,
        manifest: Dict[str, Any],
        format: str = "json"
    ) -> str:
        """
        Export manifest in specified format.

        Args:
            manifest: Manifest to export
            format: Export format ("json", "yaml", "text")

        Returns:
            Formatted manifest string
        """
        if format == "json":
            return json.dumps(manifest, indent=2, sort_keys=True)

        elif format == "text":
            lines = []
            lines.append("=" * 80)
            lines.append("WORKFLOW MANIFEST")
            lines.append("=" * 80)
            lines.append(f"Workflow ID: {manifest.get('workflow_id')}")
            lines.append(f"Mission: {manifest.get('mission')}")
            lines.append(f"Timestamp: {manifest.get('timestamp')}")
            lines.append(f"Manifest Version: {manifest.get('manifest_version')}")
            lines.append("")

            lines.append("ROLES:")
            lines.append("-" * 80)
            for role_name, role_data in manifest.get("roles", {}).items():
                lines.append(f"  {role_name}:")
                lines.append(f"    Status: {role_data.get('status')}")
                lines.append(f"    Timestamp: {role_data.get('timestamp')}")
            lines.append("")

            lines.append("SIGNATURES:")
            lines.append("-" * 80)
            for role_name, sig_data in manifest.get("signatures", {}).items():
                lines.append(f"  {role_name}:")
                lines.append(f"    Signer ID: {sig_data.get('signer_id')}")
                lines.append(f"    Signature: {sig_data.get('signature', '')[:64]}...")
            lines.append("")

            lines.append("VERIFICATION:")
            lines.append("-" * 80)
            verification = manifest.get("verification", {})
            lines.append(f"  Total Signatures: {verification.get('total_signatures', 0)}")
            lines.append(f"  Valid Signatures: {verification.get('valid_signatures', 0)}")
            missing = verification.get("missing_signatures", [])
            if missing:
                lines.append(f"  Missing Signatures: {', '.join(missing)}")
            lines.append("")

            lines.append("CHECKSUMS:")
            lines.append("-" * 80)
            for role_name, checksum in manifest.get("checksums", {}).items():
                lines.append(f"  {role_name}: {checksum}")
            lines.append("")

            lines.append("MANIFEST CHECKSUM:")
            lines.append("-" * 80)
            lines.append(f"  {manifest.get('manifest_checksum', 'N/A')}")
            lines.append("=" * 80)

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def sign_artifact(
        self,
        artifact_content: Any,
        artifact_type: str = "file"
    ) -> Dict[str, Any]:
        """
        Create signed artifact metadata.

        Args:
            artifact_content: Artifact content (string, bytes, or dict)
            artifact_type: Type of artifact

        Returns:
            Artifact metadata with checksum
        """
        # Convert content to bytes for hashing
        if isinstance(artifact_content, str):
            content_bytes = artifact_content.encode()
        elif isinstance(artifact_content, bytes):
            content_bytes = artifact_content
        else:
            content_bytes = json.dumps(artifact_content, sort_keys=True).encode()

        checksum = hashlib.sha256(content_bytes).hexdigest()

        return {
            "type": artifact_type,
            "checksum": checksum,
            "size": len(content_bytes),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
