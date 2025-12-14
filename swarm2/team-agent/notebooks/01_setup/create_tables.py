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
# MAGIC %md
# MAGIC ## 1. Create Unity Catalog Schema

# COMMAND ----------
# Create schema if it doesn't exist
spark.sql("""
  CREATE SCHEMA IF NOT EXISTS ai_eval
  COMMENT 'AI Episode Evaluation Platform'
  LOCATION 's3://your-bucket/ai_eval'
""")

# Verify schema created
spark.sql("SHOW SCHEMAS").filter("databaseName = 'ai_eval'").show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Create Episodes Table

# COMMAND ----------
# Read and execute episodes table DDL
with open('/Workspace/Repos/your-repo/sql/schema/episodes.sql', 'r') as f:
    episodes_ddl = f.read()

spark.sql(episodes_ddl)

# Verify table created
spark.sql("DESCRIBE TABLE EXTENDED ai_eval.episodes").show(truncate=False)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Create Episode Steps Table

# COMMAND ----------
# Read and execute steps table DDL
with open('/Workspace/Repos/your-repo/sql/schema/episode_steps.sql', 'r') as f:
    steps_ddl = f.read()

spark.sql(steps_ddl)

# Verify table created
spark.sql("DESCRIBE TABLE EXTENDED ai_eval.episode_steps").show(truncate=False)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Create Episode Evaluations Table

# COMMAND ----------
# Read and execute evaluations table DDL
with open('/Workspace/Repos/your-repo/sql/schema/episode_evaluations.sql', 'r') as f:
    evals_ddl = f.read()

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

# Insert sample episode
spark.createDataFrame([sample_episode]).write \
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
