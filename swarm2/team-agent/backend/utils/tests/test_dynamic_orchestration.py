
import pytest
import os
from swarms.team_agent.orchestrator import Orchestrator
from swarms.team_agent.core.message import AgentMessage
from swarms.team_agent.core.dispatcher import MessageDispatcher

class TestDynamicOrchestration:
    
    def test_dispatcher_init(self):
        orch = Orchestrator(output_dir="./test_output")
        assert isinstance(orch.dispatcher, MessageDispatcher)
        # Orchestrator should register itself
        assert orch.id in orch.dispatcher.registry
        
    def test_message_flow(self):
        """Test full dynamic execution flow with a mock mission."""
        orch = Orchestrator(output_dir="./test_output")
        
        # This will trigger the _execute_workflow which now uses messaging
        result = orch.execute("Test dynamic orchestration flow for a python script")
        
        # Verify result structure
        assert result["workflow_id"] is not None
        assert result["final_record"] is not None
        
        # Verify architecture output (result of message exchange)
        assert "architecture" in result["final_record"]
        assert result["final_record"]["architecture"]["status"] == "designed"

if __name__ == "__main__":
    t = TestDynamicOrchestration()
    t.test_dispatcher_init()
    t.test_message_flow()
    print("Dynamic Orchestration Tests Passed")
