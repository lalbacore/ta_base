"""
Pytest configuration and shared fixtures for Team Agent tests.

Provides:
- Database setup/teardown
- Test isolation
- Common test utilities
- Shared fixtures
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.database import init_backend_db, get_backend_session


@pytest.fixture(scope='session')
def init_test_database():
    """Initialize test database once per test session."""
    init_backend_db()
    yield
    # Cleanup after all tests


@pytest.fixture
def temp_output_dir():
    """Provide a temporary output directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def db_session():
    """Provide a database session for tests."""
    with get_backend_session() as session:
        yield session


@pytest.fixture
def sample_mission_request():
    """Provide a sample mission request for testing."""
    return {
        "description": "Create a simple hello world Python script",
        "max_cost": 10.0,
        "auto_approve_trusted": True,
        "required_capabilities": []
    }


@pytest.fixture
def sample_architecture():
    """Provide sample architecture output for testing."""
    return {
        'mission': 'Create a simple hello world Python script',
        'components': ['greeting_module', 'output_handler'],
        'architecture_type': 'modular_monolith',
        'tech_stack': {
            'language': 'Python 3.9+',
            'framework': 'None (standard library)',
            'testing': 'pytest',
            'documentation': 'Markdown'
        },
        'design_patterns': ['factory', 'singleton', 'observer']
    }


# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
