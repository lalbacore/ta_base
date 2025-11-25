from typing import Any, Dict, Callable

def capability_to_tool(cap) -> Dict[str, Any]:
    """
    Convert a capability object into an MCP-like tool descriptor.
    """
    meta = getattr(cap, "metadata", {}) or {}
    name = meta.get("name") or cap.__class__.__name__.lower()
    description = meta.get("description") or f"Capability: {name}"
    # Simple schema; extend as needed
    input_schema = {"type": "object", "properties": {"mission": {"type": "string"}}, "required": ["mission"]}
    return {
        "name": name,
        "description": description,
        "input_schema": input_schema,
    }

def tool_invoker(registry, name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Return a callable that invokes the named capability via registry.
    """
    def _invoke(args: Dict[str, Any]) -> Dict[str, Any]:
        cap = None
        if hasattr(registry, "get"):
            cap = registry.get(name)
        if not cap:
            # fallback scan
            for c in getattr(registry, "capabilities", []) or []:
                meta = getattr(c, "metadata", {}) or {}
                n = meta.get("name") or c.__class__.__name__.lower()
                if n == name:
                    cap = c
                    break
        if not cap or not hasattr(cap, "execute"):
            return {"error": f"tool {name} not available"}
        return cap.execute(args)
    return _invoke