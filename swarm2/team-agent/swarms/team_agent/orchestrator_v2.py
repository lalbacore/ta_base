"""
Enhanced Orchestrator - Dynamic capability composition.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

from .roles import Architect, Critic, Governance, Recorder
from .capabilities import CapabilityRegistry
from .marketplace import MarketplaceRegistry
from .factory import FactoryAgent


class DynamicOrchestrator:
    """Orchestrator that assembles workflows based on mission requirements."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        
        # Core agents
        self.architect = None  # Created per workflow
        self.critic = None
        self.governance = None
        self.recorder = None
        
        # Capability management
        self.capability_registry = CapabilityRegistry()
        self.marketplace = MarketplaceRegistry()
        self.factory = FactoryAgent()
        
        # Load available capabilities
        self._load_local_capabilities()
    
    def _load_local_capabilities(self):
        """Load locally available capabilities."""
        # Scan swarms/team_agent/capabilities/ for plugins
        capabilities_dir = Path(__file__).parent / "capabilities"
        for cap_file in capabilities_dir.glob("**/*.py"):
            if cap_file.stem != "__init__":
                self.capability_registry.register_from_file(cap_file)
    
    def execute_mission(self, mission_file: Path) -> Dict[str, Any]:
        """Execute a mission from YAML file."""
        # 1. Parse mission
        with open(mission_file) as f:
            mission = yaml.safe_load(f)
        
        # 2. Analyze requirements
        requirements = self._analyze_requirements(mission)
        
        # 3. Check capabilities
        workflow_plan = self._plan_workflow(requirements)
        
        # 4. Get governance approval
        if not self._get_approval(workflow_plan):
            return {"status": "rejected", "reason": "governance_denied"}
        
        # 5. Assemble agents
        agents = self._assemble_agents(workflow_plan)
        
        # 6. Execute workflow
        return self._execute_workflow(agents, mission)
    
    def _analyze_requirements(self, mission: Dict) -> Dict[str, Any]:
        """Analyze what capabilities are needed."""
        required = mission.get("required_capabilities", [])
        
        return {
            "capabilities": required,
            "knowledge_sources": mission.get("knowledge_sources", []),
            "governance": mission.get("governance", {}),
            "marketplace_prefs": mission.get("marketplace", {}),
        }
    
    def _plan_workflow(self, requirements: Dict) -> Dict[str, Any]:
        """Create workflow plan by matching capabilities."""
        plan = {
            "local_agents": [],
            "external_agents": [],
            "new_capabilities_needed": [],
            "estimated_cost": 0.0,
        }
        
        for cap in requirements["capabilities"]:
            # Check local registry
            local_match = self.capability_registry.find(cap)
            
            if local_match:
                plan["local_agents"].append(local_match)
            else:
                # Check marketplace
                if requirements["marketplace_prefs"].get("allow_external_agents"):
                    external_match = self.marketplace.find(cap)
                    
                    if external_match:
                        plan["external_agents"].append(external_match)
                        plan["estimated_cost"] += external_match.get("cost", 0)
                    else:
                        # Need to create new capability
                        plan["new_capabilities_needed"].append(cap)
        
        return plan
    
    def _get_approval(self, plan: Dict) -> bool:
        """Get governance/human approval for workflow plan."""
        # If using external agents or creating new ones, require approval
        needs_approval = (
            len(plan["external_agents"]) > 0 or
            len(plan["new_capabilities_needed"]) > 0
        )
        
        if needs_approval:
            print("\n" + "="*60)
            print("  WORKFLOW PLAN REQUIRES APPROVAL")
            print("="*60)
            print(f"\nLocal agents: {len(plan['local_agents'])}")
            print(f"External agents: {len(plan['external_agents'])}")
            print(f"New capabilities needed: {len(plan['new_capabilities_needed'])}")
            print(f"Estimated cost: ${plan['estimated_cost']:.2f}")
            print()
            
            response = input("Approve this workflow plan? (yes/no): ").strip().lower()
            return response in ["yes", "y"]
        
        return True  # Auto-approve if using only local capabilities
    
    def _assemble_agents(self, plan: Dict) -> List[Any]:
        """Assemble the agent team for execution."""
        agents = []
        
        # Add local agents
        for local_cap in plan["local_agents"]:
            agent = local_cap.create_agent()
            agents.append(agent)
        
        # Connect to external agents
        for external_cap in plan["external_agents"]:
            agent = self.marketplace.connect(external_cap)
            agents.append(agent)
        
        # Create new capabilities if approved
        for new_cap in plan["new_capabilities_needed"]:
            print(f"\n🏭 Factory creating new capability: {new_cap['type']}")
            agent = self.factory.create_capability(new_cap)
            agents.append(agent)
            
            # Register for future use
            self.capability_registry.register(new_cap, agent)
        
        return agents
    
    def _execute_workflow(self, agents: List, mission: Dict) -> Dict[str, Any]:
        """Execute the assembled workflow."""
        # Standard workflow: Architect → Builder → Critic → Governance → Recorder
        # But builder now uses dynamic capabilities from assembled agents
        
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize core agents with workflow ID
        self.architect = Architect(workflow_id)
        self.critic = Critic(workflow_id)
        self.governance = Governance(workflow_id)
        self.recorder = Recorder(workflow_id, str(self.output_dir))
        
        # Run workflow with dynamic builder
        context = {"input": mission.get("description", "")}
        
        architecture = self.architect.run(context)
        
        # Builder uses assembled capabilities
        builder = self._create_dynamic_builder(agents, workflow_id)
        implementation = builder.run({"input": architecture})
        
        review = self.critic.run({"input": implementation})
        decision = self.governance.run({"input": review})
        
        record = self.recorder.run({
            "input": {
                "architecture": architecture,
                "implementation": implementation,
                "review": review,
                "decision": decision,
            }
        })
        
        return record
    
    def _create_dynamic_builder(self, capabilities: List, workflow_id: str):
        """Create a builder that uses assembled capabilities."""
        from .roles.dynamic_builder import DynamicBuilder
        return DynamicBuilder(workflow_id, capabilities)