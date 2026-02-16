-- Table for storing admin action logs
CREATE TABLE IF NOT EXISTS admin_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    executor_id TEXT NOT NULL,  -- Discord user ID
    executor_username TEXT NOT NULL,
    command_name TEXT NOT NULL,
    command_args JSONB DEFAULT '{}',  -- Store command parameters
    target_id TEXT,  -- Target user/queue if applicable
    action_result TEXT NOT NULL CHECK (action_result IN ('success', 'failure', 'error')),
    error_message TEXT,
    server_id TEXT NOT NULL,  -- Discord server/guild ID
    metadata JSONB DEFAULT '{}'  -- Additional context (e.g., queue state, bot status, etc.)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp ON admin_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_admin_logs_executor_id ON admin_logs(executor_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_command_name ON admin_logs(command_name);
CREATE INDEX IF NOT EXISTS idx_admin_logs_action_result ON admin_logs(action_result);
CREATE INDEX IF NOT EXISTS idx_admin_logs_server_id ON admin_logs(server_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_target_id ON admin_logs(target_id) WHERE target_id IS NOT NULL;

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_admin_logs_executor_timestamp ON admin_logs(executor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_admin_logs_command_timestamp ON admin_logs(command_name, timestamp DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE admin_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for admin_logs
-- Only authenticated users can view logs (typically admin dashboard access)
CREATE POLICY "Authenticated users can view admin logs"
    ON admin_logs
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Service role can insert logs (for bot to write logs)
CREATE POLICY "Service role can insert admin logs"
    ON admin_logs
    FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

-- Add helpful comments
COMMENT ON TABLE admin_logs IS 'Tracks all admin command executions for audit trail';
COMMENT ON COLUMN admin_logs.executor_id IS 'Discord user ID of the admin who executed the command';
COMMENT ON COLUMN admin_logs.command_name IS 'Name of the admin command (e.g., /admin stats, /admin pause_queue)';
COMMENT ON COLUMN admin_logs.command_args IS 'JSON object containing command parameters and arguments';
COMMENT ON COLUMN admin_logs.target_id IS 'ID of the target entity if applicable (user ID, queue name, etc.)';
COMMENT ON COLUMN admin_logs.action_result IS 'Result of the command execution: success, failure, or error';
COMMENT ON COLUMN admin_logs.server_id IS 'Discord server/guild ID where the command was executed';
COMMENT ON COLUMN admin_logs.metadata IS 'Additional contextual information (e.g., system state before/after)';
