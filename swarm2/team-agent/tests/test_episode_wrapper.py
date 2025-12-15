
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "notebooks", "04_integration"))
sys.path.append(os.path.join(PROJECT_ROOT, "notebooks", "02_evaluator"))

# Mock dependencies globablly for the test module
mock_pyspark = MagicMock()
mock_sql = MagicMock()
mock_pyspark.sql = mock_sql
mock_pyspark.sql.types = MagicMock()
mock_pyspark.sql.functions = MagicMock()

sys.modules["pyspark"] = mock_pyspark
sys.modules["pyspark.sql"] = mock_sql
sys.modules["pyspark.sql.types"] = mock_pyspark.sql.types
sys.modules["pyspark.sql.functions"] = mock_pyspark.sql.functions
sys.modules["mlflow"] = MagicMock()

# Import module under test
import episode_wrapper

class TestEpisodeWrapper(unittest.TestCase):
    
    def setUp(self):
        self.mock_spark = MagicMock()
        self.transaction = episode_wrapper.EpisodeTransaction(
            spark=self.mock_spark, 
            workflow_type="mcp", 
            transaction_id="test-123"
        )
        # Mock pandas globally for the tests
        self.mock_pd = MagicMock()
        sys.modules["pandas"] = self.mock_pd

        # Mock evaluator_job globally
        self.mock_evaluator_job = MagicMock()
        sys.modules["evaluator_job"] = self.mock_evaluator_job

    def test_initialization(self):
        """Test wrapper initializes with correct state."""
        self.assertEqual(self.transaction.episode_id, "test-123")
        self.assertEqual(self.transaction.workflow_type, "mcp")
        self.assertEqual(self.transaction.steps, [])
        self.assertEqual(self.transaction.status, "running")

    def test_add_step(self):
        """Test adding a step."""
        step_id = self.transaction.add_step(
            task_name="test_task",
            prompt="do this",
            output="ok",
            tokens_in=10,
            tokens_out=20
        )
        
        self.assertEqual(step_id, 0)
        self.assertEqual(len(self.transaction.steps), 1)
        self.assertEqual(self.transaction.steps[0]["task_name"], "test_task")
        self.assertEqual(self.transaction.steps[0]["tokens_in"], 10)

    def test_commit(self):
        """Test commit uses Pandas DataFrame creation (Serverless workaround)."""
        # Setup mock return for spark.createDataFrame
        mock_df = MagicMock()
        self.mock_spark.createDataFrame.return_value = mock_df
        
        # Setup pandas dataframe mock
        self.mock_pd.DataFrame.return_value = "mock_pandas_df"
        
        # Call commit
        self.transaction.commit()
        
        # Assertions
        # 1. Verify pd.DataFrame was called (proving we use the workaround)
        self.assertTrue(self.mock_pd.DataFrame.called, "Must convert to Pandas DataFrame first")
        
        # 2. Verify spark.createDataFrame was called with the pandas df
        self.mock_spark.createDataFrame.assert_called_with("mock_pandas_df", schema=self.transaction.episode_struct)
        
        # 3. Verify write was called
        # commit calls createDataFrame twice (episodes, steps)
        # We just verify it was called at least once with the right format
        self.assertTrue(mock_df.write.format.called)
        mock_df.write.format.assert_called_with("delta")

    def test_evaluate_calls_job(self):
        """Test that evaluate() instantiates EvaluatorJob and calls evaluate_episode."""
        # Setup mock Evaluator class on the mocked module
        MockEvaluatorClass = MagicMock()
        self.mock_evaluator_job.EpisodeEvaluator = MockEvaluatorClass
        
        # Setup instance and return value
        mock_eval_instance = MockEvaluatorClass.return_value
        mock_eval_instance.evaluate_episode.return_value = {
            "scrutability_level": "scrutable",
            "scrutability_score": 0.9,
            "computes": True
        }
        
        # Call evaluate
        result = self.transaction.evaluate()
        
        # Assertions
        MockEvaluatorClass.assert_called_with(self.mock_spark)
        mock_eval_instance.evaluate_episode.assert_called_with("test-123")
        self.assertTrue(result["computes"])

if __name__ == '__main__':
    unittest.main()
