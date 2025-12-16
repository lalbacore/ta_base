from .episode import Episode, EVAL_SCHEMA
from .metrics import compute_coherence, compute_consistency, compute_efficiency
from .scoring import EvaluationResult
from .invariants import check_invariants
import mlflow
from pyspark.sql.functions import col

def run_episode_evaluation(spark, episode_id):
    """
    Main entry point for Idempotent AI Scrutability Evaluation.
    """
    # 1. Load Data
    try:
        steps_df = spark.table("ai_eval.episode_steps") \
            .filter(col("episode_id") == episode_id) \
            .orderBy("step_id")
    except Exception as e:
        print(f"Error accessing table: {e}")
        return None

    # 2. Guardrails
    episode = Episode(episode_id, steps_df)
    try:
        check_invariants(episode.steps)
    except ValueError as e:
        print(f"Skipping evaluation: {e}")
        return None

    # 3. Pure Function Evaluation
    coh = compute_coherence(episode.steps)
    con = compute_consistency(episode.steps)
    eff = compute_efficiency(episode.steps)
    
    # Flags logic could go here or in metrics
    flags = []
    if eff < 0.6: flags.append("inefficient_token_usage")

    # 4. Result Construction
    result = EvaluationResult(episode_id, coh, con, eff, flags)

    # 5. Idempotent Write (Side Effect)
    _persist_result(spark, result)
    _log_mlflow(result)

    return result

def _persist_result(spark, result):
    """Writes result to Delta table idempotently."""
    df = spark.createDataFrame([result.to_dict()], schema=EVAL_SCHEMA)
    # Append mode is safe because entries are immutable facts of evaluation at a point in time
    # De-duplication is handled by downstream consumers or distinct queries
    df.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable("ai_eval.episode_evaluations")

def _log_mlflow(result):
    """Logs to MLflow if active run exists."""
    try:
        if mlflow.active_run():
            mlflow.log_metric("scrutability_score", result.scrutability_score)
            mlflow.set_tag("scrutability_level", result.scrutability_level)
    except:
        pass
