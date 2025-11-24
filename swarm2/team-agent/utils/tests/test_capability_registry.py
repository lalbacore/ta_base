"""
Tests for CapabilityRegistry.
"""

import pytest

from swarms.team_agent.capabilities.registry import CapabilityRegistry
from swarms.team_agent.capabilities.document_generator import DocumentGenerator
from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability


class TestCapabilityRegistry:
    """Test CapabilityRegistry functionality."""
    
    def test_initialization(self):
        """Test registry initializes empty."""
        registry = CapabilityRegistry()
        
        assert len(registry.capabilities) == 0
        assert len(registry._by_type) == 0
        assert len(registry._by_domain) == 0
    
    def test_register_single_capability(self):
        """Test registering a single capability."""
        registry = CapabilityRegistry()
        cap = DocumentGenerator()
        
        registry.register(cap)
        
        assert len(registry.capabilities) == 1
        assert registry.capabilities[0] == cap
    
    def test_register_multiple_capabilities(self):
        """Test registering multiple capabilities."""
        registry = CapabilityRegistry()
        
        cap1 = DocumentGenerator()
        cap2 = HRTGuideCapability()
        
        registry.register(cap1)
        registry.register(cap2)
        
        assert len(registry.capabilities) == 2
    
    def test_indexing_by_type(self):
        """Test capabilities are indexed by type."""
        registry = CapabilityRegistry()
        
        cap1 = DocumentGenerator()
        cap2 = HRTGuideCapability()
        
        registry.register(cap1)
        registry.register(cap2)
        
        # Both are document_generation type
        doc_gen_caps = registry.get_by_type("document_generation")
        assert len(doc_gen_caps) == 2
    
    def test_indexing_by_domain(self):
        """Test capabilities are indexed by domain."""
        registry = CapabilityRegistry()
        
        cap1 = DocumentGenerator()  # domain: general
        cap2 = HRTGuideCapability()  # domain: medical
        
        registry.register(cap1)
        registry.register(cap2)
        
        general_caps = registry.get_by_domain("general")
        medical_caps = registry.get_by_domain("medical")
        
        assert len(general_caps) == 1
        assert len(medical_caps) == 1
        assert general_caps[0] == cap1
        assert medical_caps[0] == cap2
    
    def test_find_exact_match(self):
        """Test finding capability with exact match."""
        registry = CapabilityRegistry()
        
        cap = HRTGuideCapability()
        registry.register(cap)
        
        found = registry.find({
            "type": "document_generation",
            "domain": "medical"
        })
        
        assert found is not None
        assert found == cap
    
    def test_find_no_match(self):
        """Test finding returns None when no match."""
        registry = CapabilityRegistry()
        
        cap = DocumentGenerator()
        registry.register(cap)
        
        found = registry.find({
            "type": "nonexistent_type"
        })
        
        assert found is None
    
    def test_find_all_matches(self):
        """Test finding all matching capabilities."""
        registry = CapabilityRegistry()
        
        cap1 = DocumentGenerator()
        cap2 = HRTGuideCapability()
        
        registry.register(cap1)
        registry.register(cap2)
        
        # Both are document_generation
        all_doc_gen = registry.find_all({
            "type": "document_generation"
        })
        
        assert len(all_doc_gen) == 2
    
    def test_find_all_with_domain_filter(self):
        """Test finding all with domain filter."""
        registry = CapabilityRegistry()
        
        cap1 = DocumentGenerator()
        cap2 = HRTGuideCapability()
        
        registry.register(cap1)
        registry.register(cap2)
        
        # Only medical domain
        medical_caps = registry.find_all({
            "domain": "medical"
        })
        
        assert len(medical_caps) == 1
        assert medical_caps[0] == cap2
    
    def test_list_capabilities(self):
        """Test listing all capabilities."""
        registry = CapabilityRegistry()
        
        cap1 = DocumentGenerator()
        cap2 = HRTGuideCapability()
        
        registry.register(cap1)
        registry.register(cap2)
        
        cap_list = registry.list_capabilities()
        
        assert len(cap_list) == 2
        assert all("metadata" in cap for cap in cap_list)
        assert all("class" in cap for cap in cap_list)
    
    def test_empty_registry_operations(self):
        """Test operations on empty registry."""
        registry = CapabilityRegistry()
        
        assert registry.find({"type": "any"}) is None
        assert registry.find_all({"type": "any"}) == []
        assert registry.get_by_type("any") == []
        assert registry.get_by_domain("any") == []
        assert registry.list_capabilities() == []
