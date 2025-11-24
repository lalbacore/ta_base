"""
DynamicBuilder: selects and runs an appropriate capability or falls back.
Handles capability entries that may be objects or plain dict metadata.
"""
from typing import Optional, Dict, Any
from . import CapabilityRegistry, HRTGuideCapability, BaseCapability


def _get_capability_name(cap) -> Optional[str]:
    if hasattr(cap, "name"):
        return cap.name
    if isinstance(cap, dict):
        return cap.get("name")
    return None


class DynamicBuilder:
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or CapabilityRegistry()
        # Only auto-register HRT if not already present
        if HRTGuideCapability:
            existing_names = {
                _get_capability_name(c) for c in self.registry.list_capabilities()
            }
            if "hrt_guide_generator" not in existing_names:
                try:
                    self.registry.register(HRTGuideCapability())
                except Exception:
                    pass

    def select_capability(self, mission: str):
        mission_lower = mission.lower()
        # Explicit HRT keyword detection
        if HRTGuideCapability and "hormone" in mission_lower and "therapy" in mission_lower:
            return HRTGuideCapability()
        
        # Try registry find but handle string query safely
        try:
            cap = self.registry.find(mission_lower)
            if cap and hasattr(cap, "execute"):
                return cap
        except Exception:
            pass
        
        return None  # fallback

    def run(self, mission: str, architecture: str) -> Dict[str, Any]:
        capability = self.select_capability(mission)
        if capability:
            try:
                result = capability.execute(
                    {"mission": mission, "architecture": architecture}
                )
                artifacts = result.get("artifacts", {})
                return {
                    "capability_used": _get_capability_name(capability) or "unknown_capability",
                    "artifacts": artifacts,
                    "metadata": getattr(capability, "metadata", {}),
                }
            except Exception:
                pass  # fallback on execution error

        # Fallback path
        fallback_code = (
            f"# Fallback implementation for mission:\n"
            f"# {mission}\n\n"
            f"def main():\n"
            f"    print('Mission: {mission}')\n\n"
            f"if __name__ == '__main__':\n"
            f"    main()\n"
        )
        return {
            "capability_used": "fallback",
            "artifacts": {
                "primary_code": fallback_code
            },
            "metadata": {
                "type": "fallback",
                "domains": [],
            },
        }