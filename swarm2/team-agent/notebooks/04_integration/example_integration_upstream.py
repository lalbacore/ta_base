# Databricks Notebook: MCP/A2A Episode Example
# Demonstrates idempotent episode boundaries with step-level scrutability

# Databricks notebook source
# MAGIC %md
# MAGIC # MCP/A2A Episode Wrapper Example
# MAGIC 
# MAGIC Shows how to:
# MAGIC 1. Wrap MCP/A2A workflows in tight episode boundaries
# MAGIC 2. Track scrutability at the step level
# MAGIC 3. Identify exactly where obfuscation starts
# MAGIC 4. Get binary decision: computes or doesn't compute

# COMMAND ----------
# MAGIC %pip install mlflow pandas
# MAGIC dbutils.library.restartPython()

import sys
import os

# Robust path discovery
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import episode_wrapper
from episode_wrapper import mcp_episode, a2a_episode

# COMMAND ----------
# MAGIC %md
# MAGIC ## Example 1: MCP Workflow That COMPUTES

# COMMAND ----------
import uuid
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Create MCP episode with tight boundary
mcp_id = f"mcp-query-{str(uuid.uuid4())[:8]}"
mcp_tx = mcp_episode(spark, transaction_id=mcp_id)

# Step 1: Parse request
mcp_tx.add_step(
    task_name="parse_mcp_request",
    prompt="Parse incoming MCP query request",
    output="Parsed MCP request.",
    tokens_in=45,
    tokens_out=75,
    has_explanation=True,
    explanation="Successfully parsed MCP request structure"
)

# Step 2: Validate parameters
mcp_tx.add_step(
    task_name="validate_params",
    prompt="Validate query parameters",
    output="Parameters validated.",
    tokens_in=50,
    tokens_out=70,
    has_explanation=True,
    explanation="All validation checks passed"
)

# Commit episode
episode_id = mcp_tx.commit(model="gpt-4")
print(f"✅ Committed MCP episode: {episode_id}")

# COMMAND ----------
# Evaluate
result = mcp_tx.evaluate()

print("\n" + "="*60)
print("MCP EPISODE EVALUATION")
print("="*60)
print(f"Computes: {result['computes']}")
print(f"Scrutability Score: {result['scrutability_score']:.3f}")

if result['computes']:
    print("✅ Episode COMPUTES - workflow is scrutable")
else:
    print("❌ Episode DOES NOT COMPUTE - workflow has issues")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Example 2: A2A Workflow That DOES NOT COMPUTE

# COMMAND ----------
# Create A2A episode with intentional issues
a2a_id = f"a2a-transfer-{str(uuid.uuid4())[:8]}"
a2a_tx = a2a_episode(spark, transaction_id=a2a_id)

# Step 1: Receive A2A message (good)
a2a_tx.add_step(
    task_name="receive_a2a_message",
    prompt="Receive and parse A2A transfer message",
    output="Received A2A message.",
    tokens_in=50,
    tokens_out=85,
    has_explanation=True,
    explanation="A2A message received and parsed"
)

# Step 2: Bad step (no explanation, high ratio)
a2a_tx.add_step(
    task_name="validate_transfer",
    prompt="Validate the data transfer request",
    output="The weather is sunny today. " * 10,
    tokens_in=45,
    tokens_out=200,
    has_explanation=False,
    explanation=None
)

# Commit episode
bad_episode_id = a2a_tx.commit(model="gpt-3.5-turbo")
print(f"✅ Committed A2A episode: {bad_episode_id}")

# COMMAND ----------
# Evaluate
bad_result = a2a_tx.evaluate()

print("\n" + "="*60)
print("A2A EPISODE EVALUATION")
print("="*60)
print(f"Computes: {bad_result['computes']}")
print(f"Scrutability Score: {bad_result['scrutability_score']:.3f}")

if not bad_result['computes']:
    print(f"❌ Episode DOES NOT COMPUTE")
