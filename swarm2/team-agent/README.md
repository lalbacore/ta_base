# AI Workflow Evaluator (v0.3.1)

> **"This system is explicitly not designed to generate, modify, or execute AI workflows."**

Its sole function is **idempotent evaluation**: given the same inputs, it will always produce the same assessment. It exists to **observe, score, and attest** to AI behavior.

## Overview

A clean, focused library for evaluating the **scrutability** (transparency) of AI agent episodes on Databricks.

## Structure

```
ai_workflow_evaluator/
├── evaluator/
│   ├── episode.py      # Episode data structures & schema
│   ├── metrics.py      # Raw metric calculations (coherence, consistency)
│   ├── scoring.py      # Aggregation logic and scrutability thresholds
│   └── invariants.py   # Safety checks and assertions
├── pyproject.toml      # Package configuration
└── notebooks/
    └── demo_evaluator.ipynb  # Single source of truth demo
```

## Usage

```python
from ai_workflow_evaluator.evaluator import run_episode_evaluation

# Run idempotent evaluation
result = run_episode_evaluation(spark, episode_id="12345")

print(f"Score: {result.score} ({result.level})")
```

## Installation

```bash
pip install .
```
