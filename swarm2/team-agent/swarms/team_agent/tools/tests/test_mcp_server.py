"""Tests for MCP Server."""

import pytest
import json

from swarms.team_agent.tools import ToolRegistry, CodeGeneratorTool, CodeValidatorTool
from swarms.team_agent.tools.mcp_server import (
    MCPToolServer, MCPServerConfig, create_default_server
)


class TestMCPServerConfig:
    def test_default_config(self):
        config = MCPServerConfig()
        assert config.name == "team-agent-tools"
        assert config.version == "1.0.0"
        assert config.require_auth is False
    
    def test_custom_config(self):
        config = MCPServerConfig(name="custom", allowed_tools=["code_generator"])
        assert config.name == "custom"
        assert config.allowed_tools == ["code_generator"]


class TestMCPToolServer:
    def test_server_creation(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        
        server = MCPToolServer(registry)
        assert server.config.name == "team-agent-tools"
        assert len(server._get_exposed_tool_names()) == 1
    
    def test_tool_filtering(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        registry.register(CodeValidatorTool())
        
        config = MCPServerConfig(allowed_tools=["code_generator"])
        server = MCPToolServer(registry, config)
        
        names = server._get_exposed_tool_names()
        assert len(names) == 1
        assert names[0] == "code_generator"
    
    def test_metadata_to_mcp_schema(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        
        server = MCPToolServer(registry)
        tools_meta = server._get_exposed_tools_metadata()
        schema = server._metadata_to_mcp_schema(tools_meta[0])
        
        assert schema["name"] == "code_generator"
        assert "description" in schema
        assert "inputSchema" in schema
    
    @pytest.mark.asyncio
    async def test_handle_list_tools(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        registry.register(CodeValidatorTool())
        
        server = MCPToolServer(registry)
        tools = await server.handle_list_tools()
        
        assert len(tools) == 2
        names = [t["name"] for t in tools]
        assert "code_generator" in names
        assert "code_validator" in names
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_success(self):
        registry = ToolRegistry()
        registry.register(CodeValidatorTool())
        
        server = MCPToolServer(registry)
        result = await server.handle_call_tool(
            "code_validator",
            {"code": "print('hello')", "language": "python"}
        )
        
        assert result["isError"] is False
        content = json.loads(result["content"][0]["text"])
        assert content["valid"] is True
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_not_found(self):
        registry = ToolRegistry()
        config = MCPServerConfig(allowed_tools=["code_validator"])
        server = MCPToolServer(registry, config)
        
        result = await server.handle_call_tool("nonexistent", {})
        assert result["isError"] is True
    
    def test_get_stats(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        
        server = MCPToolServer(registry)
        stats = server.get_stats()
        
        assert stats["name"] == "team-agent-tools"
        assert stats["tools_exposed"] == 1
        assert stats["requests_handled"] == 0


class TestCreateDefaultServer:
    def test_creates_server_with_tools(self):
        server = create_default_server()
        
        tool_names = server._get_exposed_tool_names()
        
        assert "code_generator" in tool_names
        assert "code_validator" in tool_names
        assert "code_reviewer" in tool_names
        # FileWriterTool should be excluded for security
        assert "file_writer" not in tool_names
