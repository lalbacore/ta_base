"""
Base tool interface and registry.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING_GOVERNANCE = "pending_governance"
    DENIED = "denied"


@dataclass
class ToolResult:
    """Result from tool execution."""
    status: ToolStatus
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        return self.status == ToolStatus.SUCCESS


@dataclass
class ToolMetadata:
    """Tool metadata for registry and MCP exposure."""
    name: str
    description: str
    version: str = "1.0.0"
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    requires_governance: bool = False
    trust_domain: str = "execution"
    tags: List[str] = field(default_factory=list)


class BaseTool(ABC):
    """
    Base class for all tools.
    
    Tools are standalone units of functionality that:
    - Can be invoked by any agent
    - Can be exposed via MCP
    - Can require governance approval
    - Are independently testable
    """
    
    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    def validate_input(self, **kwargs) -> Optional[str]:
        """
        Validate input parameters.
        Returns error message if invalid, None if valid.
        """
        return None
    
    def get_mcp_schema(self) -> Dict[str, Any]:
        """Return MCP-compatible tool definition."""
        meta = self.metadata
        return {
            "name": meta.name,
            "description": meta.description,
            "inputSchema": {
                "type": "object",
                "properties": meta.input_schema,
            }
        }
    
    def __call__(self, **kwargs) -> ToolResult:
        """Allow tool to be called directly."""
        error = self.validate_input(**kwargs)
        if error:
            return ToolResult(
                status=ToolStatus.FAILURE,
                error=f"Input validation failed: {error}"
            )
        
        try:
            return self.execute(**kwargs)
        except Exception as e:
            logger.exception(f"Tool {self.metadata.name} failed")
            return ToolResult(
                status=ToolStatus.FAILURE,
                error=str(e)
            )


class ToolRegistry:
    """
    Central registry for all tools.
    
    Provides:
    - Tool registration and lookup
    - MCP schema generation
    - Governance integration points
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._by_tag: Dict[str, List[str]] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        name = tool.metadata.name
        if name in self._tools:
            logger.warning(f"Overwriting existing tool: {name}")
        
        self._tools[name] = tool
        
        for tag in tool.metadata.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(name)
        
        logger.info(f"Registered tool: {name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_by_tag(self, tag: str) -> List[BaseTool]:
        """Get all tools with a given tag."""
        names = self._by_tag.get(tag, [])
        return [self._tools[n] for n in names if n in self._tools]
    
    def list_tools(self) -> List[ToolMetadata]:
        """List all registered tools."""
        return [t.metadata for t in self._tools.values()]
    
    def invoke(
        self, 
        name: str, 
        governance_callback: Optional[callable] = None,
        **kwargs
    ) -> ToolResult:
        """Invoke a tool by name with optional governance check."""
        tool = self.get(name)
        if not tool:
            return ToolResult(
                status=ToolStatus.FAILURE,
                error=f"Tool not found: {name}"
            )
        
        if tool.metadata.requires_governance and governance_callback:
            approved = governance_callback(
                tool_name=name,
                parameters=kwargs,
                metadata=tool.metadata
            )
            if not approved:
                return ToolResult(
                    status=ToolStatus.DENIED,
                    error="Governance approval denied"
                )
        
        return tool(**kwargs)
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in MCP format."""
        return [t.get_mcp_schema() for t in self._tools.values()]
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools
