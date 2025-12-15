# Databricks Notebook: Episode Evaluator Job
# Stateless, deterministic Spark job for scrutability evaluation

# Databricks notebook source
# MAGIC %md
# MAGIC # AI Episode Evaluator
# MAGIC 
# MAGIC Stateless Spark job that evaluates episode scrutability.
# MAGIC 
# MAGIC **Input:** episode_id
# MAGIC **Reads:** ai_eval.episode_steps
# MAGIC **Writes:** ai_eval.episode_evaluations
# MAGIC **Logs:** MLflow metrics

# COMMAND ----------
# MAGIC %pip install mlflow pandas
# MAGIC dbutils.library.restartPython()

# COMMAND ----------
import mlflow
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime

# COMMAND ----------
# MAGIC %md
# MAGIC ## Episode Evaluator Class

# COMMAND ----------
class EpisodeEvaluator:
    """
    Stateless, deterministic episode evaluator.
    
    Computes scrutability scores based on:
    - Coherence (semantic consistency)
    - Consistency (logical consistency)
    - Efficiency (token efficiency)
    """
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.evaluator_version = "1.0.0"
    
    def evaluate_episode(self, episode_id: str):
        """
        Evaluate a single episode.
        
        Args:
            episode_id: Episode to evaluate
            
        Returns:
            Evaluation results dictionary
        """
        start_time = datetime.now()
        
        # Start MLflow run
        with mlflow.start_run(run_name=f"eval_{episode_id}"):
            
            # 1. Load episode steps
            steps_df = self.load_episode_steps(episode_id)
            
            if steps_df.count() == 0:
                raise ValueError(f"No steps found for episode {episode_id}")
            
            # 2. Compute scores
            coherence = self.compute_coherence(steps_df)
            consistency = self.compute_consistency(steps_df)
            efficiency = self.compute_efficiency(steps_df)
            
            # 3. Detect issues and generate flags
            flags = self.detect_flags(coherence, consistency, efficiency)
            
            # 4. Compute overall scrutability
            scrutability = self.compute_scrutability(
                coherence, consistency, efficiency
            )
            
            # 5. Write evaluation to Delta
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self.write_evaluation(
                episode_id, coherence, consistency, 
                efficiency, scrutability, flags, duration_ms
            )
            
            # 6. Log to MLflow
            self.log_to_mlflow(
                episode_id, coherence, consistency, 
                efficiency, scrutability
            )
            
            return {
                "episode_id": episode_id,
                "scrutability_score": scrutability["score"],
                "scrutability_level": scrutability["level"],
                "duration_ms": duration_ms
            }
    
    def load_episode_steps(self, episode_id: str):
        """Load steps for episode from Delta table."""
        return self.spark.table("ai_eval.episode_steps") \
            .filter(col("episode_id") == episode_id) \
            .orderBy("step_id")
    
    def compute_coherence(self, steps_df):
        """
        Compute semantic coherence using embeddings.
        
        Returns:
            {
                "score": float,
                "avg_similarity": float,
                "jumps": int,
                "jump_details": List[Tuple[int, float]]
            }
        """
        from coherence import compute_coherence_score
        return compute_coherence_score(self.spark, steps_df)
    
    def compute_consistency(self, steps_df):
        """
        Detect logical consistency issues.
        
        Returns:
            {
                "score": float,
                "contradictions": int,
                "inversions": int,
                "drifts": int,
                "details": Dict
            }
        """
        from consistency import compute_consistency_score
        return compute_consistency_score(self.spark, steps_df)
    
    def compute_efficiency(self, steps_df):
        """
        Compute token efficiency metrics.
        
        Returns:
            {
                "score": float,
                "ratio": float,
                "per_delta": float,
                "repetition": float
            }
        """
        from efficiency import compute_efficiency_score
        return compute_efficiency_score(self.spark, steps_df)
    
    def detect_flags(self, coherence, consistency, efficiency):
        """Generate specific issue flags."""
        flags = []
        
        # Semantic jump flags
        for step_id, similarity in coherence.get("jump_details", []):
            flags.append(f"semantic_jump_step_{step_id}")
        
        # Contradiction flags
        for i, j in consistency.get("details", {}).get("contradiction_pairs", []):
            flags.append(f"contradiction_steps_{i}_{j}")
        
        # Instruction drift flags
        for step_id in consistency.get("details", {}).get("drift_steps", []):
            flags.append(f"instruction_ignored_step_{step_id}")
        
        # Confidence inversion flags
        for step_id in consistency.get("details", {}).get("inversion_steps", []):
            flags.append(f"confidence_inversion_step_{step_id}")
        
        # Efficiency flags
        if efficiency["ratio"] > 5.0:
            flags.append("high_token_ratio")
        if efficiency["repetition"] > 0.5:
            flags.append("high_repetition")
        
        return flags
    
    def compute_scrutability(self, coherence, consistency, efficiency):
        """
        Compute overall scrutability score.
        
        Weighted average:
        - Coherence: 40%
        - Consistency: 40%
        - Efficiency: 20%
        """
        score = (
            coherence["score"] * 0.4 +
            consistency["score"] * 0.4 +
            efficiency["score"] * 0.2
        )
        
        # Classify scrutability level
        if score >= 0.8:
            level = "scrutable"
        elif score >= 0.3:
            level = "partially_scrutable"
        else:
            level = "inscrutable"
        
        return {"score": score, "level": level}
    
    def write_evaluation(self, episode_id, coherence, consistency, 
                        efficiency, scrutability, flags, duration_ms):
        """Write evaluation results to Delta table."""
        
        eval_data = [{
            "episode_id": episode_id,
            "coherence_score": coherence["score"],
            "consistency_score": consistency["score"],
            "efficiency_score": efficiency["score"],
            "scrutability_score": scrutability["score"],
            "scrutability_level": scrutability["level"],
            "semantic_jumps": coherence.get("jumps", 0),
            "contradictions": consistency.get("contradictions", 0),
            "confidence_inversions": consistency.get("inversions", 0),
            "instruction_drifts": consistency.get("drifts", 0),
            "token_ratio": efficiency.get("ratio", 0.0),
            "tokens_per_semantic_delta": efficiency.get("per_delta", 0.0),
            "repetition_rate": efficiency.get("repetition", 0.0),
            "flags": flags,
            "notes": self.generate_notes(coherence, consistency, efficiency),
            "evaluator_version": self.evaluator_version,
            "evaluated_at": datetime.now(),
            "evaluation_duration_ms": duration_ms
        }]
        
        import pandas as pd
        eval_df = self.spark.createDataFrame(pd.DataFrame(eval_data))
        eval_df.write.format("delta").mode("append") \
            .saveAsTable("ai_eval.episode_evaluations")
    
    def generate_notes(self, coherence, consistency, efficiency):
        """Generate human-readable evaluation notes."""
        notes = []
        
        if coherence["jumps"] > 0:
            notes.append(f"Found {coherence['jumps']} semantic jumps")
        
        if consistency["contradictions"] > 0:
            notes.append(f"Detected {consistency['contradictions']} contradictions")
        
        if consistency["drifts"] > 0:
            notes.append(f"Found {consistency['drifts']} instruction drifts")
        
        if efficiency["ratio"] > 3.0:
            notes.append(f"High token ratio: {efficiency['ratio']:.2f}")
        
        if efficiency["repetition"] > 0.3:
            notes.append(f"High repetition rate: {efficiency['repetition']:.2%}")
        
        return "; ".join(notes) if notes else "No major issues detected"
    
    def log_to_mlflow(self, episode_id, coherence, consistency, 
                     efficiency, scrutability):
        """Log metrics to MLflow."""
        
        # Log scores
        mlflow.log_metric("coherence_score", coherence["score"])
        mlflow.log_metric("consistency_score", consistency["score"])
        mlflow.log_metric("efficiency_score", efficiency["score"])
        mlflow.log_metric("scrutability_score", scrutability["score"])
        
        # Log detailed metrics
        mlflow.log_metric("semantic_jumps", coherence.get("jumps", 0))
        mlflow.log_metric("contradictions", consistency.get("contradictions", 0))
        mlflow.log_metric("confidence_inversions", consistency.get("inversions", 0))
        mlflow.log_metric("instruction_drifts", consistency.get("drifts", 0))
        mlflow.log_metric("token_ratio", efficiency.get("ratio", 0.0))
        mlflow.log_metric("repetition_rate", efficiency.get("repetition", 0.0))
        
        # Log parameters
        mlflow.log_param("episode_id", episode_id)
        mlflow.log_param("evaluator_version", self.evaluator_version)
        
        # Get model from episode
        episode = self.spark.table("ai_eval.episodes") \
            .filter(col("episode_id") == episode_id) \
            .select("model").collect()
        
        if episode:
            mlflow.log_param("model", episode[0].model)
        
        # Tags
        mlflow.set_tag("scrutability_level", scrutability["level"])
        mlflow.set_tag("episode_id", episode_id)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Batch Evaluation (Embarrassingly Parallel)

# COMMAND ----------
def evaluate_episodes_batch(spark, episode_ids):
    """
    Evaluate multiple episodes in parallel.
    
    Uses Spark's parallelism for embarrassingly parallel execution.
    
    Args:
        spark: SparkSession
        episode_ids: List of episode IDs to evaluate
        
    Returns:
        List of (episode_id, status, error) tuples
    """
    evaluator = EpisodeEvaluator(spark)
    
    # Create RDD of episode IDs
    episodes_rdd = spark.sparkContext.parallelize(episode_ids)
    
    # Map each episode to evaluation (parallel)
    def eval_wrapper(episode_id):
        try:
            result = evaluator.evaluate_episode(episode_id)
            return (episode_id, "success", None, result["scrutability_score"])
        except Exception as e:
            return (episode_id, "failed", str(e), None)
    
    results = episodes_rdd.map(eval_wrapper).collect()
    
    return results

# COMMAND ----------
# MAGIC %md
# MAGIC ## Main Entry Point

# COMMAND ----------
if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    
    # Get episode IDs from job parameter
    episode_ids_param = dbutils.widgets.get("episode_ids")
    episode_ids = episode_ids_param.split(",")
    
    print(f"Evaluating {len(episode_ids)} episodes...")
    
    # Run batch evaluation
    results = evaluate_episodes_batch(spark, episode_ids)
    
    # Log summary
    success_count = sum(1 for _, status, _, _ in results if status == "success")
    failed_count = len(results) - success_count
    
    print(f"\n=== Evaluation Complete ===")
    print(f"Success: {success_count}/{len(results)}")
    print(f"Failed: {failed_count}/{len(results)}")
    
    if failed_count > 0:
        print("\nFailed episodes:")
        for ep_id, status, error, _ in results:
            if status == "failed":
                print(f"  {ep_id}: {error}")
    
    # Display results
    import pandas as pd
    results_df = spark.createDataFrame(
        pd.DataFrame([(ep, status, score) for ep, status, _, score in results],
        columns=["episode_id", "status", "scrutability_score"])
    )
    display(results_df)
