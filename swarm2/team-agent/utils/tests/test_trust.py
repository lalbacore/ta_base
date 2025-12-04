"""
Tests for Agent Trust Scoring System.

Tests reputation tracking, trust score calculation, event recording,
and CLI integration.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from swarms.team_agent.crypto import (
    AgentReputationTracker,
    EventType,
    TrustMetrics
)


class TestAgentReputationTracker(unittest.TestCase):
    """Test Agent Reputation Tracker core functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_trust.db"
        self.tracker = AgentReputationTracker(db_path=self.db_path)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_tracker(self):
        """Test creating reputation tracker."""
        self.assertIsNotNone(self.tracker)
        self.assertTrue(self.db_path.exists())

    def test_register_agent(self):
        """Test registering a new agent."""
        result = self.tracker.register_agent("test-agent")
        self.assertTrue(result)

        # Registering again should return False
        result = self.tracker.register_agent("test-agent")
        self.assertFalse(result)

    def test_get_agent_metrics_new_agent(self):
        """Test getting metrics for newly registered agent."""
        self.tracker.register_agent("test-agent")
        metrics = self.tracker.get_agent_metrics("test-agent")

        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.agent_id, "test-agent")
        self.assertEqual(metrics.total_operations, 0)
        self.assertEqual(metrics.trust_score, 100.0)
        self.assertEqual(metrics.security_incidents, 0)

    def test_get_agent_metrics_nonexistent(self):
        """Test getting metrics for non-existent agent."""
        metrics = self.tracker.get_agent_metrics("nonexistent")
        self.assertIsNone(metrics)

    def test_record_operation_success(self):
        """Test recording successful operation."""
        self.tracker.record_event(
            "test-agent",
            EventType.OPERATION_SUCCESS,
            response_time=0.5
        )

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.total_operations, 1)
        self.assertEqual(metrics.successful_operations, 1)
        self.assertEqual(metrics.success_rate, 100.0)
        self.assertEqual(metrics.trust_score, 100.0)

    def test_record_operation_failure(self):
        """Test recording failed operation."""
        self.tracker.record_event(
            "test-agent",
            EventType.OPERATION_FAILURE
        )

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.total_operations, 1)
        self.assertEqual(metrics.failed_operations, 1)
        self.assertEqual(metrics.failure_rate, 100.0)

    def test_record_operation_error(self):
        """Test recording error operation."""
        self.tracker.record_event(
            "test-agent",
            EventType.OPERATION_ERROR
        )

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.total_operations, 1)
        self.assertEqual(metrics.error_operations, 1)
        self.assertEqual(metrics.error_rate, 100.0)

    def test_record_security_incident(self):
        """Test recording security incident."""
        self.tracker.record_event(
            "test-agent",
            EventType.SECURITY_INCIDENT,
            metadata={"reason": "unauthorized access"}
        )

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.security_incidents, 1)
        # Trust score should be reduced
        self.assertLess(metrics.trust_score, 100.0)

    def test_record_certificate_revoked(self):
        """Test recording certificate revocation."""
        self.tracker.record_event(
            "test-agent",
            EventType.CERTIFICATE_REVOKED
        )

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.certificate_revocations, 1)
        self.assertEqual(metrics.security_incidents, 1)

    def test_record_policy_violation(self):
        """Test recording policy violation."""
        self.tracker.record_event(
            "test-agent",
            EventType.POLICY_VIOLATION
        )

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.policy_violations, 1)
        self.assertEqual(metrics.security_incidents, 1)


class TestTrustScoreCalculation(unittest.TestCase):
    """Test trust score calculation logic."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_trust.db"
        self.tracker = AgentReputationTracker(db_path=self.db_path)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_perfect_score(self):
        """Test perfect trust score with all successful operations."""
        # Record 10 successful operations
        for _ in range(10):
            self.tracker.record_event(
                "perfect-agent",
                EventType.OPERATION_SUCCESS
            )

        metrics = self.tracker.get_agent_metrics("perfect-agent")
        self.assertEqual(metrics.success_rate, 100.0)
        self.assertEqual(metrics.error_rate, 0.0)
        self.assertEqual(metrics.trust_score, 100.0)

    def test_mixed_operations(self):
        """Test trust score with mixed operations."""
        # 7 successes, 2 failures, 1 error
        for _ in range(7):
            self.tracker.record_event("mixed-agent", EventType.OPERATION_SUCCESS)
        for _ in range(2):
            self.tracker.record_event("mixed-agent", EventType.OPERATION_FAILURE)
        self.tracker.record_event("mixed-agent", EventType.OPERATION_ERROR)

        metrics = self.tracker.get_agent_metrics("mixed-agent")
        self.assertEqual(metrics.total_operations, 10)
        self.assertEqual(metrics.success_rate, 70.0)
        self.assertEqual(metrics.error_rate, 10.0)

        # Score should be between 0 and 100
        self.assertGreater(metrics.trust_score, 0.0)
        self.assertLess(metrics.trust_score, 100.0)

    def test_security_incidents_reduce_score(self):
        """Test that security incidents reduce trust score."""
        # Perfect operations
        for _ in range(10):
            self.tracker.record_event("secure-agent", EventType.OPERATION_SUCCESS)

        score_before = self.tracker.get_agent_metrics("secure-agent").trust_score

        # Record security incident
        self.tracker.record_event("secure-agent", EventType.SECURITY_INCIDENT)

        score_after = self.tracker.get_agent_metrics("secure-agent").trust_score

        self.assertLess(score_after, score_before)

    def test_multiple_security_incidents(self):
        """Test multiple security incidents severely reduce score."""
        # Record mostly failed operations
        for _ in range(2):
            self.tracker.record_event("bad-agent", EventType.OPERATION_SUCCESS)
        for _ in range(8):
            self.tracker.record_event("bad-agent", EventType.OPERATION_FAILURE)

        # Record multiple security incidents
        for _ in range(8):
            self.tracker.record_event("bad-agent", EventType.SECURITY_INCIDENT)

        metrics = self.tracker.get_agent_metrics("bad-agent")
        self.assertEqual(metrics.security_incidents, 8)
        # Score should be significantly reduced (low success rate + high incidents)
        self.assertLess(metrics.trust_score, 50.0)

    def test_score_calculation_weights(self):
        """Test trust score with custom weights."""
        # Create tracker with custom weights
        custom_weights = {
            'success_rate': 0.50,
            'error_rate': 0.25,
            'security': 0.15,
            'uptime': 0.10,
        }
        tracker = AgentReputationTracker(
            db_path=self.temp_dir / "custom_weights.db",
            weights=custom_weights
        )

        # Record operations
        for _ in range(8):
            tracker.record_event("custom-agent", EventType.OPERATION_SUCCESS)
        for _ in range(2):
            tracker.record_event("custom-agent", EventType.OPERATION_ERROR)

        metrics = tracker.get_agent_metrics("custom-agent")
        # Should have a trust score calculated with custom weights
        self.assertGreater(metrics.trust_score, 0.0)
        self.assertLessEqual(metrics.trust_score, 100.0)


class TestAgentMetrics(unittest.TestCase):
    """Test TrustMetrics calculations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_trust.db"
        self.tracker = AgentReputationTracker(db_path=self.db_path)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        # 7 successes out of 10 operations
        for _ in range(7):
            self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS)
        for _ in range(3):
            self.tracker.record_event("test-agent", EventType.OPERATION_FAILURE)

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.success_rate, 70.0)

    def test_error_rate_calculation(self):
        """Test error rate calculation."""
        # 3 errors out of 10 operations
        for _ in range(7):
            self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS)
        for _ in range(3):
            self.tracker.record_event("test-agent", EventType.OPERATION_ERROR)

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.error_rate, 30.0)

    def test_failure_rate_calculation(self):
        """Test failure rate calculation."""
        # 2 failures out of 10 operations
        for _ in range(8):
            self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS)
        for _ in range(2):
            self.tracker.record_event("test-agent", EventType.OPERATION_FAILURE)

        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertEqual(metrics.failure_rate, 20.0)

    def test_average_response_time(self):
        """Test average response time calculation."""
        # Record operations with different response times
        self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS, response_time=0.5)
        self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS, response_time=1.0)
        self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS, response_time=0.75)

        metrics = self.tracker.get_agent_metrics("test-agent")
        # Average should be (0.5 + 1.0 + 0.75) / 3 = 0.75
        self.assertAlmostEqual(metrics.average_response_time, 0.75, places=2)


class TestAgentManagement(unittest.TestCase):
    """Test agent management operations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_trust.db"
        self.tracker = AgentReputationTracker(db_path=self.db_path)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_list_all_agents(self):
        """Test listing all agents."""
        # Register multiple agents
        for i in range(5):
            self.tracker.register_agent(f"agent-{i}")

        agents = self.tracker.list_all_agents()
        self.assertEqual(len(agents), 5)

        # Should be sorted by trust score (descending)
        for i in range(len(agents) - 1):
            self.assertGreaterEqual(agents[i].trust_score, agents[i + 1].trust_score)

    def test_list_agents_sorted_by_score(self):
        """Test that agents are sorted by trust score."""
        # Create agents with different scores
        self.tracker.record_event("good-agent", EventType.OPERATION_SUCCESS)
        self.tracker.record_event("bad-agent", EventType.OPERATION_ERROR)
        self.tracker.record_event("bad-agent", EventType.SECURITY_INCIDENT)

        agents = self.tracker.list_all_agents()
        self.assertEqual(len(agents), 2)
        # Good agent should be first (higher score)
        self.assertEqual(agents[0].agent_id, "good-agent")
        self.assertEqual(agents[1].agent_id, "bad-agent")
        self.assertGreater(agents[0].trust_score, agents[1].trust_score)

    def test_delete_agent(self):
        """Test deleting an agent."""
        self.tracker.register_agent("test-agent")
        self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS)

        # Verify agent exists
        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertIsNotNone(metrics)

        # Delete agent
        result = self.tracker.delete_agent("test-agent")
        self.assertTrue(result)

        # Verify agent is gone
        metrics = self.tracker.get_agent_metrics("test-agent")
        self.assertIsNone(metrics)

    def test_delete_nonexistent_agent(self):
        """Test deleting non-existent agent."""
        result = self.tracker.delete_agent("nonexistent")
        self.assertFalse(result)

    def test_get_statistics(self):
        """Test getting system statistics."""
        # Create multiple agents with various events
        for i in range(3):
            for _ in range(5):
                self.tracker.record_event(f"agent-{i}", EventType.OPERATION_SUCCESS)

        self.tracker.record_event("agent-1", EventType.SECURITY_INCIDENT)

        stats = self.tracker.get_statistics()

        self.assertEqual(stats['total_agents'], 3)
        self.assertEqual(stats['total_operations'], 15)
        self.assertEqual(stats['total_security_incidents'], 1)
        self.assertGreater(stats['average_trust_score'], 0.0)
        self.assertLessEqual(stats['average_trust_score'], 100.0)


class TestTrustHistory(unittest.TestCase):
    """Test trust score history tracking."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_trust.db"
        self.tracker = AgentReputationTracker(db_path=self.db_path)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_trust_history_recorded(self):
        """Test that trust score history is recorded."""
        # Record events that change trust score
        self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS)
        self.tracker.record_event("test-agent", EventType.OPERATION_ERROR)
        self.tracker.record_event("test-agent", EventType.SECURITY_INCIDENT)

        history = self.tracker.get_trust_history("test-agent")

        # Should have history records (one per event as score changes)
        self.assertGreater(len(history), 0)

        # Each record should have required fields
        for record in history:
            self.assertIn("timestamp", record)
            self.assertIn("trust_score", record)
            self.assertIn("success_rate", record)
            self.assertIn("error_rate", record)

    def test_trust_history_limit(self):
        """Test limiting trust history results."""
        # Record many events
        for _ in range(20):
            self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS)

        history = self.tracker.get_trust_history("test-agent", limit=5)
        self.assertLessEqual(len(history), 5)

    def test_trust_history_empty(self):
        """Test getting history for agent with no history."""
        self.tracker.register_agent("test-agent")
        history = self.tracker.get_trust_history("test-agent")
        self.assertEqual(len(history), 0)


class TestEventHistory(unittest.TestCase):
    """Test event history tracking."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_trust.db"
        self.tracker = AgentReputationTracker(db_path=self.db_path)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_recent_events(self):
        """Test getting recent events."""
        # Record various events
        self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS)
        self.tracker.record_event("test-agent", EventType.OPERATION_FAILURE)
        self.tracker.record_event("test-agent", EventType.SECURITY_INCIDENT,
                                 metadata={"reason": "test"})

        events = self.tracker.get_recent_events("test-agent")

        self.assertEqual(len(events), 3)

        # Events should be in reverse chronological order (most recent first)
        # Most recent event was security incident
        self.assertEqual(events[0]["event_type"], EventType.SECURITY_INCIDENT.value)

    def test_recent_events_with_metadata(self):
        """Test events with metadata."""
        metadata = {"key": "value", "num": 42}
        self.tracker.record_event("test-agent", EventType.SECURITY_INCIDENT,
                                 metadata=metadata)

        events = self.tracker.get_recent_events("test-agent")

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["metadata"], metadata)

    def test_recent_events_limit(self):
        """Test limiting recent events."""
        # Record many events
        for i in range(20):
            self.tracker.record_event("test-agent", EventType.OPERATION_SUCCESS)

        events = self.tracker.get_recent_events("test-agent", limit=5)
        self.assertEqual(len(events), 5)


class TestIntegration(unittest.TestCase):
    """Test full workflow integration."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_trust.db"
        self.tracker = AgentReputationTracker(db_path=self.db_path)

    def tearDown(self):
        """Clean up."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_full_agent_lifecycle(self):
        """Test complete agent lifecycle."""
        agent_id = "test-agent"

        # Register
        self.tracker.register_agent(agent_id)

        # Record various operations
        for _ in range(10):
            self.tracker.record_event(agent_id, EventType.OPERATION_SUCCESS, response_time=0.5)
        for _ in range(2):
            self.tracker.record_event(agent_id, EventType.OPERATION_ERROR)
        self.tracker.record_event(agent_id, EventType.SECURITY_INCIDENT)

        # Check metrics
        metrics = self.tracker.get_agent_metrics(agent_id)
        self.assertEqual(metrics.total_operations, 12)
        self.assertEqual(metrics.successful_operations, 10)
        self.assertEqual(metrics.error_operations, 2)
        self.assertEqual(metrics.security_incidents, 1)

        # Check history
        history = self.tracker.get_trust_history(agent_id)
        self.assertGreater(len(history), 0)

        # Check events
        events = self.tracker.get_recent_events(agent_id)
        self.assertEqual(len(events), 13)  # 10 + 2 + 1

        # Delete
        result = self.tracker.delete_agent(agent_id)
        self.assertTrue(result)

        # Verify deleted
        metrics = self.tracker.get_agent_metrics(agent_id)
        self.assertIsNone(metrics)


if __name__ == "__main__":
    unittest.main()
