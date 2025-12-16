from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, 
    BooleanType, DoubleType, ArrayType, TimestampType
)

# Definitive Schemas
EPISODE_SCHEMA = StructType([
    StructField("episode_id", StringType(), False),
    StructField("run_id", StringType(), True),
    StructField("model", StringType(), True),
    StructField("start_ts", TimestampType(), True),
    StructField("end_ts", TimestampType(), True),
    StructField("status", StringType(), True),
    # ... other fields as needed
])

STEP_SCHEMA = StructType([
    StructField("episode_id", StringType(), False),
    StructField("step_id", IntegerType(), False),
    StructField("task_name", StringType(), True),
    StructField("output", StringType(), True),
    StructField("has_explanation", BooleanType(), True),
    StructField("tokens_in", IntegerType(), True),
    StructField("tokens_out", IntegerType(), True),
    StructField("explanation", StringType(), True),
    # ... other fields
])

EVAL_SCHEMA = StructType([
    StructField("episode_id", StringType(), False),
    StructField("coherence_score", DoubleType(), True),
    StructField("consistency_score", DoubleType(), True),
    StructField("efficiency_score", DoubleType(), True),
    StructField("scrutability_score", DoubleType(), True),
    StructField("scrutability_level", StringType(), True),
    StructField("flags", ArrayType(StringType()), True),
    StructField("evaluated_at", StringType(), True),
    StructField("evaluator_version", StringType(), True)
])

class Episode:
    """Represents an episode to be evaluated."""
    def __init__(self, episode_id, steps_df):
        self.episode_id = episode_id
        self.steps_df = steps_df
        # Lazy load steps
        self._steps = None

    @property
    def steps(self):
        if self._steps is None:
            self._steps = self.steps_df.collect()
        return self._steps
