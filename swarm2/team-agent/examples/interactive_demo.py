"""
Interactive Demo - Chat-style interaction with Team Agent.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.orchestrator import Orchestrator


def print_header():
    """Print welcome header."""
    print()
    print("=" * 80)
    print("  🤖 Team Agent - Interactive Demo")
    print("=" * 80)
    print()
    print("Welcome! I can help you build Python applications.")
    print()
    print("Commands:")
    print("  - Type your mission (e.g., 'Build a TODO list app')")
    print("  - Type 'quit' or 'exit' to end")
    print("  - Type 'help' for examples")
    print()


def show_examples():
    """Show example missions."""
    print()
    print("📚 Example Missions:")
    print()
    print("  1. Build a calculator with basic operations")
    print("  2. Create a TODO list application")
    print("  3. Build a simple file organizer")
    print("  4. Create a password generator")
    print("  5. Build a CSV data analyzer")
    print()


def main():
    """Run interactive demo."""
    print_header()
    
    orchestrator = Orchestrator(output_dir="output")
    
    while True:
        try:
            # Get mission
            mission = input("🎯 Mission: ").strip()
            
            if not mission:
                continue
            
            # Handle commands
            if mission.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if mission.lower() == 'help':
                show_examples()
                continue
            
            # Execute mission
            print()
            print("⚙️  Executing workflow...")
            print()
            
            results = orchestrator.execute(mission)
            
            # Show results
            print()
            print("=" * 80)
            print("  ✅ Complete!")
            print("=" * 80)
            print()
            
            final_record = results.get("final_record", {})
            
            print(f"📊 Score: {final_record.get('composite_score', 0)}/100")
            print(f"✅ Status: {final_record.get('status', 'unknown')}")
            
            # Show artifacts
            artifacts = final_record.get("published_artifacts", {})
            if artifacts:
                primary = artifacts.get("primary_code")
                if primary:
                    print(f"\n📦 Code saved to: {primary}")
                    print(f"▶️  Run with: cd {Path(primary).parent} && ./run.sh")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()