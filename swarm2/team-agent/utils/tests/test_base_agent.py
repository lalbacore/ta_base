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
        self.assertIsInstance(result, bool)

    def test_act(self):
        agent = BaseAgent("TestAgent", "id_test", ["test"], {"can_test": True})
        result = agent.act("Run tests")
        self.assertEqual(result, {"test_results": "All tests passed"})

    def test_record(self):
        self.agent.record("test_event")

    def test_describe(self):
        metadata = self.agent.describe()
        self.assertIsInstance(metadata, dict)

if __name__ == '__main__':
    unittest.main()