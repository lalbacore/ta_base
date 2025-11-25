"""
File I/O tools.
"""

import os
from pathlib import Path
from typing import Optional
from .base import BaseTool, ToolMetadata, ToolResult, ToolStatus


class FileWriterTool(BaseTool):
    """Write content to files."""
    
    def __init__(self, base_path: Optional[str] = None):
        self._base_path = Path(base_path) if base_path else Path.cwd()
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file_writer",
            description="Write content to a file",
            version="1.0.0",
            input_schema={
                "path": {"type": "string", "description": "File path (relative to base)"},
                "content": {"type": "string", "description": "Content to write"},
                "mode": {"type": "string", "default": "overwrite"},
                "create_dirs": {"type": "boolean", "default": True}
            },
            output_schema={
                "path": {"type": "string"},
                "bytes_written": {"type": "integer"}
            },
            requires_governance=True,
            trust_domain="execution",
            tags=["file", "io", "builder", "dangerous"]
        )
    
    def validate_input(self, **kwargs) -> Optional[str]:
        if "path" not in kwargs:
            return "path is required"
        if "content" not in kwargs:
            return "content is required"
        
        path = kwargs["path"]
        if ".." in path or path.startswith("/"):
            return "Invalid path: must be relative and cannot contain '..'"
        return None
    
    def execute(self, **kwargs) -> ToolResult:
        rel_path = kwargs["path"]
        content = kwargs["content"]
        mode = kwargs.get("mode", "overwrite")
        create_dirs = kwargs.get("create_dirs", True)
        
        full_path = self._base_path / rel_path
        
        if create_dirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        write_mode = "w" if mode == "overwrite" else "a"
        with open(full_path, write_mode) as f:
            bytes_written = f.write(content)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output={"path": str(full_path), "bytes_written": bytes_written},
            metadata={"mode": mode, "relative_path": rel_path}
        )


class FileReaderTool(BaseTool):
    """Read content from files."""
    
    def __init__(self, base_path: Optional[str] = None):
        self._base_path = Path(base_path) if base_path else Path.cwd()
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file_reader",
            description="Read content from a file",
            version="1.0.0",
            input_schema={
                "path": {"type": "string", "description": "File path"},
                "encoding": {"type": "string", "default": "utf-8"}
            },
            output_schema={
                "content": {"type": "string"},
                "size": {"type": "integer"}
            },
            requires_governance=False,
            trust_domain="execution",
            tags=["file", "io", "reader"]
        )
    
    def validate_input(self, **kwargs) -> Optional[str]:
        if "path" not in kwargs:
            return "path is required"
        if ".." in kwargs["path"]:
            return "Invalid path: cannot contain '..'"
        return None
    
    def execute(self, **kwargs) -> ToolResult:
        rel_path = kwargs["path"]
        encoding = kwargs.get("encoding", "utf-8")
        
        if os.path.isabs(rel_path):
            full_path = Path(rel_path)
        else:
            full_path = self._base_path / rel_path
        
        if not full_path.exists():
            return ToolResult(
                status=ToolStatus.FAILURE,
                error=f"File not found: {rel_path}"
            )
        
        with open(full_path, "r", encoding=encoding) as f:
            content = f.read()
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output={"content": content, "size": len(content)},
            metadata={"path": str(full_path), "encoding": encoding}
        )
