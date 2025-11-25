"""
Tests for enhanced workflow with better quality checks.

These tests focus on behavior:
- Does the Critic produce a review with a score?
- Does Governance make approval decisions?
- Does the workflow complete successfully?
"""

import unittest

from swarms.team_agent.roles import Critic, Governance


class TestEnhancedCritic(unittest.TestCase):
    """Test the Critic agent review capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.critic = Critic()
    
    def test_simple_code_analysis(self):
        """Test analyzing code produces a review."""
        implementation = {
            "build": {
                "status": "built",
                "code": "def main(): print('Hello')",
                "language": "python"
            }
        }
        
        result = self.critic.run(implementation)
        
        # Behavioral: did we get a review?
        self.assertEqual(result["status"], "reviewed")
        self.assertIn("score", result)
        self.assertIn("findings", result)
        self.assertIn("passed", result)
    
    def test_review_provides_feedback(self):
        """Test that review includes actionable feedback."""
        implementation = {
            "build": {
                "status": "built",
                "artifacts": [{"type": "code", "name": "main.py"}]
            }
        }
        
        result = self.critic.run(implementation)
        
        # Behavioral: is there feedback?
        self.assertIn("feedback", result)
        self.assertIsInstance(result["feedback"], str)
        self.assertGreater(len(result["feedback"]), 0)
    
    def test_review_identifies_risks(self):
        """Test that review can identify risks."""
        implementation = {
            "build": {"status": "built"}
        }
        
        result = self.critic.run(implementation)
        
        # Behavioral: are risks reported?
        self.assertIn("risks", result)
        self.assertIsInstance(result["risks"], list)


class TestEnhancedGovernance(unittest.TestCase):
    """Test the Governance agent decision capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.governance = Governance()
    
    def test_approval_for_passing_review(self):
        """Test approval for a passing review."""
        review = {
            "status": "reviewed",
            "score": 0.85,
            "passed": True,
            "recommendation": "approved"
        }
        
        result = self.governance.run(review)
        
        # Behavioral: did we get a decision?
        self.assertEqual(result["status"], "enforced")
        self.assertIn("allowed", result)
        self.assertTrue(result["allowed"])
    
    def test_rejection_for_failing_review(self):
        """Test handling of a failing review."""
        review = {
            "status": "reviewed",
            "score": 0.3,
            "passed": False,
            "recommendation": "needs_revision"
        }
        
        result = self.governance.run(review)
        
        # Behavioral: did governance make a decision?
        self.assertEqual(result["status"], "enforced")
        self.assertIn("allowed", result)
        # Low score should not be allowed
        self.assertFalse(result["allowed"])
    
    def test_governance_tracks_decisions(self):
        """Test that governance tracks its decisions."""
        review = {
            "status": "reviewed",
            "score": 0.75,
            "passed": True
        }
        
        self.governance.run(review)
        
        # Behavioral: is the decision recorded?
        self.assertEqual(len(self.governance.decisions), 1)


class TestWorkflowIntegration(unittest.TestCase):
    """Test workflow integration between agents."""
    
    def test_critic_to_governance_flow(self):
        """Test that Critic output flows to Governance."""
        critic = Critic()
        governance = Governance()
        
        # Critic reviews a build
        build_payload = {
            "design": {"status": "designed", "components": []},
            "build": {"status": "built", "artifacts": []}
        }
        review = critic.act(build_payload)
        
        # Governance evaluates the review
        decision = governance.run(review)
        
        # Behavioral: did the flow complete?
        self.assertEqual(review["status"], "reviewed")
        self.assertEqual(decision["status"], "enforced")
        self.assertIn("allowed", decision)


if __name__ == '__main__':
    unittest.main()