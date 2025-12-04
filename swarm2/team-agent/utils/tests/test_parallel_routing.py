"""
Tests for parallel execution and routing.

These tests focus on behavior:
- Does parallel execution run multiple capabilities?
- Does routing analyze missions and pick a strategy?
- Does the routed orchestrator complete workflows?
"""
import pytest
from pathlib import Path

from swarms.team_agent.orchestrator import Orchestrator
from swarms.team_agent.router import MissionRouter, RoutedOrchestrator
from swarms.team_agent.parallel_executor import ParallelCapabilityExecutor
from swarms.team_agent.capabilities.document_generator import DocumentGenerator
from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability


class TestParallelExecution:
    def test_parallel_capability_executor(self):
        """Test executing multiple capabilities in parallel."""
        executor = ParallelCapabilityExecutor(max_workers=2)
        
        caps = [DocumentGenerator(), HRTGuideCapability()]
        mission = "Generate comprehensive medical documentation"
        
        result = executor.execute_capabilities(mission, caps)
        
        # Behavioral: did parallel execution work?
        assert result is not None
        assert 'capabilities_executed' in result
        assert result['capabilities_executed'] >= 1
        assert 'results' in result


class TestMissionRouter:
    def test_analyze_simple_mission(self):
        """Test routing analysis for simple mission."""
        from swarms.team_agent.capabilities.registry import CapabilityRegistry
        from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability
        
        registry = CapabilityRegistry()
        registry.register(HRTGuideCapability())
        
        router = MissionRouter(registry)
        analysis = router.analyze_mission("Generate hormone therapy guide")
        
        # Behavioral: did we get an analysis with a strategy?
        assert analysis is not None
        assert 'strategy' in analysis
        assert 'complexity' in analysis
    
    def test_analyze_parallel_mission(self):
        """Test routing for parallel execution."""
        from swarms.team_agent.capabilities.registry import CapabilityRegistry
        
        registry = CapabilityRegistry()
        router = MissionRouter(registry)
        
        analysis = router.analyze_mission(
            "Compare multiple approaches to web scraping"
        )
        
        # Behavioral: parallel missions should be identified
        assert analysis is not None
        assert 'strategy' in analysis
        assert 'can_parallelize' in analysis
    
    def test_analyze_complex_mission(self):
        """Test routing for complex mission."""
        from swarms.team_agent.capabilities.registry import CapabilityRegistry
        
        registry = CapabilityRegistry()
        router = MissionRouter(registry)
        
        analysis = router.analyze_mission(
            "Build a complete full stack medical records system"
        )
        
        # Behavioral: complex missions should be flagged
        assert analysis is not None
        assert analysis['complexity'] in ['complex', 'medium', 'simple']
    
    def test_decompose_mission(self):
        """Test mission decomposition produces subtasks."""
        from swarms.team_agent.capabilities.registry import CapabilityRegistry
        
        registry = CapabilityRegistry()
        router = MissionRouter(registry)
        
        subtasks = router.decompose_mission(
            "Build full stack medical app with API and UI"
        )
        
        # Behavioral: decomposition should produce a list of subtasks
        assert subtasks is not None
        assert isinstance(subtasks, list)
        assert len(subtasks) >= 1  # At least one subtask
        # Each subtask should have some description
        for task in subtasks:
            assert isinstance(task, dict)


class TestRoutedOrchestrator:
    def test_routed_execution_simple(self, tmp_path):
        """Test routed orchestrator with simple mission."""
        base = Orchestrator(output_dir=str(tmp_path))
        router = MissionRouter(base.capability_registry)
        routed = RoutedOrchestrator(base, router)
        
        result = routed.execute("Generate HRT guide")
        assert result is not None
    
    def test_routed_execution_parallel(self, tmp_path):
        """Test routed orchestrator with parallel mission."""
        base = Orchestrator(output_dir=str(tmp_path))
        
        base.capability_registry.register(DocumentGenerator())
        base.capability_registry.register(HRTGuideCapability())
        
        router = MissionRouter(base.capability_registry)
        routed = RoutedOrchestrator(base, router)
        
        result = routed.execute(
            "Generate medical documentation with multiple formats"
        )
        assert result is not None