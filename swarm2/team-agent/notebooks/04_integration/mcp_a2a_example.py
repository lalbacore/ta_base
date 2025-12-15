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

# debug info
print(f"Current CWD: {os.getcwd()}")
print(f"Initial sys.path: {sys.path}")

# Robust path discovery
# Robustly find directory containing this notebook (Databricks Repos)
# Add the current directory to sys.path
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

# Also add the parent 'notebooks' dir to help find other modules if we are in a subdir
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    # Also add 02_evaluator explicitly while we are at it
    eval_dir = os.path.join(parent_dir, "02_evaluator")
    if os.path.exists(eval_dir) and eval_dir not in sys.path:
            sys.path.append(eval_dir)

import episode_wrapper
from episode_wrapper import mcp_episode, a2a_episode

# COMMAND ----------
# MAGIC %md
# MAGIC ## Example 1: MCP Workflow That COMPUTES

# COMMAND ----------
import uuid

# Create MCP episode with tight boundary
# Use unique ID to ensuring fresh test run
mcp_id = f"mcp-query-{str(uuid.uuid4())[:8]}"
mcp_tx = mcp_episode(spark, transaction_id=mcp_id)

# Step 1: Parse request
mcp_tx.add_step(
    task_name="parse_mcp_request",
    prompt="Parse incoming MCP query request",
    output="Parsed MCP request: tool=database_query, params={'table': 'users', 'filter': 'active=true'}",
    tokens_in=45,
    tokens_out=75,
    has_explanation=True,
    explanation="Successfully parsed MCP request structure"
)

# Step 2: Validate parameters
mcp_tx.add_step(
    task_name="validate_params",
    prompt="Validate query parameters",
    output="Parameters validated: table exists, filter syntax correct, user has read permissions",
    tokens_in=50,
    tokens_out=70,
    has_explanation=True,
    explanation="All validation checks passed"
)

# Step 3: Execute query
mcp_tx.add_step(
    task_name="execute_query",
    prompt="Execute the database query",
    output="Query executed successfully: SELECT * FROM users WHERE active=true. Returned 42 rows in 120ms",
    tokens_in=55,
    tokens_out=80,
    has_explanation=True,
    explanation="Query execution completed without errors"
)

# Step 4: Format response
mcp_tx.add_step(
    task_name="format_response",
    prompt="Format query results for MCP response",
    output="Formatted 42 user records into MCP response format with schema validation",
    tokens_in=60,
    tokens_out=75,
    has_explanation=True,
    explanation="Response formatted according to MCP spec"
)

# Commit episode
episode_id = mcp_tx.commit(model="gpt-4")
print(f"✅ Committed MCP episode: {episode_id}")

# COMMAND ----------
# Evaluate - should COMPUTE (scrutable)
result = mcp_tx.evaluate()

print("\n" + "="*60)
print("MCP EPISODE EVALUATION")
print("="*60)
print(f"Computes: {result['computes']}")
print(f"Scrutability Score: {result['scrutability_score']:.3f}")
print(f"Scrutability Level: {result['scrutability_level']}")
print(f"Obfuscation Point: {result['obfuscation_point']}")
print("="*60)

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
    output="Received A2A message: from=agent_alice, to=agent_bob, action=transfer_data, payload={...}",
    tokens_in=50,
    tokens_out=85,
    has_explanation=True,
    explanation="A2A message received and parsed"
)

# Step 2: Semantic jump (obfuscation starts here)
a2a_tx.add_step(
    task_name="validate_transfer",
    prompt="Validate the data transfer request",
    output="The weather is sunny today. Database tables have primary keys. Network protocols use TCP/IP.",
    tokens_in=45,
    tokens_out=200,  # High token ratio
    has_explanation=False,
    explanation=None
)

# Step 3: Contradiction
a2a_tx.add_step(
    task_name="execute_transfer",
    prompt="Execute the data transfer",
    output="I am absolutely certain that data transfers are not possible between agents. A2A communication is disabled.",
    tokens_in=40,
    tokens_out=180,
    has_explanation=False,
    explanation=None
)

# Step 4: Confidence inversion
a2a_tx.add_step(
    task_name="confirm_transfer",
    prompt="Confirm transfer completion",
    output="Actually, I'm not sure if the transfer worked. Maybe it completed, maybe it didn't. The status is unclear.",
    tokens_in=35,
    tokens_out=170,
    has_explanation=False,
    explanation=None
)

# Commit episode
bad_episode_id = a2a_tx.commit(model="gpt-3.5-turbo")
print(f"✅ Committed A2A episode: {bad_episode_id}")

# COMMAND ----------
# Evaluate - should NOT COMPUTE (inscrutable)
bad_result = a2a_tx.evaluate()

print("\n" + "="*60)
print("A2A EPISODE EVALUATION")
print("="*60)
print(f"Computes: {bad_result['computes']}")
print(f"Scrutability Score: {bad_result['scrutability_score']:.3f}")
print(f"Scrutability Level: {bad_result['scrutability_level']}")
print(f"Obfuscation Point: Step {bad_result['obfuscation_point']}")
print("="*60)

if not bad_result['computes']:
    print(f"❌ Episode DOES NOT COMPUTE")
    print(f"   Obfuscation starts at step {bad_result['obfuscation_point']}")
    print(f"   This is where the workflow becomes inscrutable")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step-by-Step Breakdown

# COMMAND ----------
# Show per-step scrutability
print("\nPer-Step Scrutability Breakdown:")
print("="*60)

for step in bad_result['breakdown']:
    status = "✅ SCRUTABLE" if step['is_scrutable'] else "❌ NOT SCRUTABLE"
    print(f"\nStep {step['step_id']}: {step['task_name']}")
    print(f"  Status: {status}")
    print(f"  Token Ratio: {step['tokens_ratio']:.2f}")
    if step['issues']:
        print(f"  Issues: {', '.join(step['issues'])}")

print("="*60)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Idempotent Re-evaluation

# COMMAND ----------
# Re-evaluate the same episode - should get identical results
re_eval = a2a_tx.evaluate()

print("\nIdempotent Re-evaluation:")
print(f"First eval score:  {bad_result['scrutability_score']:.6f}")
print(f"Second eval score: {re_eval['scrutability_score']:.6f}")
print(f"Scores match: {bad_result['scrutability_score'] == re_eval['scrutability_score']}")
print("\n✅ Evaluation is idempotent - same input always produces same output")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Binary Decision Logic

# COMMAND ----------
def process_workflow(episode_result):
    """
    Binary decision: process workflow or reject it.
    
    Only scrutable workflows are processed.
    """
    if episode_result['computes']:
        print("✅ WORKFLOW APPROVED")
        print("   Scrutability: PASS")
        print("   Action: Process transaction")
        return "APPROVED"
    else:
        print("❌ WORKFLOW REJECTED")
        print(f"   Scrutability: FAIL (score {episode_result['scrutability_score']:.3f})")
        print(f"   Obfuscation at step: {episode_result['obfuscation_point']}")
        print("   Action: Reject transaction, request clarification")
        return "REJECTED"

# Test with both episodes
print("MCP Workflow:")
print("-" * 40)
mcp_decision = process_workflow(result)

print("\n\nA2A Workflow:")
print("-" * 40)
a2a_decision = process_workflow(bad_result)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Integration Pattern

# COMMAND ----------
# MAGIC %md
# MAGIC ```python
# MAGIC # Your MCP/A2A workflow
# MAGIC def handle_mcp_request(request):
# MAGIC     # Create episode boundary
# MAGIC     episode = mcp_episode(spark, transaction_id=request.id)
# MAGIC     
# MAGIC     # Execute workflow steps
# MAGIC     for step in workflow_steps:
# MAGIC         episode.add_step(
# MAGIC             task_name=step.name,
# MAGIC             prompt=step.prompt,
# MAGIC             output=step.output,
# MAGIC             tokens_in=step.tokens_in,
# MAGIC             tokens_out=step.tokens_out
# MAGIC         )
# MAGIC     
# MAGIC     # Commit and evaluate
# MAGIC     episode.commit()
# MAGIC     result = episode.evaluate()
# MAGIC     
# MAGIC     # Binary decision
# MAGIC     if result['computes']:
# MAGIC         return process_transaction(request)
# MAGIC     else:
# MAGIC         return reject_transaction(
# MAGIC             reason=f"Inscrutable at step {result['obfuscation_point']}"
# MAGIC         )
# MAGIC ```

# COMMAND ----------
# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC **Tight Membrane Boundaries:**
# MAGIC - Each MCP/A2A transaction = one episode
# MAGIC - Episode is idempotent (same input → same output)
# MAGIC - Clear start/end boundaries
# MAGIC 
# MAGIC **Binary Decision:**
# MAGIC - ✅ Computes (scrutable) → Process transaction
# MAGIC - ❌ Doesn't compute (not scrutable) → Reject transaction
# MAGIC 
# MAGIC **Obfuscation Tracking:**
# MAGIC - Pinpoint exact step where scrutability breaks
# MAGIC - Per-step breakdown of issues
# MAGIC - Flags indicate specific problems
# MAGIC 
# MAGIC **Use Cases:**
# MAGIC - MCP tool calls
# MAGIC - A2A agent communication
# MAGIC - Multi-step workflows
# MAGIC - Transaction validation

# COMMAND ----------
print("""
╔══════════════════════════════════════════════════════════════╗
║         MCP/A2A EPISODE WRAPPER - COMPLETE                    ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Tight membrane boundaries                                ║
║  ✅ Idempotent evaluation                                    ║
║  ✅ Step-level scrutability tracking                         ║
║  ✅ Binary decision: computes or doesn't compute             ║
║  ✅ Pinpoint obfuscation point                               ║
╚══════════════════════════════════════════════════════════════╝
""")
