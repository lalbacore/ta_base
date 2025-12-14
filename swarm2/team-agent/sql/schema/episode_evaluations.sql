-- Episode Evaluations Table - Scrutability Scores
-- Output from stateless Spark evaluator job

CREATE TABLE IF NOT EXISTS ai_eval.episode_evaluations (
  -- Primary identifier
  episode_id STRING NOT NULL COMMENT 'Foreign key to episodes table',
  
  -- Core scrutability scores (0.0 - 1.0)
  coherence_score DOUBLE COMMENT 'Semantic coherence score',
  consistency_score DOUBLE COMMENT 'Logical consistency score',
  efficiency_score DOUBLE COMMENT 'Token efficiency score',
  
  -- Overall scrutability
  scrutability_score DOUBLE COMMENT 'Weighted average of all scores',
  scrutability_level STRING COMMENT 'Classification: scrutable, partially_scrutable, inscrutable',
  
  -- Detailed issue counts
  semantic_jumps INT COMMENT 'Number of unexplained semantic jumps',
  contradictions INT COMMENT 'Number of logical contradictions detected',
  confidence_inversions INT COMMENT 'Number of confidence reversals',
  instruction_drifts INT COMMENT 'Number of instruction deviations',
  
  -- Efficiency metrics
  token_ratio DOUBLE COMMENT 'Ratio of output tokens to input tokens',
  tokens_per_semantic_delta DOUBLE COMMENT 'Tokens per unique concept',
  repetition_rate DOUBLE COMMENT 'Rate of repeated content (0.0-1.0)',
  
  -- Issue flags
  flags ARRAY<STRING> COMMENT 'Specific issue flags (e.g., semantic_jump_step_4)',
  notes STRING COMMENT 'Human-readable evaluation notes',
  
  -- Evaluation metadata
  evaluator_version STRING COMMENT 'Version of evaluator that produced this result',
  evaluated_at TIMESTAMP COMMENT 'When evaluation was performed',
  evaluation_duration_ms INT COMMENT 'How long evaluation took',
  
  -- Auto-generated partition column
  created_date DATE GENERATED ALWAYS AS (CAST(evaluated_at AS DATE)) COMMENT 'Partition column for performance'
)
USING DELTA
COMMENT 'Episode scrutability evaluations - deterministic, replayable results'
PARTITIONED BY (created_date)
LOCATION 's3://your-bucket/ai_eval/episode_evaluations'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- Primary key
ALTER TABLE ai_eval.episode_evaluations 
ADD CONSTRAINT evals_pk PRIMARY KEY (episode_id);

-- Foreign key to episodes
ALTER TABLE ai_eval.episode_evaluations 
ADD CONSTRAINT evals_fk FOREIGN KEY (episode_id) 
REFERENCES ai_eval.episodes(episode_id);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_evals_scrutability_level ON ai_eval.episode_evaluations (scrutability_level);
CREATE INDEX IF NOT EXISTS idx_evals_scrutability_score ON ai_eval.episode_evaluations (scrutability_score);
CREATE INDEX IF NOT EXISTS idx_evals_evaluated_at ON ai_eval.episode_evaluations (evaluated_at);

-- Sample query to verify
-- SELECT episode_id, scrutability_score, scrutability_level, flags
-- FROM ai_eval.episode_evaluations
-- WHERE scrutability_level = 'inscrutable'
-- ORDER BY evaluated_at DESC;
