# Databricks notebook source
# MAGIC %md
# MAGIC # Large Scale Test Data Generation
# MAGIC 
# MAGIC Generates a diverse set of episodes to test the Scrutability Evaluator.
# MAGIC 
# MAGIC **Categories:**
# MAGIC 1. **Scrutable (50%)**: Clean, coherent, consistent, efficient.
# MAGIC 2. **Partially Scrutable (30%)**:
# MAGIC    - **Drift**: Starts well, wanders off topic.
# MAGIC    - **Contradiction**: Valid steps but logical inconsistencies.
# MAGIC    - **Inefficient**: Verbose, low reasoning-to-token ratio.
# MAGIC 3. **Inscrutable (20%)**: Low coherence, random noise, hallucinations.

# COMMAND ----------
# Install dependencies
%pip install faker numpy scipy mlflow pandas

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
import uuid
import random
import numpy as np
from datetime import datetime, timedelta
from pyspark.sql.types import *
import builtins  # Explicit builtins to avoid Spark shadowing

# COMMAND ----------
# MAGIC %md
# MAGIC ## 0. Cleanup (Fresh State)
# MAGIC Start with a clean slate to avoid schema conflicts (Integer vs Long inference issues).

# COMMAND ----------
spark.sql("DROP TABLE IF EXISTS ai_eval.episodes")
spark.sql("DROP TABLE IF EXISTS ai_eval.episode_steps")
spark.sql("DROP TABLE IF EXISTS ai_eval.episode_evaluations")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Schemas

# COMMAND ----------
# Episode Schema
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

# Step Schema
step_struct = StructType([
    StructField("episode_id", StringType(), False),
    StructField("step_id", IntegerType(), False),
    StructField("task_name", StringType(), True),
    StructField("model", StringType(), True),
    StructField("prompt", StringType(), True),
    StructField("output", StringType(), True),
    StructField("tokens_in", IntegerType(), True),
    StructField("tokens_out", IntegerType(), True),
    StructField("latency_ms", IntegerType(), True),
    StructField("ts", TimestampType(), True),
    StructField("has_explanation", BooleanType(), True),
    StructField("explanation", StringType(), True),
    StructField("reasoning_quality", DoubleType(), True),
    StructField("metadata", MapType(StringType(), StringType()), True)
])

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Generators

# COMMAND ----------
def generate_base_episode(model="gpt-4", type_label="scrutable"):
    ep_id = str(uuid.uuid4())
    start = datetime.now() - timedelta(minutes=random.randint(0, 10000))
    
    return {
        "episode_id": ep_id,
        "run_id": f"batch_gen_{datetime.now().strftime('%Y%m%d')}",
        "job_id": "large_dataset_gen",
        "model": model,
        "start_ts": start,
        "end_ts": start + timedelta(seconds=random.randint(10, 120)),
        "status": "completed",
        "total_steps": 3,
        "metadata": {"type": "generated", "category": type_label}
    }

def generate_step(ep_id, step_id, task, prompt, output, ts, explanation=None, quality=0.9, t_in=50, t_out=60):
    return {
        "episode_id": ep_id,
        "step_id": step_id,
        "task_name": task,
        "model": "gpt-4",
        "prompt": prompt,
        "output": output,
        "tokens_in": t_in,
        "tokens_out": t_out,
        "latency_ms": random.randint(400, 1500),
        "ts": ts,
        "has_explanation": explanation is not None,
        "explanation": explanation,
        "reasoning_quality": quality,
        "metadata": {}
    }

# --- SCENARIOS ---

def create_scrutable():
    """Good quality flow"""
    ep = generate_base_episode("gpt-4", "scrutable")
    steps = [
        generate_step(ep["episode_id"], 0, "plan", "Create plan", "I will execute X, Y, Z.", ep["start_ts"], "Planning phase", 0.95),
        generate_step(ep["episode_id"], 1, "execute", "Execute X", "Executing X resulted in success.", ep["start_ts"]+timedelta(seconds=10), "Execution phase", 0.95),
        generate_step(ep["episode_id"], 2, "verify", "Verify results", "Verification passed.", ep["start_ts"]+timedelta(seconds=20), "Verification phase", 0.95)
    ]
    return ep, steps

def create_drift():
    """Starts good, ends unrelated"""
    ep = generate_base_episode("gpt-3.5-turbo", "partial_drift")
    steps = [
        generate_step(ep["episode_id"], 0, "ask", "What is the capital of France?", "The capital of France is Paris.", ep["start_ts"], "Direct answer", 0.9),
        generate_step(ep["episode_id"], 1, "elaborate", "Tell me more.", "Paris is known for the Eiffel Tower.", ep["start_ts"]+timedelta(seconds=10), "Elaboration", 0.8),
        generate_step(ep["episode_id"], 2, "drift", "Continue.", "The weather in Mars is cold. Also I like pizza.", ep["start_ts"]+timedelta(seconds=20), "Drifting", 0.2)
    ]
    return ep, steps

def create_contradiction():
    """Contains logical conflict"""
    ep = generate_base_episode("gpt-4", "partial_contradiction")
    steps = [
        generate_step(ep["episode_id"], 0, "status", "System status?", "All systems are operational.", ep["start_ts"], "Status check", 0.9),
        generate_step(ep["episode_id"], 1, "alert", "Any alerts?", "No active alerts.", ep["start_ts"]+timedelta(seconds=10), "Alert check", 0.9),
        generate_step(ep["episode_id"], 2, "summary", "Summarize.", "Summary: Critical failure in system. Multiple alerts active.", ep["start_ts"]+timedelta(seconds=20), "Contradictory summary", 0.3)
    ]
    return ep, steps

def create_inefficient():
    """Verbose, low signal-to-noise"""
    ep = generate_base_episode("gpt-3.5-turbo", "partial_inefficient")
    long_text = "This is a very long and repetitive sentence that does not add much value but consumes a lot of tokens. " * 10
    steps = [
        generate_step(ep["episode_id"], 0, "simple", "Say hello.", f"Hello. {long_text}", ep["start_ts"], "Verbose hello", 0.4, t_out=300),
        generate_step(ep["episode_id"], 1, "simple", "Say bye.", f"Goodbye. {long_text}", ep["start_ts"]+timedelta(seconds=10), "Verbose bye", 0.4, t_out=300),
        generate_step(ep["episode_id"], 2, "simple", "Done?", f"Yes. {long_text}", ep["start_ts"]+timedelta(seconds=20), "Verbose yes", 0.4, t_out=300)
    ]
    return ep, steps

def create_inscrutable():
    """Garbage output"""
    ep = generate_base_episode("random_model", "inscrutable")
    steps = [
        generate_step(ep["episode_id"], 0, "noise", "???", "x8s7df87s6d8f76s8d7f6", ep["start_ts"], None, 0.0),
        generate_step(ep["episode_id"], 1, "noise", "???", "asoidu aoisdu aoisdu", ep["start_ts"]+timedelta(seconds=5), None, 0.0),
        generate_step(ep["episode_id"], 2, "noise", "???", "ERROR ERROR NULL", ep["start_ts"]+timedelta(seconds=10), None, 0.0)
    ]
    return ep, steps

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Generation Loop

# COMMAND ----------
# Configuration
COUNTS = {
    "scrutable": 50,
    "drift": 10,
    "contradiction": 10,
    "inefficient": 10,
    "inscrutable": 20
}

all_episodes = []
all_steps = []

print("🚀 Starting Data Generation...")

# Generate Scrutable
for _ in range(COUNTS["scrutable"]):
    ep, steps = create_scrutable()
    all_episodes.append(ep)
    all_steps.extend(steps)

# Generate Drift
for _ in range(COUNTS["drift"]):
    ep, steps = create_drift()
    all_episodes.append(ep)
    all_steps.extend(steps)

# Generate Contradiction
for _ in range(COUNTS["contradiction"]):
    ep, steps = create_contradiction()
    all_episodes.append(ep)
    all_steps.extend(steps)

# Generate Inefficient
for _ in range(COUNTS["inefficient"]):
    ep, steps = create_inefficient()
    all_episodes.append(ep)
    all_steps.extend(steps)

# Generate Inscrutable
for _ in range(COUNTS["inscrutable"]):
    ep, steps = create_inscrutable()
    all_episodes.append(ep)
    all_steps.extend(steps)

print(f"✅ Generated {len(all_episodes)} episodes and {len(all_steps)} steps.")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Write to Delta

# COMMAND ----------
# Using explicit schemas from test_suite.py to avoid type inference issues
import pandas as pd
batch_ep_df = spark.createDataFrame(pd.DataFrame(all_episodes), schema=episode_struct)
batch_step_df = spark.createDataFrame(pd.DataFrame(all_steps), schema=step_struct)

# Append to tables
batch_ep_df.write.format("delta").mode("append").saveAsTable("ai_eval.episodes")
batch_step_df.write.format("delta").mode("append").saveAsTable("ai_eval.episode_steps")

print("✅ Successfully appended data to Delta tables.")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Verification Query

# COMMAND ----------
# Check counts
count_ep = spark.table("ai_eval.episodes").count()
print(f"Total Episodes in DB: {count_ep}")

display(spark.sql("SELECT metadata.category, count(*) as count FROM ai_eval.episodes GROUP BY metadata.category"))
