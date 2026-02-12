-- Table for storing indexed repository information
CREATE TABLE IF NOT EXISTS indexed_repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_full_name VARCHAR(255) NOT NULL,  -- e.g., 'owner/repo'
    graph_name VARCHAR(255) NOT NULL,            -- Name of the graph in FalkorDB
    indexing_status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (indexing_status IN ('pending', 'completed', 'failed')),
    indexed_by_discord_id VARCHAR(255),          -- Discord user who requested indexing
    indexed_at TIMESTAMPTZ,                      -- When indexing completed
    node_count INTEGER DEFAULT 0,                -- Number of nodes in the graph
    edge_count INTEGER DEFAULT 0,                -- Number of edges in the graph
    last_error TEXT,                             -- Last error message if failed
    is_deleted BOOLEAN NOT NULL DEFAULT false,   -- Soft delete flag
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Ensure unique repository entries (that are not deleted)
    UNIQUE(repository_full_name) WHERE (is_deleted = false)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_indexed_repos_full_name ON indexed_repositories(repository_full_name);
CREATE INDEX IF NOT EXISTS idx_indexed_repos_status ON indexed_repositories(indexing_status);
CREATE INDEX IF NOT EXISTS idx_indexed_repos_is_deleted ON indexed_repositories(is_deleted);
CREATE INDEX IF NOT EXISTS idx_indexed_repos_discord_id ON indexed_repositories(indexed_by_discord_id);

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_indexed_repositories_updated_at
    BEFORE UPDATE ON indexed_repositories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Note: No RLS policies are added here because this table is accessed by the backend service
-- If you want to enable RLS, you'll need to add appropriate policies

-- Add helpful comments
COMMENT ON TABLE indexed_repositories IS 'Stores metadata about repositories that have been indexed for code graph analysis';
COMMENT ON COLUMN indexed_repositories.graph_name IS 'The name of the graph created in FalkorDB';
COMMENT ON COLUMN indexed_repositories.indexing_status IS 'Current status: pending, completed, or failed';
