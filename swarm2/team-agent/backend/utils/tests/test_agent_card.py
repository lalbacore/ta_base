"""
Test agent card system - models, database, and basic operations.

This test verifies:
- Agent card creation and retrieval
- Agent template creation
- Agent invocation tracking
- Model serialization (to_dict)
"""
import sys
import os
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import backend_engine, BackendSession
from app.models.base import Base
from app.models.agent import AgentCard, AgentTemplate, AgentInvocation


def setup_database():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(backend_engine)
    print("✓ Database tables created/verified")


def test_agent_card_creation():
    """Test creating and retrieving an agent card."""
    print("\n=== Test 1: Agent Card Creation ===")

    session = BackendSession()

    try:
        # Create test agent card
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        agent_card = AgentCard(
            agent_id=agent_id,
            agent_name="Test Python Code Generator",
            agent_type="specialist",
            description="Generates production-ready Python code",
            version="1.0.0",
            capabilities=["code_generation", "python"],
            specialties=["backend", "api"],
            supported_languages=["python"],
            base_class="BaseRole",
            config_schema={
                "type": "object",
                "properties": {
                    "python_version": {"type": "string"},
                    "use_type_hints": {"type": "boolean"}
                }
            },
            default_config={
                "python_version": "3.11",
                "use_type_hints": True
            },
            author="Test Suite",
            license="MIT",
            tags=["python", "code-gen", "test"],
            trust_score=85.0,
            status="active",
            module_path="swarms.team_agent.roles.specialized.python_coder",
            class_name="PythonCoder"
        )

        session.add(agent_card)
        session.commit()

        print(f"✓ Created agent card: {agent_id}")

        # Retrieve and verify
        retrieved = session.query(AgentCard).filter_by(agent_id=agent_id).first()
        assert retrieved is not None, "Agent card not found!"
        assert retrieved.agent_name == "Test Python Code Generator"
        assert retrieved.trust_score == 85.0
        assert "python" in retrieved.capabilities

        print(f"✓ Retrieved agent card: {retrieved.agent_name}")
        print(f"  - Type: {retrieved.agent_type}")
        print(f"  - Capabilities: {', '.join(retrieved.capabilities)}")
        print(f"  - Trust Score: {retrieved.trust_score}")

        # Test to_dict serialization
        agent_dict = retrieved.to_dict()
        assert 'agent_id' in agent_dict
        assert 'capabilities' in agent_dict
        assert agent_dict['trust_score'] == 85.0

        print(f"✓ to_dict() serialization works")

        return agent_id

    finally:
        session.close()


def test_agent_template(agent_id):
    """Test creating agent template."""
    print("\n=== Test 2: Agent Template Creation ===")

    session = BackendSession()

    try:
        template_id = f"test_template_{uuid.uuid4().hex[:8]}"
        template = AgentTemplate(
            template_id=template_id,
            template_name="Python Code Reviewer Template",
            template_type="reviewer",
            description="Template for Python code review agents",
            base_agent_card_id=agent_id,
            configuration={
                "check_pep8": True,
                "check_security": True,
                "min_quality_score": 80
            }
        )

        session.add(template)
        session.commit()

        print(f"✓ Created agent template: {template_id}")

        # Retrieve with relationship
        retrieved = session.query(AgentTemplate).filter_by(template_id=template_id).first()
        assert retrieved is not None
        assert retrieved.base_agent_card_id == agent_id

        # Test relationship
        if retrieved.base_agent_card:
            print(f"✓ Template linked to agent: {retrieved.base_agent_card.agent_name}")

        return template_id

    finally:
        session.close()


def test_agent_invocation(agent_id):
    """Test recording agent invocation."""
    print("\n=== Test 3: Agent Invocation Tracking ===")

    session = BackendSession()

    try:
        invocation_id = f"test_invocation_{uuid.uuid4().hex[:8]}"
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"

        invocation = AgentInvocation(
            invocation_id=invocation_id,
            agent_id=agent_id,
            workflow_id=workflow_id,
            mission_id="mission_test",
            stage="implementation",
            input_data={"mission": "Generate Python API"},
            output_data={"artifacts": ["main.py", "test_main.py"]},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration=15.5,
            status="success",
            rating=4.5
        )

        session.add(invocation)
        session.commit()

        print(f"✓ Created invocation: {invocation_id}")

        # Retrieve and verify
        retrieved = session.query(AgentInvocation).filter_by(invocation_id=invocation_id).first()
        assert retrieved is not None
        assert retrieved.status == "success"
        assert retrieved.duration == 15.5
        assert retrieved.rating == 4.5

        print(f"✓ Invocation recorded:")
        print(f"  - Agent: {retrieved.agent_id}")
        print(f"  - Workflow: {retrieved.workflow_id}")
        print(f"  - Status: {retrieved.status}")
        print(f"  - Duration: {retrieved.duration}s")
        print(f"  - Rating: {retrieved.rating}/5")

        # Test relationship
        if retrieved.agent_card:
            print(f"✓ Invocation linked to agent: {retrieved.agent_card.agent_name}")

        return invocation_id

    finally:
        session.close()


def test_agent_discovery():
    """Test querying agents by capabilities and trust score."""
    print("\n=== Test 4: Agent Discovery ===")

    session = BackendSession()

    try:
        # Find agents with Python capability
        python_agents = session.query(AgentCard).filter(
            AgentCard.capabilities.contains('["code_generation"')
        ).all()

        print(f"✓ Found {len(python_agents)} agent(s) with code_generation capability")
        for agent in python_agents:
            print(f"  - {agent.agent_name} (trust: {agent.trust_score})")

        # Find high-trust agents
        high_trust_agents = session.query(AgentCard).filter(
            AgentCard.trust_score >= 80.0
        ).all()

        print(f"✓ Found {len(high_trust_agents)} agent(s) with trust score >= 80")

        # Find active agents
        active_agents = session.query(AgentCard).filter(
            AgentCard.status == 'active'
        ).all()

        print(f"✓ Found {len(active_agents)} active agent(s)")

    finally:
        session.close()


def cleanup_test_data(agent_id, template_id, invocation_id):
    """Clean up test data."""
    print("\n=== Cleanup Test Data ===")

    session = BackendSession()

    try:
        # Delete invocation
        session.query(AgentInvocation).filter_by(invocation_id=invocation_id).delete()
        print(f"✓ Deleted invocation: {invocation_id}")

        # Delete template
        session.query(AgentTemplate).filter_by(template_id=template_id).delete()
        print(f"✓ Deleted template: {template_id}")

        # Delete agent card
        session.query(AgentCard).filter_by(agent_id=agent_id).delete()
        print(f"✓ Deleted agent card: {agent_id}")

        session.commit()

    finally:
        session.close()


def main():
    """Run all tests."""
    print("="*60)
    print("AGENT CARD SYSTEM TEST")
    print("="*60)

    # Setup
    setup_database()

    # Run tests
    agent_id = test_agent_card_creation()
    template_id = test_agent_template(agent_id)
    invocation_id = test_agent_invocation(agent_id)
    test_agent_discovery()

    # Cleanup
    cleanup_test_data(agent_id, template_id, invocation_id)

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60)


if __name__ == "__main__":
    main()
