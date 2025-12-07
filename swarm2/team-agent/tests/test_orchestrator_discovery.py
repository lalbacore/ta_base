
import sys
import os
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

from unittest.mock import MagicMock

from swarms.team_agent.orchestrator import Orchestrator

def test_discovery():
    print("Initializing Orchestrator to test discovery...")
    try:
        # Instantiate Orchestrator
        orch = Orchestrator(output_dir="./test_output")
        
        # Mock register_specialist to capture calls (since DB is broken)
        orch.agent_manager.register_specialist = MagicMock()
        
        # Trigger registration manually (since it runs in __init__ before we mocked)
        # Actually, we should mock BEFORE __init__ if possible, or just call the method again.
        # Calling the private method again is easiest to test logic.
        orch._register_specialist_agents()
        
        # Check calls
        calls = orch.agent_manager.register_specialist.call_args_list
        print(f"Register calls: {len(calls)}")
        
        found = False
        for call in calls:
            agent = call[0][0]
            print(f"Registered: {agent.name} ({agent.__class__.__name__})")
            if agent.name == "Test Python Specialist":
                found = True
                
        if found:
            print("SUCCESS: Test Python Specialist was discovered and loaded!")
        else:
            print("FAILURE: Test Agent NOT found in registration calls.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error initializing Orchestrator: {e}")
        # Print full traceback
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_discovery()
