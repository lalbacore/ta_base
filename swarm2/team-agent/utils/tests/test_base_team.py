import unittest
from base.base_team import BaseTeam

class TestBaseTeam(unittest.TestCase):
    
    def setUp(self):
        self.team = BaseTeam()
    
    def test_team_initialization(self):
        """Test that BaseTeam initializes with all 5 agents."""
        self.assertIsNotNone(self.team.architect)
        self.assertIsNotNone(self.team.builder)
        self.assertIsNotNone(self.team.critic)
        self.assertIsNotNone(self.team.governance)
        self.assertIsNotNone(self.team.recorder)
    
    def test_team_run_valid_request(self):
        """Test that team successfully processes a valid request."""
        result = self.team.run("Build a secure API")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("workflow_id", result)
        self.assertIn("result", result)
        self.assertIn("stages", result)
    
    def test_team_run_invalid_request(self):
        """Test that team rejects invalid requests."""
        result = self.team.run("")
        self.assertEqual(result["status"], "failed")
        self.assertIn("reason", result)
        
        result2 = self.team.run(None)
        self.assertEqual(result2["status"], "failed")
    
    def test_team_workflow_has_all_stages(self):
        """Test that successful workflow includes all 5 stages."""
        result = self.team.run("Build a system")
        
        self.assertEqual(result["status"], "success")
        stages = result["stages"]
        
        self.assertIn("architect", stages)
        self.assertIn("builder", stages)
        self.assertIn("critic", stages)
        self.assertIn("governance", stages)
        self.assertIn("recorder", stages)
        
        for stage_name, stage in stages.items():
            self.assertEqual(stage["status"], "complete")
    
    def test_team_records_workflow_history(self):
        """Test that team tracks workflow history."""
        self.team.run("Build system 1")
        self.team.run("Build system 2")
        self.team.run("Build system 3")
        
        history = self.team.get_workflow_history()
        self.assertEqual(history["total_workflows"], 3)
        self.assertEqual(history["successful"], 3)
    
    def test_team_provides_agent_stats(self):
        """Test that team provides agent statistics."""
        self.team.run("Build a system")
        
        stats = self.team.get_agent_stats()
        
        self.assertIn("architect", stats)
        self.assertIn("builder", stats)
        self.assertIn("critic", stats)
        self.assertIn("governance", stats)
        self.assertIn("recorder", stats)
        
        self.assertEqual(stats["architect"]["designs_created"], 1)
        self.assertEqual(stats["builder"]["builds_created"], 1)
        self.assertEqual(stats["critic"]["reviews_conducted"], 1)
        self.assertEqual(stats["governance"]["decisions_made"], 1)
        self.assertEqual(stats["recorder"]["records_created"], 1)
    
    def test_team_result_has_signature(self):
        """Test that team result includes cryptographic signature."""
        result = self.team.run("Build a system")
        
        record = result["result"]
        self.assertIn("signature", record)
        signature = record["signature"]
        self.assertIn("algorithm", signature)
        self.assertIn("hash", signature)
        self.assertEqual(signature["algorithm"], "SHA256")
    
    def test_team_result_has_audit_trail(self):
        """Test that team result includes complete audit trail."""
        result = self.team.run("Build a system")
        
        record = result["result"]
        self.assertIn("audit_log", record)
        audit = record["audit_log"]
        
        self.assertIn("design_phase", audit)
        self.assertIn("build_phase", audit)
        self.assertIn("review_phase", audit)
        self.assertIn("governance_phase", audit)
    
    def test_team_multiple_requests_independent(self):
        """Test that multiple requests are processed independently."""
        result1 = self.team.run("Request 1")
        result2 = self.team.run("Request 2")
        result3 = self.team.run("Request 3")
        
        self.assertNotEqual(result1["workflow_id"], result2["workflow_id"])
        self.assertNotEqual(result2["workflow_id"], result3["workflow_id"])
        self.assertEqual(result1["request"], "Request 1")
        self.assertEqual(result2["request"], "Request 2")
        self.assertEqual(result3["request"], "Request 3")
    
    def test_team_result_exports_ready(self):
        """Test that team result is ready for export to multiple systems."""
        result = self.team.run("Build a system")
        
        record = result["result"]
        exports = record["export_ready"]
        
        self.assertIn("siem_export", exports)
        self.assertIn("a2a_export", exports)
        self.assertIn("mcp_export", exports)
        self.assertIn("blockchain_export", exports)
        
        for export_type in exports.values():
            self.assertTrue(export_type["ready"])
    
    def test_team_composite_score_in_result(self):
        """Test that team result includes composite score."""
        result = self.team.run("Build a system")
        
        record = result["result"]
        composite = record["composite_score"]
        
        self.assertIn("overall", composite)
        self.assertIn("stages", composite)
        self.assertGreater(composite["overall"], 0)
        self.assertLessEqual(composite["overall"], 100)
    
    def test_team_workflow_summary_shows_approval(self):
        """Test that workflow summary shows final approval status."""
        result = self.team.run("Build a system")
        
        record = result["result"]
        summary = record["workflow_summary"]
        
        self.assertIn("final_status", summary)
        self.assertEqual(summary["final_status"], "APPROVED")
    
    def test_team_handles_empty_string(self):
        """Test that team gracefully handles empty string requests."""
        result = self.team.run("")
        self.assertEqual(result["status"], "failed")
    
    def test_team_handles_whitespace_only(self):
        """Test that team gracefully handles whitespace-only requests."""
        result = self.team.run("   ")
        # This will get through to architect but architect should reject it
        self.assertIn(result["status"], ["failed", "rejected"])
    
    def test_team_workflow_id_format(self):
        """Test that workflow IDs follow expected format."""
        result = self.team.run("Build a system")
        workflow_id = result["workflow_id"]
        
        self.assertTrue(workflow_id.startswith("workflow_"))
        self.assertEqual(len(result["workflow_id"].split("_")), 2)
    
    def test_team_request_preserved_in_result(self):
        """Test that original request is preserved in result."""
        request = "Build a secure microservices platform"
        result = self.team.run(request)
        
        self.assertEqual(result["request"], request)
    
    def test_team_stats_after_multiple_runs(self):
        """Test that agent stats accumulate correctly."""
        for i in range(5):
            self.team.run(f"Request {i}")
        
        stats = self.team.get_agent_stats()
        
        self.assertEqual(stats["architect"]["designs_created"], 5)
        self.assertEqual(stats["builder"]["builds_created"], 5)
        self.assertEqual(stats["critic"]["reviews_conducted"], 5)
        self.assertEqual(stats["governance"]["decisions_made"], 5)
        self.assertEqual(stats["recorder"]["records_created"], 5)
    
    def test_team_history_summary(self):
        """Test that workflow history summary is accurate."""
        for i in range(7):
            self.team.run(f"Request {i}")
        
        history = self.team.get_workflow_history()
        
        self.assertEqual(history["total_workflows"], 7)
        self.assertEqual(history["successful"], 7)
        self.assertEqual(history["rejected"], 0)
        self.assertEqual(history["failed"], 0)

if __name__ == '__main__':
    unittest.main()