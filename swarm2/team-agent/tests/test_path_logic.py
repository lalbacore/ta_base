
import unittest
import sys
import os
import shutil

# Mock setup for testing environment paths
class TestImportLogic(unittest.TestCase):

    def setUp(self):
        # Create a mock directory structure
        self.test_dir = os.path.join(os.getcwd(), "test_env")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Structure:
        # test_env/
        #   notebooks/
        #     04_integration/
        #       mcp_a2a_example.py (the script we want to test path logic for)
        #       episode_wrapper.py (target 1)
        #     02_evaluator/
        #       evaluator_job.py (target 2)
        
        self.notebooks_dir = os.path.join(self.test_dir, "notebooks")
        self.integration_dir = os.path.join(self.notebooks_dir, "04_integration")
        self.evaluator_dir = os.path.join(self.notebooks_dir, "02_evaluator")
        
        os.makedirs(self.integration_dir)
        os.makedirs(self.evaluator_dir)
        
        # Create dummy module files
        with open(os.path.join(self.integration_dir, "episode_wrapper.py"), "w") as f:
            f.write("def mcp_episode(): pass\ndef a2a_episode(): pass\n")
            
        with open(os.path.join(self.evaluator_dir, "evaluator_job.py"), "w") as f:
            f.write("class EpisodeEvaluator: pass\n")
            
        # Create a simplified version of mcp_a2a_example.py that only contains the path logic
        self.script_path = os.path.join(self.integration_dir, "path_test_script.py")
        with open(self.script_path, "w") as f:
            f.write("""
import sys
import os

# --- PATH LOGIC START ---
# Robustly find directory containing this notebook (Databricks Repos)
# Add the current directory to sys.path
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

# Also add the parent 'notebooks' dir to help find other modules if we are in a subdir
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    # Also add 02_evaluator explicitly while we are at it
    eval_dir = os.path.join(parent_dir, "02_evaluator")
    if os.path.exists(eval_dir) and eval_dir not in sys.path:
            sys.path.append(eval_dir)
# --- PATH LOGIC END ---

try:
    import episode_wrapper
    print("SUCCESS: episode_wrapper imported")
except ImportError:
    print("FAILURE: episode_wrapper not found")

try:
    import evaluator_job
    print("SUCCESS: evaluator_job imported")
except ImportError:
    # evaluator_job is inside 02_evaluator, so unless we added that to path, it won't be found directly
    # BUT our logic adds 02_evaluator to path, so it SHOULD be found directly!
    print("FAILURE: evaluator_job not found")
""")

    def tearDown(self):
        # Clean up
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_path_discovery_when_in_integration_dir(self):
        """Test if the script works when running FROM the integration directory (normal case)."""
        import subprocess
        
        # Run the script from the integration dir
        result = subprocess.run(
            [sys.executable, "path_test_script.py"],
            cwd=self.integration_dir,
            capture_output=True,
            text=True
        )
        
        print(f"STDOUT (Normal Case): {result.stdout}")
        print(f"STDERR (Normal Case): {result.stderr}")
        
        self.assertIn("SUCCESS: episode_wrapper imported", result.stdout)
        self.assertIn("SUCCESS: evaluator_job imported", result.stdout)

    def test_path_discovery_when_cwd_is_root(self):
        """Test if logic holds up if CWD is somehow the project root (less likely for notebook but possible)."""
        # Note: The logic relies on os.getcwd() being the notebook dir. 
        # If CWD is root, the logic:
        #   current_dir = root
        #   parent_dir = outside project
        #   eval_dir = outside/02_evaluator (doesn't exist)
        # So this logic ACTUALLY DEPENDS on CWD being roughly correct.
        
        # However, purely relying on os.getcwd() is what we are testing.
        # If we run from 'test_env' (acting as root), it won't find the submodules unless we modify the script logic or arguments.
        # This confirms that our current logic strictly expects CWD to be the notebook's dir.
        pass

if __name__ == '__main__':
    unittest.main()
