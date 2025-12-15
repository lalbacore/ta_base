# Databricks Notebook: Setup Delta Tables
# Create Unity Catalog schema and Delta tables for AI evaluation

# Databricks notebook source
# MAGIC %md
# MAGIC # AI Evaluation Platform - Delta Table Setup
# MAGIC 
# MAGIC This notebook creates the foundational Delta Lake tables for the AI episode evaluation platform.
# MAGIC 
# MAGIC **Tables Created:**
# MAGIC 1. `ai_eval.episodes` - Immutable episode records
# MAGIC 2. `ai_eval.episode_steps` - Execution trace
# MAGIC 3. `ai_eval.episode_evaluations` - Scrutability scores

# COMMAND ----------
# MAGIC %pip install pandas
# MAGIC dbutils.library.restartPython()

# COMMAND ----------
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, MapType
import pandas as pd

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Create Unity Catalog Schema

# COMMAND ----------
# Create schema if it doesn't exist
spark.sql("CREATE SCHEMA IF NOT EXISTS ai_eval COMMENT 'AI Episode Evaluation Platform'")

# Verify schema created
spark.sql("SHOW SCHEMAS").filter("databaseName = 'ai_eval'").show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Create Episodes Table

# COMMAND ----------
# Define Episodes Table DDL
episodes_ddl = """
CREATE TABLE IF NOT EXISTS ai_eval.episodes (
  episode_id STRING NOT NULL,
  run_id STRING,
  job_id STRING,
  model STRING,
  start_ts TIMESTAMP,
  end_ts TIMESTAMP,
  status STRING,
  total_steps INT,
  metadata MAP<STRING, STRING>
) USING DELTA
"""

spark.sql(episodes_ddl)

# Verify table created
spark.sql("DESCRIBE TABLE EXTENDED ai_eval.episodes").show(truncate=False)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Create Episode Steps Table

# COMMAND ----------
# Define Steps Table DDL
steps_ddl = """
CREATE TABLE IF NOT EXISTS ai_eval.episode_steps (
  episode_id STRING NOT NULL,
  step_id INT NOT NULL,
  task_name STRING,
  model STRING,
  prompt STRING,
  output STRING,
  tokens_in INT,
  tokens_out INT,
  latency_ms INT,
  ts TIMESTAMP,
  has_explanation BOOLEAN,
  explanation STRING,
  reasoning_quality DOUBLE,
  metadata MAP<STRING, STRING>
) USING DELTA
"""

spark.sql(steps_ddl)

# Verify table created
spark.sql("DESCRIBE TABLE EXTENDED ai_eval.episode_steps").show(truncate=False)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Create Episode Evaluations Table

# COMMAND ----------
# Define Evaluations Table DDL
evals_ddl = """
CREATE TABLE IF NOT EXISTS ai_eval.episode_evaluations (
  episode_id STRING NOT NULL,
  coherence_score DOUBLE,
  consistency_score DOUBLE,
  efficiency_score DOUBLE,
  scrutability_score DOUBLE,
  scrutability_level STRING,
  semantic_jumps INT,
  contradictions INT,
  confidence_inversions INT,
  instruction_drifts INT,
  token_ratio DOUBLE,
  tokens_per_semantic_delta DOUBLE,
  repetition_rate DOUBLE,
  flags ARRAY<STRING>,
  notes STRING,
  evaluator_version STRING,
  evaluated_at TIMESTAMP,
  evaluation_duration_ms INT
) USING DELTA
"""

spark.sql(evals_ddl)

# Verify table created
spark.sql("DESCRIBE TABLE EXTENDED ai_eval.episode_evaluations").show(truncate=False)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Verify Table Relationships

# COMMAND ----------
# Show all tables in schema
spark.sql("SHOW TABLES IN ai_eval").show()

# Show table properties
for table in ['episodes', 'episode_steps', 'episode_evaluations']:
    print(f"\n=== {table} ===")
    spark.sql(f"DESCRIBE EXTENDED ai_eval.{table}").show(truncate=False)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Create Sample Data (Optional)

# COMMAND ----------
from datetime import datetime
import uuid

# Sample episode
sample_episode = {
    "episode_id": str(uuid.uuid4()),
    "run_id": "sample_run_001",
    "job_id": "sample_job_001",
    "model": "gpt-4",
    "start_ts": datetime.now(),
    "end_ts": None,
    "status": "running",
    "total_steps": 0,
    "metadata": {"prompt": "Sample AI task"}
}

# Define explicit schema for sample
episode_struct = StructType([
    StructField("episode_id", StringType(), False),
    StructField("run_id", StringType(), True),
    StructField("job_id", StringType(), True),
    StructField("model", StringType(), True),
    StructField("start_ts", TimestampType(), True),
    StructField("end_ts", TimestampType(), True),
    StructField("status", StringType(), True),
    StructField("total_steps", IntegerType(), True),
    StructField("metadata", MapType(StringType(), StringType()), True)
])

# Insert sample episode using Pandas and Explicit Schema
spark.createDataFrame(pd.DataFrame([sample_episode]), schema=episode_struct).write \
    .format("delta") \
    .mode("append") \
    .saveAsTable("ai_eval.episodes")

print(f"Created sample episode: {sample_episode['episode_id']}")

# COMMAND ----------
# Verify sample data
spark.sql("SELECT * FROM ai_eval.episodes").show(truncate=False)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Setup Complete! ✅
# MAGIC 
# MAGIC Next steps:
# MAGIC 1. Build Spark evaluator job
# MAGIC 2. Integrate with AI pipelines
# MAGIC 3. Set up MLflow tracking
