# Databricks Notebook: Scrutability Dashboard
# Interactive dashboard for episode scrutability analysis

# Databricks notebook source
# MAGIC %md
# MAGIC # AI Episode Scrutability Dashboard
# MAGIC 
# MAGIC Interactive dashboard for analyzing episode scrutability across models, time, and metrics.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------
from pyspark.sql.functions import *
from pyspark.sql.window import Window
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Overview Metrics

# COMMAND ----------
# Load evaluations
evals_df = spark.table("ai_eval.episode_evaluations")

# Aggregate stats
stats = evals_df.agg(
    count("*").alias("total_episodes"),
    avg("scrutability_score").alias("avg_scrutability"),
    avg("coherence_score").alias("avg_coherence"),
    avg("consistency_score").alias("avg_consistency"),
    avg("efficiency_score").alias("avg_efficiency"),
    sum(when(col("scrutability_level") == "scrutable", 1).otherwise(0)).alias("scrutable_count"),
    sum(when(col("scrutability_level") == "partially_scrutable", 1).otherwise(0)).alias("partial_count"),
    sum(when(col("scrutability_level") == "inscrutable", 1).otherwise(0)).alias("inscrutable_count")
).toPandas()

display(stats)

# COMMAND ----------
# Create metrics cards
print(f"""
╔══════════════════════════════════════════════════════════════╗
║                  SCRUTABILITY OVERVIEW                        ║
╠══════════════════════════════════════════════════════════════╣
║  Total Episodes:        {stats['total_episodes'][0]:>6}                      ║
║  Avg Scrutability:      {stats['avg_scrutability'][0]:>6.2f}                      ║
║  Avg Coherence:         {stats['avg_coherence'][0]:>6.2f}                      ║
║  Avg Consistency:       {stats['avg_consistency'][0]:>6.2f}                      ║
║  Avg Efficiency:        {stats['avg_efficiency'][0]:>6.2f}                      ║
╠══════════════════════════════════════════════════════════════╣
║  Scrutable:             {stats['scrutable_count'][0]:>6} ({stats['scrutable_count'][0]/stats['total_episodes'][0]*100:>5.1f}%)              ║
║  Partially Scrutable:   {stats['partial_count'][0]:>6} ({stats['partial_count'][0]/stats['total_episodes'][0]*100:>5.1f}%)              ║
║  Inscrutable:           {stats['inscrutable_count'][0]:>6} ({stats['inscrutable_count'][0]/stats['total_episodes'][0]*100:>5.1f}%)              ║
╚══════════════════════════════════════════════════════════════╝
""")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Scrutability Distribution

# COMMAND ----------
# Distribution by level
dist_df = evals_df.groupBy("scrutability_level") \
    .agg(count("*").alias("count")) \
    .toPandas()

fig = px.pie(
    dist_df,
    values="count",
    names="scrutability_level",
    title="Scrutability Distribution",
    color="scrutability_level",
    color_discrete_map={
        "scrutable": "#10b981",
        "partially_scrutable": "#f59e0b",
        "inscrutable": "#ef4444"
    }
)
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Score Distribution Histograms

# COMMAND ----------
# Get all scores
scores_df = evals_df.select(
    "scrutability_score",
    "coherence_score",
    "consistency_score",
    "efficiency_score"
).toPandas()

# Create subplots
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Scrutability Score", "Coherence Score", 
                   "Consistency Score", "Efficiency Score")
)

# Add histograms
fig.add_trace(
    go.Histogram(x=scores_df["scrutability_score"], name="Scrutability", nbinsx=20),
    row=1, col=1
)
fig.add_trace(
    go.Histogram(x=scores_df["coherence_score"], name="Coherence", nbinsx=20),
    row=1, col=2
)
fig.add_trace(
    go.Histogram(x=scores_df["consistency_score"], name="Consistency", nbinsx=20),
    row=2, col=1
)
fig.add_trace(
    go.Histogram(x=scores_df["efficiency_score"], name="Efficiency", nbinsx=20),
    row=2, col=2
)

fig.update_layout(height=600, showlegend=False, title_text="Score Distributions")
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Model Comparison

# COMMAND ----------
# Join episodes with evaluations to get model info
model_scores = spark.table("ai_eval.episodes") \
    .join(evals_df, "episode_id") \
    .groupBy("model") \
    .agg(
        avg("scrutability_score").alias("avg_scrutability"),
        avg("coherence_score").alias("avg_coherence"),
        avg("consistency_score").alias("avg_consistency"),
        avg("efficiency_score").alias("avg_efficiency"),
        count("*").alias("num_episodes")
    ) \
    .orderBy(desc("avg_scrutability")) \
    .toPandas()

display(model_scores)

# COMMAND ----------
# Model comparison bar chart
fig = px.bar(
    model_scores,
    x="model",
    y=["avg_coherence", "avg_consistency", "avg_efficiency"],
    title="Model Scrutability Comparison",
    barmode="group",
    labels={"value": "Score", "variable": "Metric"},
    color_discrete_map={
        "avg_coherence": "#3b82f6",
        "avg_consistency": "#8b5cf6",
        "avg_efficiency": "#10b981"
    }
)
fig.update_layout(yaxis_range=[0, 1])
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Scrutability Over Time

# COMMAND ----------
# Time series
time_series = evals_df \
    .withColumn("date", to_date("evaluated_at")) \
    .groupBy("date") \
    .agg(
        avg("scrutability_score").alias("avg_scrutability"),
        avg("coherence_score").alias("avg_coherence"),
        avg("consistency_score").alias("avg_consistency"),
        avg("efficiency_score").alias("avg_efficiency")
    ) \
    .orderBy("date") \
    .toPandas()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=time_series["date"],
    y=time_series["avg_scrutability"],
    name="Scrutability",
    line=dict(color="#3b82f6", width=3)
))

fig.add_trace(go.Scatter(
    x=time_series["date"],
    y=time_series["avg_coherence"],
    name="Coherence",
    line=dict(color="#10b981", width=2, dash="dash")
))

fig.add_trace(go.Scatter(
    x=time_series["date"],
    y=time_series["avg_consistency"],
    name="Consistency",
    line=dict(color="#8b5cf6", width=2, dash="dash")
))

fig.add_trace(go.Scatter(
    x=time_series["date"],
    y=time_series["avg_efficiency"],
    name="Efficiency",
    line=dict(color="#f59e0b", width=2, dash="dash")
))

fig.update_layout(
    title="Scrutability Trend Over Time",
    xaxis_title="Date",
    yaxis_title="Score",
    yaxis_range=[0, 1],
    hovermode="x unified"
)

fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Issue Flags Analysis

# COMMAND ----------
# Explode flags and count
flags_df = evals_df \
    .select(explode("flags").alias("flag")) \
    .groupBy("flag") \
    .count() \
    .orderBy(desc("count")) \
    .limit(15) \
    .toPandas()

fig = px.bar(
    flags_df,
    x="count",
    y="flag",
    orientation="h",
    title="Top 15 Issue Flags",
    labels={"count": "Occurrences", "flag": "Flag"},
    color="count",
    color_continuous_scale="Reds"
)
fig.update_layout(yaxis={'categoryorder':'total ascending'})
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Low Scrutability Episodes

# COMMAND ----------
# Episodes with low scrutability
low_scrutability = spark.table("ai_eval.episodes") \
    .join(evals_df, "episode_id") \
    .filter(col("scrutability_score") < 0.5) \
    .select(
        "episode_id",
        "model",
        "scrutability_score",
        "coherence_score",
        "consistency_score",
        "efficiency_score",
        "flags",
        "notes",
        "evaluated_at"
    ) \
    .orderBy(desc("evaluated_at")) \
    .limit(20)

display(low_scrutability)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 8. Correlation Analysis

# COMMAND ----------
# Correlation between metrics
correlation_df = evals_df.select(
    "scrutability_score",
    "coherence_score",
    "consistency_score",
    "efficiency_score",
    "token_ratio",
    "repetition_rate"
).toPandas()

correlation_matrix = correlation_df.corr()

fig = px.imshow(
    correlation_matrix,
    labels=dict(color="Correlation"),
    x=correlation_matrix.columns,
    y=correlation_matrix.columns,
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="Metric Correlation Matrix"
)
fig.update_layout(width=700, height=700)
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 9. Efficiency Metrics Deep Dive

# COMMAND ----------
# Token efficiency analysis
efficiency_df = evals_df.select(
    "episode_id",
    "token_ratio",
    "tokens_per_semantic_delta",
    "repetition_rate",
    "efficiency_score"
).toPandas()

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=("Token Ratio", "Tokens per Concept", "Repetition Rate")
)

fig.add_trace(
    go.Box(y=efficiency_df["token_ratio"], name="Token Ratio"),
    row=1, col=1
)
fig.add_trace(
    go.Box(y=efficiency_df["tokens_per_semantic_delta"], name="Tokens/Concept"),
    row=1, col=2
)
fig.add_trace(
    go.Box(y=efficiency_df["repetition_rate"], name="Repetition"),
    row=1, col=3
)

fig.update_layout(height=400, showlegend=False, title_text="Efficiency Metrics Distribution")
fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 10. Export Summary Report

# COMMAND ----------
# Generate summary report
summary_report = f"""
# AI Episode Scrutability Report
Generated: {pd.Timestamp.now()}

## Overall Statistics
- Total Episodes Evaluated: {stats['total_episodes'][0]}
- Average Scrutability Score: {stats['avg_scrutability'][0]:.3f}
- Scrutable Episodes: {stats['scrutable_count'][0]} ({stats['scrutable_count'][0]/stats['total_episodes'][0]*100:.1f}%)
- Partially Scrutable: {stats['partial_count'][0]} ({stats['partial_count'][0]/stats['total_episodes'][0]*100:.1f}%)
- Inscrutable Episodes: {stats['inscrutable_count'][0]} ({stats['inscrutable_count'][0]/stats['total_episodes'][0]*100:.1f}%)

## Component Scores
- Average Coherence: {stats['avg_coherence'][0]:.3f}
- Average Consistency: {stats['avg_consistency'][0]:.3f}
- Average Efficiency: {stats['avg_efficiency'][0]:.3f}

## Top Models by Scrutability
{model_scores.to_string(index=False)}

## Recommendations
{"- Focus on improving coherence for models with low scores" if stats['avg_coherence'][0] < 0.7 else ""}
{"- Address consistency issues (contradictions, drift)" if stats['avg_consistency'][0] < 0.7 else ""}
{"- Optimize token efficiency to reduce costs" if stats['avg_efficiency'][0] < 0.6 else ""}
"""

print(summary_report)

# Save to file
dbutils.fs.put("/tmp/scrutability_report.txt", summary_report, overwrite=True)
print("\nReport saved to /tmp/scrutability_report.txt")
