"""
Hello World Demo V2 - Using Real Orchestrator with Turing Tape
Demonstrates:
- Five-agent workflow with real run() methods
- Checkpoint/resume capability
- Normalized logging
- Progress tracking
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow.orchestrator import WorkflowOrchestrator
from workflow.tape import WorkflowTape
import json


def print_banner(text):
    """Print a nice banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def run_hello_world():
    """Run the Hello World workflow using the orchestrator."""
    
    print_banner("🚀 TEAM AGENT V2: Real Workflow with Turing Tape")
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(team_id="hello_world_team")
    
    # Define mission
    mission = "Build a Python program that prints 'Hello, World!' with proper documentation"
    print(f"📝 Mission: {mission}\n")
    
    # Execute workflow
    print("⚙️  Executing five-agent workflow...\n")
    
    try:
        results = orchestrator.execute_workflow(mission)
        
        print_banner("✅ WORKFLOW COMPLETED")
        
        # Show results
        print(f"🆔 Workflow ID: {results['workflow_id']}")
        print(f"\n📊 Progress:")
        progress = results['progress']
        print(f"   Total Stages: {progress['total_stages']}")
        print(f"   Completed: {progress['completed']}")
        print(f"   Progress: {progress['progress_percent']:.1f}%")
        
        print(f"\n🏗️  Architecture:")
        arch = results['results']['architect']
        print(f"   Strategy: {arch['strategy']}")
        print(f"   Components: {', '.join(arch['components'])}")
        
        print(f"\n🔨 Implementation:")
        impl = results['results']['builder']
        print(f"   Language: {impl['language']}")
        print(f"   Lines of Code: {impl['metadata']['lines_of_code']}")
        
        print(f"\n🔍 Quality Review:")
        review = results['results']['critic']
        print(f"   Quality Score: {review['quality_score']}/100")
        print(f"   Issues: {len(review['issues'])}")
        print(f"   Recommendation: {review['recommendation']}")
        
        print(f"\n⚖️  Governance:")
        gov = results['results']['governance']
        print(f"   Compliance Score: {gov['compliance_score']}/100")
        print(f"   Decision: {gov['decision']}")
        print(f"   Violations: {len(gov['violations'])}")
        
        print(f"\n📋 Final Record:")
        record = results['final_record']
        print(f"   Composite Score: {record['composite_score']['overall']}/100")
        print(f"   Status: {record['status']}")
        print(f"   Signature: {record['signature']['hash'][:16]}...")
        
        # Show generated code
        print_banner("📄 GENERATED CODE")
        print(impl['code'])
        print("=" * 80)
        
        # Show tape location
        print(f"\n💾 Workflow state saved to: data/tapes/{results['workflow_id']}.json")
        print(f"📝 Logs saved to: logs/")
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def resume_workflow_demo(workflow_id: str):
    """Demonstrate resuming a workflow from checkpoint."""
    
    print_banner(f"🔄 RESUMING WORKFLOW: {workflow_id}")
    
    # Load tape to show current state
    tape = WorkflowTape.load(workflow_id)
    if not tape:
        print(f"❌ Workflow {workflow_id} not found!")
        return
    
    print(f"📝 Mission: {tape.mission}")
    print(f"📊 Current Status: {tape.status}")
    print(f"🎯 Current Stage: {tape.current_stage}")
    
    progress = tape.get_progress()
    print(f"\n📈 Progress: {progress['completed']}/{progress['total_stages']} stages completed")
    
    # Show stage status
    print("\n📋 Stage Status:")
    for stage_name, checkpoint in tape.stages.items():
        status_icon = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌"
        }.get(checkpoint.status.value, "❓")
        print(f"   {status_icon} {stage_name}: {checkpoint.status.value}")
    
    # Resume if not complete
    if not tape.is_complete():
        print("\n⚙️  Resuming workflow...\n")
        orchestrator = WorkflowOrchestrator()
        results = orchestrator.execute_workflow(tape.mission, workflow_id)
        print(f"\n✅ Workflow resumed and completed!")
        return results
    else:
        print("\n✅ Workflow already complete!")
        return None


def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Team Agent Hello World Demo V2')
    parser.add_argument('--resume', type=str, help='Resume a workflow by ID')
    args = parser.parse_args()
    
    if args.resume:
        resume_workflow_demo(args.resume)
    else:
        results = run_hello_world()
        
        if results:
            workflow_id = results['workflow_id']
            print("\n" + "=" * 80)
            print("💡 TIP: You can resume this workflow later with:")
            print(f"   python examples/hello_world_v2.py --resume {workflow_id}")
            print("=" * 80 + "\n")


if __name__ == "__main__":
    main()