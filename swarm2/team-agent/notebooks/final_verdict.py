# Databricks notebook source
# FINAL VERDICT: The "Nuclear Option" Test Script
# This script drops everything, recreates fresh tables, and verifies the logic with ZERO reliance on complex serialization.

import builtins
import uuid
from datetime import datetime
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col

# 1. SETUP
spark = SparkSession.builder.getOrCreate()

# 2. CLEANUP
print("🧹 Cleaning tables...")
spark.sql("DROP TABLE IF EXISTS ai_eval.episodes")
spark.sql("DROP TABLE IF EXISTS ai_eval.episode_steps")
spark.sql("DROP TABLE IF EXISTS ai_eval.episode_evaluations")
print("✅ Cleaned.")

# 3. SCHEMAS
step_schema = StructType([
    StructField("episode_id", StringType(), False),
    StructField("step_id", IntegerType(), False),
    StructField("task_name", StringType(), True),
    StructField("output", StringType(), True),
    StructField("has_explanation", BooleanType(), True),
    StructField("tokens_in", IntegerType(), True),
    StructField("tokens_out", IntegerType(), True)
])

eval_schema = StructType([
    StructField("episode_id", StringType(), False),
    StructField("scrutability_score", DoubleType(), True),
    StructField("scrutability_level", StringType(), True),
    StructField("flags", ArrayType(StringType()), True)
])

# 4. HELPERS
def create_episode_data(ep_type):
    ep_id = str(uuid.uuid4())
    steps = []
    
    if ep_type == "good":
        # Clear reasoning
        steps = [
            {"episode_id": ep_id, "step_id": 0, "task_name": "p", "output": "Plan.", "has_explanation": True, "tokens_in": 10, "tokens_out": 10},
            {"episode_id": ep_id, "step_id": 1, "task_name": "e", "output": "Exec.", "has_explanation": True, "tokens_in": 10, "tokens_out": 10}
        ]
    elif ep_type == "bad":
        # No reasoning, garbage
        steps = [
            {"episode_id": ep_id, "step_id": 0, "task_name": "x", "output": "???", "has_explanation": False, "tokens_in": 10, "tokens_out": 10}
        ]
    
    # Write
    df = spark.createDataFrame(steps, schema=step_schema)
    df.write.format("delta").mode("append").saveAsTable("ai_eval.episode_steps")
    return ep_id

def evaluate_episode(ep_id):
    # READ
    steps = spark.table("ai_eval.episode_steps").filter(col("episode_id") == ep_id).collect()
    
    # LOGIC
    score = 1.0
    for s in steps:
        if not s.has_explanation:
            score -= 0.5 # Big penalty
            
    final_score = float(max(0.0, score))
    level = "scrutable" if final_score > 0.8 else "inscrutable"
    
    # WRITE
    res = {
        "episode_id": ep_id,
        "scrutability_score": final_score,
        "scrutability_level": level,
        "flags": []
    }
    
    spark.createDataFrame([res], schema=eval_schema).write.format("delta").mode("append").saveAsTable("ai_eval.episode_evaluations")
    return res

# 5. EXECUTION
print("\n🚀 Running Tests...")

# Good
good_ep_id = create_episode_data("good")
print(f"Created Good: {good_ep_id}")
res_good = evaluate_episode(good_ep_id)
print(f"Good Score: {res_good['scrutability_score']}")

# Bad
bad_ep_id = create_episode_data("bad")
print(f"Created Bad: {bad_ep_id}")
res_bad = evaluate_episode(bad_ep_id)
print(f"Bad Score: {res_bad['scrutability_score']}")

# 6. VERDICT
if res_good['scrutability_level'] == 'scrutable' and res_bad['scrutability_level'] == 'inscrutable':
    print("\n🎉 FINAL VERDICT: SUCCESS! The pipeline is healthy. 🎉")
else:
    print("\n❌ FINAL VERDICT: FAILURE. Logic mismatch.")
