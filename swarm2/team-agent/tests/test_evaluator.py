# Test Suite for Episode Evaluator
# Tests coherence, consistency, and efficiency modules

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from datetime import datetime


@pytest.fixture(scope="session")
def spark():
    """Create Spark session for testing."""
    return SparkSession.builder \
        .appName("EvaluatorTests") \
        .master("local[2]") \
        .getOrCreate()


@pytest.fixture
def sample_steps_df(spark):
    """Create sample episode steps for testing."""
    schema = StructType([
        StructField("episode_id", StringType(), False),
        StructField("step_id", IntegerType(), False),
        StructField("task_name", StringType()),
        StructField("model", StringType()),
        StructField("prompt", StringType()),
        StructField("output", StringType()),
        StructField("tokens_in", IntegerType()),
        StructField("tokens_out", IntegerType()),
        StructField("latency_ms", IntegerType()),
        StructField("ts", TimestampType())
    ])
    
    data = [
        ("test-ep-1", 0, "task1", "gpt-4", "Analyze the data", 
         "I will analyze the data by examining patterns", 100, 150, 1000, datetime.now()),
        ("test-ep-1", 1, "task2", "gpt-4", "Continue analysis",
         "The patterns show clear trends in user behavior", 80, 120, 900, datetime.now()),
        ("test-ep-1", 2, "task3", "gpt-4", "Summarize findings",
         "In summary, the analysis reveals significant insights", 90, 130, 950, datetime.now()),
    ]
    
    return spark.createDataFrame(data, schema)


def test_coherence_scoring(spark, sample_steps_df):
    """Test coherence scoring module."""
    from coherence import compute_coherence_score
    
    result = compute_coherence_score(spark, sample_steps_df)
    
    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0
    assert "avg_similarity" in result
    assert "jumps" in result
    assert isinstance(result["jumps"], int)


def test_coherence_single_step(spark):
    """Test coherence with single step (edge case)."""
    from coherence import compute_coherence_score
    
    schema = StructType([
        StructField("step_id", IntegerType()),
        StructField("output", StringType())
    ])
    
    single_step = spark.createDataFrame(
        [(0, "Single step output")],
        schema
    )
    
    result = compute_coherence_score(spark, single_step)
    
    assert result["score"] == 1.0
    assert result["jumps"] == 0


def test_consistency_detection(spark, sample_steps_df):
    """Test consistency detection module."""
    from consistency import compute_consistency_score
    
    result = compute_consistency_score(spark, sample_steps_df)
    
    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0
    assert "contradictions" in result
    assert "inversions" in result
    assert "drifts" in result


def test_contradiction_detection():
    """Test contradiction detection logic."""
    from consistency import _contradicts
    
    # Test contradiction
    text1 = "The system is working correctly"
    text2 = "The system is not working correctly"
    assert _contradicts(text1, text2)
    
    # Test no contradiction
    text3 = "The system is fast"
    text4 = "The system is reliable"
    assert not _contradicts(text3, text4)


def test_confidence_inversion():
    """Test confidence inversion detection."""
    from consistency import _confidence_inverted
    
    # Test inversion
    text1 = "I am absolutely certain this is correct"
    text2 = "I'm not sure if this is right"
    assert _confidence_inverted(text1, text2)
    
    # Test no inversion
    text3 = "This seems correct"
    text4 = "This is definitely correct"
    assert not _confidence_inverted(text3, text4)


def test_efficiency_metrics(spark, sample_steps_df):
    """Test efficiency metrics module."""
    from efficiency import compute_efficiency_score
    
    result = compute_efficiency_score(spark, sample_steps_df)
    
    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0
    assert "ratio" in result
    assert "per_delta" in result
    assert "repetition" in result


def test_token_ratio_calculation(spark):
    """Test token ratio calculation."""
    from efficiency import compute_efficiency_score
    
    schema = StructType([
        StructField("tokens_in", IntegerType()),
        StructField("tokens_out", IntegerType()),
        StructField("output", StringType())
    ])
    
    # High ratio (inefficient)
    high_ratio_df = spark.createDataFrame([
        (100, 500, "Very long output with lots of tokens"),
        (100, 500, "Another very long output")
    ], schema)
    
    result = compute_efficiency_score(spark, high_ratio_df)
    assert result["ratio"] == 10.0  # 1000/100


def test_repetition_detection(spark):
    """Test repetition rate calculation."""
    from efficiency import _compute_repetition
    
    schema = StructType([
        StructField("output", StringType())
    ])
    
    # High repetition
    repetitive_df = spark.createDataFrame([
        ("The quick brown fox jumps over the lazy dog",),
        ("The quick brown fox jumps over the lazy dog",),
        ("The quick brown fox jumps over the lazy dog",)
    ], schema)
    
    repetition = _compute_repetition(repetitive_df)
    assert repetition > 0.5  # High repetition


def test_evaluator_end_to_end(spark, sample_steps_df):
    """Test complete evaluator workflow."""
    # This would require mocking Delta tables and MLflow
    # Skipping for now - will test in Databricks environment
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
