-- Episodes Table - Immutable Episode Records
-- This is the read-only truth. No mutation ever.

CREATE TABLE IF NOT EXISTS ai_eval.episodes (
  -- Primary identifiers
  episode_id STRING NOT NULL COMMENT 'Unique episode identifier',
  run_id STRING COMMENT 'Databricks run_id',
  job_id STRING COMMENT 'Databricks job_id',
  
  -- Episode metadata
  model STRING COMMENT 'LLM model used (e.g., gpt-4, claude-3)',
  start_ts TIMESTAMP COMMENT 'Episode start timestamp',
  end_ts TIMESTAMP COMMENT 'Episode end timestamp',
  status STRING COMMENT 'Episode status: running, completed, failed',
  total_steps INT COMMENT 'Total number of steps in episode',
  
  -- Flexible metadata
  metadata MAP<STRING, STRING> COMMENT 'Additional metadata as key-value pairs',
  
  -- Auto-generated partition column
  created_date DATE GENERATED ALWAYS AS (CAST(start_ts AS DATE)) COMMENT 'Partition column for performance'
) 
USING DELTA
COMMENT 'Immutable episode records - append only, no updates'
PARTITIONED BY (created_date)
LOCATION 's3://your-bucket/ai_eval/episodes'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- Primary key constraint
ALTER TABLE ai_eval.episodes 
ADD CONSTRAINT episodes_pk PRIMARY KEY (episode_id);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_episodes_model ON ai_eval.episodes (model);
CREATE INDEX IF NOT EXISTS idx_episodes_status ON ai_eval.episodes (status);
CREATE INDEX IF NOT EXISTS idx_episodes_start_ts ON ai_eval.episodes (start_ts);

-- Sample query to verify
-- SELECT * FROM ai_eval.episodes WHERE created_date >= current_date() - INTERVAL 7 DAYS;
