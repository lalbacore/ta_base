"""
Mission Router - Analyzes missions and determines execution strategy.
"""
from typing import Dict, Any, List, Set


class MissionRouter:
    """Routes missions to appropriate capabilities and execution strategies."""
    
    def __init__(self, registry):
        """
        Initialize router with capability registry.
        
        Args:
            registry: CapabilityRegistry instance
        """
        self.registry = registry
    
    def analyze_mission(self, mission: str) -> Dict[str, Any]:
        """
        Analyze mission and determine execution strategy.
        
        Args:
            mission: Mission description string
        
        Returns:
            Analysis dict with strategy, capabilities, workflow, etc.
        """
        ctx = {"mission": mission, "input": mission}
        matching_objects: List[Any] = []

        # Snapshot available names (for final fallback)
        all_names: List[str] = []
        try:
            if hasattr(self.registry, "list_capabilities"):
                names = self.registry.list_capabilities()
                all_names = list(names) if names else []
        except Exception:
            pass

        # 1) Try registry.find_all_matches with string and dict
        try:
            fam = getattr(self.registry, "find_all_matches", None)
            if callable(fam):
                matches = fam(mission)
                if matches:
                    matching_objects = list(matches)
                if not matching_objects:
                    matches = fam(ctx)
                    if matches:
                        matching_objects = list(matches)
        except Exception:
            pass

        # 2) Try registry.find (single best match)
        if not matching_objects:
            try:
                f = getattr(self.registry, "find", None)
                if callable(f):
                    found = f(mission)
                    if not found:
                        found = f(ctx)
                    if found:
                        matching_objects = [found]
            except Exception:
                pass

        # 3) Fallback: collect capability objects and evaluate matches
        if not matching_objects:
            candidates: List[Any] = []

            # Direct list attribute
            caps_list = getattr(self.registry, "capabilities", None)
            if isinstance(caps_list, list):
                candidates.extend(caps_list)

            # Common internal maps
            for attr in ("_capability_map", "_capabilities_by_name", "_capabilities_by_type", "_capabilities_by_domain"):
                mapping = getattr(self.registry, attr, None)
                if isinstance(mapping, dict):
                    for v in mapping.values():
                        if isinstance(v, list):
                            candidates.extend(v)
                        else:
                            candidates.append(v)

            # Any dict/list attributes holding capability-like objects
            try:
                for v in getattr(self.registry, "__dict__", {}).values():
                    if isinstance(v, dict):
                        candidates.extend([obj for obj in v.values() if hasattr(obj, "matches")])
                    elif isinstance(v, list):
                        candidates.extend([obj for obj in v if hasattr(obj, "matches")])
            except Exception:
                pass

            # Dedupe by id
            seen: Set[int] = set()
            deduped: List[Any] = []
            for c in candidates:
                oid = id(c)
                if oid not in seen:
                    seen.add(oid)
                    deduped.append(c)

            # Evaluate matches (prefer dict context)
            for cap_obj in deduped:
                try:
                    if cap_obj.matches(ctx) or cap_obj.matches(mission):
                        matching_objects.append(cap_obj)
                except Exception:
                    continue

        # Convert to names
        matching_capabilities = [
            (getattr(cap, "metadata", {}) or {}).get("name", cap.__class__.__name__.lower())
            for cap in matching_objects
        ]

        # Final fallback: if still empty, use available capability names
        if not matching_capabilities and all_names:
            matching_capabilities = all_names

        # Strategy and flags
        if len(matching_capabilities) == 1:
            strategy = "single_capability"
        elif len(matching_capabilities) > 1:
            strategy = "parallel_capabilities"
        else:
            strategy = "decompose_and_route"
        
        complexity = "simple" if len(mission.split()) < 10 else "complex"
        requires_decomposition = len(matching_capabilities) == 0
        can_parallelize = len(matching_capabilities) > 1
        
        return {
            "strategy": strategy,
            "capabilities": matching_capabilities,
            "workflow": {
                "phases": ["architecture", "implementation", "review", "recording"],
                "parallelizable": can_parallelize
            },
            "complexity": complexity,
            "requires_decomposition": requires_decomposition,
            "can_parallelize": can_parallelize
        }