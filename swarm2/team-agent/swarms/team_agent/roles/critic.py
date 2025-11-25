"""
Critic Agent - Reviews designs and builds for quality.
"""

from __future__ import annotations
from typing import Dict, Any, List
import uuid


class Critic:
    """
    Reviews designs and builds for quality and compliance.
    """

    def __init__(self, name: str = "Critic", id: str = "agent_critic_001"):
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
            "min_quality_score": 0.6,  # added
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
        Review the design and build artifacts.
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

        # Simple scoring heuristics
        design_score = 0.85 if design.get("status") == "designed" else 0.5
        build_score = 0.80 if build.get("status") == "built" else 0.5
        overall_score = round((design_score + build_score) / 2, 2)

        findings: List[Dict[str, Any]] = []
        if design.get("components"):
            findings.append({"type": "info", "message": f"Design has {len(design['components'])} components"})
        if build.get("artifacts"):
            findings.append({"type": "info", "message": f"Build has {len(build['artifacts'])} artifacts"})

        # Determine if review passed
        passed = overall_score >= 0.6

        # Identify risks
        risks: List[Dict[str, Any]] = []
        if not design.get("components"):
            risks.append({"level": "medium", "description": "No components defined"})
        if overall_score < 0.7:
            risks.append({"level": "low", "description": "Score below optimal threshold"})

        review = {
            "status": "reviewed",
            "review_id": review_id,
            "score": overall_score,
            "overall_score": overall_score,  # added - alias for tests
            "design_score": design_score,
            "build_score": build_score,
            "findings": findings,
            "feedback": f"Review complete with score {overall_score}. {'Approved.' if passed else 'Needs revision.'}",  # added
            "passed": passed,  # added
            "risks": risks,  # added
            "recommendation": "approved" if passed else "needs_revision",
            "summary": f"Review complete. Overall score: {overall_score}",
        }

        self.reviews.append(review)
        return review

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the critic with a context dict.
        Extracts design/build from context and delegates to act().
        """
        # Handle various input formats
        if "design" in context or "build" in context:
            return self.act(context)
        # If context has implementation, treat as build
        if "implementation" in context or "code" in context:
            return self.act({"build": context})
        # Fallback: wrap entire context as build
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
            "reviews_conducted": self.reviews_created,  # added - alias for tests
            "capabilities": self.capabilities,
            "policy": self.policy,
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