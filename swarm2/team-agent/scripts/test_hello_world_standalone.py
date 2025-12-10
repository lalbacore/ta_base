#!/usr/bin/env python3
"""
Standalone Hello World Mission Test

Tests the complete mission lifecycle without pytest to avoid dependency conflicts.
This script can be run directly: python scripts/test_hello_world_standalone.py
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'backend'))

from app.database import get_backend_session, init_backend_db
from app.models.agent import AgentCard
from swarms.team_agent.roles_v2 import Architect, Builder, Critic, Governance, Recorder


class TestRunner:
    """Simple test runner."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name):
        """Decorator to register a test."""
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator
    
    def assert_true(self, condition, message="Assertion failed"):
        """Assert that condition is true."""
        if not condition:
            raise AssertionError(message)
    
    def assert_equal(self, a, b, message=None):
        """Assert that a equals b."""
        if a != b:
            msg = message or f"Expected {a} == {b}"
            raise AssertionError(msg)
    
    def assert_in(self, item, container, message=None):
        """Assert that item is in container."""
        if item not in container:
            msg = message or f"Expected {item} in {container}"
            raise AssertionError(msg)
    
    def run(self):
        """Run all tests."""
        print("=" * 70)
        print("Hello World Mission Test Suite")
        print("=" * 70)
        print()
        
        for name, test_func in self.tests:
            try:
                print(f"Running: {name}...", end=" ")
                test_func(self)
                print("✓ PASS")
                self.passed += 1
            except Exception as e:
                print(f"✗ FAIL")
                print(f"  Error: {e}")
                self.failed += 1
        
        print()
        print("=" * 70)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 70)
        
        return self.failed == 0


# Create test runner
runner = TestRunner()


@runner.test("Database initialization")
def test_database_init(t):
    """Test that database can be initialized."""
    init_backend_db()
    with get_backend_session() as session:
        count = session.query(AgentCard).count()
        t.assert_true(count >= 0, "Database query should work")


@runner.test("Architect role instantiation")
def test_architect_init(t):
    """Test that Architect role can be instantiated."""
    architect = Architect(workflow_id="test-001")
    t.assert_equal(architect.role_name, "architect")


@runner.test("Architect generates architecture")
def test_architect_run(t):
    """Test that Architect generates architecture."""
    architect = Architect(workflow_id="test-002")
    result = architect.run({
        'input': 'Create a simple hello world Python script',
        'instructions': {}
    })
    
    t.assert_in('mission', result)
    t.assert_in('components', result)
    t.assert_in('architecture_type', result)


@runner.test("Builder role instantiation")
def test_builder_init(t):
    """Test that Builder role can be instantiated."""
    builder = Builder(workflow_id="test-003")
    t.assert_equal(builder.role_name, "builder")


@runner.test("Builder generates hello world code")
def test_builder_hello_world(t):
    """Test that Builder generates hello world code."""
    builder = Builder(workflow_id="test-004")
    
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
    
    result = builder.run({
        'input': architecture,
        'instructions': {}
    })
    
    t.assert_in('code', result)
    t.assert_in('filename', result)
    t.assert_in('Hello, World!', result['code'])
    
    # Verify it's valid Python
    import ast
    try:
        ast.parse(result['code'])
    except SyntaxError:
        raise AssertionError("Generated code is not valid Python")


@runner.test("Critic role instantiation")
def test_critic_init(t):
    """Test that Critic role can be instantiated."""
    critic = Critic(workflow_id="test-005")
    t.assert_equal(critic.role_name, "critic")


@runner.test("Critic reviews code")
def test_critic_run(t):
    """Test that Critic reviews code."""
    critic = Critic(workflow_id="test-006")
    
    implementation = {
        'code': 'print("Hello, World!")',
        'filename': 'hello_world.py',
        'tests': '',
        'documentation': ''
    }
    
    result = critic.run({
        'input': implementation,
        'instructions': {}
    })
    
    t.assert_in('quality_score', result)
    t.assert_in('issues', result)


@runner.test("Governance role instantiation")
def test_governance_init(t):
    """Test that Governance role can be instantiated."""
    governance = Governance(workflow_id="test-007")
    t.assert_equal(governance.role_name, "governance")


@runner.test("Governance makes decision")
def test_governance_run(t):
    """Test that Governance makes approval decision."""
    governance = Governance(workflow_id="test-008")
    
    review = {
        'quality_score': 85,
        'issues': [],
        'recommendations': []
    }
    
    result = governance.run({
        'input': review,
        'instructions': {}
    })
    
    t.assert_in('decision', result)
    t.assert_in(result['decision'], ['approved', 'rejected', 'needs_review'])


@runner.test("Recorder role instantiation")
def test_recorder_init(t):
    """Test that Recorder role can be instantiated."""
    recorder = Recorder(workflow_id="test-009")
    t.assert_equal(recorder.role_name, "recorder")


@runner.test("End-to-end workflow execution")
def test_e2e_workflow(t):
    """Test complete workflow through all stages."""
    workflow_id = "test-e2e-001"
    
    # Stage 1: Architect
    architect = Architect(workflow_id)
    arch_result = architect.run({
        'input': 'Create a simple hello world Python script',
        'instructions': {}
    })
    t.assert_in('mission', arch_result)
    
    # Stage 2: Builder
    builder = Builder(workflow_id)
    build_result = builder.run({
        'input': arch_result,
        'instructions': {}
    })
    t.assert_in('code', build_result)
    t.assert_in('Hello, World!', build_result['code'])
    
    # Stage 3: Critic
    critic = Critic(workflow_id)
    critic_result = critic.run({
        'input': build_result,
        'instructions': {}
    })
    t.assert_in('quality_score', critic_result)
    
    # Stage 4: Governance
    governance = Governance(workflow_id)
    gov_result = governance.run({
        'input': critic_result,
        'instructions': {}
    })
    t.assert_in('decision', gov_result)
    
    print(f"\n    Workflow completed with decision: {gov_result['decision']}")


@runner.test("Artifact file creation")
def test_artifact_creation(t):
    """Test that artifacts can be written to disk."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        artifact_path = Path(temp_dir) / 'hello_world.py'
        
        artifact_content = '''#!/usr/bin/env python3
"""Simple Hello World Program"""

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
        
        artifact_path.write_text(artifact_content)
        
        t.assert_true(artifact_path.exists())
        t.assert_in('Hello, World!', artifact_path.read_text())
        
        # Verify it's valid Python
        import ast
        ast.parse(artifact_content)
        
    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
