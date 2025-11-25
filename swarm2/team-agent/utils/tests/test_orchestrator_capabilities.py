"""
Integration tests for Orchestrator with capability system.
"""
from pathlib import Path

from swarms.team_agent.orchestrator import Orchestrator
from swarms.team_agent.roles.base_role import BaseRole
from utils.capabilities import HRTGuideCapability


class TestOrchestratorCapabilities:
    """Test orchestrator integration with capabilities."""

    def test_hrt_capability_used(self, tmp_path):
        """Test that HRT capability is used for hormone therapy missions."""
        o = Orchestrator(output_dir=str(tmp_path))

        mission = "Generate hormone replacement therapy guide"
        result = o.execute(mission)

        # Verify HRT capability was used
        capability_used = result["final_record"]["capability_used"]
        assert capability_used == "hrt_guide_generator"

    def test_artifacts_written(self, tmp_path):
        """Test that capability artifacts are written to disk."""
        o = Orchestrator(output_dir=str(tmp_path))

        mission = "Generate hormone replacement therapy guide"
        result = o.execute(mission)

        # Check artifacts were published
        artifacts = result["final_record"]["published_artifacts"]
        assert len(artifacts) > 0

        # Verify files exist
        for artifact_path in artifacts.values():
            assert Path(artifact_path).exists()


# Mock roles for testing (if needed)
class MockArchitect(BaseRole):
    def run(self, context):
        return {"components": ["test"]}


class MockCritic(BaseRole):
    def run(self, context):
        return {"issues": [], "score": 10}
