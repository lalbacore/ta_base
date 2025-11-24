"""
Execute the original README.md mission to scaffold the team-agent framework.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.orchestrator import Orchestrator


def run_original_mission():
    """Run the mission defined in the root README."""
    
    mission_text = """
    Scaffold the core framework of team-agent, a modular AI agent system using Python.
    The system should support standalone agents and composable teams.
    
    Requirements:
    - Create BaseAgent class with __init__, evaluate_intent, act, record, describe methods
    - Create role map with architect, builder, critic, compliance, recorder agents
    - Each role should have intent, capabilities, and policy examples
    - Add comprehensive README with architecture and directory structure
    - Credit founding idea: Intent → Capability → Governance triangle
    """
    
    print("=" * 80)
    print("  ORIGINAL MISSION: Scaffold Team-Agent Framework")
    print("=" * 80)
    print()
    print("📋 Mission: Build the core team-agent framework")
    print()
    print("⚙️  Executing workflow...")
    print()
    
    # Execute with orchestrator
    orchestrator = Orchestrator(output_dir="output")
    results = orchestrator.execute(mission_text)
    
    # Display results
    print()
    print("=" * 80)
    print("  ✅ ORIGINAL MISSION COMPLETE")
    print("=" * 80)
    print()
    
    final_record = results.get('final_record', {})
    
    print(f"🆔 Workflow ID: {results.get('workflow_id', 'unknown')}")
    print(f"📊 Composite Score: {final_record.get('composite_score', 0)}/100")
    print(f"✅ Status: {final_record.get('status', 'unknown')}")
    print()
    
    # Show artifacts
    artifacts = final_record.get('published_artifacts', {})
    if artifacts:
        print("📦 Published Artifacts:")
        for name, path in artifacts.items():
            print(f"   • {name}: {path}")
        
        primary = artifacts.get("primary_code")
        if primary:
            print()
            print("▶️  To run the generated code:")
            print(f"   cd {Path(primary).parent}")
            print("   ./run.sh")
    
    print()


if __name__ == "__main__":
    run_original_mission()