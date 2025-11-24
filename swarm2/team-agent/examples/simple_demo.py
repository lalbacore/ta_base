"""
Simple Demo - Quick test of the Team Agent workflow.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.orchestrator import Orchestrator


def main():
    """Run a simple demo."""
    print("=" * 80)
    print("  Team Agent - Simple Demo")
    print("=" * 80)
    print()
    
    # Create orchestrator
    orchestrator = Orchestrator(output_dir="output")
    
    # Define a simple mission
    mission = "Build a Python calculator with add, subtract, multiply, and divide"
    
    print(f"📝 Mission: {mission}")
    print()
    print("⚙️  Executing workflow...")
    print()
    
    # Execute
    results = orchestrator.execute(mission)
    
    # Show results
    print()
    print("=" * 80)
    print("  ✅ Workflow Complete!")
    print("=" * 80)
    print()
    
    final_record = results.get("final_record", {})
    
    print(f"🆔 Workflow ID: {results.get('workflow_id', 'unknown')}")
    print(f"📊 Composite Score: {final_record.get('composite_score', 0)}/100")
    print(f"✅ Status: {final_record.get('status', 'unknown')}")
    
    # Show artifacts
    artifacts = final_record.get("published_artifacts", {})
    if artifacts:
        print()
        print("📦 Published Artifacts:")
        for name, path in artifacts.items():
            print(f"   • {name}: {path}")
        
        # Show how to run
        primary = artifacts.get("primary_code")
        if primary:
            print()
            print("▶️  To run the generated code:")
            print(f"   cd {Path(primary).parent}")
            print("   ./run.sh")
    
    print()


if __name__ == "__main__":
    main()