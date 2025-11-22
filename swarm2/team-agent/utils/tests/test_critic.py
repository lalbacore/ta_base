import unittest
from swarms.team_agent.roles import Architect, Builder, Critic

class TestCritic(unittest.TestCase):
    
    def setUp(self):
        self.critic = Critic()
        self.architect = Architect()
        self.builder = Builder()
    
    def test_critic_initialization(self):
        """Test that Critic initializes with correct attributes."""
        self.assertEqual(self.critic.name, "Critic")
        self.assertEqual(self.critic.id, "agent_critic_001")
        self.assertIn("review_design", self.critic.capabilities)
        self.assertTrue(self.critic.policy["can_review"])
    
    def test_critic_evaluate_intent_valid(self):
        """Test that valid review packages are evaluated as True."""
        package = {"design": {"status": "designed"}}
        result = self.critic.evaluate_intent(package)
        self.assertTrue(result)
        
        package2 = {"build": {"status": "built"}}
        result2 = self.critic.evaluate_intent(package2)
        self.assertTrue(result2)
    
    def test_critic_evaluate_intent_invalid(self):
        """Test that invalid review packages are evaluated as False."""
        self.assertFalse(self.critic.evaluate_intent(None))
        self.assertFalse(self.critic.evaluate_intent({}))
        self.assertFalse(self.critic.evaluate_intent({"foo": "bar"}))
    
    def test_critic_review_valid_design(self):
        """Test that Critic can review a valid design."""
        design = self.architect.act("Build a system")
        review = self.critic.act({"design": design})
        
        self.assertEqual(review["status"], "reviewed")
        self.assertIn("design_score", review)
        self.assertIn("overall_score", review)
        self.assertIn("feedback", review)
        self.assertIn("passed", review)
    
    def test_critic_review_valid_build(self):
        """Test that Critic can review a valid build."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"build": build})
        
        self.assertEqual(review["status"], "reviewed")
        self.assertIn("build_score", review)
        self.assertIsNotNone(review["build_score"])
    
    def test_critic_review_design_and_build(self):
        """Test that Critic can review both design and build."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        self.assertEqual(review["status"], "reviewed")
        self.assertIsNotNone(review["design_score"])
        self.assertIsNotNone(review["build_score"])
    
    def test_critic_review_invalid_package(self):
        """Test that Critic refuses invalid packages."""
        review = self.critic.act({})
        self.assertEqual(review["status"], "refused")
        self.assertIn("reason", review)
    
    def test_critic_passes_quality_threshold(self):
        """Test that high-quality designs and builds pass."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        self.assertTrue(review["passed"])
        self.assertGreaterEqual(review["overall_score"], self.critic.policy["min_quality_score"])
    
    def test_critic_identifies_risks(self):
        """Test that Critic identifies potential risks."""
        design = self.architect.act("Build a system")
        review = self.critic.act({"design": design})
        
        self.assertIn("risks", review)
        self.assertIsInstance(review["risks"], list)
    
    def test_critic_tracks_reviews(self):
        """Test that Critic tracks conducted reviews."""
        design1 = self.architect.act("Design 1")
        design2 = self.architect.act("Design 2")
        design3 = self.architect.act("Design 3")
        
        self.critic.act({"design": design1})
        self.critic.act({"design": design2})
        self.critic.act({"design": design3})
        
        self.assertEqual(len(self.critic.reviews), 3)
    
    def test_critic_describe(self):
        """Test that Critic provides accurate metadata."""
        design = self.architect.act("Test design")
        self.critic.act({"design": design})
        metadata = self.critic.describe()
        
        self.assertEqual(metadata["name"], "Critic")
        self.assertEqual(metadata["reviews_conducted"], 1)
    
    def test_architect_builder_critic_workflow(self):
        """Test end-to-end Architect -> Builder -> Critic workflow."""
        # Architect designs
        design = self.architect.act("Build a scalable system")
        self.assertEqual(design["status"], "designed")
        
        # Builder implements
        build = self.builder.act(design)
        self.assertEqual(build["status"], "built")
        
        # Critic reviews
        review = self.critic.act({"design": design, "build": build})
        self.assertEqual(review["status"], "reviewed")
        self.assertTrue(review["passed"])

if __name__ == '__main__':
    unittest.main()