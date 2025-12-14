-- Episode Steps Table - Execution Trace
-- Databricks Job tasks or Agent steps

CREATE TABLE IF NOT EXISTS ai_eval.episode_steps (
  -- Primary identifiers
  episode_id STRING NOT NULL COMMENT 'Foreign key to episodes table',
  step_id INT NOT NULL COMMENT 'Step sequence number (0-indexed)',
  
  -- Step metadata
  task_name STRING COMMENT 'Task or agent name',
  model STRING COMMENT 'Model used for this specific step',
  
  -- Input/Output
  prompt STRING COMMENT 'Input prompt for this step',
  output STRING COMMENT 'Generated output from this step',
  
  -- Token metrics
  tokens_in INT COMMENT 'Input tokens consumed',
  tokens_out INT COMMENT 'Output tokens generated',
  latency_ms INT COMMENT 'Step execution latency in milliseconds',
  
  -- Timestamp
  ts TIMESTAMP COMMENT 'Step execution timestamp',
  
  -- Scrutability fields
  has_explanation BOOLEAN DEFAULT FALSE COMMENT 'Whether step includes explanation',
  explanation STRING COMMENT 'Step explanation or reasoning',
  reasoning_quality DOUBLE COMMENT 'Quality score of reasoning (0.0-1.0)',
  
  -- Flexible metadata
  metadata MAP<STRING, STRING> COMMENT 'Additional step metadata',
  
  -- Auto-generated partition column
  created_date DATE GENERATED ALWAYS AS (CAST(ts AS DATE)) COMMENT 'Partition column for performance'
)
USING DELTA
COMMENT 'Episode execution trace - immutable step records'
PARTITIONED BY (created_date)
LOCATION 's3://your-bucket/ai_eval/episode_steps'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- Composite primary key
ALTER TABLE ai_eval.episode_steps 
ADD CONSTRAINT steps_pk PRIMARY KEY (episode_id, step_id);

-- Foreign key to episodes
ALTER TABLE ai_eval.episode_steps 
ADD CONSTRAINT steps_fk FOREIGN KEY (episode_id) 
REFERENCES ai_eval.episodes(episode_id);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_steps_episode ON ai_eval.episode_steps (episode_id);
CREATE INDEX IF NOT EXISTS idx_steps_model ON ai_eval.episode_steps (model);
CREATE INDEX IF NOT EXISTS idx_steps_ts ON ai_eval.episode_steps (ts);

-- Sample query to verify
-- SELECT episode_id, step_id, task_name, tokens_in, tokens_out 
-- FROM ai_eval.episode_steps 
-- WHERE episode_id = 'your-episode-id' 
-- ORDER BY step_id;
