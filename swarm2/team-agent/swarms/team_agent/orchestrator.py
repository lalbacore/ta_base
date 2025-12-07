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

# Agent Manager
from swarms.team_agent.agent_manager import AgentManager
from swarms.team_agent.state.turing_tape import TuringTape

try:
    from utils.capabilities import HRTGuideCapability
except ImportError:
    try:
        from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability
    except Exception:
        HRTGuideCapability = None

# Import specialist agents (new agent-capability model)
try:
    from swarms.team_agent.specialists import LegalSpecialist
except ImportError:
    LegalSpecialist = None

try:
    from swarms.team_agent.specialists import AWSSpecialist, AzureSpecialist, GCPSpecialist, OCISpecialist
except ImportError:
    AWSSpecialist = None
    AzureSpecialist = None
    GCPSpecialist = None
    OCISpecialist = None

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

        # Initialize databases (backend.db, trust.db, registry.db)
        try:
            from app.database import init_backend_db
            init_backend_db()
            self.logger.info("Backend databases initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize backend databases: {e}")

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

        # Initialize Agent Manager for workflow agent tracking
        self.agent_manager = AgentManager()

        # Initialize DynamicBuilder with agent_manager for specialist selection
        self.dynamic_builder = DynamicBuilder(
            registry=self.capability_registry,
            agent_manager=self.agent_manager
        )

        # Register specialist agents (new agent-capability model)
        self._register_specialist_agents()

        self.logger.info("Orchestrator initialized with agent-capability system, PKI, and agent management")

    def _register_specialist_agents(self):
        """Register specialist agents with their capabilities."""
        specialists_registered = 0

        # Register LegalSpecialist
        if LegalSpecialist:
            try:
                legal_specialist = LegalSpecialist()
                self.agent_manager.register_specialist(legal_specialist)
                specialists_registered += 1
                self.logger.info("Registered LegalSpecialist")
            except Exception as e:
                self.logger.error(f"Failed to register LegalSpecialist: {e}")

        # Register AWSSpecialist
        if AWSSpecialist:
            try:
                aws_specialist = AWSSpecialist()
                self.agent_manager.register_specialist(aws_specialist)
                specialists_registered += 1
                self.logger.info("Registered AWSSpecialist")
            except Exception as e:
                self.logger.error(f"Failed to register AWSSpecialist: {e}")

        # Register AzureSpecialist
        if AzureSpecialist:
            try:
                azure_specialist = AzureSpecialist()
                self.agent_manager.register_specialist(azure_specialist)
                specialists_registered += 1
                self.logger.info("Registered AzureSpecialist")
            except Exception as e:
                self.logger.error(f"Failed to register AzureSpecialist: {e}")

        # Register GCPSpecialist
        if GCPSpecialist:
            try:
                gcp_specialist = GCPSpecialist()
                self.agent_manager.register_specialist(gcp_specialist)
                specialists_registered += 1
                self.logger.info("Registered GCPSpecialist")
            except Exception as e:
                self.logger.error(f"Failed to register GCPSpecialist: {e}")

        # Register OCISpecialist
        if OCISpecialist:
            try:
                oci_specialist = OCISpecialist()
                self.agent_manager.register_specialist(oci_specialist)
                specialists_registered += 1
                self.logger.info("Registered OCISpecialist")
            except Exception as e:
                self.logger.error(f"Failed to register OCISpecialist: {e}")

        # Register HRTSpecialist (future - when implemented)
        # if HRTSpecialist:
        #     try:
        #         hrt_specialist = HRTSpecialist()
        #         self.agent_manager.register_specialist(hrt_specialist)
        #         specialists_registered += 1
        #     except Exception as e:
        #         self.logger.error(f"Failed to register HRTSpecialist: {e}")

        self.logger.info(f"Registered {specialists_registered} specialist agents")

    def execute(self, mission: str) -> dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_workflow_id = f"wf_{timestamp}"
        self.logger.info(f"Created new workflow {self.current_workflow_id}")

        # Initialize Turing Tape for this workflow
        self.tape = TuringTape(workflow_id=self.current_workflow_id)
        self.tape.append("orchestrator", "workflow_start", {"mission": mission})

        # Create agents with their respective certificate chains
        architect = Architect(
            self.current_workflow_id,
            cert_chain=self.cert_chains[TrustDomain.EXECUTION]
        )
        # Note: No longer creating Builder - using DynamicBuilder instead
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

        # Register workflow agents in agent_cards table
        self.agent_manager.ensure_registered(architect)
        self.agent_manager.ensure_registered(critic)
        self.agent_manager.ensure_registered(recorder)
        if governance:
            self.agent_manager.ensure_registered(governance)

        final_record = self._execute_workflow(mission, architect, critic, recorder, governance)
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

    def _execute_workflow(self, mission: str, architect, critic, recorder, governance=None) -> dict:
        self.logger.info(f"Starting workflow execution: {mission}")

        # Phase 1
        self.logger.info("Phase 1: Architecture")
        architect_output = self._run_agent(architect, {"mission": mission})
        self.agent_manager.track_invocation(
            architect.id, self.current_workflow_id, architect_output, success=True
        )
        self.tape.append("architect", "design_complete", architect_output)

        # Optional governance pre-check
        if governance:
            try:
                governance_pre = self._run_agent(governance, {"stage": "pre_build", "architecture": architect_output})
                self.agent_manager.track_invocation(
                    governance.id, self.current_workflow_id, governance_pre, success=True
                )
                self.tape.append("governance", "policy_check_pre_build", governance_pre)
            except Exception as e:
                self.agent_manager.track_invocation(
                    governance.id, self.current_workflow_id, None, success=False, error=str(e)
                )

        # Phase 2
        self.logger.info("Phase 2: Implementation")
        # Set workflow ID on DynamicBuilder for specialist agent instantiation
        self.dynamic_builder.set_workflow_id(self.current_workflow_id)

        # Use DynamicBuilder with specialist agent selection
        architecture_str = json.dumps(architect_output, default=str) if isinstance(architect_output, dict) else str(architect_output)
        builder_result = self.dynamic_builder.run(mission=mission, architecture=architecture_str)

        # Track specialist/capability invocation
        agent_used = builder_result.get("agent_used", "FallbackBuilder")
        capability_used = builder_result.get("capability_used", "fallback")

        # Track as specialist agent if metadata includes agent_id
        metadata = builder_result.get("metadata", {})
        agent_id = metadata.get("agent_id")

        if agent_id:
            # Specialist agent was used - track the agent
            self.agent_manager.track_invocation(
                agent_id, self.current_workflow_id, builder_result, success=True
            )
        else:
            # Fallback was used - track as pseudo-agent
            self.agent_manager.track_invocation(
                f"capability_{capability_used}", self.current_workflow_id, builder_result, success=True
            )
        
        self.tape.append("builder", "build_complete", builder_result)

        # Phase 3: Review
        self.logger.info("Phase 3: Review")

        # Extract code/content from builder result
        # DynamicBuilder returns artifacts as a list
        artifacts = builder_result.get("artifacts", [])
        if isinstance(artifacts, list) and artifacts:
            # Combine all artifact content for review
            code = "\n\n".join(artifact.get("content", "") for artifact in artifacts)
        elif isinstance(artifacts, dict):
            # Fallback for old dict format
            code = artifacts.get("primary_code", "")
        else:
            # Legacy Builder format with generated_code
            generated_code = builder_result.get("generated_code", [])
            if generated_code:
                code = "\n\n".join(item.get("code", "") for item in generated_code)
            else:
                code = ""

        critic_payload = {
            "mission": mission,
            "architecture": architect_output,
            "implementation": builder_result,
            "code": code,
        }
        critic_output = self._run_agent(critic, critic_payload)
        self.agent_manager.track_invocation(
            critic.id, self.current_workflow_id, critic_output, success=True
        )
        self.tape.append("critic", "review_complete", critic_output)

        # Optional governance post-review
        if governance:
            try:
                governance_post = self._run_agent(governance, {
                    "stage": "post_review",
                    "review": critic_output,
                    "implementation": builder_result
                })
                self.agent_manager.track_invocation(
                    governance.id, self.current_workflow_id, governance_post, success=True
                )
                self.tape.append("governance", "policy_check_post_review", governance_post)
            except Exception as e:
                self.agent_manager.track_invocation(
                    governance.id, self.current_workflow_id, None, success=False, error=str(e)
                )

        # Phase 4: Recording/Publishing
        self.logger.info("Phase 4: Recording/Publishing")
        workflow_dir = Path(self.output_dir) / self.current_workflow_id
        workflow_dir.mkdir(parents=True, exist_ok=True)

        published_artifacts = {}

        # Handle DynamicBuilder artifacts (list format)
        artifacts = builder_result.get("artifacts", [])
        if isinstance(artifacts, list) and artifacts:
            # Write out artifacts from DynamicBuilder's list
            for artifact in artifacts:
                filename = artifact.get("filename", artifact.get("name", "unknown") + ".txt")
                content = artifact.get("content", "")
                if content:
                    path = workflow_dir / filename
                    path.write_text(content)
                    published_artifacts[artifact.get("name", "unknown")] = str(path)

            # Use first artifact as primary
            if artifacts:
                published_artifacts["primary_artifact"] = published_artifacts.get(
                    artifacts[0].get("name", "unknown"), ""
                )
        # Handle legacy dict format
        elif isinstance(artifacts, dict):
            for name, content in artifacts.items():
                suffix = ".py" if not any(name.endswith(ext) for ext in (".md", ".txt", ".json")) else ""
                path = workflow_dir / f"{name}{suffix}"
                path.write_text(content)
                published_artifacts[name] = str(path)
        # Handle legacy Builder generated_code format
        else:
            generated_code = builder_result.get("generated_code", [])
            if generated_code:
                for item in generated_code:
                    component = item.get("component", "unknown")
                    code = item.get("code", "")
                    if code:
                        filename = f"{component}.py"
                        path = workflow_dir / filename
                        path.write_text(code)
                        published_artifacts[component] = str(path)

                if generated_code:
                    published_artifacts["primary_code"] = published_artifacts.get(
                        generated_code[0].get("component", "unknown"), ""
                    )

        recorder_payload = {
            "mission": mission,
            "architecture": architect_output,
            "implementation": builder_result,
            "review": critic_output,
            "artifacts": published_artifacts
        }
        recorder_output = self._run_agent(recorder, recorder_payload)
        self.agent_manager.track_invocation(
            recorder.id, self.current_workflow_id, recorder_output, success=True
        )
        self.tape.append("recorder", "published", recorder_output)

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