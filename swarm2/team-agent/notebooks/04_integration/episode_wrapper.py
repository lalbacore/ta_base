# MCP/A2A Episode Wrapper
# Provides idempotent episode boundaries for MCP and A2A workflows

from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional
from pyspark.sql import SparkSession


class EpisodeTransaction:
    """
    Tight membrane wrapper for MCP/A2A workflow episodes.
    
    Provides:
    - Idempotent episode boundaries
    - Step-level scrutability tracking
    - Pinpoint where obfuscation starts
    - Binary decision: computes (scrutable) or doesn't compute (not scrutable)
    """
    
    def __init__(self, spark: SparkSession, workflow_type: str, transaction_id: Optional[str] = None):
        """
        Initialize episode transaction.
        
        Args:
            spark: SparkSession
            workflow_type: "mcp" or "a2a"
            transaction_id: Optional transaction ID (generated if not provided)
        """
        from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType, DoubleType, MapType
        self.spark = spark
        self.workflow_type = workflow_type
        self.episode_id = transaction_id or str(uuid.uuid4())
        self.steps = []
        self.start_ts = datetime.now()
        self.status = "running"
        self.obfuscation_point = None  # Step where scrutability breaks

        # Define Explicit Schemas (Matches test_suite.py)
        self.episode_struct = StructType([
            StructField("episode_id", StringType(), False),
            StructField("run_id", StringType(), True),
            StructField("job_id", StringType(), True),
            StructField("model", StringType(), True),
            StructField("start_ts", TimestampType(), True),
            StructField("end_ts", TimestampType(), True),
            StructField("status", StringType(), True),
            StructField("total_steps", IntegerType(), True),
            StructField("metadata", MapType(StringType(), StringType()), True)
        ])

        self.step_struct = StructType([
            StructField("episode_id", StringType(), False),
            StructField("step_id", IntegerType(), False),
            StructField("task_name", StringType(), True),
            StructField("model", StringType(), True),
            StructField("prompt", StringType(), True),
            StructField("output", StringType(), True),
            StructField("tokens_in", IntegerType(), True),
            StructField("tokens_out", IntegerType(), True),
            StructField("latency_ms", IntegerType(), True),
            StructField("ts", TimestampType(), True),
            StructField("has_explanation", BooleanType(), True),
            StructField("explanation", StringType(), True),
            StructField("reasoning_quality", DoubleType(), True),
            StructField("metadata", MapType(StringType(), StringType()), True)
        ])
        
    def add_step(self, 
                 task_name: str,
                 prompt: str,
                 output: str,
                 tokens_in: int,
                 tokens_out: int,
                 model: str = "gpt-4",
                 has_explanation: bool = False,
                 explanation: Optional[str] = None) -> int:
        """
        Add a step to the episode.
        
        Returns:
            step_id: The ID of the added step
        """
        step_id = len(self.steps)
        
        step = {
            "episode_id": self.episode_id,
            "step_id": step_id,
            "task_name": task_name,
            "model": model,
            "prompt": prompt,
            "output": output,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latency_ms": 0,  # Can be measured if needed
            "ts": datetime.now(),
            "has_explanation": has_explanation,
            "explanation": explanation,
            "reasoning_quality": None,  # Will be computed by evaluator
            "metadata": {}
        }
        
        self.steps.append(step)
        return step_id
    
    def commit(self, model: str = "gpt-4") -> str:
        """
        Commit episode to Delta tables.
        
        Returns:
            episode_id
        """
        # Create episode record
        episode = {
            "episode_id": self.episode_id,
            "run_id": f"run_{self.workflow_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "job_id": f"job_{self.workflow_type}",
            "model": model,
            "start_ts": self.start_ts,
            "end_ts": datetime.now(),
            "status": self.status,
            "total_steps": len(self.steps),
            "metadata": {
                "workflow_type": self.workflow_type,
                "transaction_id": self.episode_id
            }
        }
        
        # Write to Delta
        # Write to Delta with explicit schema
        # Use persist schema to avoid inference errors (Integer vs Long)
        self.spark.createDataFrame([episode], schema=self.episode_struct).write \
            .format("delta").mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable("ai_eval.episodes")
        
        self.spark.createDataFrame(self.steps, schema=self.step_struct).write \
            .format("delta").mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable("ai_eval.episode_steps")
        
        return self.episode_id
    
        }

    
    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluate episode scrutability.
        
        Returns:
            {
                "computes": bool,  # True if scrutable, False otherwise
                "scrutability_score": float,
                "scrutability_level": str,
                "obfuscation_point": int or None,  # Step where it breaks
                "breakdown": {...}
            }
        """
        # Ensure evaluator module is visible
        import sys
        import os
        
        # Add 02_evaluator to path if not present
        # Assuming struct: notebooks/04_integration/wrapper.py -> ../02_evaluator/
        current_dir = os.getcwd()
        if "04_integration" in current_dir:
            eval_dir = os.path.abspath(os.path.join(current_dir, "../02_evaluator"))
        else:
            # Fallback for when running from root or elsewhere
            eval_dir = os.path.abspath("notebooks/02_evaluator")
            
        if eval_dir not in sys.path:
            sys.path.append(eval_dir)

        try:
            from evaluator_job import EpisodeEvaluator
        except ImportError:
            # Try importing as package if top-level
            from notebooks.02_evaluator.evaluator_job import EpisodeEvaluator
        
        evaluator = EpisodeEvaluator(self.spark)
        result = evaluator.evaluate_episode(self.episode_id)
        
        # Determine if it "computes"
        computes = result["scrutability_level"] == "scrutable"
        
        # Find obfuscation point if not scrutable
        obfuscation_point = None
        if not computes:
            obfuscation_point = self._find_obfuscation_point()
        
        return {
            "computes": computes,
            "scrutability_score": result["scrutability_score"],
            "scrutability_level": result["scrutability_level"],
            "obfuscation_point": obfuscation_point,
            "breakdown": self._get_step_breakdown()
        }
    
    def _find_obfuscation_point(self) -> Optional[int]:
        """
        Find the step where obfuscation starts.
        
        Uses step-by-step evaluation to pinpoint the exact step.
        """
        # Get evaluation flags
        eval_result = self.spark.sql(f"""
            SELECT flags 
            FROM ai_eval.episode_evaluations 
            WHERE episode_id = '{self.episode_id}'
        """).collect()
        
        if not eval_result or not eval_result[0].flags:
            return None
        
        # Parse flags to find earliest problematic step
        flags = eval_result[0].flags
        min_step = None
        
        for flag in flags:
            # Extract step number from flags like "semantic_jump_step_4"
            if "step_" in flag:
                try:
                    step_num = int(flag.split("step_")[-1].split("_")[0])
                    if min_step is None or step_num < min_step:
                        min_step = step_num
                except:
                    pass
        
        return min_step
    
    def _get_step_breakdown(self) -> List[Dict[str, Any]]:
        """
        Get per-step scrutability breakdown.
        
        Returns list of steps with individual scrutability indicators.
        """
        # Get evaluation details
        eval_result = self.spark.sql(f"""
            SELECT 
                semantic_jumps,
                contradictions,
                instruction_drifts,
                flags
            FROM ai_eval.episode_evaluations 
            WHERE episode_id = '{self.episode_id}'
        """).collect()[0]
        
        flags = eval_result.flags or []
        
        # Build per-step breakdown
        breakdown = []
        for i, step in enumerate(self.steps):
            step_flags = [f for f in flags if f"step_{i}" in f]
            
            breakdown.append({
                "step_id": i,
                "task_name": step["task_name"],
                "is_scrutable": len(step_flags) == 0,
                "issues": step_flags,
                "tokens_ratio": step["tokens_out"] / max(step["tokens_in"], 1)
            })
        
        return breakdown


# Convenience function for MCP workflows
def mcp_episode(spark: SparkSession, transaction_id: Optional[str] = None) -> EpisodeTransaction:
    """Create an MCP episode transaction."""
    return EpisodeTransaction(spark, "mcp", transaction_id)


# Convenience function for A2A workflows
def a2a_episode(spark: SparkSession, transaction_id: Optional[str] = None) -> EpisodeTransaction:
    """Create an A2A episode transaction."""
    return EpisodeTransaction(spark, "a2a", transaction_id)


# Example usage
if __name__ == "__main__":
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder.getOrCreate()
    
    # Create MCP episode
    episode = mcp_episode(spark)
    
    # Add steps
    episode.add_step(
        task_name="parse_request",
        prompt="Parse the MCP request",
        output="Parsed request: action=query, params={...}",
        tokens_in=50,
        tokens_out=80
    )
    
    episode.add_step(
        task_name="execute_query",
        prompt="Execute the database query",
        output="Query executed successfully, returned 10 rows",
        tokens_in=60,
        tokens_out=90
    )
    
    # Commit to Delta
    episode_id = episode.commit()
    
    # Evaluate
    result = episode.evaluate()
    
    if result["computes"]:
        print("✅ Episode COMPUTES (scrutable)")
    else:
        print(f"❌ Episode DOES NOT COMPUTE")
        print(f"   Obfuscation starts at step: {result['obfuscation_point']}")
        print(f"   Scrutability score: {result['scrutability_score']:.3f}")
