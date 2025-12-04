"""
Critic Agent - Reviews designs and builds for quality.
Uses ToolRegistry for code review and scoring.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import uuid

from ..tools import ToolRegistry, ReviewTool, ScoringTool, CodeValidatorTool

# Import crypto modules (optional)
try:
    from swarms.team_agent.crypto import Signer
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Signer = None


class Critic:
    """
    Reviews designs and builds for quality and compliance.
    Uses tools for review and scoring.
    """

    def __init__(
        self,
        workflow_id: str = "unknown",
        name: str = "Critic",
        id: str = "agent_critic_001",
        registry: Optional[ToolRegistry] = None,
        cert_chain: Optional[Dict[str, bytes]] = None
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.id = id
        self.metadata = {
            "id": self.id,
            "name": self.name,
            "description": "Reviews designs and builds for quality and compliance.",
        }
        self.policy: Dict[str, Any] = {
            "can_review": True,
            "require_approval": False,
            "min_quality_score": 0.6,
        }
        self.reviews_created = 0
        self.reviews: List[Dict[str, Any]] = []
        self.capabilities: List[str] = [
            "review_design",
            "review_build",
            "evaluate_quality",
            "describe",
            "act",
        ]
        
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
                    signer_id="critic"
                )
            except Exception:
                pass

    def _register_default_tools(self) -> None:
        """Register default tools if not already present."""
        if "code_reviewer" not in self._registry:
            self._registry.register(ReviewTool())
        if "content_scorer" not in self._registry:
            self._registry.register(ScoringTool())
        if "code_validator" not in self._registry:
            self._registry.register(CodeValidatorTool())

    def evaluate_input(self, payload: Any) -> bool:
        """
        Quick validation of review input.
        Returns False for empty/invalid input, True otherwise.
        """
        if not payload or not isinstance(payload, dict):
            return False
        design = payload.get("design", {})
        build = payload.get("build", {})
        return bool(design or build)

    def evaluate_intent(self, intent: Any) -> bool:
        """
        Quick validation of intent/payload input.
        Returns False for empty/invalid input, True otherwise.
        """
        if intent is None:
            return False
        if isinstance(intent, str):
            return bool(intent.strip())
        if isinstance(intent, dict):
            return self.evaluate_input(intent)
        return False

    def act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review the design and build artifacts using tools.
        Returns a review with score and feedback.
        """
        if not self.evaluate_input(payload):
            return {
                "status": "refused",
                "reason": "invalid_input",
                "message": "Payload must contain design and/or build.",
            }

        review_id = str(uuid.uuid4())
        self.reviews_created += 1

        design = payload.get("design", {})
        build = payload.get("build", {})

        # Use tools for analysis
        all_findings: List[Dict[str, Any]] = []
        tool_results = []
        
        # Review build code if available
        build_code = ""
        if build.get("generated_code"):
            for gen in build["generated_code"]:
                build_code += gen.get("code", "") + "\n"
        elif build.get("code"):
            build_code = build["code"]
        
        if build_code:
            # Use review tool
            review_result = self._registry.invoke(
                "code_reviewer",
                content=build_code,
                criteria=["security", "quality", "maintainability"]
            )
            if review_result.success:
                all_findings.extend(review_result.output.get("issues", []))
                all_findings.extend([
                    {"type": "suggestion", **s} 
                    for s in review_result.output.get("suggestions", [])
                ])
                tool_results.append({
                    "tool": "code_reviewer",
                    "issues": len(review_result.output.get("issues", [])),
                    "suggestions": len(review_result.output.get("suggestions", [])),
                })
            
            # Use scoring tool
            score_result = self._registry.invoke("content_scorer", content=build_code)
            if score_result.success:
                tool_results.append({
                    "tool": "content_scorer",
                    "overall_score": score_result.output.get("overall_score", 0),
                    "breakdown": score_result.output.get("breakdown", []),
                })

        # Calculate scores
        design_score = 0.85 if design.get("status") == "designed" else 0.5
        build_score = 0.80 if build.get("status") == "built" else 0.5
        
        # Adjust build score based on tool findings
        issue_count = sum(1 for f in all_findings if f.get("type") in ["security", "style"])
        if issue_count > 0:
            build_score = max(0.3, build_score - (issue_count * 0.05))
        
        overall_score = round((design_score + build_score) / 2, 2)

        # Add design findings
        if design.get("components"):
            all_findings.append({"type": "info", "message": f"Design has {len(design['components'])} components"})
        if build.get("artifacts"):
            all_findings.append({"type": "info", "message": f"Build has {len(build['artifacts'])} artifacts"})

        # Determine if review passed
        passed = overall_score >= self.policy.get("min_quality_score", 0.6)

        # Identify risks
        risks: List[Dict[str, Any]] = []
        if not design.get("components"):
            risks.append({"level": "medium", "description": "No components defined"})
        if overall_score < 0.7:
            risks.append({"level": "low", "description": "Score below optimal threshold"})
        
        # Add risks from security findings
        security_issues = [f for f in all_findings if f.get("type") == "security"]
        for si in security_issues:
            risks.append({"level": "high", "description": si.get("message", "Security issue detected")})

        review = {
            "status": "reviewed",
            "review_id": review_id,
            "score": overall_score,
            "overall_score": overall_score,
            "design_score": design_score,
            "build_score": build_score,
            "findings": all_findings,
            "feedback": f"Review complete with score {overall_score}. {'Approved.' if passed else 'Needs revision.'}",
            "passed": passed,
            "risks": risks,
            "recommendation": "approved" if passed else "needs_revision",
            "summary": f"Review complete. Overall score: {overall_score}",
            "tool_results": tool_results,
            "tools_used": ["code_reviewer", "content_scorer"],
        }

        self.reviews.append(review)

        # Sign output if signer is available
        if self.signer and CRYPTO_AVAILABLE:
            review = self.signer.sign_dict(review)

        return review

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the critic with a context dict.
        Extracts design/build from context and delegates to act().
        """
        if "design" in context or "build" in context:
            return self.act(context)
        if "implementation" in context or "code" in context:
            return self.act({"build": context})
        return self.act({"build": context})

    def describe(self) -> Dict[str, Any]:
        """
        Return metadata and simple I/O schema for this role.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.metadata.get("description", ""),
            "type": "role",
            "role": "critic",
            "reviews_created": self.reviews_created,
            "reviews_conducted": self.reviews_created,
            "capabilities": self.capabilities,
            "policy": self.policy,
            "tools_available": [t.name for t in self._registry.list_tools()],
            "inputs": {
                "design": {"type": "object", "required": False},
                "build": {"type": "object", "required": False},
            },
            "outputs": {
                "status": {"type": "string", "enum": ["reviewed", "refused"]},
                "review_id": {"type": "string"},
                "score": {"type": "number"},
                "findings": {"type": "array"},
            },
        }
