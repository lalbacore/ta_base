"""
Real-world test scenarios for Team Agent capabilities.
"""
from swarms.team_agent.orchestrator import Orchestrator
from swarms.team_agent.router import MissionRouter, RoutedOrchestrator


def scenario_1_simple_capability():
    """Scenario 1: Single specialized capability"""
    print("\n" + "="*60)
    print("SCENARIO 1: Simple HRT Guide Generation")
    print("="*60)
    
    o = Orchestrator(output_dir="./test_outputs/scenario1")
    result = o.execute("Generate comprehensive hormone replacement therapy guide")
    
    print(f"\n✓ Workflow ID: {result['workflow_id']}")
    print(f"✓ Capability Used: {result['final_record']['capability_used']}")
    print(f"✓ Artifacts: {len(result['final_record']['published_artifacts'])}")
    
    return result


def scenario_2_fallback():
    """Scenario 2: Fallback to generic builder"""
    print("\n" + "="*60)
    print("SCENARIO 2: Generic Mission (Fallback)")
    print("="*60)
    
    o = Orchestrator(output_dir="./test_outputs/scenario2")
    result = o.execute("Create a simple calculator application")
    
    print(f"\n✓ Workflow ID: {result['workflow_id']}")
    print(f"✓ Capability Used: {result['final_record']['capability_used']}")
    
    return result


def scenario_3_parallel():
    """Scenario 3: Parallel capability execution"""
    print("\n" + "="*60)
    print("SCENARIO 3: Parallel Capabilities")
    print("="*60)
    
    from swarms.team_agent.capabilities.document_generator import DocumentGenerator
    from swarms.team_agent.capabilities.medical.hrt_guide import HRTGuideCapability
    
    o = Orchestrator(output_dir="./test_outputs/scenario3")
    o.capability_registry.register(DocumentGenerator())
    
    router = MissionRouter(o.capability_registry)
    routed = RoutedOrchestrator(o, router)
    
    result = routed.execute_with_routing(
        "Generate medical documentation with multiple format options"
    )
    
    print(f"\n✓ Strategy: {result['routing_analysis']['strategy']}")
    print(f"✓ Capabilities Found: {len(result['routing_analysis']['capabilities'])}")
    
    return result


def scenario_4_complex():
    """Scenario 4: Complex multi-phase mission"""
    print("\n" + "="*60)
    print("SCENARIO 4: Complex Mission Decomposition")
    print("="*60)
    
    o = Orchestrator(output_dir="./test_outputs/scenario4")
    router = MissionRouter(o.capability_registry)
    routed = RoutedOrchestrator(o, router)
    
    result = routed.execute_with_routing(
        "Build a complete full stack medical records management system"
    )
    
    print(f"\n✓ Complexity: {result['routing_analysis']['complexity']}")
    print(f"✓ Requires Decomposition: {result['routing_analysis']['requires_decomposition']}")
    
    if 'subtasks' in result:
        print(f"✓ Subtasks Created: {len(result['subtasks'])}")
    
    return result


def scenario_5_comparison():
    """Scenario 5: Compare multiple approaches"""
    print("\n" + "="*60)
    print("SCENARIO 5: Comparison (Parallel Execution)")
    print("="*60)
    
    o = Orchestrator(output_dir="./test_outputs/scenario5")
    router = MissionRouter(o.capability_registry)
    
    analysis = router.analyze_mission(
        "Compare different approaches to implementing REST API authentication"
    )
    
    print(f"\n✓ Strategy Detected: {analysis['strategy']}")
    print(f"✓ Can Parallelize: {analysis['can_parallelize']}")
    print(f"✓ Suggested Workflow: {analysis['workflow']['phases']}")
    
    return analysis


if __name__ == "__main__":
    print("\n🚀 Team Agent - Real-World Test Scenarios")
    print("="*60)
    
    try:
        scenario_1_simple_capability()
        scenario_2_fallback()
        scenario_3_parallel()
        scenario_4_complex()
        scenario_5_comparison()
        
        print("\n" + "="*60)
        print("✅ All scenarios completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()