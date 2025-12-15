# Databricks Notebook: Unit Tests for Scrutability Logic
# Runs locally on the driver, verifying core logic without Spark overhead where possible.

import unittest
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# Add relevant paths
sys.path.append(os.path.abspath("../02_evaluator"))
sys.path.append(os.path.abspath("../04_integration"))

# Mock Spark Session for testing
class MockSparkSession:
    def createDataFrame(self, data, schema=None):
        return MockDataFrame(data)
        
class MockDataFrame:
    def __init__(self, data):
        if isinstance(data, pd.DataFrame):
            self.data = data.to_dict('records')
        else:
            self.data = data
            
    def collect(self):
        # Convert dicts to objects with attributes
        class Row:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
            def __getitem__(self, item):
                return getattr(self, item)
                
        return [Row(**d) for d in self.data]
        
    def write(self):
        return self
        
    def format(self, *args): return self
    def mode(self, *args): return self
    def option(self, *args): return self
    def saveAsTable(self, *args): pass


class TestScrutabilityLogic(unittest.TestCase):
    
    def setUp(self):
        # Import the evaluator class (we might need to mock Spark)
        # We'll use a local import to allow the script to set paths first
        try:
            from run_evaluation import EpisodeEvaluator
            self.EvaluatorClass = EpisodeEvaluator
        except ImportError:
            self.fail("Could not import run_evaluation.Make sure paths are correct.")

        self.mock_spark = MockSparkSession()
        self.evaluator = self.EvaluatorClass(self.mock_spark)

    def test_coherence_logic(self):
        # Test case: All steps have explanations -> High score
        steps_data = [
            {"step_id": 1, "has_explanation": True, "tokens_in": 10, "tokens_out": 20},
            {"step_id": 2, "has_explanation": True, "tokens_in": 10, "tokens_out": 20}
        ]
        mock_df = MockDataFrame(steps_data)
        
        result = self.evaluator.compute_coherence(mock_df)
        self.assertGreaterEqual(result["score"], 0.8)
        
        # Test case: No explanations -> Low score
        steps_bad = [
            {"step_id": 1, "has_explanation": False, "tokens_in": 10, "tokens_out": 20},
            {"step_id": 2, "has_explanation": False, "tokens_in": 10, "tokens_out": 20}
        ]
        mock_df_bad = MockDataFrame(steps_bad)
        result_bad = self.evaluator.compute_coherence(mock_df_bad)
        self.assertLess(result_bad["score"], 0.8)

    def test_consistency_logic(self):
        # Test case: Contradiction
        steps = [
            {"step_id": 1, "output": "I am certain of this."},
            {"step_id": 2, "output": "I am not sure anymore."}
        ]
        mock_df = MockDataFrame(steps)
        result = self.evaluator.compute_consistency(mock_df)
        self.assertEqual(result["contradictions"], 1)
        self.assertLess(result["score"], 1.0)

    def test_efficiency_logic(self):
        # Test case: Efficient
        steps = [{"step_id": 1, "tokens_in": 100, "tokens_out": 100}] # Ratio 1.0
        mock_df = MockDataFrame(steps)
        result = self.evaluator.compute_efficiency(mock_df)
        self.assertEqual(result["score"], 1.0)
        
        # Test case: Inefficient
        steps_bad = [{"step_id": 1, "tokens_in": 10, "tokens_out": 100}] # Ratio 10.0
        mock_df_bad = MockDataFrame(steps_bad)
        result_bad = self.evaluator.compute_efficiency(mock_df_bad)
        self.assertEqual(result_bad["score"], 0.5)

if __name__ == '__main__':
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestScrutabilityLogic)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        sys.exit(1)
