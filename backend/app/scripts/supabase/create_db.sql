-- Drop existing tables if they exist
DROP TABLE IF EXISTS conversation_context;
DROP TABLE IF EXISTS interactions;
DROP TABLE IF EXISTS repositories;
DROP TABLE IF EXISTS users;

-- Table: users
CREATE TABLE users (
    id UUID PRIMARY KEY NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- The email is optional to allow social-only sign-ups, but must be unique if provided.
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

    -- Verification fields to manage the GitHub linking flow.
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
    preferred_languages TEXT[],
);

-- Create index for efficient cleanup queries
CREATE INDEX IF NOT EXISTS idx_users_verification_token_expires_at
ON users(verification_token_expires_at)
WHERE verification_token_expires_at IS NOT NULL;

-- Create index for efficient verification queries
CREATE INDEX IF NOT EXISTS idx_users_discord_verification
ON users(discord_id, verification_token)
WHERE verification_token IS NOT NULL;

-- Table: repositories
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

-- Table: interactions
CREATE TABLE interactions (
    id UUID PRIMARY KEY NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    repository_id UUID REFERENCES repositories(id) ON DELETE SET NULL,
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

-- Table: conversation_contexts
CREATE TABLE conversation_context (
    id UUID PRIMARY KEY NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    memory_thread_id TEXT NOT NULL UNIQUE,
    conversation_summary TEXT,
    key_topics TEXT[],
    total_interactions INTEGER,
    session_start_time TIMESTAMPTZ,
    session_end_time TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
