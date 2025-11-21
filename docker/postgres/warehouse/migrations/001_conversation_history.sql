-- Migration: Add conversation history and entity tracking tables
-- Purpose: Enable persistent memory and context across sessions

-- Conversation history table
CREATE TABLE IF NOT EXISTS conversation_history (
    session_id UUID PRIMARY KEY,
    user_id VARCHAR(255),
    messages JSONB NOT NULL DEFAULT '[]',
    entities JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversation_history(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_last_activity ON conversation_history(last_activity);

-- GIN index for JSONB queries
CREATE INDEX IF NOT EXISTS idx_conversation_entities ON conversation_history USING GIN (entities);

COMMENT ON TABLE conversation_history IS 'Persistent storage for chat conversations with entity tracking';
COMMENT ON COLUMN conversation_history.messages IS 'Array of chat messages (user/assistant)';
COMMENT ON COLUMN conversation_history.entities IS 'Tracked entities: parts, metrics, time periods, etc.';
COMMENT ON COLUMN conversation_history.metadata IS 'Additional session metadata';
