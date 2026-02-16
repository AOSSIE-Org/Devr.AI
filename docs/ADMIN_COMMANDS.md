# Admin Commands Documentation

## Overview

The admin commands provide server administrators and bot owners with tools to manage, monitor, and troubleshoot the Devr.AI bot. All admin commands are grouped under the `/admin` command prefix.

## Permissions

Admin commands require one of the following:

- **Server Administrator**: Users with the Discord `ADMINISTRATOR` permission
- **Bot Owner**: The user ID configured in `BOT_OWNER_ID` environment variable

All admin command executions are logged for audit purposes.

## Setup

### Configure Bot Owner

Add your Discord user ID to `.env`:

```env
BOT_OWNER_ID=your_discord_user_id_here
```

To find your Discord user ID:
1. Enable Developer Mode in Discord (Settings > App Settings > Advanced)
2. Right-click your profile and select "Copy User ID"

### Run Database Migration

Execute the admin logs table migration:

```sql
-- Run in Supabase SQL Editor or via psql
\i backend/database/02_create_admin_logs_table.sql
```

Optional verification query:

```sql
SELECT to_regclass('public.admin_logs');
```

Expected result: `admin_logs`

> Note: On startup, the backend checks whether `admin_logs` exists. If missing,
> admin commands still run, but admin-action logging is skipped until migration is applied.

## Commands

### /admin stats

Display bot statistics and metrics.

**Usage:** `/admin stats`

**Shows:**
- Server count and total members
- Active threads
- Bot latency and uptime
- Memory usage
- Messages processed (today and 7-day)
- Queue status by priority

### /admin health

Check system health and service status.

**Usage:** `/admin health`

**Checks:**
- Supabase database connection
- RabbitMQ message queue
- Weaviate vector store
- FalkorDB availability
- Gemini API availability

**Status Indicators:**
- Green: Healthy
- Orange: Degraded
- Red: Unhealthy

### /admin user_info

Get detailed information about a user.

**Usage:** `/admin user_info user:<@user>`

**Parameters:**
- `user`: The Discord user to look up (mention or ID)

**Shows:**
- Discord profile (username, ID, account creation date)
- GitHub verification status
- Linked GitHub username (if verified)
- Message count
- Active thread status
- Role count

### /admin user_reset

Reset user state with confirmation.

**Usage:** `/admin user_reset user:<@user> [options]`

**Parameters:**
- `user`: The Discord user to reset
- `reset_memory`: Clear conversation memory (default: False)
- `reset_thread`: Close active thread (default: False)
- `reset_verification`: Clear GitHub verification (default: False)

**Requires Confirmation:** Yes

### /admin queue_status

Check message queue status.

**Usage:** `/admin queue_status`

**Shows:**
- Pending messages by priority (High, Medium, Low)
- Consumer count per queue
- Total pending messages

**Color Indicators:**
- Green: 0 pending
- Blue: 1-9 pending
- Orange: 10-49 pending
- Red: 50+ pending

### /admin queue_clear

Clear messages from the queue.

**Usage:** `/admin queue_clear [priority]`

**Parameters:**
- `priority`: Which queue to clear
  - `all` (default): Clear all queues
  - `high`: Clear high priority only
  - `medium`: Clear medium priority only
  - `low`: Clear low priority only

**Requires Confirmation:** Yes

### /admin cache_clear

Clear cached data.

**Usage:** `/admin cache_clear [cache_type]`

**Parameters:**
- `cache_type`: What to clear
  - `all` (default): Clear all caches
  - `active_threads`: Clear tracked threads
  - `embeddings`: Clear embedding cache
  - `memories`: Clear memory cache

**Requires Confirmation:** Yes (for `all` only)

## Logging

All admin command executions are logged to the `admin_logs` table with:

- Timestamp
- Executor ID and username
- Command name and arguments
- Target user (if applicable)
- Result (success/failure/error)
- Error message (if failed)
- Server ID
- Additional metadata

### Viewing Logs

Query logs via Supabase dashboard or API:

```python
from app.utils.admin_logger import get_admin_logs

# Get recent logs
logs = await get_admin_logs(limit=50)

# Filter by executor
logs = await get_admin_logs(executor_id="123456789")

# Filter by command
logs = await get_admin_logs(command_name="queue_clear")

# Get statistics
from app.utils.admin_logger import get_admin_log_stats
stats = await get_admin_log_stats(server_id="987654321")
```

## Best Practices

### When to Use Queue Clear
- Stuck messages that won't process
- After system errors that corrupted messages
- During maintenance windows

### When to Use User Reset
- User reports conversation issues
- Memory corruption
- Re-verification needed

### When to Use Cache Clear
- After configuration changes
- Memory pressure issues
- Stale data problems

## Troubleshooting

### Commands Not Appearing

1. Wait for Discord to sync slash commands (can take up to 1 hour)
2. Try `/admin` and check autocomplete
3. Restart the bot to force sync

### Permission Denied

1. Verify you have `ADMINISTRATOR` permission in the server
2. Check if `BOT_OWNER_ID` is set correctly in `.env`
3. Verify the bot was restarted after config changes

### Health Check Failures

- **Supabase**: Check credentials in `.env`
- **RabbitMQ**: Verify Docker container is running
- **Weaviate**: Check Docker container and port 8080
- **Gemini API**: Verify API key is valid

### Queue Not Clearing

1. Check RabbitMQ connection with `/admin health`
2. Verify Docker containers are running
3. Check RabbitMQ management console (port 15672)
