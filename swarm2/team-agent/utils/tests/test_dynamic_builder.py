"""
Tests for DynamicBuilder.
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
    
    def test_run_with_capability(self):
        """Test running builder with matching capability."""
        caps = [DocumentGenerator()]
        builder = DynamicBuilder("test_workflow", caps)
        
        context = {
            "input": {
                "mission": "Generate a guide",
                "components": []
            }
        }
        
        result = builder.run(context)
        
        assert "code" in result
        assert "filename" in result
        assert "artifacts" in result
        assert "capability_used" in result
    
    def test_run_fallback_no_capability(self):
        """Test fallback implementation when no capability."""
        builder = DynamicBuilder("test_workflow", [])
        
        context = {
            "input": {
                "mission": "Test mission",
                "components": []
            }
        }
        
        result = builder.run(context)
        
        assert "code" in result
        assert "filename" in result
        assert result["filename"] == "main.py"
        assert "Test mission" in result["code"]
    
    def test_fallback_implementation_structure(self):
        """Test fallback implementation has correct structure."""
        builder = DynamicBuilder("test_workflow", [])
        
        result = builder._fallback_implementation("Test", {})
        
        assert "code" in result
        assert "filename" in result
        assert "tests" in result
        assert "documentation" in result
        assert "#!/usr/bin/env python3" in result["code"]
