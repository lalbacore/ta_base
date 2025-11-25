"""
Tests for Governance agent.

These tests focus on behavior:
- Does Governance make approval/rejection decisions?
- Does Governance track its decisions?
- Does the workflow complete end-to-end?
"""

import unittest
from swarms.team_agent.roles import Architect, Builder, Critic, Governance


class TestGovernance(unittest.TestCase):
    
    def setUp(self):
        self.governance = Governance()
        self.architect = Architect()
        self.builder = Builder()
        self.critic = Critic()
    
    def test_governance_initialization(self):
        """Test that Governance initializes correctly."""
        self.assertEqual(self.governance.name, "Governance")
        self.assertIn("enforce_policy", self.governance.capabilities)
    
    def test_governance_allows_passing_review(self):
        """Test that Governance allows reviews that pass."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        decision = self.governance.act(review)
        
        # Behavioral: did we get a decision?
        self.assertEqual(decision["status"], "enforced")
        self.assertIn("allowed", decision)
        self.assertIn("decision_id", decision)
    
    def test_governance_rejects_low_score(self):
        """Test that Governance rejects low-scoring reviews."""
        review = {
            "status": "reviewed",
            "score": 0.3,  # Below threshold
            "passed": False
        }
        
        decision = self.governance.act(review)
        
        # Behavioral: low score should not be allowed
        self.assertEqual(decision["status"], "enforced")
        self.assertFalse(decision["allowed"])
    
    def test_governance_tracks_decisions(self):
        """Test that Governance tracks made decisions."""
        design = self.architect.act("Design 1")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        for i in range(3):
            self.governance.act(review)
        
        # Behavioral: decisions should be tracked
        self.assertEqual(len(self.governance.decisions), 3)
    
    def test_governance_describe(self):
        """Test that Governance provides metadata."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        self.governance.act(review)
        
        metadata = self.governance.describe()
        
        # Behavioral: metadata should reflect state
        self.assertEqual(metadata["name"], "Governance")
        self.assertEqual(metadata["decisions_made"], 1)
    
    def test_architect_builder_critic_governance_workflow(self):
        """Test end-to-end workflow up to Governance."""
        # Architect designs
        design = self.architect.act("Build a scalable system")
        self.assertEqual(design["status"], "designed")
        
        # Builder implements
        build = self.builder.act(design)
        self.assertEqual(build["status"], "built")
        
        # Critic reviews
        review = self.critic.act({"design": design, "build": build})
        self.assertEqual(review["status"], "reviewed")
        
        # Governance enforces
        decision = self.governance.act(review)
        self.assertEqual(decision["status"], "enforced")
        self.assertIn("allowed", decision)


if __name__ == '__main__':
    unittest.main()