"""
Team Agent Orchestrator - Main coordination layer.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from swarms.team_agent.roles import (
    Architect,
    Builder,
    Critic,
    Recorder,
    Governance,  # add if available
)
from utils.logging import get_logger

# Correct capability imports
from swarms.team_agent.capabilities.registry import CapabilityRegistry
from utils.capabilities.dynamic_builder import DynamicBuilder

# PKI imports
from swarms.team_agent.crypto import PKIManager, TrustDomain

try:
    from utils.capabilities import HRTGuideCapability
except ImportError:
    try:
        from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability
    except Exception:
        HRTGuideCapability = None


class Orchestrator:
    """
    Orchestrator for coordinating multi-agent workflows with capability-aware building.
    """

    def __init__(self, output_dir: str = "./team_output", max_iterations: int = 3):
        self.output_dir = output_dir
        self.max_iterations = max_iterations
        self.current_workflow_id = None
        self.logger = get_logger("orchestrator")
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize PKI infrastructure
        self.pki_manager = PKIManager()
        self.pki_manager.initialize_pki()
        self.logger.info("PKI infrastructure initialized")

        # Load certificate chains for each trust domain
        self.cert_chains = {
            TrustDomain.GOVERNMENT: self.pki_manager.get_certificate_chain(TrustDomain.GOVERNMENT),
            TrustDomain.EXECUTION: self.pki_manager.get_certificate_chain(TrustDomain.EXECUTION),
            TrustDomain.LOGGING: self.pki_manager.get_certificate_chain(TrustDomain.LOGGING),
        }

        self.capability_registry = CapabilityRegistry()
        self._register_default_capabilities()
        self.dynamic_builder = DynamicBuilder(registry=self.capability_registry)
        self.logger.info("Orchestrator initialized with capability system and PKI")

    def _register_default_capabilities(self):
        if HRTGuideCapability:
            try:
                self.capability_registry.register(HRTGuideCapability())
            except Exception:
                pass
        self.logger.info(f"Registered {len(self.capability_registry.list_capabilities())} capabilities")

    def execute(self, mission: str) -> dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_workflow_id = f"wf_{timestamp}"
        self.logger.info(f"Created new workflow {self.current_workflow_id}")

        # Create agents with their respective certificate chains
        architect = Architect(
            self.current_workflow_id,
            cert_chain=self.cert_chains[TrustDomain.EXECUTION]
        )
        builder = Builder(
            self.current_workflow_id,
            cert_chain=self.cert_chains[TrustDomain.EXECUTION]
        )
        critic = Critic(
            self.current_workflow_id,
            cert_chain=self.cert_chains[TrustDomain.EXECUTION]
        )
        recorder = Recorder(
            self.current_workflow_id,
            cert_chain=self.cert_chains[TrustDomain.LOGGING]
        )
        governance = None
        try:
            governance = Governance(
                self.current_workflow_id,
                cert_chain=self.cert_chains[TrustDomain.GOVERNMENT]
            )
        except Exception:
            pass

        final_record = self._execute_workflow(mission, architect, builder, critic, recorder, governance)
        return {"workflow_id": self.current_workflow_id, "final_record": final_record}

    def _prepare_context(self, base: dict | str) -> dict:
        """Return normalized context for role agents."""
        if isinstance(base, str):
            return {"input": base, "raw_input": base}
        if "input" not in base:
            # Preserve original while providing input string form
            base["input"] = json.dumps(base, default=str)
        return base

    def _run_agent(self, agent, payload):
        ctx = self._prepare_context(payload)
        return agent.run(ctx)

    def _execute_workflow(self, mission: str, architect, builder, critic, recorder, governance=None) -> dict:
        self.logger.info(f"Starting workflow execution: {mission}")

        # Phase 1
        self.logger.info("Phase 1: Architecture")
        architect_output = self._run_agent(architect, {"mission": mission})

        # Optional governance pre-check
        if governance:
            try:
                self._run_agent(governance, {"stage": "pre_build", "architecture": architect_output})
            except Exception:
                pass

        # Phase 2
        self.logger.info("Phase 2: Implementation")
        # Use actual Builder agent with LLM-powered code generation
        builder_result = self._run_agent(builder, architect_output)

        # Phase 3: Review
        self.logger.info("Phase 3: Review")

        # Extract code from builder result
        # Builder returns generated_code list with component code
        generated_code = builder_result.get("generated_code", [])
        if generated_code:
            # Combine all component code for review
            code = "\n\n".join(item.get("code", "") for item in generated_code)
        else:
            # Fallback for dict format (DynamicBuilder)
            artifacts = builder_result.get("artifacts", {})
            if isinstance(artifacts, dict):
                code = artifacts.get("primary_code", "")
            else:
                code = ""

        critic_payload = {
            "mission": mission,
            "architecture": architect_output,
            "implementation": builder_result,
            "code": code,
        }
        critic_output = self._run_agent(critic, critic_payload)

        # Optional governance post-review
        if governance:
            try:
                self._run_agent(governance, {
                    "stage": "post_review",
                    "review": critic_output,
                    "implementation": builder_result
                })
            except Exception:
                pass

        # Phase 4: Recording/Publishing
        self.logger.info("Phase 4: Recording/Publishing")
        workflow_dir = Path(self.output_dir) / self.current_workflow_id
        workflow_dir.mkdir(parents=True, exist_ok=True)

        published_artifacts = {}

        # Check if Builder generated code
        generated_code = builder_result.get("generated_code", [])
        if generated_code:
            # Write out code from Builder's generated_code list
            for item in generated_code:
                component = item.get("component", "unknown")
                code = item.get("code", "")
                if code:
                    filename = f"{component}.py"
                    path = workflow_dir / filename
                    path.write_text(code)
                    published_artifacts[component] = str(path)

            # Use first component as primary code
            if generated_code:
                published_artifacts["primary_code"] = published_artifacts.get(
                    generated_code[0].get("component", "unknown"), ""
                )
        else:
            # Fallback for DynamicBuilder dict format
            artifacts = builder_result.get("artifacts", {})
            if isinstance(artifacts, dict):
                for name, content in artifacts.items():
                    suffix = ".py" if not any(name.endswith(ext) for ext in (".md", ".txt", ".json")) else ""
                    path = workflow_dir / f"{name}{suffix}"
                    path.write_text(content)
                    published_artifacts[name] = str(path)

        recorder_payload = {
            "mission": mission,
            "architecture": architect_output,
            "implementation": builder_result,
            "review": critic_output,
            "artifacts": published_artifacts
        }
        self._run_agent(recorder, recorder_payload)

        return {
            "workflow_id": self.current_workflow_id,
            "mission": mission,
            "architecture": architect_output,
            "implementation": builder_result,
            "review": critic_output,
            "published_artifacts": published_artifacts,
            "capability_used": builder_result.get("capability_used", "default"),
            "timestamp": datetime.now().isoformat(),
        }