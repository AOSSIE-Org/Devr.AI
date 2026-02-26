-- Create users table to store extended user profile information
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Contact & Identity
    email TEXT,
    
    -- Platform Integrations
    discord_id TEXT UNIQUE,
    discord_username TEXT,
    github_id TEXT UNIQUE,
    github_username TEXT,
    slack_id TEXT UNIQUE,
    slack_username TEXT,
    
    -- Profile Information
    display_name TEXT NOT NULL DEFAULT 'User',
    avatar_url TEXT,
    bio TEXT,
    location TEXT,
    
    -- Verification
    is_verified BOOLEAN NOT NULL DEFAULT false,
    verification_token TEXT,
    verification_token_expires_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    
    -- Stats & Metadata
    skills JSONB DEFAULT '{}',
    github_stats JSONB DEFAULT '{}',
    last_active_discord TIMESTAMPTZ,
    last_active_github TIMESTAMPTZ,
    last_active_slack TIMESTAMPTZ,
    total_interactions_count INTEGER NOT NULL DEFAULT 0,
    preferred_languages TEXT[] DEFAULT '{}'
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_discord_id ON public.users(discord_id);
CREATE INDEX IF NOT EXISTS idx_users_github_id ON public.users(github_id);
CREATE INDEX IF NOT EXISTS idx_users_slack_id ON public.users(slack_id);
CREATE INDEX IF NOT EXISTS idx_users_github_username ON public.users(github_username);

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
-- Users can view their own profile
CREATE POLICY "Users can view their own profile"
    ON public.users
    FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update their own profile"
    ON public.users
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Function to handle new user creation from auth.users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, display_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1), 'User'),
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create user profile when auth user is created
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Add helpful comments
COMMENT ON TABLE public.users IS 'Extended user profile information synced with auth.users';
COMMENT ON COLUMN public.users.display_name IS 'User display name from signup or profile update';
COMMENT ON COLUMN public.users.skills IS 'User skills and expertise areas';
COMMENT ON COLUMN public.users.github_stats IS 'Cached GitHub statistics';
COMMENT ON COLUMN public.users.preferred_languages IS 'Array of preferred programming languages';
