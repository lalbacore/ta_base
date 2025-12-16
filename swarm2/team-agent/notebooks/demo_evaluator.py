# Databricks Notebook: Demo Evaluator
# Standard demonstration of the Idempotent AI Workflow Evaluator library.

# COMMAND ----------
# MAGIC %pip install .

# COMMAND ----------
from ai_workflow_evaluator import run_episode_evaluation
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Example Episode ID (replace with real ID from your data)
EPISODE_ID = "example_123" 

print(f"🔬 Evaluating Episode: {EPISODE_ID}")

# Run Evaluation
result = run_episode_evaluation(spark, EPISODE_ID)

if result:
    print(f"✅ Evaluation Complete")
    print(f"   Score: {result.scrutability_score:.2f}")
    print(f"   Level: {result.scrutability_level}")
    print(f"   Flags: {result.flags}")
else:
    print("⚠️ Evaluation failed or skipped (check data availability).")
