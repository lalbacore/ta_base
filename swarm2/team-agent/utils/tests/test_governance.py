import unittest
from swarms.team_agent.roles import Architect, Builder, Critic, Governance

class TestGovernance(unittest.TestCase):
    
    def setUp(self):
        self.governance = Governance()
        self.architect = Architect()
        self.builder = Builder()
        self.critic = Critic()
    
    def test_governance_initialization(self):
        """Test that Governance initializes with correct attributes."""
        self.assertEqual(self.governance.name, "Governance")
        self.assertEqual(self.governance.id, "agent_governance_001")
        self.assertIn("enforce_policy", self.governance.capabilities)
        self.assertTrue(self.governance.policy["can_enforce"])
    
    def test_governance_evaluate_intent_valid(self):
        """Test that valid governance packages are evaluated as True."""
        package = {
            "request": "Build a system",
            "review": {"status": "reviewed", "passed": True, "overall_score": 85}
        }
        result = self.governance.evaluate_intent(package)
        self.assertTrue(result)
    
    def test_governance_evaluate_intent_invalid(self):
        """Test that invalid governance packages are evaluated as False."""
        self.assertFalse(self.governance.evaluate_intent(None))
        self.assertFalse(self.governance.evaluate_intent({}))
        self.assertFalse(self.governance.evaluate_intent({"request": "Build"}))
        self.assertFalse(self.governance.evaluate_intent({"review": {}}))
    
    def test_governance_enforce_valid_request(self):
        """Test that Governance allows compliant requests."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        package = {"request": "Build a system", "review": review}
        decision = self.governance.act(package)
        
        self.assertEqual(decision["status"], "enforced")
        self.assertTrue(decision["allowed"])
        self.assertIn("decision_id", decision)
    
    def test_governance_enforce_invalid_request(self):
        """Test that Governance refuses invalid requests."""
        decision = self.governance.act({})
        self.assertEqual(decision["status"], "refused")
        self.assertIn("reason", decision)
    
    def test_governance_checks_review_passed(self):
        """Test that Governance requires review to pass."""
        review = {
            "status": "reviewed",
            "passed": False,
            "overall_score": 85,
            "risks": [],
            "feedback": []
        }
        package = {"request": "Build a system", "review": review}
        decision = self.governance.act(package)
        
        self.assertFalse(decision["allowed"])
    
    def test_governance_checks_quality_score(self):
        """Test that Governance enforces quality score threshold."""
        review = {
            "status": "reviewed",
            "passed": True,
            "overall_score": 60,  # Below threshold
            "risks": [],
            "feedback": []
        }
        package = {"request": "Build a system", "review": review}
        decision = self.governance.act(package)
        
        self.assertFalse(decision["compliant"])
    
    def test_governance_tracks_decisions(self):
        """Test that Governance tracks made decisions."""
        design = self.architect.act("Design 1")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        for i in range(3):
            package = {"request": f"Request {i}", "review": review}
            self.governance.act(package)
        
        self.assertEqual(len(self.governance.decisions), 3)
    
    def test_governance_creates_audit_trail(self):
        """Test that Governance creates audit trails."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        package = {"request": "Build a system", "review": review}
        decision = self.governance.act(package)
        
        audit_trail = decision["audit_trail"]
        self.assertIn("request_checksum", audit_trail)
        self.assertIn("review_id", audit_trail)
        self.assertIn("decision_timestamp", audit_trail)
        self.assertIn("enforced_by", audit_trail)
    
    def test_governance_generates_reasoning(self):
        """Test that Governance provides reasoning for decisions."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        package = {"request": "Build a system", "review": review}
        decision = self.governance.act(package)
        
        self.assertIn("reasoning", decision)
        self.assertTrue(len(decision["reasoning"]) > 0)
    
    def test_governance_runs_compliance_checks(self):
        """Test that Governance runs comprehensive compliance checks."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        
        package = {"request": "Build a system", "review": review}
        decision = self.governance.act(package)
        
        checks = decision["compliance_checks"]
        self.assertIn("request_valid", checks)
        self.assertIn("review_complete", checks)
        self.assertIn("quality_acceptable", checks)
        self.assertIn("risks_identified", checks)
        self.assertIn("feedback_provided", checks)
    
    def test_governance_describe(self):
        """Test that Governance provides accurate metadata."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        package = {"request": "Build a system", "review": review}
        self.governance.act(package)
        
        metadata = self.governance.describe()
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
        self.assertTrue(review["passed"])
        
        # Governance enforces
        package = {"request": "Build a scalable system", "review": review}
        decision = self.governance.act(package)
        self.assertEqual(decision["status"], "enforced")
        self.assertTrue(decision["allowed"])

if __name__ == '__main__':
    unittest.main()