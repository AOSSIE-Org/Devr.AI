import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

from app.database.supabase.client import get_supabase_client

logger = logging.getLogger(__name__)

_admin_logs_table_ready: Optional[bool] = None


async def ensure_admin_logs_table() -> bool:
    """Check whether the admin_logs table is available in the current environment."""
    global _admin_logs_table_ready

    if _admin_logs_table_ready is True:
        return True

    try:
        supabase = get_supabase_client()
        await supabase.table("admin_logs").select("id").limit(1).execute()
        _admin_logs_table_ready = True
        return True
    except Exception as e:
        logger.error(
            "admin_logs table is unavailable. Apply migration at "
            "backend/database/02_create_admin_logs_table.sql. Details: %s",
            str(e),
        )
        return False


async def log_admin_action(
    executor_id: str,
    executor_username: str,
    command_name: str,
    server_id: str,
    action_result: str = "success",
    command_args: Optional[Dict[str, Any]] = None,
    target_id: Optional[str] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Log admin command execution to database. Returns log UUID or None if failed."""
    try:
        if not await ensure_admin_logs_table():
            return None

        supabase = get_supabase_client()

        # Validate action_result
        if action_result not in ["success", "failure", "error"]:
            logger.warning(f"Invalid action_result '{action_result}', defaulting to 'error'")
            action_result = "error"

        # Prepare log entry
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "executor_id": executor_id,
            "executor_username": executor_username,
            "command_name": command_name,
            "command_args": command_args or {},
            "target_id": target_id,
            "action_result": action_result,
            "error_message": error_message,
            "server_id": server_id,
            "metadata": metadata or {},
        }

        # Insert log entry
        response = await supabase.table("admin_logs").insert(log_entry).execute()

        if response.data:
            log_id = response.data[0]["id"]
            logger.info(
                f"Admin action logged: id={log_id}, executor={executor_username}, "
                f"command={command_name}, result={action_result}"
            )
            return log_id
        else:
            logger.error(f"Failed to log admin action: {response}")
            return None

    except Exception as e:
        logger.error(f"Error logging admin action: {str(e)}", exc_info=True)
        return None


async def get_admin_logs(
    executor_id: Optional[str] = None,
    command_name: Optional[str] = None,
    server_id: Optional[str] = None,
    action_result: Optional[str] = None,
    target_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """Get admin logs with optional filtering. Supports pagination via limit/offset."""
    try:
        supabase = get_supabase_client()

        # Enforce maximum limit
        limit = min(limit, 1000)

        # Build query
        query = supabase.table("admin_logs").select("*")

        # Apply filters
        if executor_id:
            query = query.eq("executor_id", executor_id)

        if command_name:
            query = query.eq("command_name", command_name)

        if server_id:
            query = query.eq("server_id", server_id)

        if action_result:
            if action_result not in ["success", "failure", "error"]:
                logger.warning(f"Invalid action_result filter: {action_result}")
            else:
                query = query.eq("action_result", action_result)

        if target_id:
            query = query.eq("target_id", target_id)

        if start_time:
            query = query.gte("timestamp", start_time.isoformat())

        if end_time:
            query = query.lte("timestamp", end_time.isoformat())

        # Order by timestamp (newest first) and apply pagination
        query = query.order("timestamp", desc=True).range(offset, offset + limit - 1)

        # Execute query
        response = await query.execute()

        if response.data:
            logger.info(
                f"Retrieved {len(response.data)} admin logs "
                f"(limit={limit}, offset={offset})"
            )
            return response.data
        else:
            logger.info("No admin logs found matching the criteria")
            return []

    except Exception as e:
        logger.error(f"Error retrieving admin logs: {str(e)}", exc_info=True)
        return []


async def get_admin_log_stats(
    server_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Get usage stats for admin commands including success rates and top executors."""
    try:
        supabase = get_supabase_client()

        # Paginate through matching logs to avoid unbounded result sets
        batch_size = 1000
        offset = 0

        total_commands = 0
        success_count = 0
        failure_count = 0
        error_count = 0
        commands_by_type: Dict[str, int] = {}
        executor_counts: Dict[str, int] = {}

        while True:
            query = supabase.table("admin_logs").select(
                "command_name,action_result,executor_username"
            )

            if server_id:
                query = query.eq("server_id", server_id)

            if start_time:
                query = query.gte("timestamp", start_time.isoformat())

            if end_time:
                query = query.lte("timestamp", end_time.isoformat())

            query = query.order("timestamp", desc=True).range(offset, offset + batch_size - 1)

            response = await query.execute()
            logs = response.data or []

            if not logs:
                break

            total_commands += len(logs)

            for log in logs:
                action_result = log.get("action_result")
                if action_result == "success":
                    success_count += 1
                elif action_result == "failure":
                    failure_count += 1
                elif action_result == "error":
                    error_count += 1

                cmd = log.get("command_name") or "unknown"
                commands_by_type[cmd] = commands_by_type.get(cmd, 0) + 1

                executor = log.get("executor_username") or "unknown"
                executor_counts[executor] = executor_counts.get(executor, 0) + 1

            if len(logs) < batch_size:
                break

            offset += batch_size

        if total_commands == 0:
            return {
                "total_commands": 0,
                "success_count": 0,
                "failure_count": 0,
                "error_count": 0,
                "commands_by_type": {},
                "top_executors": [],
            }

        # Sort executors by count
        top_executors = [
            {"username": username, "count": count}
            for username, count in sorted(
                executor_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
        ]

        stats = {
            "total_commands": total_commands,
            "success_count": success_count,
            "failure_count": failure_count,
            "error_count": error_count,
            "success_rate": round((success_count / total_commands * 100), 2) if total_commands > 0 else 0,
            "commands_by_type": commands_by_type,
            "top_executors": top_executors,
        }

        logger.info(f"Generated admin log statistics: {total_commands} total commands")
        return stats

    except Exception as e:
        logger.error(f"Error getting admin log stats: {str(e)}", exc_info=True)
        return {
            "total_commands": 0,
            "success_count": 0,
            "failure_count": 0,
            "error_count": 0,
            "commands_by_type": {},
            "top_executors": [],
        }
