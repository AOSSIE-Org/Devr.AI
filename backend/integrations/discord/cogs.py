import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
from app.core.orchestration.queue_manager import AsyncQueueManager, QueuePriority
from app.services.auth.supabase import login_with_github
from app.services.auth.management import get_or_create_user_by_discord
from app.services.auth.verification import create_verification_session, cleanup_expired_tokens
from integrations.discord.bot import DiscordBot
from integrations.discord.views import OAuthView
from app.core.config import settings

# Try to import tasks, fallback if not available
try:
    from discord.ext import tasks
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False
    tasks = None

logger = logging.getLogger(__name__)

class DevRelCommands(commands.Cog):
    def __init__(self, bot: DiscordBot, queue_manager: AsyncQueueManager):
        self.bot = bot
        self.queue = queue_manager
        self._cleanup_task = None

    @commands.Cog.listener()
    async def on_ready(self):
        if TASKS_AVAILABLE and hasattr(self, 'cleanup_expired_tokens'):
            if not self.cleanup_expired_tokens.is_running():
                print("--> Starting the token cleanup task...")
                self.cleanup_expired_tokens.start()
        else:
            # Start manual cleanup task if tasks extension is not available
            if not self._cleanup_task:
                self._cleanup_task = asyncio.create_task(self._manual_cleanup_loop())
                print("--> Starting manual token cleanup task...")

    def cog_unload(self):
        if TASKS_AVAILABLE and hasattr(self, 'cleanup_expired_tokens'):
            self.cleanup_expired_tokens.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

    if TASKS_AVAILABLE:
        @tasks.loop(minutes=5)
        async def cleanup_expired_tokens(self):
            """Periodic cleanup of expired verification tokens"""
            try:
                print("--> Running token cleanup task...")
                await cleanup_expired_tokens()
                print("--> Token cleanup task finished.")
            except Exception as e:
                logger.error(f"Error during token cleanup: {e}")

        @cleanup_expired_tokens.before_loop
        async def before_cleanup(self):
            """Wait until the bot is ready before starting cleanup"""
            await self.bot.wait_until_ready()

    async def _manual_cleanup_loop(self):
        """Manual cleanup loop if tasks extension is not available"""
        await self.bot.wait_until_ready()
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                print("--> Running manual token cleanup task...")
                await cleanup_expired_tokens()
                print("--> Manual token cleanup task finished.")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error during manual token cleanup: {e}")

    @app_commands.command(name="reset", description="Reset your DevRel thread and memory.")
    async def reset_thread(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        cleanup = {
            "type": "clear_thread_memory",
            "memory_thread_id": user_id,
            "user_id": user_id,
            "cleanup_reason": "manual_reset"
        }
        await self.queue.enqueue(cleanup, QueuePriority.HIGH)
        self.bot.active_threads.pop(user_id, None)
        await interaction.response.send_message("Your DevRel thread & memory have been reset!", ephemeral=True)

    @app_commands.command(name="help", description="Show DevRel assistant help.")
    async def help_devrel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="DevRel Assistant Help",
            description="I can help you with Devr.AI related questions!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands",
            value=(
                "• `/reset` - Reset your DevRel thread and memory\n"
                "• `/help` - Show this help message\n"
                "• `/verify_github` - Link your GitHub account\n"
                "• `/verification_status` - Check your verification status\n"
            ),
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="verification_status",
                          description="Check your GitHub verification status.")
    async def verification_status(self, interaction: discord.Interaction):
        try:
            user_profile = await get_or_create_user_by_discord(
                discord_id=str(interaction.user.id),
                display_name=interaction.user.display_name,
                discord_username=interaction.user.name,
                avatar_url=str(interaction.user.avatar.url) if interaction.user.avatar else None,
            )
            if user_profile.is_verified and user_profile.github_id:
                embed = discord.Embed(title="✅ Verification Status",
                                      color=discord.Color.green())
                embed.add_field(name="GitHub Account", value=f"`{user_profile.github_username}`", inline=True)
                embed.add_field(name="Status", value="✅ Verified", inline=True)
            else:
                embed = discord.Embed(title="❌ Verification Status",
                                      description="Your GitHub account is not linked.",
                                      color=discord.Color.red())
                embed.add_field(name="Next Steps",
                                value="Use `/verify_github` to link your GitHub account.",
                                inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error checking verification status: {e}")
            await interaction.response.send_message("❌ Error checking verification status.", ephemeral=True)

    @app_commands.command(name="verify_github", description="Link your GitHub account.")
    async def verify_github(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            user_profile = await get_or_create_user_by_discord(
                discord_id=str(interaction.user.id),
                display_name=interaction.user.display_name,
                discord_username=interaction.user.name,
                avatar_url=str(interaction.user.avatar.url) if interaction.user.avatar else None,
            )
            if user_profile.is_verified and user_profile.github_id:
                embed = discord.Embed(
                    title="✅ Already Verified",
                    description=f"Your GitHub account `{user_profile.github_username}` is already linked!",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            if user_profile.verification_token:
                embed = discord.Embed(
                    title="⏳ Verification Pending",
                    description="You already have a verification in progress.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="What to do",
                    value="Please complete the existing verification or wait for it to expire (5 minutes).",
                    inline=False
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            session_id = await create_verification_session(str(interaction.user.id))
            if not session_id:
                raise Exception("Failed to create verification session.")

            callback_url = f"{settings.backend_url}/v1/auth/callback?session={session_id}"
            auth_url_data = await login_with_github(redirect_to=callback_url)
            auth_url = auth_url_data.get("url")
            if not auth_url:
                raise Exception("Failed to generate OAuth URL.")

            embed = discord.Embed(
                title="🔗 Link Your GitHub Account",
                description=(
                    "Click the button below to securely link your GitHub account.\n\n"
                    "**What happens next:**\n"
                    "1. You'll be redirected to GitHub\n"
                    "2. Authorize the Devr.AI application\n"
                    "3. You'll be redirected back with confirmation\n"
                    "4. Your accounts will be linked!"
                ),
                color=discord.Color.blue()
            )
            embed.add_field(
                name="⏰ Expiry Time",
                value="This verification link expires in **5 minutes** for security.",
                inline=False
            )
            embed.add_field(
                name="🔒 Security Notice",
                value="We only request access to your public GitHub profile. No private data is accessed.",
                inline=False
            )

            view = OAuthView(auth_url, "GitHub")
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in /verify_github: {e}")
            error_embed = discord.Embed(
                title="❌ Verification Error",
                description="An error occurred. Please contact an administrator.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """This function is called by the bot to load the cog."""
    await bot.add_cog(DevRelCommands(bot, bot.queue_manager))
