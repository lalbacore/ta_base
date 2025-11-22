import unittest
from base.base_agent import BaseAgent

class TestBaseAgent(unittest.TestCase):

    def setUp(self):
        self.agent = BaseAgent(name="TestAgent", id="001", capabilities=["test"], policy="test_policy")

    def test_initialization(self):
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.id, "001")
        self.assertIn("test", self.agent.capabilities)
        self.assertEqual(self.agent.policy, "test_policy")

    def test_evaluate_intent(self):
        result = self.agent.evaluate_intent("test_intent")
        self.assertIsInstance(result, bool)  # Assuming it returns a boolean

    def test_act(self):
        result = self.agent.act("test_intent")
        self.assertIn(result, ["executed", "refused"])  # Assuming it returns either of these strings

    def test_record(self):
        self.agent.record("test_event")
        # Here you would check if the event was logged correctly, 
        # but since we don't have a logging mechanism in this stub, we will skip this.

    def test_describe(self):
        metadata = self.agent.describe()
        self.assertIsInstance(metadata, dict)  # Assuming it returns a dictionary

if __name__ == '__main__':
    unittest.main()