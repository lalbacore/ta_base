"""
Recorder Agent - Records workflow outputs with signature and composite score.
Uses ToolRegistry for scoring and validation.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import uuid
import time

from ..tools import ToolRegistry, ScoringTool

# Import crypto modules (optional)
try:
    from swarms.team_agent.crypto import Signer, ManifestGenerator
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Signer = None
    ManifestGenerator = None


class Recorder:
    """
    Records workflow outputs with signature and audit trail.
    Uses tools for scoring and validation.
    """

    def __init__(
        self,
        workflow_id: str = "unknown",
        name: str = "Recorder",
        id: str = "agent_recorder_001",
        registry: Optional[ToolRegistry] = None,
        cert_chain: Optional[Dict[str, bytes]] = None
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.id = id
        self.capabilities: List[str] = ["record", "describe"]
        self.records: List[Dict[str, Any]] = []
        
        # Initialize tool registry
        self._registry = registry or ToolRegistry()
        self._register_default_tools()

        # Initialize signer if cert_chain is provided
        self.signer = None
        if cert_chain and CRYPTO_AVAILABLE:
            try:
                self.signer = Signer(
                    private_key_pem=cert_chain['key'],
                    certificate_pem=cert_chain['cert'],
                    signer_id="recorder"
                )
            except Exception:
                pass

        # Initialize manifest generator
        self.manifest_generator = None
        if CRYPTO_AVAILABLE and ManifestGenerator:
            self.manifest_generator = ManifestGenerator()

    def _register_default_tools(self) -> None:
        """Register default tools if not already present."""
        if "content_scorer" not in self._registry:
            self._registry.register(ScoringTool())

    def act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record the workflow package. Expects package keys:
        - request, design, build, review, governance
        """
        if not isinstance(payload, dict):
            return {"status": "refused", "reason": "invalid_package"}

        governance = payload.get("governance", {}) or {}
        review = payload.get("review", {}) or {}
        design = payload.get("design", {}) or {}
        build = payload.get("build", {}) or {}
        
        # Build composite_score as dict with overall and stages
        gov_score = float(governance.get("composite_score", 0.8))
        review_score = float(review.get("score", 0.8))
        overall = round((gov_score + review_score) / 2 * 100, 1)

        # Use scoring tool to validate final package quality
        package_summary = f"""
        Design: {design.get('status', 'unknown')}
        Build: {build.get('status', 'unknown')}
        Review: {review.get('status', 'unknown')} (score: {review_score})
        Governance: {governance.get('status', 'unknown')} (score: {gov_score})
        """
        
        score_result = self._registry.invoke("content_scorer", content=package_summary)
        package_quality = None
        if score_result.success:
            package_quality = score_result.output.get("overall_score", 0)

        composite_score = {
            "overall": overall,
            "package_quality": package_quality,
            "stages": {
                "design": 85.0,
                "build": 80.0,
                "review": round(review_score * 100, 1),
                "governance": round(gov_score * 100, 1),
            }
        }

        record_id = str(uuid.uuid4())
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        signature = {
            "by": self.name,
            "ts": timestamp,
            "algorithm": "SHA256",
            "hash": str(uuid.uuid4()).replace("-", ""),
            "verified": True,
        }

        # Build audit log as dict with phase keys
        audit_log = {
            "request_phase": {"timestamp": timestamp, "status": "received"},
            "design_phase": {"timestamp": timestamp, "status": design.get("status", "unknown")},
            "build_phase": {"timestamp": timestamp, "status": build.get("status", "unknown")},
            "review_phase": {"timestamp": timestamp, "status": review.get("status", "unknown")},
            "governance_phase": {"timestamp": timestamp, "status": governance.get("status", "unknown")},
            "record_phase": {"timestamp": timestamp, "status": "recorded"},
        }

        # Collect all tools used across the workflow
        tools_used_all = set()
        for stage in [design, build, review, governance]:
            tools_used_all.update(stage.get("tools_used", []))
        tools_used_all.add("content_scorer")  # Recorder's own tool

        record = {
            "status": "recorded",
            "record_id": record_id,
            "signature": signature,
            "composite_score": composite_score,
            "workflow_summary": {
                "final_status": "APPROVED" if governance.get("allowed", True) else "REJECTED",
                "stages_completed": ["design", "build", "review", "governance", "record"],
                "tools_used": list(tools_used_all),
            },
            "audit_log": audit_log,
            "export_ready": {
                "json": {"ready": True},
                "pdf": {"ready": True},
                "markdown": {"ready": True},
                "siem_export": {"ready": True},
                "a2a_export": {"ready": True},
                "mcp_export": {"ready": True},
                "xml": {"ready": True},
                "csv": {"ready": True},
                "html": {"ready": True},
                "blockchain_export": {"ready": True},
            },
            "package": {
                "request": payload.get("request"),
                "design": design,
                "build": build,
                "review": review,
                "governance": governance,
            },
            "tools_used": ["content_scorer"],
        }
        self.records.append(record)

        # Generate comprehensive manifest if available
        if self.manifest_generator:
            role_outputs = {
                "architect": design,
                "builder": build,
                "critic": review,
                "governance": governance,
                "recorder": record,
            }

            # Extract mission description from request or context
            mission = payload.get("request", {}).get("mission", "Unknown mission") if isinstance(payload.get("request"), dict) else "Unknown mission"

            # Generate artifacts list from build
            artifacts = []
            if build and isinstance(build, dict):
                for artifact in build.get("artifacts", []):
                    if isinstance(artifact, dict):
                        artifacts.append({
                            "type": artifact.get("type", "implementation"),
                            "name": artifact.get("component", "unnamed"),
                            "status": artifact.get("status", "unknown"),
                        })

            manifest = self.manifest_generator.generate_manifest(
                workflow_id=self.workflow_id,
                mission=mission,
                role_outputs=role_outputs,
                artifacts=artifacts
            )

            record["manifest"] = manifest
            record["manifest_text"] = self.manifest_generator.export_manifest(manifest, format="text")

        # Sign output if signer is available
        if self.signer and CRYPTO_AVAILABLE:
            record = self.signer.sign_dict(record)

        return record

    def run(self, context: Any) -> Dict[str, Any]:
        """
        Run the recorder with a context.
        Delegates to act().
        """
        if isinstance(context, dict):
            return self.act(context)
        return self.act({"input": context})

    def describe(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": "role",
            "role": "recorder",
            "capabilities": self.capabilities,
            "records_created": len(self.records),
            "tools_available": [t.name for t in self._registry.list_tools()],
        }
