
from swarms.team_agent.specialists.base import BaseSpecialist

class TestSpecialist(BaseSpecialist):
    """
    Test Specialist for verification of dynamic loading.
    """
    def __init__(self, agent_id="test_specialist_v1", workflow_id=None):
        super().__init__(
            agent_id=agent_id,
            workflow_id=workflow_id
        )
        # Override name set by BaseSpecialist
        self.name = "Test Python Specialist"
        
    def get_metadata(self):
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_type": "specialist",
            "description": "Mock specialist for testing",
            "module_path": "swarms.team_agent.specialists.test_specialist",
            "class_name": "TestSpecialist",
             "trust_domain": "EXECUTION",
             "version": "1.0.0",
             "capabilities": []
        }
