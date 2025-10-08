import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import asyncio
from app.core.orchestration.queue_manager import AsyncQueueManager, QueuePriority
from app.services.auth.supabase import login_with_github
from app.services.auth.management import get_or_create_user_by_discord
from app.services.auth.verification import create_verification_session, cleanup_expired_tokens
from app.services.codegraph.repo_service import RepoService
from integrations.discord.bot import DiscordBot
from integrations.discord.views import OAuthView
from app.core.config import settings

logger = logging.getLogger(__name__)

class DevRelCommands(commands.Cog):
    def __init__(self, bot: DiscordBot, queue_manager: AsyncQueueManager):
        self.bot = bot
        self.queue = queue_manager

    def cog_load(self):
        """Called when the cog is loaded"""
        self.cleanup_expired_tokens.start()

    def cog_unload(self):
        self.cleanup_expired_tokens.cancel()

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

    @app_commands.command(name="index_repository", description="Index a GitHub repository")
    @app_commands.describe(repository="GitHub URL or owner/repo (e.g., AOSSIE-Org/Devr.AI)")
    async def index_repository(self, interaction: discord.Interaction, repository: str):
        """Index a GitHub repository into FalkorDB code graph"""
        await interaction.response.defer(thinking=True)

        try:
            service = RepoService()

            embed = discord.Embed(
                title="🔄 Indexing Repository",
                description=(
                    f"Indexing `{repository}`...\n\n"
                    "This typically takes 5-30 minutes depending on repository size."
                ),
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Current Status",
                value="⏳ Cloning and analyzing repository...",
                inline=False
            )
            embed.set_footer(text="You'll be notified when complete")
            # Sends progress message and keeps a handle to edit later
            progress_msg = await interaction.followup.send(embed=embed)

            logger.info(f"Indexing request from {interaction.user.id}: {repository}")

            async def _run_index_and_update():
                try:
                    result = await service.index_repo(repository, str(interaction.user.id))
                    if result.get("status") == "success":
                        success_embed = discord.Embed(
                            title="✅ Repository Indexed",
                            description=f"Successfully indexed `{result['repo']}`",
                            color=discord.Color.green()
                        )
                        success_embed.add_field(
                            name="Graph Name",
                            value=f"`{result['graph_name']}`",
                            inline=True
                        )
                        success_embed.add_field(
                            name="📊 Statistics",
                            value=(
                                f"**Nodes:** {result.get('nodes', 0):,}\n"
                                f"**Edges:** {result.get('edges', 0):,}"
                            ),
                            inline=True
                        )
                        success_embed.add_field(
                            name="💡 How to Query",
                            value=(
                                f"Ask questions like:\n"
                                f"• *Where is authentication in {result['repo']}?*\n"
                                f"• *How is {result['repo']} organized?*\n"
                                f"• *List all classes in {result['repo']}*"
                            ),
                            inline=False
                        )
                        success_embed.set_footer(text="Ready to answer your questions!")
                        await progress_msg.edit(embed=success_embed)
                    else:
                        error_msg = result.get("message", "Unknown error")
                        error_embed = discord.Embed(
                            title="❌ Indexing Failed",
                            description=f"Could not index `{repository}`",
                            color=discord.Color.red()
                        )
                        error_embed.add_field(
                            name="Error",
                            value=f"```{error_msg[:500]}```",
                            inline=False
                        )

                        tip = None
                        if "already indexed" in error_msg.lower():
                            tip = "This repository is already indexed! You can query it directly."
                        elif "pending" in error_msg.lower():
                            tip = "Indexing is in progress. Check status with `/list_indexed_repos`"

                        if tip:
                            error_embed.add_field(
                                name="💡 Tip",
                                value=tip,
                                inline=False
                            )
                        else:
                            error_embed.add_field(
                                name="💡 Troubleshooting",
                                value=(
                                    "• Verify the repository URL is correct\n"
                                    "• Ensure the repository is public\n"
                                    "• Check if you've reached indexing limits"
                                ),
                                inline=False
                            )

                        await progress_msg.edit(embed=error_embed)
                except Exception:
                    logger.exception("Indexing task failed")
                    await progress_msg.edit(
                        embed=discord.Embed(
                            title="❌ Indexing Error",
                            description="An unexpected error occurred. Please try again later.",
                            color=discord.Color.red()
                        )
                    )

            asyncio.create_task(_run_index_and_update())

        except Exception as e:
            logger.error(f"Index command error: {e}", exc_info=True)

            error_embed = discord.Embed(
                title="❌ Command Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="Details",
                value=f"```{str(e)[:500]}```",
                inline=False
            )
            error_embed.set_footer(text="Please try again or contact support")
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(name="delete_index", description="Delete indexed repository")
    @app_commands.describe(repository="Repository name (owner/repo)")
    async def delete_index(self, interaction: discord.Interaction, repository: str):
        """Delete a repository index"""
        await interaction.response.defer(thinking=True)

        try:
            service = RepoService()
            logger.info(f"Delete request from {interaction.user.id}: {repository}")

            result = await service.delete_repo(repository, str(interaction.user.id))

            if result["status"] == "success":
                embed = discord.Embed(
                    title="🗑️ Index Deleted",
                    description=f"Successfully deleted index for `{result['repo']}`",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Graph Name",
                    value=f"`{result['graph_name']}`",
                    inline=False
                )
                embed.set_footer(text="You can re-index anytime with /index_repository")
                await interaction.followup.send(embed=embed)
            else:
                error_embed = discord.Embed(
                    title="❌ Deletion Failed",
                    description=f"Could not delete `{repository}`",
                    color=discord.Color.red()
                )
                error_embed.add_field(
                    name="Error",
                    value=result.get('message', 'Unknown error')[:500],
                    inline=False
                )
                await interaction.followup.send(embed=error_embed)

        except Exception as e:
            logger.error(f"Delete command error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @app_commands.command(name="list_indexed_repos", description="List your indexed repositories")
    async def list_indexed_repos(self, interaction: discord.Interaction):
        """List user's indexed repositories"""
        await interaction.response.defer()

        try:
            service = RepoService()
            repos = await service.list_repos(str(interaction.user.id))

            if not repos:
                await interaction.followup.send("You haven't indexed any repositories yet.")
                return

            embed = discord.Embed(
                title="Your Indexed Repositories",
                description=f"{len(repos)} indexed repositories",
                color=discord.Color.blue()
            )

            for repo in repos[:10]:
                status_emoji = {"pending": "⏳", "completed": "✅", "failed": "❌"}
                emoji = status_emoji.get(repo["indexing_status"], "❓")

                embed.add_field(
                    name=repo["repository_full_name"],
                    value=f"{emoji} {repo['indexing_status']} | Nodes: {repo['node_count']}",
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"List command error: {e}")
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot: commands.Bot):
    """This function is called by the bot to load the cog."""
    await bot.add_cog(DevRelCommands(bot, bot.queue_manager))
