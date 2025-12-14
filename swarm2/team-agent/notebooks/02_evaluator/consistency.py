# Consistency Detection Module
# Detects contradictions, confidence inversions, and instruction drift

from pyspark.sql import SparkSession
import re


def compute_consistency_score(spark: SparkSession, steps_df):
    """
    Detect logical consistency issues:
    - Contradictions (conflicting statements)
    - Confidence inversions (high → low confidence on same topic)
    - Instruction drift (ignoring original instructions)
    
    Args:
        spark: SparkSession
        steps_df: DataFrame with episode steps
        
    Returns:
        {
            "score": float (0.0-1.0),
            "contradictions": int,
            "inversions": int,
            "drifts": int,
            "details": Dict with specific issues
        }
    """
    
    steps = steps_df.select("step_id", "prompt", "output").collect()
    
    if len(steps) == 0:
        return {
            "score": 1.0,
            "contradictions": 0,
            "inversions": 0,
            "drifts": 0,
            "details": {}
        }
    
    contradictions = []
    inversions = []
    drifts = []
    
    # 1. Detect contradictions (pairwise comparison)
    for i in range(len(steps)):
        for j in range(i + 1, len(steps)):
            if _contradicts(steps[i].output, steps[j].output):
                contradictions.append((steps[i].step_id, steps[j].step_id))
    
    # 2. Detect confidence inversions
    for i in range(len(steps) - 1):
        if _confidence_inverted(steps[i].output, steps[i + 1].output):
            inversions.append(steps[i + 1].step_id)
    
    # 3. Detect instruction drift
    if len(steps) > 0:
        original_prompt = steps[0].prompt
        for i, step in enumerate(steps[1:], 1):
            if _drifts_from_instruction(original_prompt, step.output):
                drifts.append(step.step_id)
    
    # 4. Compute consistency score
    total_issues = len(contradictions) + len(inversions) + len(drifts)
    consistency_score = max(0.0, 1.0 - 0.1 * total_issues)
    
    return {
        "score": consistency_score,
        "contradictions": len(contradictions),
        "inversions": len(inversions),
        "drifts": len(drifts),
        "details": {
            "contradiction_pairs": contradictions,
            "inversion_steps": inversions,
            "drift_steps": drifts
        }
    }


def _contradicts(text1, text2):
    """
    Simple contradiction detection using negation patterns.
    
    More sophisticated approach would use NLI (Natural Language Inference) model.
    """
    # Negation patterns
    negations = ["not", "never", "no", "isn't", "aren't", "wasn't", "weren't", 
                 "don't", "doesn't", "didn't", "cannot", "can't", "won't", "wouldn't"]
    
    # Extract key phrases (simple approach: nouns and verbs)
    phrases1 = set(_extract_key_phrases(text1))
    phrases2 = set(_extract_key_phrases(text2))
    
    # Check for negation of same concept
    common_phrases = phrases1 & phrases2
    
    for phrase in common_phrases:
        # Check if one text has negation and other doesn't
        text1_has_neg = any(neg in text1.lower() for neg in negations)
        text2_has_neg = any(neg in text2.lower() for neg in negations)
        
        if text1_has_neg != text2_has_neg:
            # Check if negation is near the common phrase
            if _negation_near_phrase(text1, phrase, negations) != \
               _negation_near_phrase(text2, phrase, negations):
                return True
    
    return False


def _confidence_inverted(text1, text2):
    """
    Detect confidence level inversion.
    
    High confidence → Low confidence on related topic.
    """
    high_conf_patterns = [
        "certain", "definitely", "absolutely", "sure", "confident",
        "clearly", "obviously", "undoubtedly", "without a doubt"
    ]
    
    low_conf_patterns = [
        "maybe", "perhaps", "might", "possibly", "unsure", 
        "not sure", "uncertain", "unclear", "could be", "may be"
    ]
    
    text1_lower = text1.lower()
    text2_lower = text2.lower()
    
    # Check if text1 has high confidence and text2 has low confidence
    text1_high = any(pattern in text1_lower for pattern in high_conf_patterns)
    text2_low = any(pattern in text2_lower for pattern in low_conf_patterns)
    
    return text1_high and text2_low


def _drifts_from_instruction(prompt, output):
    """
    Detect instruction drift.
    
    Checks if output ignores or contradicts original instructions.
    """
    # Extract action verbs from prompt
    action_verbs = [
        "analyze", "summarize", "explain", "list", "compare", 
        "describe", "evaluate", "identify", "create", "generate"
    ]
    
    prompt_lower = prompt.lower()
    output_lower = output.lower()
    
    # Check if prompt contains action verb but output doesn't follow it
    for verb in action_verbs:
        if verb in prompt_lower:
            # Check if output addresses the verb
            # Simple heuristic: verb or related words should appear in output
            related_words = _get_related_words(verb)
            
            if not any(word in output_lower for word in related_words):
                return True
    
    return False


def _extract_key_phrases(text):
    """Extract key phrases (simplified: just words)."""
    # Remove punctuation and split
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    
    # Filter stop words (simplified)
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
    
    return [w for w in words if w not in stop_words and len(w) > 3]


def _negation_near_phrase(text, phrase, negations, window=5):
    """Check if negation appears near phrase."""
    words = text.lower().split()
    
    try:
        phrase_idx = words.index(phrase.lower())
        
        # Check window around phrase
        start = max(0, phrase_idx - window)
        end = min(len(words), phrase_idx + window + 1)
        
        window_words = words[start:end]
        
        return any(neg in window_words for neg in negations)
    except ValueError:
        return False


def _get_related_words(verb):
    """Get words related to action verb."""
    related = {
        "analyze": ["analysis", "examined", "studied", "analyzed"],
        "summarize": ["summary", "summarized", "overview", "brief"],
        "explain": ["explanation", "explained", "because", "reason"],
        "list": ["listed", "items", "following", "include"],
        "compare": ["comparison", "compared", "versus", "difference"],
        "describe": ["description", "described", "details", "characteristics"],
        "evaluate": ["evaluation", "assessed", "judged", "rating"],
        "identify": ["identified", "found", "discovered", "recognized"],
        "create": ["created", "generated", "built", "made"],
        "generate": ["generated", "created", "produced", "output"]
    }
    
    return related.get(verb, [verb])
