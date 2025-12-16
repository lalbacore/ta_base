def compute_coherence(steps):
    """Compute semantic coherence based on explanations."""
    score = 0.8
    for step in steps:
        if not step.has_explanation:
            score -= 0.1
    return max(0.0, score)

def compute_consistency(steps):
    """Detect logical consistency issues."""
    combined_text = " ".join([s.output or "" for s in steps]).lower()
    contradictions = 0
    if "certain" in combined_text and "not sure" in combined_text:
        contradictions += 1
    
    return 1.0 if contradictions == 0 else 0.5

def compute_efficiency(steps):
    """Compute token efficiency ratio."""
    total_in = sum(s.tokens_in or 0 for s in steps)
    total_out = sum(s.tokens_out or 0 for s in steps)
    
    if total_in == 0:
        ratio = 0.0
    else:
        ratio = total_out / total_in
        
    return 1.0 if ratio < 2.0 else 0.5
