from datetime import datetime

def aggregate_scores(coherence, consistency, efficiency):
    """
    Compute final scrutability score (0.0 - 1.0).
    Weights: Coherence (40%), Consistency (40%), Efficiency (20%)
    """
    total = (coherence * 0.4) + (consistency * 0.4) + (efficiency * 0.2)
    return float(total)

def classify_level(score):
    """Classify score into scrutability levels."""
    if score >= 0.8: return "scrutable"
    if score >= 0.3: return "partially_scrutable"
    return "inscrutable"

class EvaluationResult:
    def __init__(self, episode_id, coherence, consistency, efficiency, flags=None):
        self.episode_id = episode_id
        self.coherence_score = coherence
        self.consistency_score = consistency
        self.efficiency_score = efficiency
        self.scrutability_score = aggregate_scores(coherence, consistency, efficiency)
        self.scrutability_level = classify_level(self.scrutability_score)
        self.flags = flags or []
        self.evaluated_at = str(datetime.now())
        self.evaluator_version = "0.3.1"

    def to_dict(self):
        return {
            "episode_id": self.episode_id,
            "coherence_score": self.coherence_score,
            "consistency_score": self.consistency_score,
            "efficiency_score": self.efficiency_score,
            "scrutability_score": self.scrutability_score,
            "scrutability_level": self.scrutability_level,
            "flags": self.flags,
            "evaluated_at": self.evaluated_at,
            "evaluator_version": self.evaluator_version
        }
