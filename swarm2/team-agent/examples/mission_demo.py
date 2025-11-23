"""
Mission-Based Demo - Demonstrates enhanced workflow with mission files.
Shows how to execute missions with stage-specific instructions.
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.orchestrator import Orchestrator  # Changed this line


def print_banner(text, char="="):
    """Print a nice banner."""
    print("\n" + char * 80)
    print(f"  {text}")
    print(char * 80 + "\n")


def print_detailed_results(results: dict):
    """Print detailed workflow results."""
    
    print_banner("✅ WORKFLOW COMPLETED")
    
    # Basic info
    print(f"🆔 Workflow ID: {results['workflow_id']}")
    print(f"📝 Mission: {results['mission']}")
    
    # Progress
    print(f"\n📊 Progress:")
    progress = results['progress']
    print(f"   Total Stages: {progress['total_stages']}")
    print(f"   Completed: {progress['completed']}")
    print(f"   Progress: {progress['progress_percent']:.1f}%")
    
    # Architecture
    print(f"\n🏗️  Architecture:")
    arch = results['results']['architect']
    print(f"   Complexity: {arch['structure']['complexity']}")
    print(f"   Pattern: {arch['structure']['pattern']}")
    print(f"   Components: {len(arch['components'])}")
    print(f"   Estimated Files: {arch['estimated_files']}")
    for comp in arch['components']:
        print(f"     • {comp}")
    
    # Implementation
    print(f"\n🔨 Implementation:")
    impl = results['results']['builder']
    meta = impl['metadata']
    print(f"   Language: {impl['language']}")
    print(f"   Lines of Code: {meta['lines_of_code']}")
    print(f"   Functions: {meta['functions']}")
    print(f"   Classes: {meta['classes']}")
    print(f"   Imports: {meta['imports']}")
    print(f"   Docstrings: {meta['docstrings']}")
    
    # Quality Review
    print(f"\n🔍 Quality Review:")
    review = results['results']['critic']
    details = review['details']
    scores = details['scores']
    print(f"   Overall Quality: {review['quality_score']}/100")
    print(f"   Breakdown:")
    print(f"     • Structure: {scores['structure']}/100")
    print(f"     • Documentation: {scores['documentation']}/100")
    print(f"     • Security: {scores['security']}/100")
    print(f"     • Maintainability: {scores['maintainability']}/100")
    print(f"     • Performance: {scores['performance']}/100")
    print(f"   Issues: {len(review['issues'])}")
    if review['issues']:
        for issue in review['issues']:
            print(f"     ⚠️  {issue}")
    print(f"   Strengths: {len(review['strengths'])}")
    for strength in review['strengths']:
        print(f"     ✅ {strength}")
    print(f"   Recommendation: {review['recommendation']}")
    
    # Governance
    print(f"\n⚖️  Governance:")
    gov = results['results']['governance']
    print(f"   Compliance Score: {gov['compliance_score']}/100")
    print(f"   Decision: {gov['decision']}")
    print(f"   Policies Checked: {', '.join(gov['policies_checked'])}")
    print(f"   Violations: {len(gov['violations'])}")
    if gov['violations']:
        for violation in gov['violations']:
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(violation['severity'], '⚪')
            print(f"     {severity_emoji} {violation['policy']}: {violation.get('threshold', 'N/A')} (actual: {violation.get('actual', 'N/A')})")
    
    # Final Record
    print(f"\n📋 Final Record:")
    record = results['final_record']
    comp_score = record['composite_score']
    print(f"   Composite Score: {comp_score['overall']}/100")
    print(f"     • Quality: {comp_score['quality']}/100")
    print(f"     • Compliance: {comp_score['compliance']}/100")
    print(f"   Status: {record['status']}")
    print(f"   Requires Remediation: {record['requires_remediation']}")
    print(f"   Signature: {record['signature']['hash'][:32]}...")
    
    # Acceptance Criteria
    if 'acceptance_met' in results and results['acceptance_met']:
        print(f"\n✅ Acceptance Criteria:")
        for criterion, met in results['acceptance_met'].items():
            status = "✅ PASS" if met else "❌ FAIL"
            print(f"   {status} {criterion}")
    
    # Generated Code
    print_banner("📄 GENERATED CODE")
    print(impl['code'])
    print("=" * 80)
    
    # Artifacts
    print(f"\n💾 Artifacts:")
    print(f"   Workflow Tape: data/tapes/{results['workflow_id']}.json")
    print(f"   Logs: logs/workflow_{results['workflow_id']}.jsonl")
    print(f"   Files to Create: {', '.join(impl['files'])}")
    
    # Display published artifacts
    published = record.get("published_artifacts", {})
    if published:
        print("\n📦 Published Artifacts:")
        for artifact_type, path in published.items():
            artifact_name = artifact_type.replace('_', ' ').title()
            print(f"   {artifact_name}: {path}")
        
        # Show quick access commands
        primary_code = published.get("primary_code", "")
        if primary_code:
            print(f"\n▶️  Quick Run:")
            print(f"   cd {Path(primary_code).parent}")
            print(f"   ./run.sh")


def run_simple_mission():
    """Run a simple text-based mission."""
    print_banner("🚀 SIMPLE MISSION: Text Input", "=")
    
    orchestrator = Orchestrator(team_id="simple_demo")
    mission_text = "Build a Python program that prints 'Hello, World!' with proper documentation"
    
    print(f"📝 Mission: {mission_text}\n")
    print("⚙️  Executing workflow...\n")
    
    results = orchestrator.execute_mission(mission_text)
    print_detailed_results(results)


def load_mission_yaml(yaml_path: str) -> Optional[Dict[str, Any]]:
    """Load mission from YAML file."""
    try:
        with open(yaml_path, 'r') as file:
            mission = yaml.safe_load(file)
            return mission
    except Exception as e:
        print(f"Error loading YAML file {yaml_path}: {e}")
        return None


def display_mission_details(mission: Dict[str, Any]):
    """Display mission details."""
    print("📋 Mission Details:")
    print(f"   ID: {mission.get('mission', {}).get('id', 'N/A')}")
    print(f"   Name: {mission.get('mission', {}).get('name', 'N/A')}")
    print(f"   Description: {mission.get('mission', {}).get('description', 'N/A')}")
    print(f"   Stages: {len(mission.get('stages', []))}")
    
    # Display each stage with details
    for i, stage in enumerate(mission.get('stages', []), start=1):
        print(f"\n Stage {i}:")
        print(f"   Name: {stage.get('name', 'N/A')}")
        print(f"   Description: {stage.get('description', 'N/A')}")
        print(f"   Agent: {stage.get('agent', 'N/A')}")
        print(f"   Timeout: {stage.get('timeout', 'N/A')}")
        print(f"   Retries: {stage.get('retries', 'N/A')}")
        print(f"   On Success: {stage.get('on_success', 'N/A')}")
        print(f"   On Failure: {stage.get('on_failure', 'N/A')}")
        print(f"   Skip Conditions: {stage.get('skip_conditions', 'N/A')}")
        print(f"   Continue On: {stage.get('continue_on', 'N/A')}")
        print(f"   Break On: {stage.get('break_on', 'N/A')}")
    
    print()


def run_yaml_mission(yaml_path: str):
    """Run mission from YAML file."""
    mission = load_mission_yaml(yaml_path)
    
    if not mission:
        return
    
    # Display mission details
    display_mission_details(mission)
    
    # Create orchestrator
    orchestrator = Orchestrator(output_dir="output")  # Changed this line
    
    print("\n⚙️  Executing workflow...")
    print()
    
    # Execute - pass the mission description
    mission_text = mission.get("mission", {}).get("description", "")
    results = orchestrator.execute(mission_text)  # Changed this line
    
    # Display results
    display_results(results)


def display_results(results: Dict[str, Any]):
    """Display workflow results."""
    print("\n" + "=" * 80)
    print("  ✅ Workflow Complete!")
    print("=" * 80)
    print()
    
    final_record = results.get("final_record", {})
    
    # Basic info
    print(f"🆔 Workflow ID: {results.get('workflow_id', 'unknown')}")
    print(f"📊 Composite Score: {final_record.get('composite_score', 0):.1f}/100")
    print(f"   • Quality Score: {final_record.get('quality_score', 0):.1f}/100")
    print(f"   • Compliance Score: {final_record.get('compliance_score', 0):.1f}/100")
    print()
    
    # Status
    status = final_record.get("status", "unknown")
    status_emoji = "✅" if status == "approved" else "⚠️"
    print(f"{status_emoji} Status: {status.upper()}")
    
    if final_record.get("requires_remediation"):
        print("   ⚠️  Requires remediation")
    
    print()
    
    # Metadata
    metadata = final_record.get("metadata", {})
    if metadata:
        print("📈 Metrics:")
        
        impl_metrics = metadata.get("implementation_metrics", {})
        if impl_metrics:
            print(f"   • Lines of Code: {impl_metrics.get('lines_of_code', 0)}")
            print(f"   • Functions: {impl_metrics.get('functions', 0)}")
            print(f"   • Classes: {impl_metrics.get('classes', 0)}")
        
        if metadata.get("review_issues_count") is not None:
            print(f"   • Review Issues: {metadata.get('review_issues_count', 0)}")
        
        print()
    
    # Published artifacts
    artifacts = final_record.get("published_artifacts", {})
    if artifacts:
        print("📦 Published Artifacts:")
        for artifact_type, path in artifacts.items():
            artifact_name = artifact_type.replace('_', ' ').title()
            print(f"   • {artifact_name}: {path}")
        
        # Show quick access commands
        primary_code = artifacts.get("primary_code", "")
        if primary_code:
            print(f"\n▶️  Quick Run:")
            print(f"   cd {Path(primary_code).parent}")
            print(f"   ./run.sh")
    
    # Tape location
    tape_location = final_record.get("tape_location")
    if tape_location:
        print(f"\n📼 Workflow Tape: {tape_location}")
    
    print()


def list_missions():
    """List available mission files."""
    print_banner("📁 AVAILABLE MISSIONS", "=")
    
    missions_dir = Path(__file__).parent.parent / "missions"
    if not missions_dir.exists():
        print("❌ No missions directory found!")
        return
    
    yaml_files = list(missions_dir.glob("*.yaml"))
    
    if not yaml_files:
        print("❌ No mission files found!")
        return
    
    print(f"Found {len(yaml_files)} mission(s):\n")
    
    for yaml_file in yaml_files:
        try:
            mission = Mission.from_yaml(str(yaml_file))
            info = mission.data['mission']
            print(f"📄 {yaml_file.name}")
            print(f"   ID: {info['id']}")
            print(f"   Name: {info['name']}")
            print(f"   Description: {info['description'][:60]}...")
            print()
        except Exception as e:
            print(f"⚠️  {yaml_file.name} - Error loading: {e}\n")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(
        description='Team Agent Mission Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run simple text mission
  python examples/mission_demo.py --simple
  
  # Run YAML mission
  python examples/mission_demo.py --yaml missions/calculator.yaml
  
  # List available missions
  python examples/mission_demo.py --list
        """
    )
    
    parser.add_argument('--simple', action='store_true', 
                       help='Run simple text-based mission')
    parser.add_argument('--yaml', type=str, metavar='PATH',
                       help='Run mission from YAML file')
    parser.add_argument('--list', action='store_true',
                       help='List available mission files')
    
    args = parser.parse_args()
    
    if args.list:
        list_missions()
    elif args.yaml:
        run_yaml_mission(args.yaml)
    elif args.simple:
        run_simple_mission()
    else:
        # Default: run simple mission
        run_simple_mission()
        
        # Show tip
        print("\n" + "=" * 80)
        print("💡 TIP: Try running a YAML mission:")
        print("   python examples/mission_demo.py --yaml missions/calculator.yaml")
        print("\n   Or list available missions:")
        print("   python examples/mission_demo.py --list")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()