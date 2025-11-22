# roles.py

from base.base_agent import BaseAgent
import hashlib
import json
from datetime import datetime

class Role:
    def __init__(self, name, intent, capabilities, policy):
        self.name = name
        self.intent = intent
        self.capabilities = capabilities
        self.policy = policy

# Define agent roles
roles = {
    "architect": Role(
        name="architect",
        intent="Design the overall structure of the agent system.",
        capabilities=["system design", "architecture planning"],
        policy="Ensure all designs adhere to governance standards."
    ),
    "builder": Role(
        name="builder",
        intent="Implement the components of the agent system.",
        capabilities=["coding", "integration", "testing"],
        policy="Follow best practices in coding and documentation."
    ),
    "critic": Role(
        name="critic",
        intent="Evaluate the performance and effectiveness of agents.",
        capabilities=["analysis", "feedback", "reporting"],
        policy="Provide constructive feedback and suggestions for improvement."
    ),
    "compliance": Role(
        name="compliance",
        intent="Ensure all actions and intents comply with regulations.",
        capabilities=["regulatory knowledge", "audit"],
        policy="Maintain compliance with all relevant laws and guidelines."
    ),
    "recorder": Role(
        name="recorder",
        intent="Log actions and events for accountability.",
        capabilities=["data entry", "report generation"],
        policy="Ensure accurate and timely recording of all relevant events."
    )
}

class Architect(BaseAgent):
    """
    The Architect role is responsible for designing system architecture.
    It evaluates intents and produces detailed architectural designs.
    """
    
    def __init__(self):
        super().__init__(
            name="Architect",
            id="agent_architect_001",
            capabilities=["design_system", "evaluate_requirements", "propose_architecture"],
            policy={
                "can_design": True,
                "max_design_complexity": "high",
                "requires_approval": False
            }
        )
        self.designs = []
    
    def evaluate_intent(self, intent):
        """Check if the design intent is valid and compliant."""
        if not intent or not isinstance(intent, str):
            return False
        return len(intent.strip()) > 0
    
    def act(self, intent):
        """Design architecture based on the given intent."""
        if not self.evaluate_intent(intent):
            return {"status": "refused", "reason": "Invalid intent"}
        
        design = {
            "status": "designed",
            "intent": intent,
            "architecture": f"Proposed architecture for: {intent}",
            "components": ["frontend", "backend", "database", "api"],
            "design_id": f"design_{len(self.designs) + 1}"
        }
        self.designs.append(design)
        return design
    
    def record(self, event):
        """Log design events."""
        pass
    
    def describe(self):
        """Provide metadata about the Architect agent."""
        metadata = super().describe()
        metadata["designs_created"] = len(self.designs)
        return metadata


class Builder(BaseAgent):
    """
    The Builder role is responsible for implementing designs.
    It takes architectural designs and produces implementations.
    """
    
    def __init__(self):
        super().__init__(
            name="Builder",
            id="agent_builder_001",
            capabilities=["build_system", "implement_components", "deploy"],
            policy={
                "can_build": True,
                "requires_code_review": True,
                "deployment_approval_required": True
            }
        )
        self.builds = []
    
    def evaluate_intent(self, design):
        """Check if the design is valid and buildable."""
        if not design or not isinstance(design, dict):
            return False
        return design.get("status") == "designed"
    
    def act(self, design):
        """Build implementation based on the given design."""
        if not self.evaluate_intent(design):
            return {"status": "refused", "reason": "Invalid or incomplete design"}
        
        build = {
            "status": "built",
            "design_id": design.get("design_id"),
            "implementation": f"Implementation of {design.get('architecture')}",
            "components": self._build_components(design.get("components", [])),
            "build_id": f"build_{len(self.builds) + 1}",
            "code_quality": "high"
        }
        self.builds.append(build)
        return build
    
    def _build_components(self, components):
        """Build each component based on design."""
        return {comp: f"Implemented {comp}" for comp in components}
    
    def record(self, event):
        """Log build events."""
        pass
    
    def describe(self):
        """Provide metadata about the Builder agent."""
        metadata = super().describe()
        metadata["builds_created"] = len(self.builds)
        return metadata


class Critic(BaseAgent):
    """
    The Critic role is responsible for reviewing designs and implementations.
    It evaluates quality, compliance, and architectural soundness.
    """
    
    def __init__(self):
        super().__init__(
            name="Critic",
            id="agent_critic_001",
            capabilities=["review_design", "review_build", "quality_assessment", "risk_analysis"],
            policy={
                "can_review": True,
                "min_quality_score": 70,
                "require_reasoning": True
            }
        )
        self.reviews = []
    
    def evaluate_intent(self, review_package):
        """Check if the review package is valid."""
        if not review_package or not isinstance(review_package, dict):
            return False
        return "design" in review_package or "build" in review_package
    
    def act(self, review_package):
        """Review design and/or build for quality and compliance."""
        if not self.evaluate_intent(review_package):
            return {"status": "refused", "reason": "Invalid review package"}
        
        design = review_package.get("design")
        build = review_package.get("build")
        
        design_score = self._score_design(design) if design else None
        build_score = self._score_build(build) if build else None
        
        passed = self._determine_pass(design_score, build_score)
        
        review = {
            "status": "reviewed",
            "passed": passed,
            "design_score": design_score,
            "build_score": build_score,
            "overall_score": self._calculate_overall_score(design_score, build_score),
            "review_id": f"review_{len(self.reviews) + 1}",
            "feedback": self._generate_feedback(design_score, build_score),
            "risks": self._identify_risks(design, build)
        }
        self.reviews.append(review)
        return review
    
    def _score_design(self, design):
        """Score the architectural design."""
        if not design or design.get("status") != "designed":
            return 0
        # Base score + component count bonus
        base_score = 80
        component_bonus = len(design.get("components", [])) * 2
        return min(100, base_score + component_bonus)
    
    def _score_build(self, build):
        """Score the implementation build."""
        if not build or build.get("status") != "built":
            return 0
        # Base score + quality assessment
        base_score = 85
        code_quality_boost = 10 if build.get("code_quality") == "high" else 0
        return min(100, base_score + code_quality_boost)
    
    def _calculate_overall_score(self, design_score, build_score):
        """Calculate overall score from design and build scores."""
        scores = [s for s in [design_score, build_score] if s is not None]
        return sum(scores) / len(scores) if scores else 0
    
    def _determine_pass(self, design_score, build_score):
        """Determine if review passes based on scores."""
        min_score = self.policy["min_quality_score"]
        scores = [s for s in [design_score, build_score] if s is not None]
        return all(s >= min_score for s in scores) if scores else False
    
    def _generate_feedback(self, design_score, build_score):
        """Generate constructive feedback."""
        feedback = []
        if design_score and design_score < 80:
            feedback.append("Design architecture could be more robust")
        if build_score and build_score < 85:
            feedback.append("Implementation quality needs improvement")
        if not feedback:
            feedback.append("Design and implementation meet quality standards")
        return feedback
    
    def _identify_risks(self, design, build):
        """Identify potential risks in design or build."""
        risks = []
        if design and len(design.get("components", [])) > 5:
            risks.append("High component complexity")
        if build and not build.get("code_quality"):
            risks.append("Code quality not assessed")
        return risks
    
    def record(self, event):
        """Log review events."""
        pass
    
    def describe(self):
        """Provide metadata about the Critic agent."""
        metadata = super().describe()
        metadata["reviews_conducted"] = len(self.reviews)
        return metadata


class Governance(BaseAgent):
    """
    The Governance role is responsible for policy enforcement.
    It validates that designs, builds, and reviews comply with organizational policies.
    """
    
    def __init__(self):
        super().__init__(
            name="Governance",
            id="agent_governance_001",
            capabilities=["enforce_policy", "validate_compliance", "audit_decisions"],
            policy={
                "can_enforce": True,
                "require_original_request": True,
                "require_review_passed": True,
                "compliance_threshold": 80
            }
        )
        self.decisions = []
    
    def evaluate_intent(self, governance_package):
        """Check if the governance package is valid and complete."""
        if not governance_package or not isinstance(governance_package, dict):
            return False
        required_keys = ["request", "review"]
        return all(key in governance_package for key in required_keys)
    
    def act(self, governance_package):
        """Enforce governance policies on the workflow."""
        if not self.evaluate_intent(governance_package):
            return {"status": "refused", "reason": "Invalid governance package"}
        
        request = governance_package.get("request")
        review = governance_package.get("review")
        
        # Check policy compliance
        compliant = self._check_compliance(request, review)
        allowed = self._determine_allowed(compliant, review)
        
        decision = {
            "status": "enforced",
            "allowed": allowed,
            "compliant": compliant,
            "decision_id": f"decision_{len(self.decisions) + 1}",
            "compliance_checks": self._run_compliance_checks(request, review),
            "audit_trail": self._create_audit_trail(request, review),
            "reasoning": self._generate_reasoning(allowed, compliant)
        }
        self.decisions.append(decision)
        return decision
    
    def _check_compliance(self, request, review):
        """Check if the workflow complies with policies."""
        checks = {
            "review_passed": review.get("passed", False),
            "quality_score_acceptable": review.get("overall_score", 0) >= self.policy["compliance_threshold"],
            "no_critical_risks": len(review.get("risks", [])) < 2
        }
        return all(checks.values())
    
    def _determine_allowed(self, compliant, review):
        """Determine if work is allowed to proceed."""
        if not self.policy["require_review_passed"]:
            return True
        return compliant and review.get("passed", False)
    
    def _run_compliance_checks(self, request, review):
        """Run specific compliance checks."""
        return {
            "request_valid": bool(request),
            "review_complete": review.get("status") == "reviewed",
            "quality_acceptable": review.get("overall_score", 0) >= self.policy["compliance_threshold"],
            "risks_identified": len(review.get("risks", [])) > 0,
            "feedback_provided": len(review.get("feedback", [])) > 0
        }
    
    def _create_audit_trail(self, request, review):
        """Create an audit trail of the decision."""
        return {
            "request_checksum": hash(str(request)) % 10000,
            "review_id": review.get("review_id"),
            "decision_timestamp": "2025-11-21T00:00:00Z",
            "enforced_by": self.id
        }
    
    def _generate_reasoning(self, allowed, compliant):
        """Generate reasoning for the decision."""
        if allowed:
            return "Request complies with all policies and quality standards. Proceeding to recording phase."
        elif compliant:
            return "Request is compliant but review did not pass. Require additional review."
        else:
            return "Request does not comply with policy requirements. Action refused."
    
    def record(self, event):
        """Log governance events."""
        pass
    
    def describe(self):
        """Provide metadata about the Governance agent."""
        metadata = super().describe()
        metadata["decisions_made"] = len(self.decisions)
        return metadata


class Recorder(BaseAgent):
    """
    The Recorder role is responsible for logging, scoring, and cryptographically signing
    workflow results. It creates comprehensive audit logs and prepares records for
    distribution to SIEMs, A2A networks, MCP servers, and blockchains.
    """
    
    def __init__(self):
        super().__init__(
            name="Recorder",
            id="agent_recorder_001",
            capabilities=["log_results", "score_results", "cryptographic_sign", "audit_trail"],
            policy={
                "can_record": True,
                "require_all_stages": True,
                "enable_signing": True,
                "retention_days": 90
            }
        )
        self.records = []
    
    def evaluate_intent(self, record_package):
        """Check if the record package is valid and complete."""
        if not record_package or not isinstance(record_package, dict):
            return False
        required_keys = ["request", "design", "build", "review", "governance"]
        return all(key in record_package for key in required_keys)
    
    def act(self, record_package):
        """Record, score, and sign the complete workflow."""
        if not self.evaluate_intent(record_package):
            return {"status": "refused", "reason": "Incomplete record package"}
        
        # Calculate composite score
        composite_score = self._calculate_composite_score(record_package)
        
        # Create cryptographic signature
        signature = self._create_signature(record_package, composite_score)
        
        # Compile complete record
        record = {
            "status": "recorded",
            "record_id": f"record_{len(self.records) + 1}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "composite_score": composite_score,
            "signature": signature,
            "workflow_summary": self._create_workflow_summary(record_package),
            "audit_log": self._create_detailed_audit_log(record_package),
            "export_ready": self._prepare_exports(record_package, signature),
            "metadata": self._extract_metadata(record_package)
        }
        self.records.append(record)
        return record
    
    def _calculate_composite_score(self, record_package):
        """Calculate overall score from all workflow stages."""
        scores = {
            "design_score": record_package.get("design", {}).get("design_id") and 85 or 0,
            "build_score": record_package.get("build", {}).get("build_id") and 90 or 0,
            "review_score": record_package.get("review", {}).get("overall_score", 0),
            "governance_score": 100 if record_package.get("governance", {}).get("allowed") else 0
        }
        
        total = sum(scores.values())
        count = len([s for s in scores.values() if s > 0])
        composite = (total / count) if count > 0 else 0
        
        return {
            "overall": round(composite, 2),
            "stages": scores
        }
    
    def _create_signature(self, record_package, composite_score):
        """Create cryptographic signature of the workflow."""
        # Create a deterministic JSON representation
        payload = json.dumps({
            "request": str(record_package.get("request")),
            "design_id": record_package.get("design", {}).get("design_id"),
            "build_id": record_package.get("build", {}).get("build_id"),
            "review_id": record_package.get("review", {}).get("review_id"),
            "decision_id": record_package.get("governance", {}).get("decision_id"),
            "composite_score": composite_score["overall"]
        }, sort_keys=True)
        
        # Create SHA256 hash
        signature = hashlib.sha256(payload.encode()).hexdigest()
        return {
            "algorithm": "SHA256",
            "hash": signature,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _create_workflow_summary(self, record_package):
        """Create a summary of the complete workflow."""
        return {
            "request": record_package.get("request"),
            "design_status": record_package.get("design", {}).get("status"),
            "build_status": record_package.get("build", {}).get("status"),
            "review_status": record_package.get("review", {}).get("status"),
            "review_passed": record_package.get("review", {}).get("passed"),
            "governance_allowed": record_package.get("governance", {}).get("allowed"),
            "final_status": "APPROVED" if record_package.get("governance", {}).get("allowed") else "REJECTED"
        }
    
    def _create_detailed_audit_log(self, record_package):
        """Create detailed audit log of all stages."""
        return {
            "design_phase": {
                "id": record_package.get("design", {}).get("design_id"),
                "components": record_package.get("design", {}).get("components", []),
                "architecture": record_package.get("design", {}).get("architecture")
            },
            "build_phase": {
                "id": record_package.get("build", {}).get("build_id"),
                "code_quality": record_package.get("build", {}).get("code_quality"),
                "implementation": record_package.get("build", {}).get("implementation")
            },
            "review_phase": {
                "id": record_package.get("review", {}).get("review_id"),
                "design_score": record_package.get("review", {}).get("design_score"),
                "build_score": record_package.get("review", {}).get("build_score"),
                "feedback": record_package.get("review", {}).get("feedback", []),
                "risks": record_package.get("review", {}).get("risks", [])
            },
            "governance_phase": {
                "id": record_package.get("governance", {}).get("decision_id"),
                "compliance_checks": record_package.get("governance", {}).get("compliance_checks", {}),
                "reasoning": record_package.get("governance", {}).get("reasoning")
            }
        }
    
    def _prepare_exports(self, record_package, signature):
        """Prepare record for export to various systems."""
        return {
            "siem_export": {
                "format": "CEF",
                "ready": True,
                "fields": ["record_id", "timestamp", "signature", "composite_score"]
            },
            "a2a_export": {
                "format": "JSON",
                "ready": True,
                "protocol": "REST/gRPC"
            },
            "mcp_export": {
                "format": "JSON-RPC",
                "ready": True,
                "endpoint_compatible": True
            },
            "blockchain_export": {
                "format": "Transaction",
                "ready": True,
                "chainable": True,
                "hash": signature["hash"]
            }
        }
    
    def _extract_metadata(self, record_package):
        """Extract metadata from all stages."""
        return {
            "total_agents_involved": 5,
            "workflow_duration_estimated": "N/A",
            "approval_chain": [
                record_package.get("design", {}).get("design_id"),
                record_package.get("build", {}).get("build_id"),
                record_package.get("review", {}).get("review_id"),
                record_package.get("governance", {}).get("decision_id")
            ],
            "recorded_by": self.id
        }
    
    def record(self, event):
        """Log recorder events."""
        pass
    
    def describe(self):
        """Provide metadata about the Recorder agent."""
        metadata = super().describe()
        metadata["records_created"] = len(self.records)
        return metadata