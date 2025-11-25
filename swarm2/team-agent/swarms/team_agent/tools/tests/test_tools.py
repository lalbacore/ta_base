"""Tests for the tool registry and tools."""

import pytest
import tempfile
from pathlib import Path

from swarms.team_agent.tools import (
    BaseTool,
    ToolResult,
    ToolRegistry,
    ToolStatus,
    CodeGeneratorTool,
    CodeValidatorTool,
    FileWriterTool,
    FileReaderTool,
    ReviewTool,
    ScoringTool,
)


class TestToolRegistry:
    """Test the tool registry."""
    
    def test_register_and_get(self):
        registry = ToolRegistry()
        tool = CodeGeneratorTool()
        registry.register(tool)
        
        assert "code_generator" in registry
        assert registry.get("code_generator") is tool
        assert len(registry) == 1
    
    def test_get_nonexistent(self):
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None
    
    def test_list_tools(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        registry.register(CodeValidatorTool())
        
        tools = registry.list_tools()
        names = [t.name for t in tools]
        
        assert "code_generator" in names
        assert "code_validator" in names
    
    def test_get_by_tag(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        registry.register(CodeValidatorTool())
        registry.register(ReviewTool())
        
        code_tools = registry.get_by_tag("code")
        assert len(code_tools) == 2
    
    def test_invoke_tool(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        
        result = registry.invoke("code_generator", specification="A hello world function")
        
        assert result.success
        assert "code" in result.output
    
    def test_invoke_nonexistent(self):
        registry = ToolRegistry()
        result = registry.invoke("nonexistent")
        
        assert not result.success
        assert "not found" in result.error
    
    def test_invoke_with_governance(self):
        registry = ToolRegistry()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileWriterTool(base_path=tmpdir)
            registry.register(tool)
            
            def deny_all(**kwargs):
                return False
            
            result = registry.invoke(
                "file_writer",
                governance_callback=deny_all,
                path="test.txt",
                content="hello"
            )
            assert result.status == ToolStatus.DENIED
            
            def approve_all(**kwargs):
                return True
            
            result = registry.invoke(
                "file_writer",
                governance_callback=approve_all,
                path="test.txt",
                content="hello"
            )
            assert result.success
    
    def test_mcp_schema_generation(self):
        registry = ToolRegistry()
        registry.register(CodeGeneratorTool())
        
        schemas = registry.get_mcp_tools()
        
        assert len(schemas) == 1
        assert schemas[0]["name"] == "code_generator"
        assert "inputSchema" in schemas[0]


class TestCodeTools:
    """Test code generation and validation tools."""
    
    def test_code_generator(self):
        tool = CodeGeneratorTool()
        result = tool(specification="A function to add two numbers")
        
        assert result.success
        assert "code" in result.output
        assert result.output["language"] == "python"
    
    def test_code_generator_validation(self):
        tool = CodeGeneratorTool()
        
        result = tool()
        assert not result.success
        assert "specification is required" in result.error
        
        result = tool(specification="   ")
        assert not result.success
    
    def test_code_validator_valid(self):
        tool = CodeValidatorTool()
        result = tool(code="def hello():\n    print('hello')\n")
        
        assert result.success
        assert result.output["valid"] is True
        assert len(result.output["errors"]) == 0
    
    def test_code_validator_invalid(self):
        tool = CodeValidatorTool()
        result = tool(code="def hello(\n    print('hello')")
        
        assert result.success
        assert result.output["valid"] is False
        assert len(result.output["errors"]) > 0
    
    def test_code_validator_strict(self):
        tool = CodeValidatorTool()
        result = tool(code="from os import *\neval('1+1')", strict=True)
        
        assert len(result.output["warnings"]) >= 2


class TestFileTools:
    """Test file I/O tools."""
    
    def test_file_writer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileWriterTool(base_path=tmpdir)
            result = tool(path="test.txt", content="hello world")
            
            assert result.success
            assert Path(tmpdir, "test.txt").exists()
            assert Path(tmpdir, "test.txt").read_text() == "hello world"
    
    def test_file_writer_creates_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileWriterTool(base_path=tmpdir)
            result = tool(path="subdir/nested/test.txt", content="nested")
            
            assert result.success
            assert Path(tmpdir, "subdir/nested/test.txt").exists()
    
    def test_file_writer_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileWriterTool(base_path=tmpdir)
            result = tool(path="../escape.txt", content="bad")
            
            assert not result.success
            assert "Invalid path" in result.error
    
    def test_file_reader(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("hello world")
            
            tool = FileReaderTool(base_path=tmpdir)
            result = tool(path="test.txt")
            
            assert result.success
            assert result.output["content"] == "hello world"
    
    def test_file_reader_not_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileReaderTool(base_path=tmpdir)
            result = tool(path="nonexistent.txt")
            
            assert not result.success
            assert "not found" in result.error.lower()


class TestAnalysisTools:
    """Test review and analysis tools."""
    
    def test_review_tool(self):
        tool = ReviewTool()
        code = 'def process_data(data):\n    # TODO: add error handling\n    password = "secret123"\n    return data\n'
        result = tool(content=code, criteria=["security", "quality"])
        
        assert result.success
        assert len(result.output["issues"]) > 0
        assert len(result.output["suggestions"]) > 0
    
    def test_scoring_tool(self):
        tool = ScoringTool()
        result = tool(content="This is a test document with some content.")
        
        assert result.success
        assert "overall_score" in result.output
        assert 0 <= result.output["overall_score"] <= 10
    
    def test_scoring_with_custom_rubric(self):
        tool = ScoringTool()
        rubric = {"accuracy": {"weight": 0.5}, "style": {"weight": 0.5}}
        result = tool(content="test", rubric=rubric)
        
        assert result.success
        assert "accuracy" in result.output["dimension_scores"]
        assert "style" in result.output["dimension_scores"]
