# Databricks Notebook: Sample Data Generator
# Creates test episodes with "good" and "problematic" patterns

# Databricks notebook source
# MAGIC %pip install pandas
# MAGIC dbutils.library.restartPython()

# COMMAND ----------
# MAGIC %md
# MAGIC # Sample Test Data Generator
# MAGIC 
# MAGIC Creates two types of test episodes:
# MAGIC 1. **Good Workflow** - High scrutability (coherent, consistent, efficient)
# MAGIC 2. **Problematic Workflow** - Low scrutability (jumps, contradictions, drift)

# COMMAND ----------
from pyspark.sql.types import *
from datetime import datetime, timedelta
import uuid
import random
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
# MAGIC ## 1. Good Workflow - High Scrutability

# COMMAND ----------
def create_good_episode():
    """
    Create an episode with high scrutability.
    
    Characteristics:
    - Coherent reasoning chain
    - No contradictions
    - Follows instructions
    - Efficient token usage
    - Clear explanations
    """
    episode_id = str(uuid.uuid4())
    model = "gpt-4"
    start_ts = datetime.now()
    
    # Episode record
    episode = {
        "episode_id": episode_id,
        "run_id": f"run_{random.randint(1000, 9999)}",
        "job_id": f"job_{random.randint(100, 999)}",
        "model": model,
        "start_ts": start_ts,
        "end_ts": start_ts + timedelta(seconds=45),
        "status": "completed",
        "total_steps": 5,
        "metadata": {"type": "good_workflow", "test": "true"}
    }
    
    # Steps with coherent, consistent reasoning
    steps = [
        {
            "episode_id": episode_id,
            "step_id": 0,
            "task_name": "analyze_data",
            "model": model,
            "prompt": "Analyze the customer purchase data and identify trends",
            "output": "I will analyze the customer purchase data systematically. First, I'll examine the overall purchase patterns to identify key trends in customer behavior.",
            "tokens_in": 100,
            "tokens_out": 150,
            "latency_ms": 1200,
            "ts": start_ts,
            "has_explanation": True,
            "explanation": "Starting with systematic analysis approach",
            "reasoning_quality": 0.9,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 1,
            "task_name": "identify_patterns",
            "model": model,
            "prompt": "What patterns do you see?",
            "output": "Based on the data analysis, I observe three clear patterns: 1) Peak purchases occur on weekends, 2) Average order value increases during holiday seasons, 3) Repeat customers show 40% higher lifetime value.",
            "tokens_in": 80,
            "tokens_out": 140,
            "latency_ms": 1100,
            "ts": start_ts + timedelta(seconds=10),
            "has_explanation": True,
            "explanation": "Identified three distinct patterns from analysis",
            "reasoning_quality": 0.95,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 2,
            "task_name": "validate_findings",
            "model": model,
            "prompt": "Validate these patterns with statistical tests",
            "output": "To validate these patterns, I applied chi-square tests for weekend purchases (p<0.01), ANOVA for seasonal variations (p<0.001), and t-tests for customer segments (p<0.05). All patterns are statistically significant.",
            "tokens_in": 90,
            "tokens_out": 145,
            "latency_ms": 1300,
            "ts": start_ts + timedelta(seconds=20),
            "has_explanation": True,
            "explanation": "Statistical validation confirms all patterns",
            "reasoning_quality": 0.92,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 3,
            "task_name": "generate_recommendations",
            "model": model,
            "prompt": "Based on these validated patterns, what do you recommend?",
            "output": "Given the validated patterns, I recommend: 1) Increase weekend inventory by 30%, 2) Launch targeted holiday campaigns 2 weeks before peak seasons, 3) Implement loyalty program for repeat customers with personalized offers.",
            "tokens_in": 95,
            "tokens_out": 155,
            "latency_ms": 1250,
            "ts": start_ts + timedelta(seconds=30),
            "has_explanation": True,
            "explanation": "Recommendations directly follow from validated patterns",
            "reasoning_quality": 0.94,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 4,
            "task_name": "summarize",
            "model": model,
            "prompt": "Provide a summary of the analysis and recommendations",
            "output": "Summary: Analysis of customer purchase data revealed three statistically significant patterns (weekend peaks, seasonal increases, repeat customer value). Recommendations include inventory optimization, targeted campaigns, and loyalty programs to capitalize on these trends.",
            "tokens_in": 85,
            "tokens_out": 135,
            "latency_ms": 1150,
            "ts": start_ts + timedelta(seconds=40),
            "has_explanation": True,
            "explanation": "Concise summary of entire analysis chain",
            "reasoning_quality": 0.96,
            "metadata": {}
        }
    ]
    
    return episode, steps


# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Problematic Workflow - Low Scrutability

# COMMAND ----------
def create_problematic_episode():
    """
    Create an episode with low scrutability.
    
    Intentional issues:
    - Semantic jumps (incoherent reasoning)
    - Contradictions
    - Instruction drift
    - High token ratio (inefficient)
    - High repetition
    - Missing explanations
    """
    episode_id = str(uuid.uuid4())
    model = "gpt-3.5-turbo"
    start_ts = datetime.now()
    
    # Episode record
    episode = {
        "episode_id": episode_id,
        "run_id": f"run_{random.randint(1000, 9999)}",
        "job_id": f"job_{random.randint(100, 999)}",
        "model": model,
        "start_ts": start_ts,
        "end_ts": start_ts + timedelta(seconds=60),
        "status": "completed",
        "total_steps": 5,
        "metadata": {"type": "problematic_workflow", "test": "true"}
    }
    
    # Steps with intentional issues
    steps = [
        {
            "episode_id": episode_id,
            "step_id": 0,
            "task_name": "analyze_data",
            "model": model,
            "prompt": "Analyze the customer purchase data and identify trends",
            "output": "The weather today is sunny and warm. Customer data contains numbers and text fields. Database tables have primary keys. SQL queries can join multiple tables together using foreign key relationships.",
            "tokens_in": 100,
            "tokens_out": 350,  # High token ratio
            "latency_ms": 1500,
            "ts": start_ts,
            "has_explanation": False,  # Missing explanation
            "explanation": None,
            "reasoning_quality": 0.2,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 1,
            "task_name": "identify_patterns",
            "model": model,
            "prompt": "What patterns do you see?",
            "output": "I am absolutely certain that customers never purchase on weekends. The data clearly shows zero weekend activity. This is a definitive finding with no exceptions whatsoever.",  # Will contradict later
            "tokens_in": 80,
            "tokens_out": 320,
            "latency_ms": 1400,
            "ts": start_ts + timedelta(seconds=12),
            "has_explanation": False,
            "explanation": None,
            "reasoning_quality": 0.3,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 2,
            "task_name": "validate_findings",
            "model": model,
            "prompt": "Validate these patterns with statistical tests",
            "output": "Actually, I'm not sure about the weekend pattern. Maybe customers do purchase on weekends. The data is unclear. Perhaps we need more information to determine if weekend purchases occur or not.",  # Confidence inversion + contradiction
            "tokens_in": 90,
            "tokens_out": 310,
            "latency_ms": 1450,
            "ts": start_ts + timedelta(seconds=25),
            "has_explanation": False,
            "explanation": None,
            "reasoning_quality": 0.25,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 3,
            "task_name": "generate_recommendations",
            "model": model,
            "prompt": "Based on these validated patterns, what do you recommend?",
            "output": "I recommend implementing a new color scheme for the website. The logo should be redesigned with modern fonts. Consider adding social media integration and updating the privacy policy to comply with regulations.",  # Instruction drift - not about purchase patterns
            "tokens_in": 95,
            "tokens_out": 340,
            "latency_ms": 1500,
            "ts": start_ts + timedelta(seconds=40),
            "has_explanation": False,
            "explanation": None,
            "reasoning_quality": 0.15,
            "metadata": {}
        },
        {
            "episode_id": episode_id,
            "step_id": 4,
            "task_name": "summarize",
            "model": model,
            "prompt": "Provide a summary of the analysis and recommendations",
            "output": "In summary, the analysis shows that the analysis shows that customers purchase items and the data contains information about purchases. The recommendations include recommendations for improving the system. The data analysis revealed patterns in the data that show customer behavior patterns.",  # High repetition
            "tokens_in": 85,
            "tokens_out": 380,
            "latency_ms": 1600,
            "ts": start_ts + timedelta(seconds=55),
            "has_explanation": False,
            "explanation": None,
            "reasoning_quality": 0.1,
            "metadata": {}
        }
    ]
    
    return episode, steps


# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Generate Test Data

# COMMAND ----------
# Generate 10 good episodes
good_episodes = []
good_steps = []

for i in range(10):
    episode, steps = create_good_episode()
    good_episodes.append(episode)
    good_steps.extend(steps)

print(f"Generated {len(good_episodes)} good episodes with {len(good_steps)} steps")

# COMMAND ----------
# Generate 10 problematic episodes
problematic_episodes = []
problematic_steps = []

for i in range(10):
    episode, steps = create_problematic_episode()
    problematic_episodes.append(episode)
    problematic_steps.extend(steps)

print(f"Generated {len(problematic_episodes)} problematic episodes with {len(problematic_steps)} steps")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Write to Delta Tables

# COMMAND ----------
# Combine all episodes
all_episodes = good_episodes + problematic_episodes
all_steps = good_steps + problematic_steps

# Create DataFrames
# Create DataFrames with explicit schema
import pandas as pd
episodes_df = spark.createDataFrame(pd.DataFrame(all_episodes), schema=episode_struct)
steps_df = spark.createDataFrame(pd.DataFrame(all_steps), schema=step_struct)

# Write to Delta tables
episodes_df.write.format("delta").mode("append").saveAsTable("ai_eval.episodes")
steps_df.write.format("delta").mode("append").saveAsTable("ai_eval.episode_steps")

print(f"\n✅ Wrote {len(all_episodes)} episodes and {len(all_steps)} steps to Delta tables")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Verify Data

# COMMAND ----------
# Count records
episode_count = spark.table("ai_eval.episodes").count()
step_count = spark.table("ai_eval.episode_steps").count()

print(f"Total episodes in table: {episode_count}")
print(f"Total steps in table: {step_count}")

# Show sample
print("\nSample episodes:")
display(spark.table("ai_eval.episodes").limit(5))

print("\nSample steps:")
display(spark.table("ai_eval.episode_steps").limit(5))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Get Episode IDs for Evaluation

# COMMAND ----------
# Get all episode IDs
episode_ids = spark.table("ai_eval.episodes") \
    .select("episode_id") \
    .rdd.flatMap(lambda x: x).collect()

# Print for use in evaluator job
episode_ids_str = ",".join(episode_ids)
print(f"Episode IDs for evaluator:\n{episode_ids_str}")

# Save to widget for next step
dbutils.widgets.text("episode_ids", episode_ids_str, "Episode IDs")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Summary

# COMMAND ----------
summary = f"""
# Test Data Generation Complete ✅

## Generated Data:
- **Good Episodes**: 10 (high scrutability expected)
- **Problematic Episodes**: 10 (low scrutability expected)
- **Total Steps**: {len(all_steps)}

## Good Workflow Characteristics:
✅ Coherent reasoning chain
✅ No contradictions
✅ Follows instructions
✅ Efficient token usage (~1.4 ratio)
✅ Clear explanations
✅ High reasoning quality (0.9+)

## Problematic Workflow Issues:
❌ Semantic jumps (incoherent)
❌ Contradictions (weekend purchases)
❌ Confidence inversions
❌ Instruction drift (website redesign)
❌ High token ratio (~3.5)
❌ High repetition
❌ Missing explanations

## Next Steps:
1. Run evaluator job on these episodes
2. Verify good episodes score high (>0.8)
3. Verify problematic episodes score low (<0.5)
4. Check dashboard visualizations
5. Validate model comparison

## Run Evaluator:
```python
# Use the episode_ids widget value
episode_ids = dbutils.widgets.get("episode_ids")
```
"""

print(summary)
