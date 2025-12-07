
import pytest
import sys
import os

# Define test files
TEST_FILES = [
    "backend/utils/tests/test_swarm_node.py",
    "backend/utils/tests/test_writing_crypto.py",
    "backend/utils/tests/test_roles_crypto.py",
    "backend/utils/tests/test_dynamic_orchestration.py"
]

def run_suite():
    print("="*60)
    print("RUNNING SWARM ARCHITECTURE FULL VERIFICATION SUITE")
    print("="*60)
    
    failures = []
    
    for test_file in TEST_FILES:
        print(f"\n---> Running {test_file}...")
        exit_code = os.system(f"PYTHONPATH=. python {test_file}")
        
        if exit_code != 0:
            failures.append(test_file)
            print(f"[FAILED] {test_file}")
        else:
            print(f"[PASSED] {test_file}")
            
    print("\n" + "="*60)
    if failures:
        print(f"SUITE COMPLETED WITH {len(failures)} FAILURES")
        for f in failures:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("SUITE COMPLETED SUCCESSFULLY - ALL SYSTEMS GREEN")
        sys.exit(0)

if __name__ == "__main__":
    run_suite()
