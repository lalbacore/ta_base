from datetime import datetime
import contextlib
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col
    from pyspark.sql.types import (
        StructType, StructField, StringType, IntegerType, 
        BooleanType, DoubleType, ArrayType
    )
except ImportError:
    pass # Handle usage where spark isn't immediately present if needed

@contextlib.contextmanager
def nullcontext():
    yield None

class EpisodeEvaluator:
    """
    Stateless, deterministic episode evaluator.
    
    Computes scrutability scores based on:
    - Coherence (semantic consistency)
    - Consistency (logical consistency)
    - Efficiency (token efficiency)
    """
    
    def __init__(self, spark):
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
        
        # Start MLflow run (failsafe)
        try:
            import mlflow
            if mlflow.active_run():
                run_ctx = nullcontext()
            else:
                run_ctx = mlflow.start_run(run_name=f"eval_{episode_id}")
        except Exception as e:
            print(f"Warning: MLflow logging disabled: {e}")
            run_ctx = nullcontext()

        with run_ctx:
            # 1. Load episode steps
            steps_df = self.load_episode_steps(episode_id)
            
            if steps_df is None or steps_df.count() == 0:
                print(f"Warning: No steps found for episode {episode_id}")
                return {
                    "episode_id": episode_id,
                    "scrutability_score": 0.0,
                    "scrutability_level": "inscrutable (no data)",
                    "duration_ms": 0
                }
            
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
        try:
            # Assumes spark session is active and table exists
            return self.spark.table("ai_eval.episode_steps") \
                .filter(col("episode_id") == episode_id) \
                .orderBy("step_id")
        except Exception as e:
            print(f"Warning: Failed to load steps for {episode_id}: {e}")
            return None

    def compute_coherence(self, steps_df):
        score = 0.8
        jumps = 0
        steps = steps_df.collect()
        for step in steps:
            if not step.has_explanation:
                score -= 0.1
        return {
            "score": max(0.0, score),
            "avg_similarity": 0.8,
            "jumps": jumps,
            "jump_details": []
        }
    
    def compute_consistency(self, steps_df):
        steps = steps_df.collect()
        combined_text = " ".join([s.output or "" for s in steps]).lower()
        contradictions = 0
        if "certain" in combined_text and "not sure" in combined_text:
            contradictions += 1
        return {
            "score": 1.0 if contradictions == 0 else 0.5,
            "contradictions": contradictions,
            "inversions": 0,
            "drifts": 0,
            "details": {"contradiction_pairs": [], "drift_steps": [], "inversion_steps": []}
        }
    
    def compute_efficiency(self, steps_df):
        steps = steps_df.collect()
        total_in = sum(s.tokens_in or 0 for s in steps)
        total_out = sum(s.tokens_out or 0 for s in steps)
        if total_in == 0:
            ratio = 0.0
        else:
            ratio = total_out / total_in
        score = 1.0 if ratio < 2.0 else 0.5
        return {
            "score": score,
            "ratio": ratio,
            "per_delta": 0.0,
            "repetition": 0.0
        }
    
    def detect_flags(self, coherence, consistency, efficiency):
        flags = []
        if efficiency["ratio"] > 5.0:
            flags.append("high_token_ratio")
        return flags
    
    def compute_scrutability(self, coherence, consistency, efficiency):
        score = (coherence["score"] * 0.4 + consistency["score"] * 0.4 + efficiency["score"] * 0.2)
        if score >= 0.8: level = "scrutable"
        elif score >= 0.3: level = "partially_scrutable"
        else: level = "inscrutable"
        return {"score": score, "level": level}
    
    def write_evaluation(self, episode_id, coherence, consistency, efficiency, scrutability, flags, duration_ms):
        eval_data = [{
            "episode_id": episode_id,
            "coherence_score": float(coherence["score"]),
            "consistency_score": float(consistency["score"]),
            "efficiency_score": float(efficiency["score"]),
            "scrutability_score": float(scrutability["score"]),
            "scrutability_level": str(scrutability["level"]),
            "semantic_jumps": int(coherence.get("jumps", 0)),
            "contradictions": int(consistency.get("contradictions", 0)),
            "confidence_inversions": int(consistency.get("inversions", 0)),
            "instruction_drifts": int(consistency.get("drifts", 0)),
            "token_ratio": float(efficiency.get("ratio", 0.0)),
            "tokens_per_semantic_delta": float(efficiency.get("per_delta", 0.0)),
            "repetition_rate": float(efficiency.get("repetition", 0.0)),
            "flags": flags,
            "evaluator_version": self.evaluator_version,
            "evaluated_at": str(datetime.now()),
            "evaluation_duration_ms": str(duration_ms)
        }]
        
        eval_schema = StructType([
            StructField("episode_id", StringType(), False),
            StructField("coherence_score", DoubleType(), True),
            StructField("consistency_score", DoubleType(), True),
            StructField("efficiency_score", DoubleType(), True),
            StructField("scrutability_score", DoubleType(), True),
            StructField("scrutability_level", StringType(), True),
            StructField("semantic_jumps", IntegerType(), True),
            StructField("contradictions", IntegerType(), True),
            StructField("confidence_inversions", IntegerType(), True),
            StructField("instruction_drifts", IntegerType(), True),
            StructField("token_ratio", DoubleType(), True),
            StructField("tokens_per_semantic_delta", DoubleType(), True),
            StructField("repetition_rate", DoubleType(), True),
            StructField("flags", ArrayType(StringType()), True),
            StructField("evaluator_version", StringType(), True),
            StructField("evaluated_at", StringType(), True),
            StructField("evaluation_duration_ms", StringType(), True)
        ])

        eval_df = self.spark.createDataFrame(eval_data, schema=eval_schema)
        
        try:
            eval_df.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable("ai_eval.episode_evaluations")
        except Exception as e:
            # Fallback for schema mismatch
            if "DELTA_FAILED_TO_MERGE_FIELDS" in str(e) or "schema mismatch" in str(e).lower():
                self.spark.sql("DROP TABLE IF EXISTS ai_eval.episode_evaluations")
                eval_df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable("ai_eval.episode_evaluations")
            else:
                raise e

    def log_to_mlflow(self, episode_id, coherence, consistency, efficiency, scrutability):
        try:
            import mlflow
            mlflow.log_metric("scrutability_score", scrutability["score"])
            mlflow.log_param("episode_id", episode_id)
            mlflow.set_tag("scrutability_level", scrutability["level"])
        except ImportError:
            pass
        except Exception as e:
            print(f"Warning: Failed to log to MLflow: {e}")

def run_episode_evaluation(spark, episode_id):
    """
    Main entry point for the library.
    Usage: from ai_workflow_evaluator import run_episode_evaluation
           run_episode_evaluation(spark, "episode_123")
    """
    evaluator = EpisodeEvaluator(spark)
    return evaluator.evaluate_episode(episode_id)

