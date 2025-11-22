import unittest
from swarms.team_agent.roles import Architect

class TestArchitect(unittest.TestCase):
    
    def setUp(self):
        self.architect = Architect()
    
    def test_architect_initialization(self):
        """Test that Architect initializes with correct attributes."""
        self.assertEqual(self.architect.name, "Architect")
        self.assertEqual(self.architect.id, "agent_architect_001")
        self.assertIn("design_system", self.architect.capabilities)
        self.assertTrue(self.architect.policy["can_design"])
    
    def test_architect_evaluate_intent_valid(self):
        """Test that valid intents are evaluated as True."""
        result = self.architect.evaluate_intent("Build a secure API")
        self.assertTrue(result)
    
    def test_architect_evaluate_intent_invalid(self):
        """Test that invalid intents are evaluated as False."""
        self.assertFalse(self.architect.evaluate_intent(""))
        self.assertFalse(self.architect.evaluate_intent(None))
        self.assertFalse(self.architect.evaluate_intent("   "))
    
    def test_architect_act_valid_intent(self):
        """Test that Architect can design for a valid intent."""
        result = self.architect.act("Build a microservices platform")
        self.assertEqual(result["status"], "designed")
        self.assertIn("architecture", result)
        self.assertIn("components", result)
        self.assertIn("design_id", result)
    
    def test_architect_act_invalid_intent(self):
        """Test that Architect refuses invalid intents."""
        result = self.architect.act("")
        self.assertEqual(result["status"], "refused")
        self.assertIn("reason", result)
    
    def test_architect_tracks_designs(self):
        """Test that Architect tracks created designs."""
        self.architect.act("Design 1")
        self.architect.act("Design 2")
        self.architect.act("Design 3")
        self.assertEqual(len(self.architect.designs), 3)
    
    def test_architect_describe(self):
        """Test that Architect provides accurate metadata."""
        self.architect.act("Test design")
        metadata = self.architect.describe()
        self.assertEqual(metadata["name"], "Architect")
        self.assertEqual(metadata["designs_created"], 1)

if __name__ == '__main__':
    unittest.main()