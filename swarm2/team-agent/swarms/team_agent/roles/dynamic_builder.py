"""
Dynamic Builder - Capability-aware builder agent.
"""
from typing import Dict, Any, Optional, List
from swarms.team_agent.roles.base_role import BaseRole
from swarms.team_agent.capabilities.registry import CapabilityRegistry
from swarms.team_agent.roles.builder import Builder


class DynamicBuilder(BaseRole):
    """Builder that dynamically selects capabilities."""
    
    def __init__(
        self,
        workflow_id: str = "unknown",
        capability_registry = None,  # Can be CapabilityRegistry or List
        capabilities: Optional[List] = None
    ):
        """
        Initialize dynamic builder.
        
        Args:
            workflow_id: Current workflow ID
            capability_registry: Registry OR list of capabilities
            capabilities: Alternative way to pass list of capabilities
        """
        super().__init__(workflow_id)
        
        # Handle capability_registry being a list (for tests)
        if isinstance(capability_registry, list):
            self.capabilities = capability_registry
            self.capability_registry = CapabilityRegistry()
            for cap in capability_registry:
                self.capability_registry.register(cap)
        elif capability_registry is not None:
            self.capability_registry = capability_registry
            self.capabilities = []
        else:
            self.capability_registry = CapabilityRegistry()
            self.capabilities = []
        
        # Support direct capabilities list parameter
        if capabilities:
            self.capabilities = capabilities
            for cap in capabilities:
                self.capability_registry.register(cap)
        
        self.fallback_builder = Builder(workflow_id)
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build implementation using capabilities or fallback.
        
        Args:
            context: Dict with 'mission' and optionally 'architecture'
        
        Returns:
            Implementation dict with artifacts
        """
        import time
        start_time = time.time()
        
        # Extract mission - handle both string and dict inputs
        if isinstance(context, str):
            mission = context
            architecture = {}
        else:
            mission = context.get("mission", "") or context.get("input", "")
            architecture = context.get("architecture", {})
        
        self._log_stage_start("dynamic_builder", mission)
        
        # Try to find matching capability
        capability = self._select_capability(mission, architecture)
        
        if capability:
            self.logger.info(f"Using capability: {capability.metadata.get('name')}")
            
            # Prepare context for capability
            cap_context = {
                "mission": mission,
                "architecture": architecture,
                "input": mission
            }
            
            # Execute capability
            result = capability.execute(cap_context)
            result["capability_used"] = capability.metadata.get("name")
            
            self._log_stage_complete("dynamic_builder", result, start_time)
            return result
        
        else:
            self.logger.info("No matching capability, using fallback")
            
            # Use fallback implementation
            result = self._fallback_implementation(mission, architecture)
            
            self._log_stage_complete("dynamic_builder", result, start_time)
            return result
    
    def _select_capability(self, mission: str, architecture: Dict[str, Any] = None) -> Optional[Any]:
        """
        Select best capability for mission.
        
        Args:
            mission: The mission string
            architecture: Optional architecture dict
        
        Returns:
            Capability instance or None
        """
        if not mission:
            return None
        
        # Ensure mission is a string
        if isinstance(mission, dict):
            mission = mission.get("input", mission.get("mission", ""))
        
        mission_lower = mission.lower()
        
        # Check for HRT/hormone therapy
        if any(keyword in mission_lower for keyword in ["hormone", "hrt", "replacement therapy"]):
            cap = self.capability_registry.find("hrt")
            if cap:
                return cap
        
        # Check for general document generation
        if any(keyword in mission_lower for keyword in ["document", "guide", "documentation"]):
            cap = self.capability_registry.find("document")
            if cap:
                return cap
        
        # Try general registry search
        return self.capability_registry.find(mission)
    
    def _fallback_implementation(self, mission: str, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback implementation when no capability matches.
        
        Args:
            mission: The mission string
            architecture: Architecture dict
        
        Returns:
            Implementation dict with basic code
        """
        # Ensure architecture is a dict
        if isinstance(architecture, str):
            architecture = {}
        
        # Use the fallback builder
        context = {
            "mission": mission,
            "architecture": architecture,
            "input": mission
        }
        
        result = self.fallback_builder.run(context)
        result["capability_used"] = "fallback_builder"
        
        return result