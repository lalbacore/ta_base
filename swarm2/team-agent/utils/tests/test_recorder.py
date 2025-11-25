"""
Tests for Recorder agent.

These tests focus on behavior:
- Does Recorder produce a record with status and ID?
- Does Recorder track its records?
- Does the end-to-end workflow complete?
"""

import unittest
from swarms.team_agent.roles import Architect, Builder, Critic, Governance, Recorder


class TestRecorder(unittest.TestCase):
    
    def setUp(self):
        self.recorder = Recorder()
        self.architect = Architect()
        self.builder = Builder()
        self.critic = Critic()
        self.governance = Governance()
    
    def _create_complete_workflow(self):
        """Helper to create a complete workflow package."""
        design = self.architect.act("Build a system")
        build = self.builder.act(design)
        review = self.critic.act({"design": design, "build": build})
        governance = self.governance.act(review)
        
        return {
            "request": "Build a system",
            "design": design,
            "build": build,
            "review": review,
            "governance": governance
        }
    
    def test_recorder_initialization(self):
        """Test that Recorder initializes correctly."""
        self.assertEqual(self.recorder.name, "Recorder")
        # Behavioral: should have some capabilities
        self.assertIsInstance(self.recorder.capabilities, list)
        self.assertGreater(len(self.recorder.capabilities), 0)
    
    def test_recorder_records_workflow(self):
        """Test that Recorder can record a workflow."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        # Behavioral: did we get a record?
        self.assertEqual(record["status"], "recorded")
        self.assertIn("record_id", record)
    
    def test_recorder_handles_empty_package(self):
        """Test that Recorder handles empty packages."""
        record = self.recorder.act({})
        
        # Behavioral: should return some status
        self.assertIn("status", record)
    
    def test_recorder_calculates_composite_score(self):
        """Test that Recorder calculates a composite score."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        # Behavioral: should have some form of score
        self.assertIn("composite_score", record)
        score = record["composite_score"]
        if isinstance(score, dict):
            self.assertIn("overall", score)
        else:
            self.assertIsInstance(score, (int, float))
    
    def test_recorder_creates_signature(self):
        """Test that Recorder creates a signature."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        # Behavioral: should have a signature with hash
        self.assertIn("signature", record)
        sig = record["signature"]
        self.assertIn("hash", sig)
        self.assertIn("algorithm", sig)
    
    def test_recorder_creates_detailed_audit_log(self):
        """Test that Recorder creates an audit log."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        # Behavioral: should have audit info
        self.assertIn("audit_log", record)
    
    def test_recorder_tracks_records(self):
        """Test that Recorder tracks created records."""
        for i in range(3):
            package = self._create_complete_workflow()
            self.recorder.act(package)
        
        # Behavioral: records should be tracked
        self.assertEqual(len(self.recorder.records), 3)
    
    def test_recorder_describe(self):
        """Test that Recorder provides metadata."""
        package = self._create_complete_workflow()
        self.recorder.act(package)
        metadata = self.recorder.describe()
        
        # Behavioral: metadata should reflect state
        self.assertEqual(metadata["name"], "Recorder")
        self.assertEqual(metadata["records_created"], 1)
    
    def test_complete_end_to_end_workflow(self):
        """Test complete end-to-end workflow with all 5 agents."""
        # Architect designs
        design = self.architect.act("Build a production-ready system")
        self.assertEqual(design["status"], "designed")
        
        # Builder implements
        build = self.builder.act(design)
        self.assertEqual(build["status"], "built")
        
        # Critic reviews
        review = self.critic.act({"design": design, "build": build})
        self.assertEqual(review["status"], "reviewed")
        
        # Governance enforces
        governance = self.governance.act(review)
        self.assertEqual(governance["status"], "enforced")
        
        # Recorder logs
        package = {
            "request": "Build a production-ready system",
            "design": design,
            "build": build,
            "review": review,
            "governance": governance
        }
        record = self.recorder.act(package)
        
        # Behavioral: workflow should complete
        self.assertEqual(record["status"], "recorded")
        self.assertIn("signature", record)


if __name__ == '__main__':
    unittest.main()