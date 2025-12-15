
import unittest
import sys
import os
import importlib

# Add project root and notebook dirs to path for testing
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOTEBOOKS_DIR = os.path.join(PROJECT_ROOT, "notebooks")
INTEGRATION_DIR = os.path.join(NOTEBOOKS_DIR, "04_integration")
EVALUATOR_DIR = os.path.join(NOTEBOOKS_DIR, "02_evaluator")

sys.path.append(PROJECT_ROOT)
sys.path.append(NOTEBOOKS_DIR)
sys.path.append(INTEGRATION_DIR)
sys.path.append(EVALUATOR_DIR)

class TestProjectStructure(unittest.TestCase):
    
    def test_directories_exist(self):
        """Verify critical project directories exist."""
        self.assertTrue(os.path.exists(INTEGRATION_DIR), "Integration dir missing")
        self.assertTrue(os.path.exists(EVALUATOR_DIR), "Evaluator dir missing")
        
    def test_critical_files_exist(self):
        """Verify critical python files exist."""
        files = [
            os.path.join(INTEGRATION_DIR, "episode_wrapper.py"),
            os.path.join(EVALUATOR_DIR, "evaluator_job.py"),
            os.path.join(INTEGRATION_DIR, "mcp_a2a_example.py"),
        ]
        for f in files:
            self.assertTrue(os.path.exists(f), f"File missing: {f}")

    def test_import_episode_wrapper(self):
        """Verify episode_wrapper can be imported."""
        # We need to mock pyspark and mlflow for imports to pass without env
        mock_pyspark = unittest.mock.MagicMock()
        mock_sql = unittest.mock.MagicMock()
        mock_pyspark.sql = mock_sql
        mock_pyspark.sql.functions = unittest.mock.MagicMock()
        mock_pyspark.sql.types = unittest.mock.MagicMock()

        with unittest.mock.patch.dict(sys.modules, {
            'pyspark': mock_pyspark, 
            'pyspark.sql': mock_sql,
            'pyspark.sql.functions': mock_pyspark.sql.functions,
            'pyspark.sql.types': mock_pyspark.sql.types,
            'mlflow': unittest.mock.MagicMock()
        }):
            try:
                import episode_wrapper
            except ImportError as e:
                self.fail(f"Failed to import episode_wrapper: {e}")

    def test_import_evaluator_job(self):
        """Verify evaluator_job can be imported."""
        mock_pyspark = unittest.mock.MagicMock()
        mock_sql = unittest.mock.MagicMock()
        mock_pyspark.sql = mock_sql
        mock_pyspark.sql.functions = unittest.mock.MagicMock()
        mock_pyspark.sql.types = unittest.mock.MagicMock()

        with unittest.mock.patch.dict(sys.modules, {
            'pyspark': mock_pyspark,
            'pyspark.sql': mock_sql,
            'pyspark.sql.functions': mock_pyspark.sql.functions,
            'pyspark.sql.types': mock_pyspark.sql.types,
            'mlflow': unittest.mock.MagicMock()
        }):
            try:
                import evaluator_job
            except ImportError as e:
                self.fail(f"Failed to import evaluator_job: {e}")

if __name__ == '__main__':
    unittest.main()
