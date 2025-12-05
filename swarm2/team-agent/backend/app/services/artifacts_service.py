"""
Artifacts Service - Bridges Flask API to ManifestGenerator.
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import Dict, Any, List, Optional
from app.data.seed_data import SAMPLE_MANIFESTS


class ArtifactsService:
    """
    Service layer for artifacts and manifests.
    Bridges Flask API to ManifestGenerator.
    """

    def __init__(self):
        # TODO: Initialize manifest generator when ready
        # from swarms.team_agent.crypto.manifest import ManifestGenerator
        # self.manifest_generator = ManifestGenerator()

        # Load seed data - SAMPLE_MANIFESTS is already a dict keyed by workflow_id
        self.manifests = SAMPLE_MANIFESTS.copy()

    def get_workflow_manifest(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow manifest."""
        # TODO: Load manifest from workflow tape or storage
        return self.manifests.get(workflow_id)

    def get_workflow_artifacts(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get workflow artifacts."""
        # TODO: Load artifacts from workflow tape
        manifest = self.manifests.get(workflow_id)
        if not manifest or 'checksums' not in manifest:
            return []

        # Convert checksums dict to artifacts list
        artifacts = []
        for filename, checksum in manifest['checksums'].items():
            artifacts.append({
                'name': filename,
                'sha256_checksum': checksum,
                'verified': True
            })
        return artifacts

    def verify_artifact(self, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify artifact signature."""
        # TODO: Use Verifier to verify artifact signature
        return {
            'valid': True,
            'errors': [],
            'warnings': []
        }

    def verify_manifest(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify manifest integrity."""
        # TODO: Use manifest_generator.verify_manifest()
        return {
            'valid': True,
            'errors': [],
            'warnings': []
        }

    def export_manifest(self, workflow_id: str, format_type: str) -> str:
        """Export manifest in specified format."""
        # TODO: Use manifest_generator.export_manifest(manifest, format=format_type)
        manifest = self.manifests.get(workflow_id)
        if not manifest:
            return ""

        if format_type == 'json':
            return json.dumps(manifest, indent=2)
        elif format_type == 'text':
            # Simple text format
            lines = [
                f"Workflow Manifest: {manifest['workflow_id']}",
                f"Generated: {manifest.get('generated_at', 'N/A')}",
                "",
                "Signatures:",
            ]
            for role, signature in manifest.get('signatures', {}).items():
                lines.append(f"  - {role}: {signature[:16]}...")
            lines.append("")
            lines.append("Artifacts:")
            for filename, checksum in manifest.get('checksums', {}).items():
                lines.append(f"  - {filename}: {checksum[:16]}...")
            return "\n".join(lines)
        return ""


# Singleton instance
artifacts_service = ArtifactsService()
