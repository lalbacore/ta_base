#!/usr/bin/env python3
"""
Quick test runner for capability system.
"""

import subprocess
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Run all capability tests."""
    print("=" * 60)
    print("  Running Capability System Tests")
    print("=" * 60)
    print()
    
    test_files = [
        "utils/tests/test_capabilities.py",
        "utils/tests/test_capability_registry.py",
        "utils/tests/test_dynamic_builder.py",
        "utils/tests/test_orchestrator_capabilities.py",
    ]
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"  Testing: {test_file}")
        print('='*60)
        
        # Run pytest with PYTHONPATH set
        result = subprocess.run(
            ["pytest", test_file, "-v"],
            env={**subprocess.os.environ, "PYTHONPATH": str(project_root)},
            capture_output=False
        )
        
        if result.returncode != 0:
            print(f"\n❌ Tests failed in {test_file}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("  ✅ ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()