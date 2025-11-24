"""
Batch Demo - Process multiple missions in sequence.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.orchestrator import Orchestrator


SAMPLE_MISSIONS = [
    "Build a simple calculator",
    "Create a TODO list app",
    "Build a password generator",
]


def main():
    """Run batch processing demo."""
    print("=" * 80)
    print("  Team Agent - Batch Processing Demo")
    print("=" * 80)
    print()
    print(f"Processing {len(SAMPLE_MISSIONS)} missions...")
    print()
    
    orchestrator = Orchestrator(output_dir="output")
    results_summary = []
    
    for i, mission in enumerate(SAMPLE_MISSIONS, 1):
        print(f"\n{'─' * 80}")
        print(f"Mission {i}/{len(SAMPLE_MISSIONS)}: {mission}")
        print('─' * 80)
        
        try:
            results = orchestrator.execute(mission)
            
            final_record = results.get("final_record", {})
            
            results_summary.append({
                "mission": mission,
                "workflow_id": results.get("workflow_id"),
                "score": final_record.get("composite_score", 0),
                "status": final_record.get("status", "unknown"),
                "artifacts": final_record.get("published_artifacts", {})
            })
            
            print(f"\n✅ Complete - Score: {final_record.get('composite_score', 0)}/100")
            
        except Exception as e:
            print(f"\n❌ Failed: {e}")
            results_summary.append({
                "mission": mission,
                "status": "failed",
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("  📊 Batch Summary")
    print("=" * 80)
    print()
    
    for i, result in enumerate(results_summary, 1):
        status_emoji = "✅" if result.get("status") == "approved" else "❌"
        print(f"{i}. {status_emoji} {result['mission']}")
        print(f"   Score: {result.get('score', 'N/A')}/100")
        print(f"   Workflow: {result.get('workflow_id', 'N/A')}")
        
        artifacts = result.get("artifacts", {})
        if artifacts.get("primary_code"):
            print(f"   Code: {artifacts['primary_code']}")
        
        print()


if __name__ == "__main__":
    main()