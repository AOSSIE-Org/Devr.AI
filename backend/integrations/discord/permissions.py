from functools import wraps
from typing import Optional, Tuple, Dict, Any
import discord
from discord import Interaction
import logging
import inspect

from app.core.config.settings import settings
from app.utils.admin_logger import log_admin_action

logger = logging.getLogger(__name__)


def is_bot_owner(user_id: int) -> bool:
    return settings.bot_owner_id is not None and user_id == settings.bot_owner_id


def is_admin(interaction: Interaction) -> bool:
    if not interaction.guild:
        return False
    member = interaction.guild.get_member(interaction.user.id)
    if not member:
        return False
    return member.guild_permissions.administrator


def get_permission_embed(
    title: str = "Permission Denied",
    description: str = "You don't have permission to use this command.",
    required_permission: str = "Administrator or Bot Owner"
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.red()
    )
    embed.add_field(name="Required Permission", value=required_permission, inline=False)
    embed.add_field(name="Contact", value="Contact the bot owner if you believe this is an error.", inline=False)
    return embed


def require_admin(func):
    @wraps(func)
    async def wrapper(self, interaction: Interaction, *args, **kwargs):
        has_permission, reason = check_permissions(interaction)

        if not has_permission:
            logger.warning(
                f"Admin command denied: user={interaction.user.id} "
                f"command={interaction.command.name if interaction.command else 'unknown'} "
                f"reason={reason}"
            )

            # Log failed permission check
            await log_admin_action(
                executor_id=str(interaction.user.id),
                executor_username=interaction.user.name,
                command_name=interaction.command.name if interaction.command else 'unknown',
                server_id=str(interaction.guild.id) if interaction.guild else 'dm',
                action_result='failure',
                error_message=f"Permission denied: {reason}",
                metadata={
                    'is_owner': is_bot_owner(interaction.user.id),
                    'is_admin': is_admin(interaction),
                }
            )

            embed = get_permission_embed()

            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return None

        logger.info(
            f"Admin command authorized: user={interaction.user.id} "
            f"is_owner={is_bot_owner(interaction.user.id)} "
            f"command={interaction.command.name if interaction.command else 'unknown'}"
        )

        # Extract command arguments for logging
        command_args = _extract_command_args(func, args, kwargs)

        # Execute the command and track success/failure
        action_result = 'success'
        error_message = None
        metadata = {
            'is_owner': is_bot_owner(interaction.user.id),
            'is_admin': is_admin(interaction),
        }

        try:
            result = await func(self, interaction, *args, **kwargs)

            # Log successful execution
            await log_admin_action(
                executor_id=str(interaction.user.id),
                executor_username=interaction.user.name,
                command_name=interaction.command.name if interaction.command else 'unknown',
                server_id=str(interaction.guild.id) if interaction.guild else 'dm',
                action_result=action_result,
                command_args=command_args,
                metadata=metadata
            )

            return result

        except Exception as e:
            action_result = 'error'
            error_message = str(e)
            logger.error(
                f"Admin command error: user={interaction.user.id} "
                f"command={interaction.command.name if interaction.command else 'unknown'} "
                f"error={error_message}"
            )

            # Log error
            await log_admin_action(
                executor_id=str(interaction.user.id),
                executor_username=interaction.user.name,
                command_name=interaction.command.name if interaction.command else 'unknown',
                server_id=str(interaction.guild.id) if interaction.guild else 'dm',
                action_result=action_result,
                command_args=command_args,
                error_message=error_message,
                metadata=metadata
            )

            # Re-raise the exception
            raise

    return wrapper


def require_bot_owner(func):
    @wraps(func)
    async def wrapper(self, interaction: Interaction, *args, **kwargs):
        if not is_bot_owner(interaction.user.id):
            logger.warning(
                f"Bot owner command denied: user={interaction.user.id} "
                f"command={interaction.command.name if interaction.command else 'unknown'}"
            )

            # Log failed permission check
            await log_admin_action(
                executor_id=str(interaction.user.id),
                executor_username=interaction.user.name,
                command_name=interaction.command.name if interaction.command else 'unknown',
                server_id=str(interaction.guild.id) if interaction.guild else 'dm',
                action_result='failure',
                error_message="Permission denied: Bot owner only",
                metadata={
                    'is_owner': False,
                    'required_permission': 'bot_owner',
                }
            )

            embed = get_permission_embed(
                title="Bot Owner Only",
                description="This command can only be used by the bot owner.",
                required_permission="Bot Owner"
            )

            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return None

        logger.info(
            f"Bot owner command authorized: user={interaction.user.id} "
            f"command={interaction.command.name if interaction.command else 'unknown'}"
        )

        # Extract command arguments for logging
        command_args = _extract_command_args(func, args, kwargs)

        # Execute the command and track success/failure
        action_result = 'success'
        error_message = None
        metadata = {
            'is_owner': True,
            'required_permission': 'bot_owner',
        }

        try:
            result = await func(self, interaction, *args, **kwargs)

            # Log successful execution
            await log_admin_action(
                executor_id=str(interaction.user.id),
                executor_username=interaction.user.name,
                command_name=interaction.command.name if interaction.command else 'unknown',
                server_id=str(interaction.guild.id) if interaction.guild else 'dm',
                action_result=action_result,
                command_args=command_args,
                metadata=metadata
            )

            return result

        except Exception as e:
            action_result = 'error'
            error_message = str(e)
            logger.error(
                f"Bot owner command error: user={interaction.user.id} "
                f"command={interaction.command.name if interaction.command else 'unknown'} "
                f"error={error_message}"
            )

            # Log error
            await log_admin_action(
                executor_id=str(interaction.user.id),
                executor_username=interaction.user.name,
                command_name=interaction.command.name if interaction.command else 'unknown',
                server_id=str(interaction.guild.id) if interaction.guild else 'dm',
                action_result=action_result,
                command_args=command_args,
                error_message=error_message,
                metadata=metadata
            )

            # Re-raise the exception
            raise

    return wrapper


def check_permissions(interaction: Interaction) -> Tuple[bool, Optional[str]]:
    if is_bot_owner(interaction.user.id):
        return True, None

    if is_admin(interaction):
        return True, None

    return False, f"User {interaction.user.id} is neither bot owner nor server administrator"


def _extract_command_args(func, args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Extract command arguments from function call for logging."""
    try:
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        # Skip 'self' and 'interaction' parameters
        param_names = [p for p in param_names if p not in ['self', 'interaction']]

        # Build argument dictionary
        command_args = {}

        # Add positional arguments
        for i, value in enumerate(args):
            if i < len(param_names):
                # Convert to string for JSON serialization
                serializable_types = (str, int, float, bool, type(None))
                command_args[param_names[i]] = (
                    value if isinstance(value, serializable_types) else str(value)
                )

        # Add keyword arguments
        for key, value in kwargs.items():
            if key not in ['self', 'interaction']:
                # Convert to string for JSON serialization
                serializable_types = (str, int, float, bool, type(None))
                command_args[key] = (
                    value if isinstance(value, serializable_types) else str(value)
                )

        return command_args

    except Exception as e:
        logger.warning(f"Failed to extract command arguments: {e}")
        return {}
