
import sys
import os
from pathlib import Path
import logging
from unittest.mock import MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# Configure logging to stdout
logging.basicConfig(level=logging.ERROR) # Lower noise

from swarms.team_agent.orchestrator import Orchestrator

def verify_all_specialists():
    print("Verifying discovery of migrated specialists...")
    try:
        orch = Orchestrator(output_dir="./test_output")
        
        # Mock register_specialist again to capture calls and avoid DB writes
        orch.agent_manager.register_specialist = MagicMock()
        
        # Trigger dynamic registration
        orch._register_specialist_agents()
        
        # Collect registered agent names
        registered_names = []
        for call in orch.agent_manager.register_specialist.call_args_list:
            agent = call[0][0]
            registered_names.append(agent.name)
            
        print(f"Discovered Agents: {registered_names}")
        
        expected_agents = [
            "Legal Specialist",
            "Writing Specialist", 
            "AWS Cloud Specialist",
            "Azure Cloud Specialist",
            "GCP Cloud Specialist",
            "OCI Cloud Specialist",
            "Test Python Specialist" # From earlier test
        ]
        
        missing = []
        for expected in expected_agents:
            if expected not in registered_names:
                missing.append(expected)
                
        if missing:
            print(f"FAILURE: Missing agents: {missing}")
            # Don't exit 1 yet, try to see why.
            # It might be because Test Specialist was in a different DB or overwritten?
            # Actually, registry is persistent sqlite, so it should be there.
        else:
            print("SUCCESS: All specialists discovered!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_all_specialists()
