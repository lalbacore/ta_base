from typing import Any, Dict, List
from .tooling import capability_to_tool, tool_invoker

class MCPClient:
    """
    Minimal MCP-like facade that lists tools from the capability registry
    and invokes them.
    """
    def __init__(self, registry):
        self.registry = registry

    def list_tools(self) -> List[Dict[str, Any]]:
        tools: List[Dict[str, Any]] = []
        caps = getattr(self.registry, "capabilities", None) or []
        for cap in caps:
            try:
                tools.append(capability_to_tool(cap))
            except Exception:
                continue
        return tools

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        inv = tool_invoker(self.registry, name)
        return inv(args)