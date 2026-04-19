import sys
import os

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("FATAL ERROR: The Anthropic `mcp` Python SDK is required. Please run 'pip install mcp'")
    sys.exit(1)

# Ensure the ta_base module is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from swarms.team_agent.orchestrator import Orchestrator
except ImportError as e:
    print(f"FATAL ERROR: Could not import Orchestrator from ta_base. {e}")
    sys.exit(1)

# Initialize FastMCP
mcp = FastMCP("Team Agent Orchestrator")

@mcp.tool()
def run_mission(mission_prompt: str) -> str:
    """
    Executes a high-level mission prompt by securely deploying the Team Agent Multi-Agent Orchestrator.
    This natively wakes up specialized autonomous agents (Architects, Builders, Cloud Specialists) 
    who will collaborate, execute workflows, and cryptographically log them to fulfill the mission_prompt.
    """
    try:
        orchestrator = Orchestrator()
        result = orchestrator.execute(mission_prompt)
        
        return f"Mission Completed Successfully.\n\n[Orchestrator Result Blob]:\n{result}"
        
    except Exception as e:
        return f"Mission Execution Failed at the Orchestrator level: {str(e)}"

if __name__ == "__main__":
    # If run as a python file directly, FastMCP defaults to standard stdio for any MCP-compliant client.
    # E.g. Claude Desktop testing.
    mcp.run(transport='stdio')
