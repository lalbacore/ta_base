"""
MCP Server - Expose tools via Model Context Protocol.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None

from .base import ToolRegistry, ToolResult, ToolMetadata


@dataclass
class MCPServerConfig:
    """Configuration for MCP server."""
    name: str = "team-agent-tools"
    version: str = "1.0.0"
    description: str = "Team Agent Tools exposed via MCP"
    require_auth: bool = False
    allowed_tools: Optional[List[str]] = None
    rate_limit: int = 100


class MCPToolServer:
    """MCP Server that exposes ToolRegistry tools."""
    
    def __init__(self, registry: ToolRegistry, config: Optional[MCPServerConfig] = None):
        self.registry = registry
        self.config = config or MCPServerConfig()
        self._server: Optional[Server] = None
        self._request_count = 0
    
    @property
    def available(self) -> bool:
        return MCP_AVAILABLE
    
    def _get_exposed_tool_names(self) -> List[str]:
        """Get list of tool names to expose."""
        tools = self.registry.list_tools()  # Returns List[ToolMetadata]
        names = [t.name for t in tools]
        if self.config.allowed_tools:
            names = [n for n in names if n in self.config.allowed_tools]
        return names
    
    def _get_exposed_tools_metadata(self) -> List[ToolMetadata]:
        """Get metadata for exposed tools."""
        tools = self.registry.list_tools()  # Returns List[ToolMetadata]
        if self.config.allowed_tools:
            tools = [t for t in tools if t.name in self.config.allowed_tools]
        return tools
    
    def _metadata_to_mcp_schema(self, meta: ToolMetadata) -> Dict[str, Any]:
        """Convert ToolMetadata to MCP tool schema."""
        return {
            "name": meta.name,
            "description": meta.description,
            "inputSchema": {
                "type": "object",
                "properties": meta.input_schema,
                "required": [k for k, v in meta.input_schema.items() 
                           if isinstance(v, dict) and v.get("required", False)]
            }
        }
    
    async def handle_list_tools(self) -> List[Dict[str, Any]]:
        """Handle tools/list request."""
        tools = self._get_exposed_tools_metadata()
        return [self._metadata_to_mcp_schema(t) for t in tools]
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        self._request_count += 1
        
        if self.config.allowed_tools and name not in self.config.allowed_tools:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Tool '{name}' not available"}]
            }
        
        result = self.registry.invoke(name, **arguments)
        
        if result.success:
            return {
                "isError": False,
                "content": [{"type": "text", "text": json.dumps(result.output, indent=2)}]
            }
        else:
            return {
                "isError": True,
                "content": [{"type": "text", "text": result.error or "Tool execution failed"}]
            }
    
    def create_server(self) -> Optional[Server]:
        """Create and configure the MCP server."""
        if not MCP_AVAILABLE:
            logger.error("MCP package not installed. Run: pip install mcp")
            return None
        
        server = Server(self.config.name)
        
        @server.list_tools()
        async def list_tools():
            tools_meta = self._get_exposed_tools_metadata()
            return [
                Tool(
                    name=t.name,
                    description=t.description,
                    inputSchema={"type": "object", "properties": t.input_schema}
                )
                for t in tools_meta
            ]
        
        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            result = self.registry.invoke(name, **arguments)
            if result.success:
                return [TextContent(type="text", text=json.dumps(result.output, indent=2))]
            else:
                raise Exception(result.error or "Tool execution failed")
        
        self._server = server
        return server
    
    async def run_stdio(self):
        """Run the server using stdio transport."""
        server = self.create_server()
        if server is None:
            raise RuntimeError("Failed to create MCP server")
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "tools_exposed": len(self._get_exposed_tool_names()),
            "requests_handled": self._request_count,
            "mcp_available": MCP_AVAILABLE,
        }


def create_default_server(registry: Optional[ToolRegistry] = None) -> MCPToolServer:
    """Create a default MCP server with standard tools."""
    if registry is None:
        from .code_tools import CodeGeneratorTool, CodeValidatorTool, CodeFormatterTool
        from .file_tools import FileReaderTool
        from .analysis_tools import ReviewTool, ScoringTool
        
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        registry.register(CodeValidatorTool())
        registry.register(CodeFormatterTool())
        registry.register(FileReaderTool())
        registry.register(ReviewTool())
        registry.register(ScoringTool())
    
    return MCPToolServer(registry)


def main():
    """Run the MCP server from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Team Agent MCP Server")
    parser.add_argument("--name", default="team-agent-tools", help="Server name")
    parser.add_argument("--list", action="store_true", help="List available tools")
    args = parser.parse_args()
    
    server = create_default_server()
    
    if args.list:
        print(f"MCP Server: {server.config.name}")
        print(f"MCP Available: {server.available}")
        print(f"\nTools ({len(server._get_exposed_tool_names())}):")
        for meta in server._get_exposed_tools_metadata():
            print(f"  - {meta.name}: {meta.description}")
        return
    
    if not server.available:
        print("Error: MCP package not installed. Run: pip install mcp")
        return
    
    print(f"Starting MCP server: {server.config.name}")
    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()
