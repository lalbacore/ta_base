"""
Enhanced Orchestrator with A2A Integration

This orchestrator extends the base orchestrator with:
- A2A capability discovery and matching
- Dynamic agent augmentation from registry
- Trust-based capability selection
- Human-in-the-loop breakpoints
"""

import json
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from swarms.team_agent.roles import (
    Architect,
    Builder,
    Critic,
    Recorder,
)

# A2A imports
from swarms.team_agent.a2a import (
    CapabilityRegistry,
    CapabilityType,
    CapabilityRequirement,
    CapabilityMatch,
    A2AClient,
    A2AServer,
)

# Crypto imports
from swarms.team_agent.crypto import (
    PKIManager,
    TrustDomain,
    AgentReputationTracker,
    Signer,
    Verifier,
)

from utils.logging import get_logger


class BreakpointType(Enum):
    """Types of human-in-the-loop breakpoints."""
    MISSION_START = "mission_start"
    CAPABILITY_SELECTION = "capability_selection"
    AGENT_SELECTION = "agent_selection"
    PHASE_COMPLETION = "phase_completion"
    ERROR_RECOVERY = "error_recovery"
    MISSION_COMPLETE = "mission_complete"


class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"


@dataclass
class Breakpoint:
    """A human-in-the-loop breakpoint."""
    breakpoint_id: str
    breakpoint_type: BreakpointType
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Context
    mission_id: Optional[str] = None
    phase: Optional[str] = None

    # Options presented to user
    options: List[Dict[str, Any]] = field(default_factory=list)
    recommendation: Optional[int] = None  # Index of recommended option

    # User decision
    status: ApprovalStatus = ApprovalStatus.PENDING
    selected_option: Optional[int] = None
    user_feedback: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MissionSpec:
    """Mission specification with capability requirements."""
    mission_id: str
    description: str

    # Capability requirements
    required_capabilities: List[CapabilityRequirement] = field(default_factory=list)
    preferred_capabilities: List[CapabilityRequirement] = field(default_factory=list)

    # Constraints
    max_cost: Optional[float] = None
    max_duration: Optional[float] = None
    min_trust_score: float = 75.0

    # Human-in-the-loop configuration
    breakpoints: List[BreakpointType] = field(default_factory=list)
    auto_approve_trusted: bool = True  # Auto-approve for high-trust agents
    auto_approve_threshold: float = 90.0

    metadata: Dict[str, Any] = field(default_factory=dict)


class OrchestratorA2A:
    """
    Enhanced orchestrator with A2A capability integration.

    Features:
    - Dynamic capability discovery from A2A registry
    - Trust-based agent selection
    - Automatic agent augmentation
    - Human-in-the-loop breakpoints
    - Mission specification with requirements
    """

    def __init__(
        self,
        output_dir: str = "./team_output",
        max_iterations: int = 3,
        enable_a2a: bool = True,
        enable_breakpoints: bool = False,
    ):
        """
        Initialize the enhanced orchestrator.

        Args:
            output_dir: Directory for workflow outputs
            max_iterations: Maximum workflow iterations
            enable_a2a: Enable A2A capability discovery
            enable_breakpoints: Enable human-in-the-loop breakpoints
        """
        self.output_dir = Path(output_dir)
        self.max_iterations = max_iterations
        self.enable_a2a = enable_a2a
        self.enable_breakpoints = enable_breakpoints

        self.current_workflow_id = None
        self.logger = get_logger("orchestrator_a2a")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize PKI infrastructure
        self.pki_manager = PKIManager()
        self.logger.info("PKI infrastructure initialized")

        # Initialize trust tracker
        self.trust_tracker = AgentReputationTracker()
        self.logger.info("Trust tracker initialized")

        # Initialize A2A capability registry
        if self.enable_a2a:
            self.capability_registry = CapabilityRegistry(
                trust_tracker=self.trust_tracker,
                pki_manager=self.pki_manager
            )
            self.logger.info("A2A capability registry initialized")
        else:
            self.capability_registry = None

        # Load certificate chains
        self.cert_chains = {
            TrustDomain.GOVERNMENT: self.pki_manager.get_certificate_chain(TrustDomain.GOVERNMENT),
            TrustDomain.EXECUTION: self.pki_manager.get_certificate_chain(TrustDomain.EXECUTION),
            TrustDomain.LOGGING: self.pki_manager.get_certificate_chain(TrustDomain.LOGGING),
        }

        # A2A clients and servers (for inter-agent communication)
        self.a2a_clients: Dict[str, A2AClient] = {}
        self.a2a_servers: Dict[str, A2AServer] = {}

        # Breakpoints
        self.breakpoints: List[Breakpoint] = []

        self.logger.info("Orchestrator initialized")

    def load_mission(self, mission_file: Path) -> MissionSpec:
        """
        Load a mission specification from file.

        Args:
            mission_file: Path to mission YAML/JSON file

        Returns:
            MissionSpec object
        """
        with open(mission_file, 'r') as f:
            if mission_file.suffix == '.json':
                data = json.load(f)
            else:
                import yaml
                data = yaml.safe_load(f)

        mission_id = data.get('id', f"mission-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        description = data.get('description', '')

        # Parse capability requirements
        required_capabilities = []
        for req_data in data.get('requirements', {}).get('capabilities', []):
            requirement = CapabilityRequirement(
                capability_type=CapabilityType(req_data['type']),
                required_version=req_data.get('version'),
                min_reputation=req_data.get('min_reputation', 75.0),
                max_price=req_data.get('max_price'),
                max_duration=req_data.get('max_duration'),
                required_tags=req_data.get('tags', []),
                required_features=req_data.get('features', {}),
                min_trust_score=req_data.get('min_trust_score', 75.0),
            )
            required_capabilities.append(requirement)

        # Parse breakpoints
        breakpoints = []
        for bp_str in data.get('breakpoints', []):
            if isinstance(bp_str, dict):
                bp_type = BreakpointType(bp_str['type'])
            else:
                bp_type = BreakpointType(bp_str)
            breakpoints.append(bp_type)

        return MissionSpec(
            mission_id=mission_id,
            description=description,
            required_capabilities=required_capabilities,
            max_cost=data.get('constraints', {}).get('max_cost'),
            max_duration=data.get('constraints', {}).get('max_duration'),
            min_trust_score=data.get('constraints', {}).get('min_trust_score', 75.0),
            breakpoints=breakpoints,
            auto_approve_trusted=data.get('auto_approve_trusted', True),
            auto_approve_threshold=data.get('auto_approve_threshold', 90.0),
            metadata=data.get('metadata', {}),
        )

    async def discover_capabilities(
        self,
        mission: MissionSpec
    ) -> Dict[str, List[CapabilityMatch]]:
        """
        Discover capabilities for mission requirements.

        Args:
            mission: Mission specification

        Returns:
            Dictionary mapping requirement -> list of matches
        """
        if not self.capability_registry:
            self.logger.warning("A2A capability registry not enabled")
            return {}

        results = {}

        for req_idx, requirement in enumerate(mission.required_capabilities):
            matches = self.capability_registry.match_capabilities(
                requirement=requirement,
                limit=10
            )

            results[f"requirement_{req_idx}"] = matches

            self.logger.info(
                f"Found {len(matches)} matches for {requirement.capability_type.value}"
            )

        return results

    async def select_best_capability(
        self,
        mission: MissionSpec,
        requirement: CapabilityRequirement,
        matches: List[CapabilityMatch],
    ) -> Optional[CapabilityMatch]:
        """
        Select the best capability match, possibly with human approval.

        Args:
            mission: Mission specification
            requirement: Capability requirement
            matches: List of capability matches

        Returns:
            Selected capability match, or None if rejected
        """
        if not matches:
            return None

        # Auto-select if only one match
        if len(matches) == 1:
            return matches[0]

        # Auto-approve if top match has very high trust and auto-approve enabled
        top_match = matches[0]
        if (
            mission.auto_approve_trusted
            and top_match.trust_score >= mission.auto_approve_threshold
            and top_match.overall_score >= 90.0
        ):
            self.logger.info(
                f"Auto-approved capability: {top_match.capability.name} "
                f"(trust={top_match.trust_score:.1f}, score={top_match.overall_score:.1f})"
            )
            return top_match

        # Check if we need human approval
        if (
            self.enable_breakpoints
            and BreakpointType.CAPABILITY_SELECTION in mission.breakpoints
        ):
            # Create breakpoint
            breakpoint = await self._create_capability_selection_breakpoint(
                mission=mission,
                requirement=requirement,
                matches=matches[:5],  # Top 5 options
            )

            # Wait for approval (in real implementation, this would be async)
            # For now, we'll auto-approve the top match
            breakpoint.status = ApprovalStatus.APPROVED
            breakpoint.selected_option = 0

            self.breakpoints.append(breakpoint)

            if breakpoint.status == ApprovalStatus.APPROVED:
                return matches[breakpoint.selected_option]
            else:
                return None

        # Default: select top match
        return top_match

    async def _create_capability_selection_breakpoint(
        self,
        mission: MissionSpec,
        requirement: CapabilityRequirement,
        matches: List[CapabilityMatch],
    ) -> Breakpoint:
        """Create a capability selection breakpoint."""
        options = []

        for match in matches:
            option = {
                "capability_id": match.capability.capability_id,
                "name": match.capability.name,
                "provider": match.provider.provider_id,
                "trust_score": match.trust_score,
                "reputation": match.reputation_score,
                "price": match.capability.price,
                "overall_score": match.overall_score,
                "reasons": match.match_reasons,
                "warnings": match.warnings,
            }
            options.append(option)

        breakpoint = Breakpoint(
            breakpoint_id=f"bp-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            breakpoint_type=BreakpointType.CAPABILITY_SELECTION,
            mission_id=mission.mission_id,
            options=options,
            recommendation=0,  # Recommend top match
            metadata={
                "requirement_type": requirement.capability_type.value,
            }
        )

        return breakpoint

    async def execute_mission(
        self,
        mission: MissionSpec,
        local_agents: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a mission with A2A capability augmentation.

        Args:
            mission: Mission specification
            local_agents: List of local agents available

        Returns:
            Execution results
        """
        self.current_workflow_id = mission.mission_id
        self.logger.info(f"Executing mission: {mission.mission_id}")

        results = {
            "mission_id": mission.mission_id,
            "status": "in_progress",
            "start_time": datetime.utcnow().isoformat(),
            "capabilities_used": [],
            "breakpoints": [],
        }

        # Discover capabilities
        if self.capability_registry:
            capability_matches = await self.discover_capabilities(mission)

            # Select best capabilities for each requirement
            selected_capabilities = []

            for req_idx, requirement in enumerate(mission.required_capabilities):
                matches = capability_matches.get(f"requirement_{req_idx}", [])

                selected = await self.select_best_capability(
                    mission=mission,
                    requirement=requirement,
                    matches=matches,
                )

                if selected:
                    selected_capabilities.append(selected)
                    results["capabilities_used"].append({
                        "requirement": requirement.capability_type.value,
                        "selected": selected.capability.name,
                        "provider": selected.provider.provider_id,
                        "score": selected.overall_score,
                    })

                    self.logger.info(
                        f"Selected capability: {selected.capability.name} "
                        f"from {selected.provider.provider_id}"
                    )

        # Execute with selected capabilities
        # (In full implementation, this would coordinate with A2AClient)

        results["status"] = "completed"
        results["end_time"] = datetime.utcnow().isoformat()
        results["breakpoints"] = [
            {
                "id": bp.breakpoint_id,
                "type": bp.breakpoint_type.value,
                "status": bp.status.value,
            }
            for bp in self.breakpoints
        ]

        return results

    async def execute_simple(self, mission_text: str) -> Dict[str, Any]:
        """
        Execute a simple mission without capability requirements.

        Args:
            mission_text: Mission description

        Returns:
            Execution results
        """
        # Create simple mission spec
        mission = MissionSpec(
            mission_id=f"mission-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            description=mission_text,
        )

        # Execute with local agents only
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_workflow_id = f"wf_{timestamp}"

        # Create agents with certificates
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

        # Execute workflow (simplified)
        architect_result = architect.run(mission_text)
        builder_result = builder.run(architect_result)
        critic_result = critic.run(builder_result)
        recorder.run(critic_result)

        return {
            "mission_id": mission.mission_id,
            "workflow_id": self.current_workflow_id,
            "status": "completed",
            "result": critic_result,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        stats = {
            "workflow_id": self.current_workflow_id,
            "a2a_enabled": self.enable_a2a,
            "breakpoints_enabled": self.enable_breakpoints,
            "total_breakpoints": len(self.breakpoints),
        }

        if self.capability_registry:
            registry_stats = self.capability_registry.get_statistics()
            stats["registry"] = registry_stats

        if self.trust_tracker:
            trust_stats = self.trust_tracker.get_statistics()
            stats["trust"] = trust_stats

        return stats
