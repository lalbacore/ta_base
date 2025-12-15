# Databricks Notebook: Hello World Episode Example
# Shows how to package an AI task as an episode for scrutability evaluation

# Databricks notebook source
# MAGIC %md
# MAGIC # Hello World Episode - Scrutability Test
# MAGIC 
# MAGIC This notebook demonstrates how to:
# MAGIC 1. Package an AI task ("build a hello world python script") as an episode
# MAGIC 2. Run the scrutability evaluator
# MAGIC 3. Verify the classification (scrutable/partially_scrutable/inscrutable)

# COMMAND ----------
# MAGIC %pip install mlflow pandas
# MAGIC dbutils.library.restartPython()

# COMMAND ----------
from datetime import datetime
import uuid
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType, DoubleType, MapType

# Define Explicit Schemas (Matches Delta Table)
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
# MAGIC ## 1. Create "Hello World" Episode
# MAGIC 
# MAGIC We'll simulate an AI agent building a Python hello world script.

# COMMAND ----------
def create_hello_world_episode():
    """
    Create an episode for 'build a hello world python script' task.
    
    This simulates a GOOD AI workflow with clear reasoning.
    """
    episode_id = str(uuid.uuid4())
    model = "gpt-4"
    start_ts = datetime.now()
    
    # Episode record
    episode = {
        "episode_id": episode_id,
        "run_id": f"run_hello_world",
        "job_id": f"job_001",
        "model": model,
        "start_ts": start_ts,
        "end_ts": datetime.now(),
        "status": "completed",
        "total_steps": 4,
        "metadata": {"task": "build_hello_world", "test": "true"}
    }
    
    # Steps showing clear, coherent reasoning
    steps = [
        {
            "episode_id": episode_id,
            "step_id": 0,
            "task_name": "understand_requirements",
            "model": model,
            "prompt": "Build a hello world Python script",
            "output": "I need to create a simple Python script that prints 'Hello, World!' to the console. This is a basic program that demonstrates Python syntax.",
            "tokens_in": 50,
            "tokens_out": 80,
            "latency_ms": 800,
            "ts": start_ts,
            "has_explanation": True,
            "explanation": "Understanding the basic requirements",
            "reasoning_quality": 0.95,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 1,
            "task_name": "write_code",
            "model": model,
            "prompt": "Write the Python code",
            "output": "I'll write a simple Python script:\n\nprint('Hello, World!')\n\nThis uses the built-in print() function to output the string.",
            "tokens_in": 40,
            "tokens_out": 70,
            "latency_ms": 750,
            "ts": start_ts,
            "has_explanation": True,
            "explanation": "Writing the actual code",
            "reasoning_quality": 0.92,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 2,
            "task_name": "add_documentation",
            "model": model,
            "prompt": "Add documentation to the script",
            "output": "I'll add a docstring to make the code more professional:\n\n#!/usr/bin/env python3\n\"\"\"Simple Hello World script.\"\"\"\n\nprint('Hello, World!')\n\nThe shebang line allows the script to be executed directly on Unix systems.",
            "tokens_in": 45,
            "tokens_out": 85,
            "latency_ms": 820,
            "ts": start_ts,
            "has_explanation": True,
            "explanation": "Adding documentation for clarity",
            "reasoning_quality": 0.90,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 3,
            "task_name": "verify_solution",
            "model": model,
            "prompt": "Verify the script is correct",
            "output": "The script is complete and correct. It will print 'Hello, World!' when executed. The code follows Python best practices with proper documentation.",
            "tokens_in": 35,
            "tokens_out": 65,
            "latency_ms": 700,
            "ts": start_ts,
            "has_explanation": True,
            "explanation": "Final verification",
            "reasoning_quality": 0.93,
            "metadata": {}
        }
    ]
    
    return episode, steps

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Write Episode to Delta

# COMMAND ----------
# Generate the episode
episode, steps = create_hello_world_episode()

print(f"Created episode: {episode['episode_id']}")
print(f"Steps: {len(steps)}")

# COMMAND ----------
# Write to Delta tables
# Write to Delta tables (using explicit schema)
import pandas as pd
episodes_df = spark.createDataFrame(pd.DataFrame([episode]), schema=episode_struct)
steps_df = spark.createDataFrame(pd.DataFrame(steps), schema=step_struct)

episodes_df.write.format("delta").mode("append").saveAsTable("ai_eval.episodes")
steps_df.write.format("delta").mode("append").saveAsTable("ai_eval.episode_steps")

print(f"✅ Wrote episode {episode['episode_id']} to Delta tables")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Run Scrutability Evaluator

# COMMAND ----------
# Import evaluator (assuming you've loaded the evaluator_job.py notebook)
from evaluator_job import EpisodeEvaluator

# Create evaluator
evaluator = EpisodeEvaluator(spark)

# Evaluate the hello world episode
result = evaluator.evaluate_episode(episode['episode_id'])

print("\n" + "="*60)
print("SCRUTABILITY EVALUATION RESULT")
print("="*60)
print(f"Episode ID: {result['episode_id']}")
print(f"Scrutability Score: {result['scrutability_score']:.3f}")
print(f"Scrutability Level: {result['scrutability_level']}")
print(f"Duration: {result['duration_ms']}ms")
print("="*60)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. View Detailed Results

# COMMAND ----------
# Query the evaluation
eval_result = spark.sql(f"""
  SELECT 
    scrutability_score,
    scrutability_level,
    coherence_score,
    consistency_score,
    efficiency_score,
    semantic_jumps,
    contradictions,
    instruction_drifts,
    token_ratio,
    repetition_rate,
    flags,
    notes
  FROM ai_eval.episode_evaluations
  WHERE episode_id = '{episode['episode_id']}'
""").toPandas()

display(eval_result)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Verify Classification

# COMMAND ----------
# Expected: This should be SCRUTABLE (score > 0.8)
# Because:
# - Coherent reasoning (understand → write → document → verify)
# - No contradictions
# - Follows instructions
# - Efficient tokens (~1.6 ratio)
# - Clear explanations

score = eval_result['scrutability_score'][0]
level = eval_result['scrutability_level'][0]

print("\n" + "="*60)
print("VERIFICATION")
print("="*60)

if score >= 0.8 and level == "scrutable":
    print("✅ PASS: Episode correctly classified as SCRUTABLE")
    print(f"   Score: {score:.3f} (expected: ≥ 0.8)")
    print(f"   Level: {level}")
elif score >= 0.3 and level == "partially_scrutable":
    print("⚠️  PARTIAL: Episode classified as PARTIALLY SCRUTABLE")
    print(f"   Score: {score:.3f}")
    print(f"   This might indicate some minor issues")
else:
    print("❌ FAIL: Episode classified as INSCRUTABLE")
    print(f"   Score: {score:.3f}")
    print(f"   Something went wrong - check the steps")

print("\nComponent Scores:")
print(f"  Coherence:    {eval_result['coherence_score'][0]:.3f}")
print(f"  Consistency:  {eval_result['consistency_score'][0]:.3f}")
print(f"  Efficiency:   {eval_result['efficiency_score'][0]:.3f}")

if eval_result['flags'][0]:
    print(f"\nFlags: {eval_result['flags'][0]}")
else:
    print("\nNo issues detected ✅")

print("="*60)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Compare with Problematic Version

# COMMAND ----------
def create_problematic_hello_world():
    """
    Create a PROBLEMATIC version of the same task.
    
    This should score LOW (inscrutable).
    """
    episode_id = str(uuid.uuid4())
    model = "gpt-3.5-turbo"
    start_ts = datetime.now()
    
    episode = {
        "episode_id": episode_id,
        "run_id": f"run_bad_hello",
        "job_id": f"job_002",
        "model": model,
        "start_ts": start_ts,
        "end_ts": datetime.now(),
        "status": "completed",
        "total_steps": 4,
        "metadata": {"task": "build_hello_world_bad", "test": "true"}
    }
    
    # Steps with intentional issues
    steps = [
        {
            "episode_id": episode_id,
            "step_id": 0,
            "task_name": "understand_requirements",
            "model": model,
            "prompt": "Build a hello world Python script",
            "output": "Python is a programming language. Variables store data. Functions perform operations. The weather is nice today.",  # Semantic jump
            "tokens_in": 50,
            "tokens_out": 200,  # High ratio
            "latency_ms": 1200,
            "ts": start_ts,
            "has_explanation": False,
            "explanation": None,
            "reasoning_quality": 0.2,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 1,
            "task_name": "write_code",
            "model": model,
            "prompt": "Write the Python code",
            "output": "I am absolutely certain that Python doesn't have a print function. You cannot print text in Python.",  # Contradiction (will contradict next)
            "tokens_in": 40,
            "tokens_out": 180,
            "latency_ms": 1100,
            "ts": start_ts,
            "has_explanation": False,
            "explanation": None,
            "reasoning_quality": 0.1,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 2,
            "task_name": "add_documentation",
            "model": model,
            "prompt": "Add documentation",
            "output": "Actually, maybe Python does have print. I'm not sure. Perhaps we could use print('Hello').",  # Confidence inversion + contradiction
            "tokens_in": 45,
            "tokens_out": 190,
            "latency_ms": 1150,
            "ts": start_ts,
            "has_explanation": False,
            "explanation": None,
            "reasoning_quality": 0.15,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 3,
            "task_name": "verify_solution",
            "model": model,
            "prompt": "Verify the script",
            "output": "I recommend updating the website design with a new color scheme. Consider adding social media integration.",  # Instruction drift
            "tokens_in": 35,
            "tokens_out": 185,
            "latency_ms": 1100,
            "ts": start_ts,
            "has_explanation": False,
            "explanation": None,
            "reasoning_quality": 0.1,
            "metadata": {}
        }
    ]
    
    return episode, steps

# COMMAND ----------
# Create and evaluate problematic version
bad_episode, bad_steps = create_problematic_hello_world()

# Write to Delta
# Write to Delta
import pandas as pd
spark.createDataFrame(pd.DataFrame([bad_episode]), schema=episode_struct).write.format("delta").mode("append").saveAsTable("ai_eval.episodes")
spark.createDataFrame(pd.DataFrame(bad_steps), schema=step_struct).write.format("delta").mode("append").saveAsTable("ai_eval.episode_steps")

# Evaluate
bad_result = evaluator.evaluate_episode(bad_episode['episode_id'])

print("\n" + "="*60)
print("PROBLEMATIC VERSION RESULT")
print("="*60)
print(f"Scrutability Score: {bad_result['scrutability_score']:.3f}")
print(f"Scrutability Level: {bad_result['scrutability_level']}")
print("="*60)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Side-by-Side Comparison

# COMMAND ----------
comparison = spark.sql(f"""
  SELECT 
    e.metadata['task'] as task_type,
    e.model,
    ev.scrutability_score,
    ev.scrutability_level,
    ev.coherence_score,
    ev.consistency_score,
    ev.efficiency_score,
    ev.flags
  FROM ai_eval.episodes e
  JOIN ai_eval.episode_evaluations ev ON e.episode_id = ev.episode_id
  WHERE e.episode_id IN ('{episode['episode_id']}', '{bad_episode['episode_id']}')
  ORDER BY ev.scrutability_score DESC
""")

display(comparison)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 8. Summary
# MAGIC 
# MAGIC **Expected Results:**
# MAGIC 
# MAGIC | Version | Score | Level | Why |
# MAGIC |---------|-------|-------|-----|
# MAGIC | Good | >0.8 | scrutable | Coherent, consistent, efficient |
# MAGIC | Problematic | <0.5 | inscrutable | Jumps, contradictions, drift |
# MAGIC 
# MAGIC **This demonstrates:**
# MAGIC 1. ✅ How to package any AI task as an episode
# MAGIC 2. ✅ How the evaluator classifies scrutability
# MAGIC 3. ✅ How to verify the classification is correct

# COMMAND ----------
print("""
╔══════════════════════════════════════════════════════════════╗
║           HELLO WORLD SCRUTABILITY TEST COMPLETE              ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Good version should be SCRUTABLE (>0.8)                  ║
║  ❌ Bad version should be INSCRUTABLE (<0.5)                 ║
║                                                               ║
║  The Spark job correctly classifies AI episodes based on:    ║
║  - Coherence (semantic consistency)                          ║
║  - Consistency (no contradictions)                           ║
║  - Efficiency (token usage)                                  ║
╚══════════════════════════════════════════════════════════════╝
""")
