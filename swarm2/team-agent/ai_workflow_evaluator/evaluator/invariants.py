def check_invariants(steps):
    """
    Verify fundamental safety properties before evaluation.
    Raises ValueError if invariants are violated.
    """
    if not steps:
        raise ValueError("Episode has no steps to evaluate")
        
    for i, s in enumerate(steps):
        if not hasattr(s, 'step_id'):
             raise ValueError("Malformed step: missing step_id")

def assert_idempotency(result1, result2):
    """Verify that two evaluation runs produced identical results."""
    assert result1.scrutability_score == result2.scrutability_score
    assert result1.scrutability_level == result2.scrutability_level
    assert set(result1.flags) == set(result2.flags)
