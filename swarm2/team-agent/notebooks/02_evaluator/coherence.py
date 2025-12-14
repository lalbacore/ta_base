# Coherence Scoring Module
# Computes semantic coherence using Word2Vec embeddings

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import Word2Vec, Tokenizer
from pyspark.sql.window import Window
import numpy as np


def compute_coherence_score(spark: SparkSession, steps_df):
    """
    Compute semantic coherence using Word2Vec embeddings.
    
    Approach:
    1. Tokenize step outputs
    2. Generate Word2Vec embeddings
    3. Compute cosine similarity between consecutive steps
    4. Detect semantic jumps (low similarity < 0.3)
    5. Score based on average similarity
    
    Args:
        spark: SparkSession
        steps_df: DataFrame with episode steps
        
    Returns:
        {
            "score": float (0.0-1.0),
            "avg_similarity": float,
            "jumps": int,
            "jump_details": List[Tuple[step_id, similarity]]
        }
    """
    
    # Check if we have enough steps
    step_count = steps_df.count()
    if step_count < 2:
        return {
            "score": 1.0,  # Single step is trivially coherent
            "avg_similarity": 1.0,
            "jumps": 0,
            "jump_details": []
        }
    
    # 1. Tokenize outputs
    tokenizer = Tokenizer(inputCol="output", outputCol="tokens")
    tokenized_df = tokenizer.transform(steps_df)
    
    # 2. Train Word2Vec model
    word2vec = Word2Vec(
        vectorSize=100,
        minCount=1,
        inputCol="tokens",
        outputCol="embedding",
        seed=42  # For determinism
    )
    model = word2vec.fit(tokenized_df)
    
    # 3. Generate embeddings
    embeddings_df = model.transform(tokenized_df)
    
    # 4. Compute pairwise cosine similarity
    # Get previous embedding using window function
    window = Window.orderBy("step_id")
    
    pairs_df = embeddings_df.withColumn(
        "prev_embedding",
        lag("embedding").over(window)
    ).filter(col("prev_embedding").isNotNull())
    
    # Define cosine similarity UDF
    @udf(returnType=DoubleType())
    def cosine_similarity_udf(vec1, vec2):
        if vec1 is None or vec2 is None:
            return 0.0
        
        # Convert to numpy arrays
        v1 = np.array(vec1.toArray())
        v2 = np.array(vec2.toArray())
        
        # Compute cosine similarity
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    # Compute similarities
    similarities_df = pairs_df.withColumn(
        "similarity",
        cosine_similarity_udf(col("embedding"), col("prev_embedding"))
    ).select("step_id", "similarity")
    
    # Collect similarities
    similarities = similarities_df.collect()
    
    if not similarities:
        return {
            "score": 1.0,
            "avg_similarity": 1.0,
            "jumps": 0,
            "jump_details": []
        }
    
    # 5. Compute metrics
    similarity_values = [row.similarity for row in similarities]
    avg_similarity = sum(similarity_values) / len(similarity_values)
    
    # Detect semantic jumps (similarity < 0.3)
    jump_threshold = 0.3
    jumps = [
        (row.step_id, row.similarity)
        for row in similarities
        if row.similarity < jump_threshold
    ]
    
    # 6. Compute coherence score
    # Penalize for jumps: -0.1 per jump
    coherence_score = avg_similarity * (1 - 0.1 * len(jumps))
    coherence_score = max(0.0, min(1.0, coherence_score))
    
    return {
        "score": coherence_score,
        "avg_similarity": avg_similarity,
        "jumps": len(jumps),
        "jump_details": jumps
    }


def compute_coherence_simple(steps_df):
    """
    Simplified coherence scoring without embeddings.
    
    Uses n-gram overlap as proxy for semantic similarity.
    Faster but less accurate than embedding-based approach.
    """
    steps = steps_df.select("step_id", "output").collect()
    
    if len(steps) < 2:
        return {
            "score": 1.0,
            "avg_similarity": 1.0,
            "jumps": 0,
            "jump_details": []
        }
    
    # Compute bigram overlap between consecutive steps
    similarities = []
    jumps = []
    
    for i in range(len(steps) - 1):
        curr_text = steps[i].output.lower()
        next_text = steps[i + 1].output.lower()
        
        # Extract bigrams
        curr_bigrams = set(_get_bigrams(curr_text))
        next_bigrams = set(_get_bigrams(next_text))
        
        # Jaccard similarity
        if not curr_bigrams or not next_bigrams:
            similarity = 0.0
        else:
            intersection = len(curr_bigrams & next_bigrams)
            union = len(curr_bigrams | next_bigrams)
            similarity = intersection / union if union > 0 else 0.0
        
        similarities.append(similarity)
        
        if similarity < 0.2:
            jumps.append((steps[i + 1].step_id, similarity))
    
    avg_similarity = sum(similarities) / len(similarities)
    coherence_score = avg_similarity * (1 - 0.1 * len(jumps))
    coherence_score = max(0.0, min(1.0, coherence_score))
    
    return {
        "score": coherence_score,
        "avg_similarity": avg_similarity,
        "jumps": len(jumps),
        "jump_details": jumps
    }


def _get_bigrams(text):
    """Extract bigrams from text."""
    words = text.split()
    return [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]
