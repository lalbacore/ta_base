"""
Quick Test - Minimal test to verify system is working.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.orchestrator import Orchestrator

print("Testing Team Agent...")
orchestrator = Orchestrator(output_dir="output")
results = orchestrator.execute("Build a simple hello world program")

final = results.get("final_record", {})
print(f"\n✅ Test {'PASSED' if final.get('status') == 'approved' else 'FAILED'}")
print(f"Score: {final.get('composite_score', 0)}/100")

artifacts = final.get("published_artifacts", {})
if artifacts.get("primary_code"):
    print(f"Code: {artifacts['primary_code']}")