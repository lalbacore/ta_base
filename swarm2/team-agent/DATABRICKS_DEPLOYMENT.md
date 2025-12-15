# Databricks Deployment Guide
# Step-by-step instructions for deploying the AI evaluation platform

## Prerequisites

- Databricks workspace (AWS, Azure, or GCP)
- Unity Catalog enabled
- Cluster with Spark 3.4+ and Python 3.10+
- MLflow enabled

---

## Step 1: Set Up Unity Catalog

### 1.1 Create Catalog (if needed)

```sql
CREATE CATALOG IF NOT EXISTS ai_evaluation
COMMENT 'AI Episode Evaluation Platform';

USE CATALOG ai_evaluation;
```

### 1.2 Create Schema

```sql
CREATE SCHEMA IF NOT EXISTS ai_eval
COMMENT 'AI Episode Scrutability Evaluation'
LOCATION 's3://your-bucket/ai_eval';  -- Update with your storage location
```

---

## Step 2: Upload Notebooks

### 2.1 Create Repo in Databricks

1. Go to **Repos** in Databricks workspace
2. Click **Add Repo**
3. Enter Git URL: `https://github.com/lalbacore/ta_base.git`
4. Path: `swarm2/team-agent`
5. Click **Create**

### 2.2 Verify Notebooks

Navigate to `/Repos/your-repo/swarm2/team-agent/notebooks/` and verify:
- `01_setup/create_tables.py`
- `02_evaluator/evaluator_job.py`
- `03_dashboard/scrutability_dashboard.py`
- `04_integration/sample_data_generator.py`

---

## Step 3: Create Delta Tables

### 3.1 Run Setup Notebook

1. Open `notebooks/01_setup/create_tables.py`
2. Attach to cluster
3. Update storage location in SQL (line 15):
   ```python
   LOCATION 's3://YOUR-BUCKET/ai_eval'
   ```
4. Run all cells
5. Verify tables created:
   ```sql
   SHOW TABLES IN ai_eval;
   ```

Expected output:
- `ai_eval.episodes`
- `ai_eval.episode_steps`
- `ai_eval.episode_evaluations`

---

## Step 4: Generate Sample Data

### 4.1 Run Data Generator

1. Open `notebooks/04_integration/sample_data_generator.py`
2. Run all cells
3. Verify data created:
   ```sql
   SELECT COUNT(*) FROM ai_eval.episodes;  -- Should be 20
   SELECT COUNT(*) FROM ai_eval.episode_steps;  -- Should be 100
   ```

### 4.2 Inspect Sample Data

```sql
-- Good episodes (should have high scrutability)
SELECT * FROM ai_eval.episodes 
WHERE metadata['type'] = 'good_workflow';

-- Problematic episodes (should have low scrutability)
SELECT * FROM ai_eval.episodes 
WHERE metadata['type'] = 'problematic_workflow';
```

---

## Step 5: Run Evaluator Job

### 5.1 Create Evaluator Job

1. Go to **Workflows** → **Jobs**
2. Click **Create Job**
3. Configure:
   - **Name**: `AI Episode Evaluator`
   - **Task**: Notebook
   - **Notebook path**: `/Repos/your-repo/swarm2/team-agent/notebooks/02_evaluator/evaluator_job.py`
   - **Cluster**: Select existing or create new
   - **Parameters**:
     ```json
     {
       "episode_ids": "ep1,ep2,ep3"  // Will be set dynamically
     }
     ```

### 5.2 Run Evaluator Manually

1. Open `notebooks/02_evaluator/evaluator_job.py`
2. Get episode IDs from data generator output
3. Create widget:
   ```python
   dbutils.widgets.text("episode_ids", "your,episode,ids,here", "Episode IDs")
   ```
4. Run all cells
5. Verify evaluations created:
   ```sql
   SELECT COUNT(*) FROM ai_eval.episode_evaluations;  -- Should be 20
   ```

---

## Step 6: View Dashboards

### 6.1 Scrutability Dashboard

1. Open `notebooks/03_dashboard/scrutability_dashboard.py`
2. Run all cells
3. Review visualizations:
   - Overview metrics
   - Distribution charts
   - Time series trends
   - Issue flags

### 6.2 Model Comparison

1. Open `notebooks/03_dashboard/model_comparison.py`
2. Run all cells
3. Review:
   - Model rankings
   - Statistical comparisons
   - Radar charts
   - Recommendations

---

## Step 7: Verify Results

### 7.1 Check Good Episodes

```sql
SELECT 
  e.episode_id,
  e.metadata['type'] as type,
  ev.scrutability_score,
  ev.scrutability_level
FROM ai_eval.episodes e
JOIN ai_eval.episode_evaluations ev ON e.episode_id = ev.episode_id
WHERE e.metadata['type'] = 'good_workflow'
ORDER BY ev.scrutability_score DESC;
```

**Expected**: Scores > 0.8, level = 'scrutable'

### 7.2 Check Problematic Episodes

```sql
SELECT 
  e.episode_id,
  e.metadata['type'] as type,
  ev.scrutability_score,
  ev.scrutability_level,
  ev.flags
FROM ai_eval.episodes e
JOIN ai_eval.episode_evaluations ev ON e.episode_id = ev.episode_id
WHERE e.metadata['type'] = 'problematic_workflow'
ORDER BY ev.scrutability_score ASC;
```

**Expected**: Scores < 0.5, level = 'inscrutable', flags present

---

## Step 8: Set Up Scheduled Jobs

### 8.1 Create Evaluator Schedule

1. Go to job created in Step 5
2. Click **Add trigger**
3. Configure:
   - **Trigger type**: Scheduled
   - **Schedule**: Every hour (or as needed)
   - **Parameters**: Dynamic episode IDs from upstream job

### 8.2 Create Data Pipeline

```python
# Upstream job emits episode_id
episode_id = "generated-episode-id"

# Trigger evaluator
dbutils.notebook.run(
    "/Repos/your-repo/swarm2/team-agent/notebooks/02_evaluator/evaluator_job.py",
    timeout_seconds=600,
    arguments={"episode_ids": episode_id}
)
```

---

## Step 9: MLflow Integration

### 9.1 View Experiments

1. Go to **Machine Learning** → **Experiments**
2. Find experiment created by evaluator
3. View runs with metrics:
   - `coherence_score`
   - `consistency_score`
   - `efficiency_score`
   - `scrutability_score`

### 9.2 Compare Models

```python
import mlflow

# Get runs for different models
runs = mlflow.search_runs(
    experiment_ids=["your-experiment-id"],
    order_by=["metrics.scrutability_score DESC"]
)

display(runs[["params.model", "metrics.scrutability_score"]])
```

---

## Step 10: Production Deployment

### 10.1 Update Storage Locations

Replace all `s3://your-bucket` with actual bucket:

```sql
-- In create_tables.py
LOCATION 's3://prod-ai-eval/episodes'
```

### 10.2 Configure Permissions

```sql
-- Grant access to schema
GRANT USAGE ON SCHEMA ai_eval TO `data-scientists`;
GRANT SELECT ON ALL TABLES IN SCHEMA ai_eval TO `data-scientists`;
```

### 10.3 Enable Auto-Optimization

```sql
ALTER TABLE ai_eval.episodes 
SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

---

## Troubleshooting

### Issue: Tables not found

**Solution**: Verify Unity Catalog schema exists
```sql
SHOW SCHEMAS IN ai_evaluation;
```

### Issue: Evaluator fails with import errors

**Solution**: Install dependencies on cluster
```bash
%pip install scipy numpy
```

### Issue: MLflow not logging

**Solution**: Check MLflow experiment exists
```python
import mlflow
mlflow.set_experiment("/Users/your-email/ai-evaluation")
```

### Issue: Low scrutability for good episodes

**Solution**: Check step data quality
```sql
SELECT * FROM ai_eval.episode_steps 
WHERE episode_id = 'problematic-episode-id';
```

---

## Next Steps

1. **Integrate with AI Pipelines**: Modify your AI workflows to emit episodes
2. **Create Alerts**: Set up notifications for low scrutability
3. **Build Custom Dashboards**: Create business-specific views
4. **Tune Thresholds**: Adjust scrutability thresholds for your use case

---

## Support

- **Documentation**: See README.md
- **SQL Queries**: See `sql/queries/scrutability_stats.sql`
- **Issues**: GitHub Issues

---

**Deployment Complete!** 🎉

Your Databricks AI Evaluation Platform is now ready to measure scrutability across models and workflows.
