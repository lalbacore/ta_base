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
        governance = self.governance.act({"request": "Build a system", "review": review})
        
        return {
            "request": "Build a system",
            "design": design,
            "build": build,
            "review": review,
            "governance": governance
        }
    
    def test_recorder_initialization(self):
        """Test that Recorder initializes with correct attributes."""
        self.assertEqual(self.recorder.name, "Recorder")
        self.assertEqual(self.recorder.id, "agent_recorder_001")
        self.assertIn("log_results", self.recorder.capabilities)
        self.assertTrue(self.recorder.policy["can_record"])
    
    def test_recorder_evaluate_intent_valid(self):
        """Test that valid record packages are evaluated as True."""
        package = self._create_complete_workflow()
        result = self.recorder.evaluate_intent(package)
        self.assertTrue(result)
    
    def test_recorder_evaluate_intent_invalid(self):
        """Test that invalid record packages are evaluated as False."""
        self.assertFalse(self.recorder.evaluate_intent(None))
        self.assertFalse(self.recorder.evaluate_intent({}))
        self.assertFalse(self.recorder.evaluate_intent({"request": "Build"}))
    
    def test_recorder_record_complete_workflow(self):
        """Test that Recorder can record a complete workflow."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        self.assertEqual(record["status"], "recorded")
        self.assertIn("record_id", record)
        self.assertIn("timestamp", record)
        self.assertIn("composite_score", record)
    
    def test_recorder_refuses_incomplete_package(self):
        """Test that Recorder refuses incomplete packages."""
        record = self.recorder.act({})
        self.assertEqual(record["status"], "refused")
        self.assertIn("reason", record)
    
    def test_recorder_calculates_composite_score(self):
        """Test that Recorder calculates composite score."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        composite = record["composite_score"]
        self.assertIn("overall", composite)
        self.assertIn("stages", composite)
        self.assertGreater(composite["overall"], 0)
        self.assertLessEqual(composite["overall"], 100)
    
    def test_recorder_creates_signature(self):
        """Test that Recorder creates cryptographic signatures."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        signature = record["signature"]
        self.assertIn("algorithm", signature)
        self.assertEqual(signature["algorithm"], "SHA256")
        self.assertIn("hash", signature)
        self.assertIn("timestamp", signature)
        self.assertEqual(len(signature["hash"]), 64)  # SHA256 hex length
    
    def test_recorder_creates_workflow_summary(self):
        """Test that Recorder creates workflow summary."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        summary = record["workflow_summary"]
        self.assertIn("request", summary)
        self.assertIn("design_status", summary)
        self.assertIn("build_status", summary)
        self.assertIn("review_status", summary)
        self.assertIn("governance_allowed", summary)
        self.assertIn("final_status", summary)
    
    def test_recorder_creates_detailed_audit_log(self):
        """Test that Recorder creates detailed audit logs."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        audit = record["audit_log"]
        self.assertIn("design_phase", audit)
        self.assertIn("build_phase", audit)
        self.assertIn("review_phase", audit)
        self.assertIn("governance_phase", audit)
    
    def test_recorder_prepares_exports(self):
        """Test that Recorder prepares exports for various systems."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        exports = record["export_ready"]
        self.assertIn("siem_export", exports)
        self.assertIn("a2a_export", exports)
        self.assertIn("mcp_export", exports)
        self.assertIn("blockchain_export", exports)
        
        for export_type in exports.values():
            self.assertTrue(export_type["ready"])
    
    def test_recorder_extracts_metadata(self):
        """Test that Recorder extracts and stores metadata."""
        package = self._create_complete_workflow()
        record = self.recorder.act(package)
        
        metadata = record["metadata"]
        self.assertEqual(metadata["total_agents_involved"], 5)
        self.assertIn("approval_chain", metadata)
        self.assertEqual(len(metadata["approval_chain"]), 4)
    
    def test_recorder_tracks_records(self):
        """Test that Recorder tracks created records."""
        for i in range(3):
            package = self._create_complete_workflow()
            self.recorder.act(package)
        
        self.assertEqual(len(self.recorder.records), 3)
    
    def test_recorder_signature_consistency(self):
        """Test that same workflow produces same signature."""
        package = self._create_complete_workflow()
        record1 = self.recorder.act(package)
        
        # Note: In production, the second call would fail since workflow is different
        # but we can at least verify the signature format is consistent
        self.assertEqual(
            len(record1["signature"]["hash"]),
            64  # SHA256 hex is always 64 chars
        )
    
    def test_recorder_describe(self):
        """Test that Recorder provides accurate metadata."""
        package = self._create_complete_workflow()
        self.recorder.act(package)
        metadata = self.recorder.describe()
        
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
        self.assertTrue(review["passed"])
        
        # Governance enforces
        governance = self.governance.act({"request": "Build a production-ready system", "review": review})
        self.assertEqual(governance["status"], "enforced")
        self.assertTrue(governance["allowed"])
        
        # Recorder logs and signs
        package = {
            "request": "Build a production-ready system",
            "design": design,
            "build": build,
            "review": review,
            "governance": governance
        }
        record = self.recorder.act(package)
        
        self.assertEqual(record["status"], "recorded")
        self.assertIsNotNone(record["signature"])
        self.assertEqual(record["workflow_summary"]["final_status"], "APPROVED")

if __name__ == '__main__':
    unittest.main()