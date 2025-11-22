import unittest
from swarms.team_agent.roles import Builder, Architect

class TestBuilder(unittest.TestCase):
    
    def setUp(self):
        self.builder = Builder()
        self.architect = Architect()
    
    def test_builder_initialization(self):
        """Test that Builder initializes with correct attributes."""
        self.assertEqual(self.builder.name, "Builder")
        self.assertEqual(self.builder.id, "agent_builder_001")
        self.assertIn("build_system", self.builder.capabilities)
        self.assertTrue(self.builder.policy["can_build"])
    
    def test_builder_evaluate_intent_valid(self):
        """Test that valid designs are evaluated as True."""
        design = {"status": "designed", "design_id": "design_1"}
        result = self.builder.evaluate_intent(design)
        self.assertTrue(result)
    
    def test_builder_evaluate_intent_invalid(self):
        """Test that invalid designs are evaluated as False."""
        self.assertFalse(self.builder.evaluate_intent(None))
        self.assertFalse(self.builder.evaluate_intent({}))
        self.assertFalse(self.builder.evaluate_intent({"status": "refused"}))
    
    def test_builder_act_valid_design(self):
        """Test that Builder can build from a valid design."""
        design = self.architect.act("Build a REST API")
        result = self.builder.act(design)
        
        self.assertEqual(result["status"], "built")
        self.assertIn("implementation", result)
        self.assertIn("components", result)
        self.assertIn("build_id", result)
        self.assertEqual(result["code_quality"], "high")
    
    def test_builder_act_invalid_design(self):
        """Test that Builder refuses invalid designs."""
        result = self.builder.act({})
        self.assertEqual(result["status"], "refused")
        self.assertIn("reason", result)
    
    def test_builder_tracks_builds(self):
        """Test that Builder tracks created builds."""
        design1 = self.architect.act("Design 1")
        design2 = self.architect.act("Design 2")
        design3 = self.architect.act("Design 3")
        
        self.builder.act(design1)
        self.builder.act(design2)
        self.builder.act(design3)
        
        self.assertEqual(len(self.builder.builds), 3)
    
    def test_builder_implements_components(self):
        """Test that Builder implements all design components."""
        design = self.architect.act("Build microservices")
        result = self.builder.act(design)
        
        components = result["components"]
        self.assertIn("frontend", components)
        self.assertIn("backend", components)
        self.assertIn("database", components)
        self.assertIn("api", components)
    
    def test_builder_describe(self):
        """Test that Builder provides accurate metadata."""
        design = self.architect.act("Test design")
        self.builder.act(design)
        metadata = self.builder.describe()
        
        self.assertEqual(metadata["name"], "Builder")
        self.assertEqual(metadata["builds_created"], 1)
    
    def test_architect_to_builder_workflow(self):
        """Test end-to-end Architect -> Builder workflow."""
        # Architect designs
        design = self.architect.act("Build a scalable web application")
        self.assertEqual(design["status"], "designed")
        
        # Builder implements
        build = self.builder.act(design)
        self.assertEqual(build["status"], "built")
        self.assertEqual(build["design_id"], design["design_id"])

if __name__ == '__main__':
    unittest.main()