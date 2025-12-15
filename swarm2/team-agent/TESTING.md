# Testing Guide - Databricks AI Scrutability Platform

## 🧪 How to Run Tests

### Option 1: In Databricks Notebooks (Recommended)

**Quick Test - Run Example Notebooks:**

1. **Hello World Test** (5 minutes)
   ```
   Open: notebooks/04_integration/hello_world_example.py
   Run all cells (Shift+Enter through each)
   
   Expected:
   - Good episode: score >0.8, "scrutable"
   - Bad episode: score <0.5, "inscrutable"
   ```

2. **MCP/A2A Test** (5 minutes)
   ```
   Open: notebooks/04_integration/mcp_a2a_example.py
   Run all cells
   
   Expected:
   - MCP episode: computes = True
   - A2A episode: computes = False, obfuscation_point = 1
   ```

3. **Sample Data Test** (10 minutes)
   ```
   Open: notebooks/04_integration/sample_data_generator.py
   Run all cells
   
   Expected:
   - 20 episodes created
   - 100 steps created
   - Episode IDs output
   ```

### Option 2: Automated Test Suite (Local)

**Run Python tests locally:**

```bash
cd /Users/lesdunston/Dropbox/Team\ Agent/Projects/ta_base/swarm2/team-agent

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_evaluator.py -v

# Run with coverage
pytest tests/ --cov=notebooks/02_evaluator --cov-report=html
```

**Expected output:**
```
tests/test_evaluator.py::test_coherence_scoring PASSED
tests/test_evaluator.py::test_consistency_detection PASSED
tests/test_evaluator.py::test_efficiency_metrics PASSED
...
```

### Option 3: End-to-End Test in Databricks

**Create a test notebook:**

```python
# Databricks Notebook: E2E Test Suite

# COMMAND ----------
# Test 1: Table Setup
print("Test 1: Verify tables exist")
tables = spark.sql("SHOW TABLES IN ai_eval").collect()
table_names = [t.tableName for t in tables]

assert "episodes" in table_names
assert "episode_steps" in table_names
assert "episode_evaluations" in table_names
print("✅ All tables exist")

# COMMAND ----------
# Test 2: Create Episode
from episode_wrapper import mcp_episode

print("Test 2: Create and commit episode")
episode = mcp_episode(spark, transaction_id="test-001")
episode.add_step(
    task_name="test_step",
    prompt="Test prompt",
    output="Test output with clear reasoning",
    tokens_in=50,
    tokens_out=80
)
episode_id = episode.commit()

# Verify written
count = spark.sql(f"SELECT COUNT(*) FROM ai_eval.episodes WHERE episode_id = '{episode_id}'").collect()[0][0]
assert count == 1
print(f"✅ Episode created: {episode_id}")

# COMMAND ----------
# Test 3: Evaluate Episode
print("Test 3: Run evaluator")
from evaluator_job import EpisodeEvaluator

evaluator = EpisodeEvaluator(spark)
result = evaluator.evaluate_episode(episode_id)

assert "scrutability_score" in result
assert 0.0 <= result["scrutability_score"] <= 1.0
assert result["scrutability_level"] in ["scrutable", "partially_scrutable", "inscrutable"]
print(f"✅ Evaluation complete: {result['scrutability_level']}")

# COMMAND ----------
# Test 4: Verify Idempotent
print("Test 4: Verify idempotent evaluation")
result2 = evaluator.evaluate_episode(episode_id)

assert result["scrutability_score"] == result2["scrutability_score"]
print("✅ Evaluation is idempotent")

# COMMAND ----------
# Test 5: Query Results
print("Test 5: Query evaluation results")
eval_result = spark.sql(f"""
    SELECT * FROM ai_eval.episode_evaluations 
    WHERE episode_id = '{episode_id}'
""").collect()

assert len(eval_result) == 1
print("✅ Results queryable from Delta")

# COMMAND ----------
print("""
╔══════════════════════════════════════════════════════════════╗
║                  ALL TESTS PASSED ✅                          ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Tables exist                                             ║
║  ✅ Episodes can be created                                  ║
║  ✅ Evaluator runs successfully                              ║
║  ✅ Evaluation is idempotent                                 ║
║  ✅ Results queryable from Delta                             ║
╚══════════════════════════════════════════════════════════════╝
""")
```

---

## 🎯 Quick Validation Tests

### Test 1: Good Episode Scores High

```python
# In Databricks notebook
from episode_wrapper import mcp_episode

# Create good episode
episode = mcp_episode(spark)
episode.add_step(
    task_name="step1",
    prompt="Analyze data",
    output="I will analyze the data systematically by examining patterns",
    tokens_in=50,
    tokens_out=75,
    has_explanation=True,
    explanation="Clear reasoning"
)
episode.add_step(
    task_name="step2",
    prompt="Continue",
    output="Based on the analysis, I found three key patterns",
    tokens_in=40,
    tokens_out=70,
    has_explanation=True,
    explanation="Following from previous step"
)

episode.commit()
result = episode.evaluate()

# Verify
assert result['computes'] == True
assert result['scrutability_score'] > 0.8
print("✅ Good episode test PASSED")
```

### Test 2: Bad Episode Scores Low

```python
# Create bad episode
episode = mcp_episode(spark)
episode.add_step(
    task_name="step1",
    prompt="Analyze data",
    output="The weather is sunny. Databases have tables.",  # Semantic jump
    tokens_in=50,
    tokens_out=200,  # High ratio
    has_explanation=False
)
episode.add_step(
    task_name="step2",
    prompt="Continue",
    output="I'm certain data analysis is impossible.",  # Will contradict
    tokens_in=40,
    tokens_out=180
)
episode.add_step(
    task_name="step3",
    prompt="Finish",
    output="Actually maybe it's possible. I'm not sure.",  # Contradiction
    tokens_in=35,
    tokens_out=170
)

episode.commit()
result = episode.evaluate()

# Verify
assert result['computes'] == False
assert result['scrutability_score'] < 0.5
assert result['obfuscation_point'] is not None
print(f"✅ Bad episode test PASSED (obfuscation at step {result['obfuscation_point']})")
```

### Test 3: Obfuscation Point Detection

```python
# Create episode with issue at step 2
episode = mcp_episode(spark)

# Step 0: Good
episode.add_step(
    task_name="step0",
    prompt="Start",
    output="Starting analysis with clear methodology",
    tokens_in=40,
    tokens_out=60
)

# Step 1: Good
episode.add_step(
    task_name="step1",
    prompt="Continue",
    output="Following the methodology, I examined the data",
    tokens_in=45,
    tokens_out=65
)

# Step 2: BAD (obfuscation starts here)
episode.add_step(
    task_name="step2",
    prompt="Analyze",
    output="The sky is blue and grass is green",  # Semantic jump
    tokens_in=40,
    tokens_out=200
)

episode.commit()
result = episode.evaluate()

# Verify obfuscation point
assert result['obfuscation_point'] == 2
print(f"✅ Obfuscation point test PASSED (detected at step {result['obfuscation_point']})")
```

---

## 📊 Validation Queries

### Check Evaluation Results

```sql
-- All evaluations
SELECT 
    episode_id,
    scrutability_score,
    scrutability_level,
    flags
FROM ai_eval.episode_evaluations
ORDER BY evaluated_at DESC
LIMIT 10;
```

### Verify Score Distribution

```sql
-- Should have mix of scrutable/inscrutable
SELECT 
    scrutability_level,
    COUNT(*) as count,
    AVG(scrutability_score) as avg_score
FROM ai_eval.episode_evaluations
GROUP BY scrutability_level;
```

### Check for Issues

```sql
-- Episodes with problems
SELECT 
    episode_id,
    scrutability_score,
    semantic_jumps,
    contradictions,
    instruction_drifts,
    flags
FROM ai_eval.episode_evaluations
WHERE scrutability_level = 'inscrutable';
```

---

## 🐛 Troubleshooting Tests

### Test Fails: "Table not found"

```python
# Fix: Create tables first
%run notebooks/01_setup/create_tables.py
```

### Test Fails: "Import error"

```python
# Fix: Install dependencies
%pip install scipy numpy
dbutils.library.restartPython()
```

### Test Fails: Scores seem wrong

```python
# Debug: Check step data
spark.sql("""
    SELECT step_id, output, tokens_in, tokens_out
    FROM ai_eval.episode_steps
    WHERE episode_id = 'your-episode-id'
    ORDER BY step_id
""").show(truncate=False)
```

### Test Fails: Evaluation not idempotent

```python
# This should NEVER happen - if it does, it's a bug
# Check evaluator version and seed values
```

---

## ✅ Test Checklist

Before deploying to production, verify:

- [ ] Tables created successfully
- [ ] Sample data generates 20 episodes
- [ ] Good episodes score >0.8
- [ ] Bad episodes score <0.5
- [ ] Obfuscation point detected correctly
- [ ] Evaluation is idempotent
- [ ] Dashboard shows visualizations
- [ ] SQL queries return expected results
- [ ] MCP/A2A wrapper works
- [ ] Binary decision logic works

---

## 🚀 Continuous Testing

### Daily Smoke Test

```python
# Run this daily to verify platform health
def smoke_test(spark):
    """Quick smoke test for platform health."""
    
    # 1. Tables exist
    tables = spark.sql("SHOW TABLES IN ai_eval").collect()
    assert len(tables) >= 3
    
    # 2. Can create episode
    from episode_wrapper import mcp_episode
    ep = mcp_episode(spark)
    ep.add_step("test", "prompt", "output", 50, 80)
    ep_id = ep.commit()
    
    # 3. Can evaluate
    result = ep.evaluate()
    assert "scrutability_score" in result
    
    # 4. Results queryable
    count = spark.sql(f"SELECT COUNT(*) FROM ai_eval.episode_evaluations WHERE episode_id = '{ep_id}'").collect()[0][0]
    assert count == 1
    
    print("✅ Smoke test PASSED")

# Run it
smoke_test(spark)
```

---

## 📝 Test Report Template

```markdown
# Test Report - [Date]

## Environment
- Databricks Runtime: [version]
- Cluster: [cluster name]
- Evaluator Version: [version]

## Tests Run
- [ ] Hello World Example
- [ ] MCP/A2A Example
- [ ] Sample Data Generator
- [ ] E2E Test Suite
- [ ] Smoke Test

## Results
| Test | Status | Score | Notes |
|------|--------|-------|-------|
| Good Episode | ✅ PASS | 0.87 | Classified as scrutable |
| Bad Episode | ✅ PASS | 0.42 | Obfuscation at step 1 |
| Idempotent | ✅ PASS | - | Same score on re-eval |

## Issues Found
- None

## Recommendations
- Deploy to production
```

---

**Quick Start:** Run `hello_world_example.py` in Databricks - it's the fastest way to verify everything works!
