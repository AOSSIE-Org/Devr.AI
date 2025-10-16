-- Table for storing organization registrations
CREATE TABLE IF NOT EXISTS organization_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('github', 'discord', 'slack', 'discourse')),
    organization_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    config JSONB DEFAULT '{}',  -- Stores org link, discord_guild_id, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Ensure one integration per user per platform
    UNIQUE(user_id, platform)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_org_integrations_user_id ON organization_integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_org_integrations_platform ON organization_integrations(platform);
CREATE INDEX IF NOT EXISTS idx_org_integrations_is_active ON organization_integrations(is_active);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_organization_integrations_updated_at
    BEFORE UPDATE ON organization_integrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE organization_integrations ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for organization_integrations
-- Users can only see and manage their own integrations
CREATE POLICY "Users can view their own integrations"
    ON organization_integrations
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own integrations"
    ON organization_integrations
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own integrations"
    ON organization_integrations
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own integrations"
    ON organization_integrations
    FOR DELETE
    USING (auth.uid() = user_id);

-- Add helpful comments
COMMENT ON TABLE organization_integrations IS 'Stores registered organizations (just metadata, no tokens)';
COMMENT ON COLUMN organization_integrations.config IS 'Platform-specific data: organization_link, discord_guild_id, etc.';

