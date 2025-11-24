"""
Tests for capability system components.
"""

import pytest
from datetime import datetime

from swarms.team_agent.capabilities.base_capability import BaseCapability
from swarms.team_agent.capabilities.document_generator import DocumentGenerator
from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability


class TestCapability(BaseCapability):
    """Test capability for unit testing."""
    
    def get_metadata(self):
        return {
            "type": "test",
            "domain": "testing",
            "version": "1.0.0",
        }
    
    def execute(self, context):
        return {
            "content": "test content",
            "metadata": {"test": True},
            "artifacts": [],
        }


class TestBaseCapability:
    """Test BaseCapability abstract class."""
    
    def test_capability_initialization(self):
        """Test capability can be instantiated."""
        cap = TestCapability()
        assert cap.metadata is not None
        assert cap.created_at is not None
        assert isinstance(cap.created_at, datetime)
    
    def test_metadata_structure(self):
        """Test metadata has expected structure."""
        cap = TestCapability()
        meta = cap.metadata
        
        assert "type" in meta
        assert "domain" in meta
        assert "version" in meta
        assert meta["type"] == "test"
        assert meta["domain"] == "testing"
    
    def test_matches_exact(self):
        """Test matching with exact requirements."""
        cap = TestCapability()
        
        # Should match exact
        assert cap.matches({"type": "test", "domain": "testing"})
        
        # Should match type only
        assert cap.matches({"type": "test"})
        
        # Should match domain only
        assert cap.matches({"domain": "testing"})
    
    def test_matches_no_match(self):
        """Test matching fails with wrong requirements."""
        cap = TestCapability()
        
        # Wrong type
        assert not cap.matches({"type": "wrong"})
        
        # Wrong domain
        assert not cap.matches({"domain": "wrong"})
        
        # Wrong specialty
        assert not cap.matches({"specialty": "nonexistent"})
    
    def test_validate_context(self):
        """Test context validation."""
        cap = TestCapability()
        
        # Valid context
        assert cap.validate_context({"mission": "test mission"})
        
        # Invalid context (missing mission)
        assert not cap.validate_context({"other": "data"})
    
    def test_to_dict(self):
        """Test serialization to dict."""
        cap = TestCapability()
        data = cap.to_dict()
        
        assert "class" in data
        assert "metadata" in data
        assert "created_at" in data
        assert data["class"] == "TestCapability"


class TestDocumentGenerator:
    """Test DocumentGenerator capability."""
    
    def test_metadata(self):
        """Test DocumentGenerator metadata."""
        cap = DocumentGenerator()
        meta = cap.metadata
        
        assert meta["type"] == "document_generation"
        assert meta["domain"] == "general"
        assert "markdown" in meta["formats"]
    
    def test_execute_basic(self):
        """Test basic document generation."""
        cap = DocumentGenerator()
        result = cap.execute({
            "mission": "Generate test document"
        })
        
        assert "content" in result
        assert "metadata" in result
        assert "artifacts" in result
        assert len(result["artifacts"]) > 0
    
    def test_execute_with_parameters(self):
        """Test document generation with parameters."""
        cap = DocumentGenerator()
        result = cap.execute({
            "mission": "Generate guide",
            "sections": ["Intro", "Body", "Conclusion"],
            "format": "markdown"
        })
        
        assert result["content"] is not None
        assert len(result["content"]) > 0
    
    def test_artifact_structure(self):
        """Test generated artifacts have correct structure."""
        cap = DocumentGenerator()
        result = cap.execute({"mission": "Test"})
        
        artifact = result["artifacts"][0]
        assert "filename" in artifact
        assert "content" in artifact
        assert "type" in artifact
        assert artifact["filename"].endswith(".md")


class TestHRTGuideCapability:
    """Test HRTGuideCapability."""
    
    def test_metadata(self):
        """Test HRT capability metadata."""
        cap = HRTGuideCapability()
        meta = cap.metadata
        
        assert meta["type"] == "document_generation"
        assert meta["domain"] == "medical"
        assert meta["specialty"] == "endocrinology"
        assert meta["subdomain"] == "hormone_replacement_therapy"
    
    def test_execute_generates_code(self):
        """Test HRT capability generates Python code."""
        cap = HRTGuideCapability()
        result = cap.execute({
            "mission": "Generate HRT clinical guide"
        })
        
        assert "content" in result
        assert "artifacts" in result
        
        # Should generate Python code
        artifact = result["artifacts"][0]
        assert artifact["filename"] == "hrt_guide_generator.py"
        assert artifact["type"] == "python"
        assert "#!/usr/bin/env python3" in artifact["content"]
    
    def test_matches_medical_requirements(self):
        """Test HRT capability matches medical requirements."""
        cap = HRTGuideCapability()
        
        # Should match medical domain
        assert cap.matches({
            "type": "document_generation",
            "domain": "medical"
        })
        
        # Should match specialty
        assert cap.matches({
            "domain": "medical",
            "specialty": "endocrinology"
        })
        
        # Should not match wrong domain
        assert not cap.matches({"domain": "general"})