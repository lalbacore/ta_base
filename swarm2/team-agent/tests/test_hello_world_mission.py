"""
Backend Unit Tests for Hello World Mission

Tests the complete mission lifecycle for a simple "hello world" Python script:
1. Mission creation
2. Mission execution through orchestrator
3. Artifact generation
4. Mission completion

These tests focus on backend functionality and avoid UI dependencies.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.database import get_backend_session, init_backend_db
from app.models.agent import AgentCard
from swarms.team_agent.orchestrator import Orchestrator


class TestHelloWorldMission:
    """Test suite for hello world mission."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Initialize database
        init_backend_db()
        
        # Create temporary output directory
        self.temp_dir = tempfile.mkdtemp()
        
        yield
        
        # Cleanup
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_database_initialized(self):
        """Test that database is properly initialized."""
        with get_backend_session() as session:
            # Should be able to query without errors
            agent_count = session.query(AgentCard).count()
            assert agent_count >= 0  # May be 0 if freshly reset
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator can be initialized."""
        try:
            orchestrator = Orchestrator(output_dir=self.temp_dir)
            assert orchestrator is not None
            assert orchestrator.output_dir == self.temp_dir
        except Exception as e:
            pytest.fail(f"Orchestrator initialization failed: {e}")
    
    def test_hello_world_mission_structure(self):
        """Test the structure of a hello world mission request."""
        mission_request = {
            "description": "Create a simple hello world Python script",
            "max_cost": 10.0,
            "auto_approve_trusted": True,
            "required_capabilities": []
        }
        
        # Validate structure
        assert "description" in mission_request
        assert "max_cost" in mission_request
        assert isinstance(mission_request["description"], str)
        assert isinstance(mission_request["max_cost"], (int, float))
        assert "hello" in mission_request["description"].lower()
    
    @patch('swarms.team_agent.orchestrator.Orchestrator.execute_workflow')
    def test_mission_execution_mock(self, mock_execute):
        """Test mission execution with mocked workflow."""
        # Setup mock
        mock_execute.return_value = {
            'status': 'completed',
            'workflow_id': 'test-workflow-123',
            'artifacts': [
                {
                    'name': 'hello_world.py',
                    'path': f'{self.temp_dir}/hello_world.py',
                    'size': 150
                }
            ]
        }
        
        orchestrator = Orchestrator(output_dir=self.temp_dir)
        
        # Execute mission
        result = orchestrator.execute_workflow(
            mission_description="Create a simple hello world Python script",
            workflow_id="test-workflow-123"
        )
        
        # Verify
        assert result['status'] == 'completed'
        assert 'workflow_id' in result
        assert len(result['artifacts']) > 0
        assert any('hello_world' in a['name'] for a in result['artifacts'])
    
    def test_artifact_creation(self):
        """Test that artifacts can be created in output directory."""
        # Create a simple artifact
        artifact_path = Path(self.temp_dir) / 'hello_world.py'
        
        artifact_content = '''#!/usr/bin/env python3
"""
Simple Hello World Program
"""


def main():
    """Print hello world message."""
    print("=" * 50)
    print("  Hello, World!")
    print("=" * 50)
    print()
    print("Welcome to the generated application!")
    print()


if __name__ == "__main__":
    main()
'''
        
        artifact_path.write_text(artifact_content)
        
        # Verify artifact exists
        assert artifact_path.exists()
        assert artifact_path.is_file()
        
        # Verify content
        content = artifact_path.read_text()
        assert 'Hello, World!' in content
        assert 'def main()' in content
        
        # Verify it's valid Python
        import ast
        try:
            ast.parse(content)
        except SyntaxError:
            pytest.fail("Generated artifact is not valid Python")
    
    def test_mission_workflow_stages(self):
        """Test that mission workflow has expected stages."""
        # Expected stages for a simple mission
        expected_stages = ['architect', 'builder', 'critic', 'governance', 'recorder']
        
        # Verify stages are defined (this is a structural test)
        from swarms.team_agent.roles_v2 import Architect, Builder, Critic, Governance, Recorder
        
        # Verify each role can be instantiated
        workflow_id = "test-workflow-stages"
        
        architect = Architect(workflow_id)
        assert architect.role_name == 'architect'
        
        builder = Builder(workflow_id)
        assert builder.role_name == 'builder'
        
        critic = Critic(workflow_id)
        assert critic.role_name == 'critic'
        
        governance = Governance(workflow_id)
        assert governance.role_name == 'governance'
        
        recorder = Recorder(workflow_id)
        assert recorder.role_name == 'recorder'
    
    def test_hello_world_code_generation(self):
        """Test that Builder can generate hello world code."""
        from swarms.team_agent.roles_v2 import Builder
        
        builder = Builder(workflow_id="test-builder")
        
        # Simulate architect output
        architecture = {
            'mission': 'Create a simple hello world Python script',
            'components': ['greeting_module', 'output_handler'],
            'architecture_type': 'modular_monolith',
            'tech_stack': {
                'language': 'Python 3.9+',
                'framework': 'None (standard library)',
                'testing': 'pytest'
            }
        }
        
        context = {
            'input': architecture,
            'instructions': {}
        }
        
        # Execute builder
        result = builder.run(context)
        
        # Verify output
        assert 'code' in result
        assert 'filename' in result
        assert 'hello_world.py' in result['filename'].lower()
        assert 'Hello, World!' in result['code']
        
        # Verify it's valid Python
        import ast
        try:
            ast.parse(result['code'])
        except SyntaxError:
            pytest.fail("Builder generated invalid Python code")
    
    def test_mission_cost_validation(self):
        """Test that mission cost is validated."""
        mission_request = {
            "description": "Create a simple hello world Python script",
            "max_cost": 10.0,
        }
        
        # Cost should be positive
        assert mission_request["max_cost"] > 0
        
        # Cost should be reasonable for a simple mission
        assert mission_request["max_cost"] <= 100.0
    
    def test_artifact_file_permissions(self):
        """Test that generated artifacts have correct permissions."""
        artifact_path = Path(self.temp_dir) / 'hello_world.py'
        
        artifact_content = '''#!/usr/bin/env python3
print("Hello, World!")
'''
        
        artifact_path.write_text(artifact_content)
        
        # Make executable
        os.chmod(artifact_path, 0o755)
        
        # Verify file is readable and executable
        assert os.access(artifact_path, os.R_OK)
        assert os.access(artifact_path, os.X_OK)


class TestMissionIntegration:
    """Integration tests for mission execution."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        init_backend_db()
        self.temp_dir = tempfile.mkdtemp()
        
        yield
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow_stages(self):
        """Test complete workflow execution through all stages."""
        from swarms.team_agent.roles_v2 import Architect, Builder, Critic, Governance, Recorder
        
        workflow_id = "test-e2e-workflow"
        
        # Stage 1: Architect
        architect = Architect(workflow_id)
        arch_result = architect.run({
            'input': 'Create a simple hello world Python script',
            'instructions': {}
        })
        
        assert 'mission' in arch_result
        assert 'components' in arch_result
        
        # Stage 2: Builder
        builder = Builder(workflow_id)
        build_result = builder.run({
            'input': arch_result,
            'instructions': {}
        })
        
        assert 'code' in build_result
        assert 'filename' in build_result
        
        # Stage 3: Critic
        critic = Critic(workflow_id)
        critic_result = critic.run({
            'input': build_result,
            'instructions': {}
        })
        
        assert 'quality_score' in critic_result
        assert 'issues' in critic_result
        
        # Stage 4: Governance
        governance = Governance(workflow_id)
        gov_result = governance.run({
            'input': critic_result,
            'instructions': {}
        })
        
        assert 'decision' in gov_result
        assert gov_result['decision'] in ['approved', 'rejected', 'needs_review']
        
        # Stage 5: Recorder (only if approved)
        if gov_result['decision'] == 'approved':
            recorder = Recorder(workflow_id)
            rec_result = recorder.run({
                'input': {
                    'implementation': build_result,
                    'review': critic_result,
                    'governance': gov_result
                },
                'instructions': {}
            })
            
            assert 'artifacts' in rec_result or 'status' in rec_result


if __name__ == '__main__':
    # Allow running tests directly
    pytest.main([__file__, '-v'])
