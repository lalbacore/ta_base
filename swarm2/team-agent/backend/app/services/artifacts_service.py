"""
Artifacts Service - Bridges Flask API to workflow artifacts.
"""
import sys
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class ArtifactsService:
    """
    Service layer for artifacts and manifests.
    Reads actual workflow artifacts from team_output directory.
    """

    def __init__(self):
        # Default output directory
        self.output_dir = Path(os.path.expanduser(
            "~/Dropbox/Team Agent/Projects/ta_base/swarm2/team-agent/team_output"
        ))

    def get_workflow_manifest(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow manifest by generating it from artifacts."""
        workflow_dir = self.output_dir / workflow_id

        if not workflow_dir.exists():
            return None

        # Generate manifest from artifacts
        artifacts = list(workflow_dir.glob('*'))
        checksums = {}

        for artifact in artifacts:
            if artifact.is_file():
                # Calculate SHA256 checksum
                content = artifact.read_bytes()
                checksum = hashlib.sha256(content).hexdigest()
                checksums[artifact.name] = checksum

        return {
            'workflow_id': workflow_id,
            'generated_at': workflow_dir.stat().st_mtime,
            'checksums': checksums,
            'artifact_count': len(checksums)
        }

    def get_workflow_artifacts(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get workflow artifacts with metadata."""
        workflow_dir = self.output_dir / workflow_id

        if not workflow_dir.exists():
            return []

        artifacts = []
        for artifact_path in workflow_dir.glob('*'):
            if artifact_path.is_file():
                # Read file content and calculate checksum
                # Safe reading with error handling
                try:
                    content = artifact_path.read_text(encoding='utf-8', errors='replace') if artifact_path.suffix in ['.py', '.txt', '.md', '.json'] else None
                except Exception:
                    content = None
                checksum = hashlib.sha256(artifact_path.read_bytes()).hexdigest()

                artifacts.append({
                    'name': artifact_path.name,
                    'path': str(artifact_path),
                    'size': artifact_path.stat().st_size,
                    'sha256_checksum': checksum,
                    'verified': True,
                    'content': content,
                    'type': artifact_path.suffix[1:] if artifact_path.suffix else 'unknown',
                    'provenance_score': 0.0 if 'manual' in artifact_path.name.lower() else (0.8 if artifact_path.suffix in ['.md', '.txt'] else 1.0)
                })

        return artifacts

    def get_artifact_content(self, workflow_id: str, artifact_name: str) -> Optional[str]:
        """Get the content of a specific artifact."""
        workflow_dir = self.output_dir / workflow_id
        artifact_path = workflow_dir / artifact_name

        if not artifact_path.exists() or not artifact_path.is_file():
            return None

        try:
            return artifact_path.read_text()
        except Exception:
            # Binary file or read error
            return None

    def verify_artifact(self, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify artifact checksum."""
        workflow_id = artifact_data.get('workflow_id')
        artifact_name = artifact_data.get('name')

        if not workflow_id or not artifact_name:
            return {
                'valid': False,
                'errors': ['Missing workflow_id or artifact name'],
                'warnings': []
            }

        workflow_dir = self.output_dir / workflow_id
        artifact_path = workflow_dir / artifact_name

        if not artifact_path.exists():
            return {
                'valid': False,
                'errors': ['Artifact not found'],
                'warnings': []
            }

        # Calculate actual checksum
        content = artifact_path.read_bytes()
        actual_checksum = hashlib.sha256(content).hexdigest()
        expected_checksum = artifact_data.get('sha256_checksum', '')

        if actual_checksum != expected_checksum:
            return {
                'valid': False,
                'errors': ['Checksum mismatch'],
                'warnings': [],
                'expected': expected_checksum,
                'actual': actual_checksum
            }

        return {
            'valid': True,
            'errors': [],
            'warnings': [],
            'checksum': actual_checksum
        }

    def verify_manifest(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify manifest integrity."""
        workflow_id = manifest_data.get('workflow_id')

        if not workflow_id:
            return {
                'valid': False,
                'errors': ['Missing workflow_id'],
                'warnings': []
            }

        # Regenerate manifest and compare checksums
        actual_manifest = self.get_workflow_manifest(workflow_id)

        if not actual_manifest:
            return {
                'valid': False,
                'errors': ['Workflow not found'],
                'warnings': []
            }

        expected_checksums = manifest_data.get('checksums', {})
        actual_checksums = actual_manifest.get('checksums', {})

        mismatches = []
        for filename, expected_checksum in expected_checksums.items():
            actual_checksum = actual_checksums.get(filename)
            if actual_checksum != expected_checksum:
                mismatches.append(f"{filename}: checksum mismatch")

        if mismatches:
            return {
                'valid': False,
                'errors': mismatches,
                'warnings': []
            }

        return {
            'valid': True,
            'errors': [],
            'warnings': []
        }

    def export_manifest(self, workflow_id: str, format_type: str) -> str:
        """Export manifest in specified format."""
        manifest = self.get_workflow_manifest(workflow_id)

        if not manifest:
            return ""

        if format_type == 'json':
            return json.dumps(manifest, indent=2)
        elif format_type == 'text':
            # Simple text format
            lines = [
                f"Workflow Manifest: {manifest['workflow_id']}",
                f"Generated: {manifest.get('generated_at', 'N/A')}",
                f"Artifact Count: {manifest.get('artifact_count', 0)}",
                "",
                "Checksums:",
            ]
            for filename, checksum in manifest.get('checksums', {}).items():
                lines.append(f"  - {filename}: {checksum}")
            return "\n".join(lines)
        return ""

    def publish_to_registry(self, workflow_id: str, artifact_name: str, publish_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish artifact to the capability registry.

        Args:
            workflow_id: Workflow that generated the artifact
            artifact_name: Name of the artifact file
            publish_data: Additional metadata (capability_type, description, price, etc.)

        Returns:
            Result dictionary with success status and details
        """
        try:
            # Get artifact details
            artifacts = self.get_workflow_artifacts(workflow_id)
            artifact = next((a for a in artifacts if a['name'] == artifact_name), None)

            if not artifact:
                return {
                    'success': False,
                    'error': f'Artifact {artifact_name} not found in workflow {workflow_id}'
                }

            # Import registry
            from swarms.team_agent.a2a.registry import CapabilityRegistry, CapabilityType
            registry = CapabilityRegistry()

            # Prepare capability data
            capability_id = f"cap_{workflow_id}_{artifact_name.replace('.', '_')}"

            # Map string to enum (default to CODE_GENERATION)
            capability_type_str = publish_data.get('capability_type', 'code_generation').upper()
            try:
                capability_type = CapabilityType[capability_type_str]
            except KeyError:
                capability_type = CapabilityType.CODE_GENERATION

            provider_id = publish_data.get('provider_id', 'team_agent_orchestrator')

            # For JSON response (use enum value, not enum object)
            capability_data = {
                'capability_id': capability_id,
                'capability_type': capability_type.value,  # Use .value for JSON serialization
                'provider_id': provider_id,
                'name': artifact_name,
                'description': publish_data.get('description', f'Generated artifact from workflow {workflow_id}'),
                'price': publish_data.get('price', 50.0),
                'metadata': {
                    'workflow_id': workflow_id,
                    'artifact_name': artifact_name,
                    'sha256_checksum': artifact['sha256_checksum'],
                    'size': artifact['size'],
                    'type': artifact['type'],
                    'verified': artifact.get('verified', True)
                }
            }

            # Register the capability
            registry.register_capability(
                provider_id=provider_id,
                capability_type=capability_type,
                name=artifact_name,
                description=publish_data.get('description', f'Generated artifact from workflow {workflow_id}'),
                version="1.0.0",
                price=publish_data.get('price', 50.0),
                requirements={
                    'workflow_id': workflow_id,
                    'sha256_checksum': artifact['sha256_checksum'],
                    'size': artifact['size'],
                    'type': artifact['type']
                }
            )

            print(f"✅ Published artifact {artifact_name} to registry as {capability_id}")

            return {
                'success': True,
                'capability_id': capability_id,
                'message': f'Successfully published {artifact_name} to the capability registry',
                'details': capability_data
            }

        except Exception as e:
            print(f"❌ Error publishing artifact: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
artifacts_service = ArtifactsService()
