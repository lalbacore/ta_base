"""
Demo: Team Agent workflow demonstration
Shows the five-agent pattern in action with mock data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.roles import (
    Architect,
    Builder,
    Critic,
    Governance,
    Recorder
)


def print_banner(text):
    """Print a nice banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def run_hello_world_workflow():
    """Run a complete workflow demonstration."""
    
    print_banner("🚀 TEAM AGENT DEMO: Five-Agent Workflow")
    
    # User request
    user_request = "Build a Python program that prints 'Hello, World!'"
    print(f"📝 User Request: {user_request}\n")
    
    # Stage 1: Architect
    print_banner("Stage 1: Architect - Designing the solution")
    architect = Architect()
    
    try:
        arch_result = architect.run(user_request)
        print(f"🏗️  Architect Output:\n{arch_result}\n")
    except Exception as e:
        print(f"⚠️  Architect returned: {e}")
        # Create mock architecture for demo
        arch_result = {
            "strategy": "Create a simple Python script with main function",
            "components": ["main function", "print statement", "docstring"],
            "architecture": "Single file Python module"
        }
        print(f"🏗️  Using mock architecture: {arch_result}\n")
    
    # Stage 2: Builder
    print_banner("Stage 2: Builder - Implementing the code")
    builder = Builder()
    
    try:
        build_result = builder.run(arch_result)
        print(f"🔨 Builder Output:\n{build_result}\n")
    except Exception as e:
        print(f"⚠️  Builder returned: {e}")
        # Create mock code for demo
        build_result = {
            "code": '''#!/usr/bin/env python3
"""
Hello World Program
A simple demonstration of Python output.
"""

def main():
    """Print Hello, World! to console."""
    print("Hello, World!")


if __name__ == "__main__":
    main()
''',
            "status": "built",
            "files": ["hello_world.py"]
        }
        print(f"🔨 Using mock code:\n{build_result['code']}\n")
    
    # Stage 3: Critic
    print_banner("Stage 3: Critic - Reviewing the implementation")
    critic = Critic()
    
    try:
        critic_result = critic.run(build_result)
        print(f"🔍 Critic Output:\n{critic_result}\n")
    except Exception as e:
        print(f"⚠️  Critic returned: {e}")
        # Create mock review for demo
        critic_result = {
            "quality_score": 95,
            "issues": [],
            "strengths": [
                "Clean structure",
                "Proper documentation",
                "Follows Python best practices"
            ],
            "recommendation": "approved"
        }
        print(f"🔍 Using mock review: {critic_result}\n")
    
    # Stage 4: Governance
    print_banner("Stage 4: Governance - Policy compliance check")
    governance = Governance()
    
    try:
        gov_result = governance.run(critic_result)
        print(f"⚖️  Governance Output:\n{gov_result}\n")
    except Exception as e:
        print(f"⚠️  Governance returned: {e}")
        # Create mock governance for demo
        gov_result = {
            "compliance_score": 100,
            "decision": "approved",
            "violations": [],
            "policies_checked": ["security", "quality", "documentation"]
        }
        print(f"⚖️  Using mock governance: {gov_result}\n")
    
    # Stage 5: Recorder
    print_banner("Stage 5: Recorder - Creating audit trail")
    recorder = Recorder()
    
    workflow_data = {
        "request": user_request,
        "architect": arch_result,
        "builder": build_result,
        "critic": critic_result,
        "governance": gov_result
    }
    
    try:
        record_result = recorder.run(workflow_data)
        print(f"📋 Recorder Output:\n{record_result}\n")
    except Exception as e:
        print(f"⚠️  Recorder returned: {e}")
        # Create mock record for demo
        import hashlib
        import json
        from datetime import datetime
        
        record_result = {
            "workflow_id": f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "signature": {
                "hash": hashlib.sha256(json.dumps(workflow_data).encode()).hexdigest()
            },
            "composite_score": {
                "overall": 97.5,
                "quality": 95,
                "compliance": 100
            },
            "status": "completed"
        }
        print(f"📋 Using mock record: {record_result}\n")
    
    # Final summary
    print_banner("📊 WORKFLOW SUMMARY")
    print(f"✅ Request: {user_request}")
    print(f"✅ Architecture: Designed ({len(arch_result.get('components', []))} components)")
    print(f"✅ Implementation: Built")
    print(f"✅ Quality Review: {critic_result.get('quality_score', 0)}/100")
    print(f"✅ Compliance: {gov_result.get('compliance_score', 0)}/100")
    print(f"✅ Decision: {gov_result.get('decision', 'N/A').upper()}")
    print(f"✅ Workflow ID: {record_result.get('workflow_id', 'N/A')}")
    print(f"✅ Composite Score: {record_result.get('composite_score', {}).get('overall', 0)}/100")
    
    if 'code' in build_result:
        print("\n" + "=" * 80)
        print("  FINAL OUTPUT - Hello World Program")
        print("=" * 80)
        print(build_result['code'])
        print("=" * 80 + "\n")
    
    return record_result


if __name__ == "__main__":
    try:
        workflow = run_hello_world_workflow()
        print("\n🎉 SUCCESS! Five-agent workflow demonstration completed!")
        print("✨ This shows the agent orchestration pattern.")
        print("💡 Next step: Wire up agents to actual LLMs for real code generation.\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()