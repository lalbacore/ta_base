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
    from swarms.team_agent.trusted_orchestrator import TrustedOrchestrator
except ImportError as e:
    print(f"FATAL ERROR: Could not import TrustedOrchestrator from ta_base. {e}")
    sys.exit(1)

# Initialize FastMCP
mcp = FastMCP("Zero-Trust Artifact Orchestrator")

@mcp.tool()
def run_mission(mission_prompt: str) -> str:
    """
    Executes a mission prompt natively through the Tripartite Zero-Trust framework.
    Rather than simply executing arbitrary code, this tool mathematically forces the framework
    to physically issue a Trusted AI Artifact manifest that is verifiably signed by the Governance chain.
    """
    try:
        orchestrator = TrustedOrchestrator()
        result = orchestrator.execute(mission_prompt)
        
        result_json = str(result)
        return f"Mission Completed under Mathematical Restraint.\n\n[Trusted AI Artifact Manifest Generated]:\n{result_json}"
        
    except Exception as e:
        return f"Mission Execution Failed at the Tripartite level: {str(e)}"

if __name__ == "__main__":
    # Standard stdio wrapping for standard MCP clients.
    mcp.run(transport='stdio')
