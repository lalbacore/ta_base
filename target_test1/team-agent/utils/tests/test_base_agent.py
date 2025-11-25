import unittest
from base.base_agent import BaseAgent

class TestBaseAgent(unittest.TestCase):

    def setUp(self):
        self.agent = BaseAgent(name="TestAgent", id="agent_001", capabilities=["test"], policy="test_policy")

    def test_initialization(self):
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.id, "agent_001")
        self.assertIn("test", self.agent.capabilities)
        self.assertEqual(self.agent.policy, "test_policy")

    def test_evaluate_intent(self):
        intent = "test_intent"
        result = self.agent.evaluate_intent(intent)
        # Assuming evaluate_intent returns True for valid intents
        self.assertTrue(result)

    def test_act(self):
        intent = "test_intent"
        result = self.agent.act(intent)
        # Assuming act returns a string indicating action taken
        self.assertIn("executed", result)

    def test_record(self):
        event = "test_event"
        self.agent.record(event)
        # Assuming record logs the event, we can check if it was logged
        # This would require a method to retrieve logged events, which is not implemented here
        # self.assertIn(event, self.agent.get_logged_events())

    def test_describe(self):
        metadata = self.agent.describe()
        self.assertIn("name", metadata)
        self.assertIn("id", metadata)
        self.assertIn("capabilities", metadata)
        self.assertIn("policy", metadata)

if __name__ == "__main__":
    unittest.main()