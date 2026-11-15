
-- =========================================================
-- DEVR.AI DATABASE SCHEMA
-- =========================================================

-- Drop existing tables if they exist
DROP TABLE IF EXISTS conversation_context CASCADE;
DROP TABLE IF EXISTS interactions CASCADE;
DROP TABLE IF EXISTS repositories CASCADE;
DROP TABLE IF EXISTS users CASCADE;


-- =========================================================
-- 1. USERS TABLE
-- =========================================================

CREATE TABLE users (
    id UUID PRIMARY KEY NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Email is optional but unique when provided
    email TEXT UNIQUE,

    -- Social IDs
    discord_id TEXT UNIQUE,
    discord_username TEXT,
    github_id TEXT UNIQUE,
    github_username TEXT,
    slack_id TEXT UNIQUE,
    slack_username TEXT,

    display_name TEXT NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    location TEXT,

    -- Verification fields
    is_verified BOOLEAN NOT NULL DEFAULT false,
    verification_token TEXT UNIQUE,
    verification_token_expires_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,

    skills JSONB,
    github_stats JSONB,

    last_active_discord TIMESTAMPTZ,
    last_active_github TIMESTAMPTZ,
    last_active_slack TIMESTAMPTZ,

    total_interactions_count INTEGER NOT NULL DEFAULT 0,
    preferred_languages TEXT[]
);


-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_verification_token_expires_at
ON users(verification_token_expires_at)
WHERE verification_token_expires_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_discord_verification
ON users(discord_id, verification_token)
WHERE verification_token IS NOT NULL;


-- =========================================================
-- 2. REPOSITORIES TABLE
-- =========================================================

CREATE TABLE repositories (
    id UUID PRIMARY KEY NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    github_id BIGINT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    description TEXT,

    stars_count INTEGER NOT NULL DEFAULT 0,
    forks_count INTEGER NOT NULL DEFAULT 0,
    open_issues_count INTEGER NOT NULL DEFAULT 0,

    languages_used TEXT[],
    topics TEXT[],

    is_indexed BOOLEAN NOT NULL DEFAULT false,
    indexed_at TIMESTAMPTZ,
    indexing_status TEXT,
    last_commit_hash TEXT
);


-- =========================================================
-- 3. INTERACTIONS TABLE
-- =========================================================

CREATE TABLE interactions (
    id UUID PRIMARY KEY NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    user_id UUID NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    repository_id UUID
        REFERENCES repositories(id) ON DELETE SET NULL,

    platform TEXT NOT NULL,
    platform_specific_id TEXT NOT NULL,
    channel_id TEXT,
    thread_id TEXT,

    content TEXT,
    interaction_type TEXT,
    sentiment_score FLOAT,
    intent_classification TEXT,
    topics_discussed TEXT[],
    metadata JSONB
);


-- =========================================================
-- 4. CONVERSATION CONTEXT TABLE
-- Updated schema
-- =========================================================

CREATE TABLE conversation_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    platform TEXT NOT NULL,
    memory_thread_id TEXT,

    conversation_summary TEXT,
    key_topics TEXT[],
    total_interactions INTEGER DEFAULT 0,

    session_start_time TIMESTAMPTZ,
    session_end_time TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- Conversation context indexes
CREATE INDEX IF NOT EXISTS idx_conversation_context_user_id
ON conversation_context(user_id);

CREATE INDEX IF NOT EXISTS idx_conversation_context_platform
ON conversation_context(platform);

CREATE INDEX IF NOT EXISTS idx_conversation_context_memory_thread_id
ON conversation_context(memory_thread_id);


-- =========================================================
-- 5. INDEXED REPOSITORIES TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS indexed_repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Repository information
    repository_full_name TEXT NOT NULL,
    graph_name TEXT NOT NULL,

    -- Indexing status
    indexing_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (indexing_status IN ('pending', 'completed', 'failed')),

    indexed_at TIMESTAMPTZ,

    -- Who indexed it
    indexed_by_discord_id TEXT NOT NULL,

    -- Soft delete
    is_deleted BOOLEAN DEFAULT false,

    -- Optional metadata
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    last_error TEXT
);


-- Indexed repositories indexes
CREATE UNIQUE INDEX IF NOT EXISTS unique_active_repo
ON indexed_repositories(repository_full_name)
WHERE is_deleted = false;

CREATE UNIQUE INDEX IF NOT EXISTS unique_active_graph
ON indexed_repositories(graph_name)
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_indexed_repos_discord
ON indexed_repositories(indexed_by_discord_id)
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_indexed_repos_status
ON indexed_repositories(indexing_status)
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_indexed_repos_full_name
ON indexed_repositories(repository_full_name)
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_indexed_repos_graph_name
ON indexed_repositories(graph_name)
WHERE is_deleted = false;


-- =========================================================
-- 6. UPDATED_AT FUNCTION
-- =========================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- =========================================================
-- 7. UPDATED_AT TRIGGERS
-- =========================================================

DROP TRIGGER IF EXISTS update_indexed_repositories_updated_at
ON indexed_repositories;

CREATE TRIGGER update_indexed_repositories_updated_at
BEFORE UPDATE ON indexed_repositories
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_conversation_context_updated_at
ON conversation_context;

CREATE TRIGGER update_conversation_context_updated_at
BEFORE UPDATE ON conversation_context
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- =========================================================
-- 8. INDEXED REPOSITORIES DOCUMENTATION
-- =========================================================

COMMENT ON TABLE indexed_repositories IS
'Tracks GitHub repositories indexed in FalkorDB';

COMMENT ON COLUMN indexed_repositories.repository_full_name IS
'Full repository name: owner/repo (e.g., AOSSIE-Org/Devr.AI)';

COMMENT ON COLUMN indexed_repositories.graph_name IS
'Graph name in FalkorDB (e.g., Devr.AI)';

COMMENT ON COLUMN indexed_repositories.is_deleted IS
'Soft delete flag - allows re-indexing the same repository later';

COMMENT ON INDEX unique_active_repo IS
'Ensures only one active (non-deleted) version of each repository exists';


-- =========================================================
-- 9. ATOMIC USER INTERACTION COUNTER
-- =========================================================

CREATE OR REPLACE FUNCTION increment_user_interaction_count(user_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    new_count INTEGER;
BEGIN
    UPDATE users
    SET total_interactions_count = total_interactions_count + 1
    WHERE id = user_uuid
    RETURNING total_interactions_count INTO new_count;

    RETURN new_count;
END;
$$ LANGUAGE plpgsql;


-- Function documentation
COMMENT ON FUNCTION increment_user_interaction_count(UUID) IS
'Atomically increments the total_interactions_count for a user. Returns the new count or NULL if user not found.';


-- =========================================================
-- END OF DEVR.AI DATABASE SCHEMA
-- =========================================================
