# Databricks Notebook: Model Comparison
# Compare scrutability across different LLM models

# Databricks notebook source
# MAGIC %md
# MAGIC # Model Scrutability Comparison
# MAGIC 
# MAGIC Compare transparency and explainability across different LLM models.

# COMMAND ----------
from pyspark.sql.functions import *
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats as scipy_stats
import pandas as pd
import mlflow

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Load Model Data

# COMMAND ----------
# Join episodes with evaluations
model_data = spark.table("ai_eval.episodes") \
    .join(spark.table("ai_eval.episode_evaluations"), "episode_id") \
    .select(
        "episode_id",
        "model",
        "scrutability_score",
        "coherence_score",
        "consistency_score",
        "efficiency_score",
        "semantic_jumps",
        "contradictions",
        "instruction_drifts",
        "token_ratio",
        "repetition_rate"
    )

display(model_data.groupBy("model").count().orderBy(desc("count")))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Statistical Comparison

# COMMAND ----------
def compare_models_statistical(model_a, model_b):
    """
    Compare two models using statistical tests.
    
    Returns p-value and effect size.
    """
    # Get scores for each model
    scores_a = model_data.filter(col("model") == model_a) \
        .select("scrutability_score").toPandas()["scrutability_score"]
    
    scores_b = model_data.filter(col("model") == model_b) \
        .select("scrutability_score").toPandas()["scrutability_score"]
    
    # T-test
    t_stat, p_value = scipy_stats.ttest_ind(scores_a, scores_b)
    
    # Effect size (Cohen's d)
    mean_diff = scores_a.mean() - scores_b.mean()
    pooled_std = ((scores_a.std()**2 + scores_b.std()**2) / 2) ** 0.5
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0
    
    return {
        "model_a": model_a,
        "model_b": model_b,
        "mean_a": scores_a.mean(),
        "mean_b": scores_b.mean(),
        "p_value": p_value,
        "cohens_d": cohens_d,
        "significant": p_value < 0.05,
        "winner": model_a if scores_a.mean() > scores_b.mean() else model_b
    }

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Pairwise Model Comparison

# COMMAND ----------
# Get all models
models = model_data.select("model").distinct().rdd.flatMap(lambda x: x).collect()

print(f"Found {len(models)} models: {models}")

# Compare all pairs
comparisons = []
for i, model_a in enumerate(models):
    for model_b in models[i+1:]:
        result = compare_models_statistical(model_a, model_b)
        comparisons.append(result)

comparisons_df = pd.DataFrame(comparisons)
display(comparisons_df)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Model Rankings

# COMMAND ----------
# Aggregate model statistics
model_rankings = model_data.groupBy("model").agg(
    count("*").alias("episodes"),
    avg("scrutability_score").alias("avg_scrutability"),
    avg("coherence_score").alias("avg_coherence"),
    avg("consistency_score").alias("avg_consistency"),
    avg("efficiency_score").alias("avg_efficiency"),
    stddev("scrutability_score").alias("std_scrutability"),
    avg("semantic_jumps").alias("avg_jumps"),
    avg("contradictions").alias("avg_contradictions"),
    avg("token_ratio").alias("avg_token_ratio")
).orderBy(desc("avg_scrutability")).toPandas()

display(model_rankings)

# COMMAND ----------
# Ranking visualization
fig = px.bar(
    model_rankings,
    x="model",
    y="avg_scrutability",
    error_y="std_scrutability",
    title="Model Scrutability Rankings",
    labels={"avg_scrutability": "Average Scrutability Score"},
    color="avg_scrutability",
    color_continuous_scale="RdYlGn",
    range_color=[0, 1]
)
fig.update_layout(yaxis_range=[0, 1])
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Component Score Comparison

# COMMAND ----------
# Radar chart for model comparison
def create_radar_chart(models_to_compare):
    """Create radar chart comparing models across metrics."""
    
    metrics = ["avg_coherence", "avg_consistency", "avg_efficiency"]
    
    fig = go.Figure()
    
    for model in models_to_compare:
        model_stats = model_rankings[model_rankings["model"] == model].iloc[0]
        
        values = [model_stats[m] for m in metrics]
        values.append(values[0])  # Close the polygon
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics + [metrics[0]],
            fill='toself',
            name=model
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="Model Component Comparison"
    )
    
    return fig

# Compare top 3 models
top_models = model_rankings.head(min(3, len(model_rankings)))["model"].tolist()
fig = create_radar_chart(top_models)
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. MLflow Model Comparison

# COMMAND ----------
def compare_models_mlflow(model_a, model_b):
    """
    Compare models using MLflow experiment data.
    """
    client = mlflow.tracking.MlflowClient()
    
    # Search for runs with each model
    runs_a = client.search_runs(
        experiment_ids=["0"],  # Update with your experiment ID
        filter_string=f"params.model = '{model_a}'"
    )
    
    runs_b = client.search_runs(
        experiment_ids=["0"],
        filter_string=f"params.model = '{model_b}'"
    )
    
    if not runs_a or not runs_b:
        print(f"No MLflow runs found for {model_a} or {model_b}")
        return None
    
    # Aggregate metrics
    avg_scrutability_a = sum(r.data.metrics.get("scrutability_score", 0) for r in runs_a) / len(runs_a)
    avg_scrutability_b = sum(r.data.metrics.get("scrutability_score", 0) for r in runs_b) / len(runs_b)
    
    return {
        "model_a": model_a,
        "model_b": model_b,
        "avg_scrutability_a": avg_scrutability_a,
        "avg_scrutability_b": avg_scrutability_b,
        "runs_a": len(runs_a),
        "runs_b": len(runs_b),
        "winner": model_a if avg_scrutability_a > avg_scrutability_b else model_b,
        "difference": abs(avg_scrutability_a - avg_scrutability_b)
    }

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Use Case Recommendations

# COMMAND ----------
def recommend_model_for_use_case(use_case):
    """
    Recommend best model for specific use case.
    
    Use cases:
    - "transparency": Highest scrutability
    - "performance": Balance of all metrics
    - "efficiency": Best token efficiency
    - "consistency": Fewest contradictions
    """
    
    if use_case == "transparency":
        best = model_rankings.nlargest(1, "avg_scrutability")
        metric = "scrutability"
    elif use_case == "performance":
        # Weighted score
        model_rankings["performance_score"] = (
            model_rankings["avg_coherence"] * 0.4 +
            model_rankings["avg_consistency"] * 0.4 +
            model_rankings["avg_efficiency"] * 0.2
        )
        best = model_rankings.nlargest(1, "performance_score")
        metric = "overall performance"
    elif use_case == "efficiency":
        best = model_rankings.nlargest(1, "avg_efficiency")
        metric = "efficiency"
    elif use_case == "consistency":
        best = model_rankings.nsmallest(1, "avg_contradictions")
        metric = "consistency"
    else:
        return None
    
    return {
        "use_case": use_case,
        "recommended_model": best["model"].values[0],
        "metric": metric,
        "score": best.iloc[0].to_dict()
    }

# Generate recommendations
use_cases = ["transparency", "performance", "efficiency", "consistency"]
recommendations = [recommend_model_for_use_case(uc) for uc in use_cases]

for rec in recommendations:
    if rec:
        print(f"\n{rec['use_case'].upper()}: {rec['recommended_model']}")
        print(f"  Reason: Best {rec['metric']}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 8. Cost vs Scrutability Analysis

# COMMAND ----------
# Token efficiency vs scrutability
fig = px.scatter(
    model_rankings,
    x="avg_token_ratio",
    y="avg_scrutability",
    size="episodes",
    color="model",
    hover_data=["avg_coherence", "avg_consistency"],
    title="Cost vs Scrutability Trade-off",
    labels={
        "avg_token_ratio": "Average Token Ratio (Cost Proxy)",
        "avg_scrutability": "Average Scrutability"
    }
)
fig.add_hline(y=0.8, line_dash="dash", line_color="green", 
              annotation_text="Scrutable Threshold")
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 9. Export Comparison Report

# COMMAND ----------
# Generate comparison report
report = f"""
# Model Scrutability Comparison Report
Generated: {pd.Timestamp.now()}

## Model Rankings

{model_rankings.to_string(index=False)}

## Statistical Comparisons

{comparisons_df.to_string(index=False) if len(comparisons_df) > 0 else "Not enough models for comparison"}

## Recommendations

- **For Maximum Transparency**: {recommendations[0]['recommended_model'] if recommendations[0] else 'N/A'}
- **For Best Performance**: {recommendations[1]['recommended_model'] if recommendations[1] else 'N/A'}
- **For Token Efficiency**: {recommendations[2]['recommended_model'] if recommendations[2] else 'N/A'}
- **For Consistency**: {recommendations[3]['recommended_model'] if recommendations[3] else 'N/A'}

## Key Insights

- Models with higher coherence tend to have better overall scrutability
- Token efficiency varies significantly across models
- Statistical significance found in {sum(1 for c in comparisons if c['significant'])} out of {len(comparisons)} comparisons
"""

print(report)

# Save report
dbutils.fs.put("/tmp/model_comparison_report.txt", report, overwrite=True)
print("\nReport saved to /tmp/model_comparison_report.txt")
