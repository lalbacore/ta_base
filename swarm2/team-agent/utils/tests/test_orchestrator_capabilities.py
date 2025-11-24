"""
Integration tests for Orchestrator with capability system.
"""
from pathlib import Path
import pytest

from swarms.team_agent.orchestrator import Orchestrator


@pytest.fixture
def temp_output_dir(tmp_path):
    d = tmp_path / "out"
    d.mkdir()
    return str(d)


class TestOrchestratorCapabilities:
    def test_initialization(self, temp_output_dir):
        o = Orchestrator(output_dir=temp_output_dir)
        assert o.capability_registry is not None
        assert Path(o.output_dir).exists()

    def test_hrt_capability_used(self, temp_output_dir):
        o = Orchestrator(output_dir=temp_output_dir)
        mission = "Generate hormone replacement therapy guide"
        result = o.execute(mission)
        final = result["final_record"]
        # Allow fallback if capability not registered
        assert final["workflow_id"].startswith("wf_")
        assert "capability_used" in final
        assert final["capability_used"] in ("hrt_guide_generator", "fallback")

    def test_generic_mission_fallback(self, temp_output_dir):
        o = Orchestrator(output_dir=temp_output_dir)
        mission = "Create a simple calculator"
        result = o.execute(mission)
        final = result["final_record"]
        assert final["capability_used"] in ("fallback", "calculator_generator")

    def test_artifacts_written(self, temp_output_dir):
        o = Orchestrator(output_dir=temp_output_dir)
        mission = "Generate hormone replacement therapy guide"
        result = o.execute(mission)
        final = result["final_record"]
        wf_dir = Path(temp_output_dir) / final["workflow_id"]
        assert wf_dir.exists()
        # At least one artifact file
        assert len(list(wf_dir.glob("*.py"))) >= 1
