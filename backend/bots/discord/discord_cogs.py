import discord
from discord.ext import commands, tasks
import logging
from app.core.orchestration.queue_manager import AsyncQueueManager, QueuePriority
from app.db.supabase.auth import login_with_github
from app.db.supabase.users_service import (
    get_or_create_user_by_discord,
    create_verification_session,
    cleanup_expired_tokens
)
from bots.discord.discord_bot import DiscordBot
from bots.discord.discord_views import OAuthView
from app.core.config import settings

logger = logging.getLogger(__name__)

class DevRelCommands(commands.Cog):
    def __init__(self, bot: DiscordBot, queue_manager: AsyncQueueManager):
        self.bot = bot
        self.queue = queue_manager
        self.cleanup_expired_tokens.start()

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.cleanup_expired_tokens.cancel()

    @tasks.loop(minutes=5)
    async def cleanup_expired_tokens(self):
        """Periodic cleanup of expired verification tokens"""
        try:
            await cleanup_expired_tokens()
        except Exception as e:
            logger.error(f"Error during token cleanup: {e}")

    @cleanup_expired_tokens.before_loop
    async def before_cleanup(self):
        """Wait until the bot is ready before starting cleanup"""
        await self.bot.wait_until_ready()

    @commands.command(name="reset")
    async def reset_thread(self, ctx: commands.Context):
        """Reset your DevRel thread and memory."""
        user_id = str(ctx.author.id)
        cleanup = {
            "type": "clear_thread_memory",
            "memory_thread_id": user_id,
            "user_id": user_id,
            "cleanup_reason": "manual_reset"
        }
        await self.queue.enqueue(cleanup, QueuePriority.HIGH)
        self.bot.active_threads.pop(user_id, None)
        await ctx.send("Your DevRel thread & memory have been reset! Send another message to start fresh.")

    @commands.command(name="help_devrel")
    async def help_devrel(self, ctx: commands.Context):
        """Show DevRel assistant help."""
        embed = discord.Embed(
            title="DevRel Assistant Help",
            description="I can help you with Devr.AI related questions!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands",
            value=(
                "• `!reset` – Reset your DevRel thread and memory\n"
                "• `!help_devrel` – Show this help message\n"
                "• `!verify_github` – Link your GitHub account\n"
                "• `!verification_status` – Check your verification status\n"
            ),
            inline=False
        )
        embed.add_field(
            name="Features",
            value=(
                "• Technical support and troubleshooting\n"
                "• Onboarding assistance\n"
                "• Web search capabilities\n"
                "• Community FAQ answers\n"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name="verification_status")
    async def verification_status(self, ctx: commands.Context):
        """Check your GitHub verification status."""
        try:
            user_profile = await get_or_create_user_by_discord(
                discord_id=str(ctx.author.id),
                display_name=ctx.author.display_name,
                discord_username=ctx.author.name,
                avatar_url=str(ctx.author.avatar.url) if ctx.author.avatar else None,
            )

            if user_profile.is_verified and user_profile.github_id:
                embed = discord.Embed(
                    title="✅ Verification Status",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="GitHub Account",
                    value=f"`{user_profile.github_username}`",
                    inline=True
                )
                embed.add_field(
                    name="Verified At",
                    value=f"<t:{int(user_profile.verified_at.timestamp())}:R>" if user_profile.verified_at else "Unknown",
                    inline=True
                )
                embed.add_field(
                    name="Status",
                    value="✅ Verified",
                    inline=True
                )
            else:
                embed = discord.Embed(
                    title="❌ Verification Status",
                    description="Your GitHub account is not linked.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Next Steps",
                    value="Use `!verify_github` to link your GitHub account.",
                    inline=False
                )

            await ctx.reply(embed=embed)

        except Exception as e:
            logger.error(f"Error checking verification status for user {ctx.author.id}: {e}")
            await ctx.reply("❌ Error checking verification status. Please try again.")

    @commands.command(name="verify_github")
    async def verify_github(self, ctx: commands.Context):
        """Initiates the GitHub account linking and verification process."""
        try:
            logger.info(f"User {ctx.author.name}({ctx.author.id}) has requested for GitHub verification")

            user_profile = await get_or_create_user_by_discord(
                discord_id=str(ctx.author.id),
                display_name=ctx.author.display_name,
                discord_username=ctx.author.name,
                avatar_url=str(ctx.author.avatar.url) if ctx.author.avatar else None,
            )

            if user_profile.is_verified and user_profile.github_id:
                embed = discord.Embed(
                    title="✅ Already Verified",
                    description=f"Your GitHub account `{user_profile.github_username}` is already linked!",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Verified At",
                    value=f"<t:{int(user_profile.verified_at.timestamp())}:R>" if user_profile.verified_at else "Unknown",
                    inline=True
                )
                await ctx.reply(embed=embed)
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
                await ctx.reply(embed=embed)
                return

            session_id = await create_verification_session(str(ctx.author.id))
            if not session_id:
                raise Exception("Failed to create verification session.")

            logger.info(f"Created verification session for user {ctx.author.id}: {session_id[:8]}...")

            if not settings.backend_url:
                raise Exception("Backend URL not configured. Please set BACKEND_URL environment variable.")

            callback_url = f"{settings.backend_url}/v1/auth/callback?session={session_id}"
            logger.info(f"Using callback URL: {callback_url}")

            auth_url_data = await login_with_github(redirect_to=callback_url)
            auth_url = auth_url_data.get("url")

            if not auth_url:
                raise Exception("Failed to generate OAuth URL.")

            logger.info(f"Generated OAuth URL for user {ctx.author.id}")

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

            try:
                await ctx.author.send(embed=embed, view=view)

                confirmation_embed = discord.Embed(
                    title="📨 Check Your DMs",
                    description="I've sent you a private message with the GitHub verification link.",
                    color=discord.Color.green()
                )
                confirmation_embed.add_field(
                    name="⏰ Time Limit",
                    value="Please complete the verification within 5 minutes.",
                    inline=False
                )
                await ctx.reply(embed=confirmation_embed)

            except discord.Forbidden:
                embed.add_field(
                    name="🔒 Privacy Notice",
                    value="**Please enable DMs for a more secure experience.**",
                    inline=False
                )
                await ctx.reply(embed=embed, view=view)

        except discord.Forbidden:
            error_embed = discord.Embed(
                title="❌ DM Error",
                description=(
                    "I couldn't send you a DM. Please:\n"
                    "1. Enable DMs from server members in your privacy settings\n"
                    "2. Try the command again"
                ),
                color=discord.Color.red()
            )
            await ctx.reply(embed=error_embed)

        except Exception as e:
            logger.error(f"Error in !verify_github for user {ctx.author.id}: {e}", exc_info=True)

            error_embed = discord.Embed(
                title="❌ Verification Error",
                description="An error occurred during verification setup. Please try again or contact support.",
                color=discord.Color.red()
            )
            if "Backend URL not configured" in str(e):
                error_embed.add_field(
                    name="Configuration Issue",
                    value="The bot is not properly configured. Please contact an administrator.",
                    inline=False
                )
            await ctx.reply(embed=error_embed)
