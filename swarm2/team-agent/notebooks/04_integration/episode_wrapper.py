# MCP/A2A Episode Wrapper
# Provides idempotent episode boundaries for MCP and A2A workflows

from datetime import datetime
import uuid
import time
from typing import List, Dict, Any, Optional
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import *

class EpisodeTransaction:
    """
    Tight membrane wrapper for MCP/A2A workflow episodes.
    """
    
    def __init__(self, spark: SparkSession, workflow_type: str, transaction_id: Optional[str] = None):
        self.spark = spark
        self.workflow_type = workflow_type
        self.episode_id = transaction_id or str(uuid.uuid4())
        self.steps = []
        self.start_ts = datetime.now()
        self.status = "running"
        
        # Schemas matching final_verdict.py / evaluator_job.py
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
        
    def add_step(self, task_name, prompt, output, tokens_in, tokens_out, 
                 model="gpt-4", has_explanation=False, explanation=None):
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
            "latency_ms": 0,
            "ts": datetime.now(),
            "has_explanation": has_explanation,
            "explanation": explanation,
            "reasoning_quality": None,
            "metadata": {}
        }
        self.steps.append(step)
        return step_id

    def commit(self, model="gpt-4"):
        episode = {
            "episode_id": self.episode_id,
            "run_id": f"run_{self.workflow_type}",
            "job_id": "interactive",
            "model": model,
            "start_ts": self.start_ts,
            "end_ts": datetime.now(),
            "status": "completed",
            "total_steps": len(self.steps),
            "metadata": {"workflow": self.workflow_type}
        }
        
        # Robust write with explicit schema
        import pandas as pd
        self.spark.createDataFrame(pd.DataFrame([episode]), schema=self.episode_struct).write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable("ai_eval.episodes")
        self.spark.createDataFrame(pd.DataFrame(self.steps), schema=self.step_struct).write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable("ai_eval.episode_steps")
        
        return self.episode_id

    def evaluate(self):
        # Dynamic import to avoid circular dependency issues
        import sys
        import os
        
        # Ensure evaluator path is visible
        current_dir = os.getcwd()
        if "04_integration" in current_dir:
            eval_dir = os.path.abspath(os.path.join(current_dir, "../02_evaluator"))
        else:
            eval_dir = os.path.abspath("notebooks/02_evaluator")
        if eval_dir not in sys.path:
            sys.path.append(eval_dir)
            
        try:
            from run_evaluation import EpisodeEvaluator
        except ImportError:
            # Fallback if running relative
            sys.path.append("../02_evaluator")
            from run_evaluation import EpisodeEvaluator

        evaluator = EpisodeEvaluator(self.spark)
        
        # Retry for consistency
        for _ in range(3):
            try:
                if self.spark.table("ai_eval.episode_steps").filter(f"episode_id = '{self.episode_id}'").count() > 0:
                    break
            except:
                time.sleep(1)
        
        result = evaluator.evaluate_episode(self.episode_id)
        
        computes = result is not None and result.get("scrutability_level") == "scrutable"
        
        # Mock breakdown for demo if not full
        breakdown = []
        for s in self.steps:
            tokens_in = s["tokens_in"] if s["tokens_in"] else 0
            breakdown.append({
                "step_id": s["step_id"],
                "task_name": s["task_name"],
                "is_scrutable": True, # Simplified
                "tokens_ratio": s["tokens_out"] / max(tokens_in, 1),
                "issues": []
            })

        return {
            "computes": computes,
            "scrutability_score": result["scrutability_score"] if result else 0.0,
            "scrutability_level": result["scrutability_level"] if result else "unknown",
            "obfuscation_point": None, # Logic simplified for wrapper
            "breakdown": breakdown
        }

def mcp_episode(spark, transaction_id=None):
    return EpisodeTransaction(spark, "mcp", transaction_id)

def a2a_episode(spark, transaction_id=None):
    return EpisodeTransaction(spark, "a2a", transaction_id)
