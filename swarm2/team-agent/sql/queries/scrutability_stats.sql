-- Common Scrutability Queries
-- Useful SQL queries for scrutability analysis

-- ============================================================================
-- 1. Overall Scrutability Statistics
-- ============================================================================

SELECT 
  COUNT(*) as total_episodes,
  AVG(scrutability_score) as avg_scrutability,
  AVG(coherence_score) as avg_coherence,
  AVG(consistency_score) as avg_consistency,
  AVG(efficiency_score) as avg_efficiency,
  SUM(CASE WHEN scrutability_level = 'scrutable' THEN 1 ELSE 0 END) as scrutable_count,
  SUM(CASE WHEN scrutability_level = 'partially_scrutable' THEN 1 ELSE 0 END) as partial_count,
  SUM(CASE WHEN scrutability_level = 'inscrutable' THEN 1 ELSE 0 END) as inscrutable_count
FROM ai_eval.episode_evaluations;

-- ============================================================================
-- 2. Model Performance Comparison
-- ============================================================================

SELECT 
  e.model,
  COUNT(*) as episodes,
  AVG(ev.scrutability_score) as avg_scrutability,
  AVG(ev.coherence_score) as avg_coherence,
  AVG(ev.consistency_score) as avg_consistency,
  AVG(ev.efficiency_score) as avg_efficiency,
  STDDEV(ev.scrutability_score) as std_scrutability
FROM ai_eval.episodes e
JOIN ai_eval.episode_evaluations ev ON e.episode_id = ev.episode_id
GROUP BY e.model
ORDER BY avg_scrutability DESC;

-- ============================================================================
-- 3. Scrutability Trend Over Time
-- ============================================================================

SELECT 
  DATE(evaluated_at) as date,
  AVG(scrutability_score) as avg_scrutability,
  AVG(coherence_score) as avg_coherence,
  AVG(consistency_score) as avg_consistency,
  AVG(efficiency_score) as avg_efficiency,
  COUNT(*) as episodes_evaluated
FROM ai_eval.episode_evaluations
WHERE evaluated_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY DATE(evaluated_at)
ORDER BY date;

-- ============================================================================
-- 4. Top Issue Flags
-- ============================================================================

SELECT 
  flag,
  COUNT(*) as occurrences
FROM ai_eval.episode_evaluations
LATERAL VIEW EXPLODE(flags) AS flag
GROUP BY flag
ORDER BY occurrences DESC
LIMIT 20;

-- ============================================================================
-- 5. Low Scrutability Episodes
-- ============================================================================

SELECT 
  e.episode_id,
  e.model,
  e.start_ts,
  ev.scrutability_score,
  ev.scrutability_level,
  ev.flags,
  ev.notes
FROM ai_eval.episodes e
JOIN ai_eval.episode_evaluations ev ON e.episode_id = ev.episode_id
WHERE ev.scrutability_score < 0.5
ORDER BY ev.evaluated_at DESC
LIMIT 50;

-- ============================================================================
-- 6. Episodes with Specific Issues
-- ============================================================================

-- Episodes with semantic jumps
SELECT 
  episode_id,
  scrutability_score,
  semantic_jumps,
  flags
FROM ai_eval.episode_evaluations
WHERE semantic_jumps > 0
ORDER BY semantic_jumps DESC;

-- Episodes with contradictions
SELECT 
  episode_id,
  scrutability_score,
  contradictions,
  flags
FROM ai_eval.episode_evaluations
WHERE contradictions > 0
ORDER BY contradictions DESC;

-- Episodes with instruction drift
SELECT 
  episode_id,
  scrutability_score,
  instruction_drifts,
  flags
FROM ai_eval.episode_evaluations
WHERE instruction_drifts > 0
ORDER BY instruction_drifts DESC;

-- ============================================================================
-- 7. Token Efficiency Analysis
-- ============================================================================

SELECT 
  e.model,
  AVG(ev.token_ratio) as avg_token_ratio,
  AVG(ev.tokens_per_semantic_delta) as avg_tokens_per_concept,
  AVG(ev.repetition_rate) as avg_repetition,
  AVG(ev.efficiency_score) as avg_efficiency
FROM ai_eval.episodes e
JOIN ai_eval.episode_evaluations ev ON e.episode_id = ev.episode_id
GROUP BY e.model
ORDER BY avg_efficiency DESC;

-- ============================================================================
-- 8. Episode Step Details
-- ============================================================================

SELECT 
  es.episode_id,
  es.step_id,
  es.task_name,
  es.tokens_in,
  es.tokens_out,
  es.latency_ms,
  es.has_explanation,
  es.reasoning_quality
FROM ai_eval.episode_steps es
WHERE es.episode_id = 'YOUR_EPISODE_ID'
ORDER BY es.step_id;

-- ============================================================================
-- 9. Scrutability by Date Range
-- ============================================================================

SELECT 
  DATE_TRUNC('week', evaluated_at) as week,
  AVG(scrutability_score) as avg_scrutability,
  COUNT(*) as episodes
FROM ai_eval.episode_evaluations
WHERE evaluated_at >= CURRENT_DATE - INTERVAL 90 DAYS
GROUP BY DATE_TRUNC('week', evaluated_at)
ORDER BY week;

-- ============================================================================
-- 10. Model Comparison (Statistical)
-- ============================================================================

WITH model_stats AS (
  SELECT 
    e.model,
    ev.scrutability_score
  FROM ai_eval.episodes e
  JOIN ai_eval.episode_evaluations ev ON e.episode_id = ev.episode_id
)
SELECT 
  model,
  COUNT(*) as n,
  AVG(scrutability_score) as mean,
  STDDEV(scrutability_score) as std,
  MIN(scrutability_score) as min,
  PERCENTILE(scrutability_score, 0.25) as q1,
  PERCENTILE(scrutability_score, 0.5) as median,
  PERCENTILE(scrutability_score, 0.75) as q3,
  MAX(scrutability_score) as max
FROM model_stats
GROUP BY model
ORDER BY mean DESC;

-- ============================================================================
-- 11. Recent Evaluations
-- ============================================================================

SELECT 
  e.episode_id,
  e.model,
  e.start_ts,
  ev.scrutability_score,
  ev.scrutability_level,
  ev.evaluated_at
FROM ai_eval.episodes e
JOIN ai_eval.episode_evaluations ev ON e.episode_id = ev.episode_id
ORDER BY ev.evaluated_at DESC
LIMIT 100;

-- ============================================================================
-- 12. Correlation Analysis
-- ============================================================================

SELECT 
  CORR(coherence_score, scrutability_score) as coherence_correlation,
  CORR(consistency_score, scrutability_score) as consistency_correlation,
  CORR(efficiency_score, scrutability_score) as efficiency_correlation,
  CORR(token_ratio, scrutability_score) as token_ratio_correlation,
  CORR(repetition_rate, scrutability_score) as repetition_correlation
FROM ai_eval.episode_evaluations;
