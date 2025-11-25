"""
Tests for DynamicBuilder.

These tests focus on behavior:
- Does capability selection work?
- Does the builder produce usable output?
- Does fallback work when no capability matches?
"""

import pytest

from swarms.team_agent.roles.dynamic_builder import DynamicBuilder
from swarms.team_agent.capabilities.document_generator import DocumentGenerator
from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability


class TestDynamicBuilder:
    """Test DynamicBuilder functionality."""
    
    def test_initialization_no_capabilities(self):
        """Test builder initializes with no capabilities."""
        builder = DynamicBuilder("test_workflow")
        
        assert builder.workflow_id == "test_workflow"
        assert builder.capabilities == []
    
    def test_initialization_with_capabilities(self):
        """Test builder initializes with capabilities."""
        caps = [DocumentGenerator(), HRTGuideCapability()]
        builder = DynamicBuilder("test_workflow", caps)
        
        assert len(builder.capabilities) == 2
    
    def test_select_capability_hrt(self):
        """Test selecting HRT capability for medical mission."""
        caps = [DocumentGenerator(), HRTGuideCapability()]
        builder = DynamicBuilder("test_workflow", caps)
        
        mission = "Generate hormone replacement therapy guide"
        architecture = {"mission": mission, "components": []}
        
        selected = builder._select_capability(mission, architecture)
        
        assert selected is not None
        assert isinstance(selected, HRTGuideCapability)
    
    def test_select_capability_general_doc(self):
        """Test selecting general doc capability."""
        caps = [DocumentGenerator()]
        builder = DynamicBuilder("test_workflow", caps)
        
        mission = "Generate a guide for Python"
        architecture = {"mission": mission, "components": []}
        
        selected = builder._select_capability(mission, architecture)
        
        assert selected is not None
        assert isinstance(selected, DocumentGenerator)
    
    def test_select_capability_no_match(self):
        """Test behavior when no capability matches."""
        builder = DynamicBuilder("test_workflow", [])
        
        mission = "Some mission"
        architecture = {"mission": mission, "components": []}
        
        selected = builder._select_capability(mission, architecture)
        
        assert selected is None
    
    def test_run_with_capability_produces_output(self):
        """Test running builder with matching capability produces usable output."""
        caps = [DocumentGenerator()]
        builder = DynamicBuilder("test_workflow", caps)
        
        context = {
            "input": {
                "mission": "Generate a guide",
                "components": []
            }
        }
        
        result = builder.run(context)
        
        # Behavioral: did we get a result with content?
        assert result is not None
        assert isinstance(result, dict)
        assert "capability_used" in result
        # Should have some form of output (code, content, or artifacts)
        has_output = any(key in result for key in ["code", "content", "artifacts", "output"])
        assert has_output, "Builder should produce some form of output"
    
    def test_run_fallback_produces_output(self):
        """Test fallback produces usable output when no capability matches."""
        builder = DynamicBuilder("test_workflow", [])
        
        context = {
            "input": {
                "mission": "Test mission",
                "components": []
            }
        }
        
        result = builder.run(context)
        
        # Behavioral: did fallback work?
        assert result is not None
        assert isinstance(result, dict)
        # Should indicate fallback was used
        assert result.get("capability_used") == "fallback_builder"
        # Should have some output
        has_output = any(key in result for key in ["code", "content", "artifacts", "output", "status"])
        assert has_output, "Fallback should produce some form of output"
    
    def test_fallback_implementation_produces_valid_result(self):
        """Test fallback implementation produces a valid result."""
        builder = DynamicBuilder("test_workflow", [])
        
        result = builder._fallback_implementation("Test", {})
        
        # Behavioral: is the result usable?
        assert result is not None
        assert isinstance(result, dict)
        # Should have some content we can work with
        assert len(result) > 0, "Fallback should return non-empty result"
