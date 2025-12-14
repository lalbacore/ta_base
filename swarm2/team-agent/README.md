# Databricks AI Episode Evaluation Platform

## Overview

A **scrutability-focused AI evaluation platform** built on Databricks, designed to measure how transparent and explainable AI decision-making is across different agents, swarms, and LLMs.

**Key Features:**
- 🔍 **Scrutability Measurement** - Quantify AI transparency (scrutable, partially scrutable, inscrutable)
- ⚡ **Spark-Powered** - Embarrassingly parallel, deterministic evaluation
- 🗄️ **Delta Lake** - Immutable episode storage with Unity Catalog governance
- 📊 **MLflow Integration** - Model comparison and experiment tracking
- 📈 **Real-time Dashboards** - Interactive scrutability analytics

---

## Architecture

```
AI Pipeline → episode_steps (Delta) → Evaluator (Spark) → episode_evaluations (Delta)
                                                         ↓
                                                    MLflow Metrics
```

**Components:**
- **Delta Lake Tables** - Immutable episode storage (Unity Catalog)
- **Spark Evaluator** - Stateless, parallel scrutability scoring
- **MLflow** - Metrics tracking and model comparison
- **Dashboards** - Interactive Databricks notebooks

---

## Scrutability Levels

### Scrutable (0.8 - 1.0)
Fully transparent decision-making with complete reasoning chain.

### Partially Scrutable (0.3 - 0.79)
Some transparency with quantified degree of explainability.

### Inscrutable (0.0 - 0.29)
Black box decision-making with minimal explainability.

---

## Evaluation Metrics

**Coherence (40%)** - Semantic consistency using embeddings
- Embedding similarity between steps
- Semantic jump detection
- Reasoning chain completeness

**Consistency (40%)** - Logical consistency
- Contradiction detection
- Confidence inversion tracking
- Instruction drift analysis

**Efficiency (20%)** - Token efficiency
- Token ratio (output/input)
- Tokens per semantic delta
- Repetition rate

---

## Quick Start

### 1. Set Up Delta Tables

```bash
# Run setup notebook
databricks workspace import notebooks/01_setup/create_tables.py
```

Or execute SQL directly:
```sql
-- Create schema
CREATE SCHEMA ai_eval;

-- Create tables
SOURCE sql/schema/episodes.sql;
SOURCE sql/schema/episode_steps.sql;
SOURCE sql/schema/episode_evaluations.sql;
```

### 2. Run Evaluator

```python
from evaluator_job import EpisodeEvaluator

evaluator = EpisodeEvaluator(spark)
evaluator.evaluate_episode("episode-123")
```

### 3. View Results

```sql
SELECT 
  episode_id,
  scrutability_score,
  scrutability_level,
  coherence_score,
  consistency_score,
  efficiency_score,
  flags
FROM ai_eval.episode_evaluations
WHERE scrutability_level = 'inscrutable'
ORDER BY evaluated_at DESC;
```

---

## Project Structure

```
databricks-ai-eval/
├── notebooks/
│   ├── 01_setup/              # Delta table creation
│   ├── 02_evaluator/          # Spark evaluation jobs
│   ├── 03_dashboard/          # Interactive dashboards
│   └── 04_integration/        # AI pipeline integration
├── sql/
│   ├── schema/                # Delta table DDL
│   └── queries/               # Common queries
├── jobs/                      # Databricks job configs
├── frontend/                  # Vue.js dashboard (optional)
├── tests/                     # Spark job tests
└── archive/                   # Archived code (crypto, PKI, etc.)
```

---

## Delta Lake Tables

### `ai_eval.episodes`
Immutable episode records (read-only truth).

| Column | Type | Description |
|--------|------|-------------|
| episode_id | STRING | Unique identifier |
| run_id | STRING | Databricks run_id |
| model | STRING | LLM model used |
| start_ts | TIMESTAMP | Start time |
| status | STRING | running, completed, failed |

### `ai_eval.episode_steps`
Execution trace with token metrics.

| Column | Type | Description |
|--------|------|-------------|
| episode_id | STRING | Foreign key |
| step_id | INT | Step sequence |
| prompt | STRING | Input prompt |
| output | STRING | Generated output |
| tokens_in | INT | Input tokens |
| tokens_out | INT | Output tokens |

### `ai_eval.episode_evaluations`
Scrutability scores and flags.

| Column | Type | Description |
|--------|------|-------------|
| episode_id | STRING | Foreign key |
| scrutability_score | DOUBLE | Overall score (0.0-1.0) |
| scrutability_level | STRING | Classification |
| coherence_score | DOUBLE | Semantic coherence |
| consistency_score | DOUBLE | Logical consistency |
| efficiency_score | DOUBLE | Token efficiency |
| flags | ARRAY<STRING> | Issue flags |

---

## Evaluation Process

1. **AI Pipeline Runs** → Emits episodes and steps to Delta
2. **Evaluator Triggered** → Spark job processes episode (non-blocking)
3. **Scores Computed** → Coherence, consistency, efficiency
4. **Results Stored** → Written to Delta evaluations table
5. **Metrics Logged** → Sent to MLflow for tracking

---

## MLflow Integration

```python
import mlflow

# Log scrutability metrics
mlflow.log_metric("coherence_score", 0.85)
mlflow.log_metric("consistency_score", 0.72)
mlflow.log_metric("efficiency_score", 0.68)
mlflow.log_metric("scrutability_score", 0.78)

# Log parameters
mlflow.log_param("model", "gpt-4")
mlflow.log_param("episode_id", "episode-123")

# Tag scrutability level
mlflow.set_tag("scrutability_level", "partially_scrutable")
```

---

## Model Comparison

Compare scrutability across different LLMs:

```python
from model_comparison import compare_models_mlflow

results = compare_models_mlflow(spark, "gpt-4", "claude-3")
# {
#   "gpt-4": 0.72,
#   "claude-3": 0.81,
#   "winner": "claude-3"
# }
```

---

## Development

### Running Tests

```bash
# Spark tests
pytest tests/test_evaluator.py

# Integration tests
pytest tests/test_delta_tables.py
```

### Local Development

```python
# Initialize Spark session
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("AI Evaluator") \
    .getOrCreate()

# Run evaluator locally
from evaluator_job import EpisodeEvaluator
evaluator = EpisodeEvaluator(spark)
evaluator.evaluate_episode("test-episode")
```

---

## Deployment

### Databricks Job Configuration

```json
{
  "name": "AI Episode Evaluator",
  "new_cluster": {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 4
  },
  "notebook_task": {
    "notebook_path": "/Repos/ai-eval/notebooks/02_evaluator/evaluator_job",
    "base_parameters": {
      "episode_ids": "episode-1,episode-2,episode-3"
    }
  }
}
```

---

## Migration from Previous Version

This platform replaces the previous Flask-based system with a Databricks-native architecture.

**What Changed:**
- ✅ Flask → Spark (scalable, parallel)
- ✅ Files → Delta Lake (immutable, governed)
- ✅ Docker → Databricks Jobs (managed)
- ✅ Effectiveness → Scrutability (transparency-focused)

**Archived Components:**
- Crypto/PKI layer → `archive/crypto/`
- Registry/Governance → `archive/registry/`
- Flask backend → `archive/flask_backend/`

---

## Contributing

1. Create feature branch
2. Add tests
3. Submit PR
4. Update documentation

---

## License

MIT License - See LICENSE file

---

## Support

For questions or issues:
- Documentation: `/docs`
- Issues: GitHub Issues
- Slack: #ai-evaluation

---

**Built with ❤️ on Databricks**
