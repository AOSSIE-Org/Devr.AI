-- =========================================================
-- STEP 1: FULL CLEANUP (Re-initialization)
-- =========================================================
DROP TABLE IF EXISTS public.indexed_repositories CASCADE;
DROP TABLE IF EXISTS public.interactions CASCADE;
DROP TABLE IF EXISTS public.conversation_context CASCADE;
DROP TABLE IF EXISTS public.organization_integrations CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- =========================================================
-- STEP 2: CREATE USERS TABLE
-- =========================================================
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id TEXT UNIQUE,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    discord_username TEXT,
    display_name TEXT,
    preferred_languages TEXT[],
    last_active_discord TIMESTAMPTZ DEFAULT NOW(),
    
    -- Verification Columns
    verification_token TEXT,
    verification_token_expires_at TIMESTAMPTZ,
    
    -- GitHub Data Columns
    github_id TEXT,
    github_username TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Access Users" ON public.users FOR ALL USING (true) WITH CHECK (true);

-- =========================================================
-- STEP 3: INTEGRATIONS TABLE
-- =========================================================
CREATE TABLE public.organization_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('github', 'discord', 'slack', 'discourse')),
    organization_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

CREATE INDEX IF NOT EXISTS idx_org_integrations_user_id ON organization_integrations(user_id);
ALTER TABLE public.organization_integrations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Access Orgs" ON organization_integrations FOR ALL USING (true) WITH CHECK (true);

-- =========================================================
-- STEP 4: MEMORY TABLES (Context & Interactions)
-- =========================================================
CREATE TABLE public.conversation_context (
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE PRIMARY KEY,
    context JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    session_id TEXT,
    input_text TEXT,
    output_text TEXT,
    tool_usage JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.conversation_context ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Context Access" ON conversation_context FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE public.interactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Interaction Access" ON interactions FOR ALL USING (true) WITH CHECK (true);

-- =========================================================
-- STEP 5: INDEXED REPOSITORIES (Complete Definition)
-- =========================================================
CREATE TABLE public.indexed_repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    repository_full_name TEXT NOT NULL,
    graph_name TEXT NOT NULL,
    
    -- ✅ All Critical Columns Included Here
    indexed_by_discord_id TEXT,
    last_error TEXT,
    indexed_at TIMESTAMPTZ DEFAULT NOW(),
    
    branch TEXT DEFAULT 'main',
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    indexing_status TEXT DEFAULT 'pending',
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, repository_full_name)
);

CREATE INDEX IF NOT EXISTS idx_indexed_repos_user ON indexed_repositories(user_id);
ALTER TABLE public.indexed_repositories ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Index Access" ON indexed_repositories FOR ALL USING (true) WITH CHECK (true);

-- =========================================================
-- STEP 6: FINAL REFRESH
-- =========================================================
NOTIFY pgrst, 'reload schema';