# Efficiency Metrics Module
# Computes token efficiency metrics

from pyspark.sql import SparkSession
from pyspark.sql.functions import *


def compute_efficiency_score(spark: SparkSession, steps_df):
    """
    Compute token efficiency metrics:
    - Token ratio (output/input)
    - Tokens per semantic delta (tokens per unique concept)
    - Repetition rate (repeated content)
    
    Args:
        spark: SparkSession
        steps_df: DataFrame with episode steps
        
    Returns:
        {
            "score": float (0.0-1.0),
            "ratio": float,
            "per_delta": float,
            "repetition": float
        }
    """
    
    # Aggregate token stats
    stats = steps_df.agg(
        sum("tokens_in").alias("total_in"),
        sum("tokens_out").alias("total_out"),
        count("*").alias("num_steps")
    ).collect()[0]
    
    if stats.total_in == 0 or stats.total_out == 0:
        return {
            "score": 0.5,  # Neutral score if no tokens
            "ratio": 0.0,
            "per_delta": 0.0,
            "repetition": 0.0
        }
    
    # 1. Token ratio (output/input)
    token_ratio = stats.total_out / max(stats.total_in, 1)
    
    # 2. Tokens per semantic delta
    unique_concepts = _count_unique_concepts(steps_df)
    tokens_per_delta = stats.total_out / max(unique_concepts, 1)
    
    # 3. Repetition rate
    repetition_rate = _compute_repetition(steps_df)
    
    # 4. Compute efficiency score
    # Lower ratio is better (concise)
    # Lower tokens/concept is better (dense)
    # Lower repetition is better (unique)
    
    ratio_score = 1.0 / (1.0 + token_ratio / 2.0)  # Normalize around ratio=2
    delta_score = 1.0 / (1.0 + tokens_per_delta / 100.0)  # Normalize around 100 tokens/concept
    repetition_score = 1.0 - repetition_rate
    
    efficiency_score = (
        ratio_score * 0.4 +
        delta_score * 0.3 +
        repetition_score * 0.3
    )
    
    return {
        "score": efficiency_score,
        "ratio": token_ratio,
        "per_delta": tokens_per_delta,
        "repetition": repetition_rate
    }


def _count_unique_concepts(steps_df):
    """
    Count unique semantic concepts.
    
    Uses distinct bigrams as proxy for concepts.
    """
    # Collect all outputs
    outputs = steps_df.select("output").collect()
    
    if not outputs:
        return 1
    
    # Extract all bigrams
    all_bigrams = set()
    
    for row in outputs:
        if not row.output:
            continue
        
        words = row.output.lower().split()
        bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]
        all_bigrams.update(bigrams)
    
    return max(len(all_bigrams), 1)


def _compute_repetition(steps_df):
    """
    Compute repetition rate.
    
    Measures how much content is repeated across steps.
    """
    outputs = steps_df.select("output").collect()
    
    if len(outputs) < 2:
        return 0.0
    
    # Combine all text
    all_text = " ".join(row.output for row in outputs if row.output)
    
    if not all_text:
        return 0.0
    
    words = all_text.split()
    
    if len(words) < 3:
        return 0.0
    
    # Count trigram repetitions
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]
    unique_trigrams = set(trigrams)
    
    # Repetition rate = 1 - (unique / total)
    repetition_rate = 1.0 - (len(unique_trigrams) / max(len(trigrams), 1))
    
    return repetition_rate


def compute_token_statistics(steps_df):
    """
    Compute detailed token statistics.
    
    Returns:
        {
            "total_tokens_in": int,
            "total_tokens_out": int,
            "avg_tokens_in": float,
            "avg_tokens_out": float,
            "max_tokens_out": int,
            "min_tokens_out": int
        }
    """
    stats = steps_df.agg(
        sum("tokens_in").alias("total_in"),
        sum("tokens_out").alias("total_out"),
        avg("tokens_in").alias("avg_in"),
        avg("tokens_out").alias("avg_out"),
        max("tokens_out").alias("max_out"),
        min("tokens_out").alias("min_out")
    ).collect()[0]
    
    return {
        "total_tokens_in": stats.total_in or 0,
        "total_tokens_out": stats.total_out or 0,
        "avg_tokens_in": stats.avg_in or 0.0,
        "avg_tokens_out": stats.avg_out or 0.0,
        "max_tokens_out": stats.max_out or 0,
        "min_tokens_out": stats.min_out or 0
    }
