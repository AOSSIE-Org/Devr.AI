import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

from app.agents.devrel.onboarding.messages import (
    build_encourage_verification_message,
    build_new_user_welcome,
    build_verified_capabilities_intro,
    build_verified_welcome,
)
from app.core.config import settings
from app.core.orchestration.queue_manager import AsyncQueueManager, QueuePriority
from app.services.auth.management import get_or_create_user_by_discord
from app.services.auth.supabase import login_with_github
from app.services.auth.verification import create_verification_session, cleanup_expired_tokens
from integrations.discord.bot import DiscordBot
from integrations.discord.views import OAuthView, OnboardingView, build_final_handoff_embed

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

async def setup(bot: commands.Bot):
    """This function is called by the bot to load the cog."""
    await bot.add_cog(DevRelCommands(bot, bot.queue_manager))
    await bot.add_cog(OnboardingCog(bot))


class OnboardingCog(commands.Cog):
    """Handles onboarding flow: welcome DM, verification prompt, and skip option."""

    def __init__(self, bot: DiscordBot):
        self.bot = bot

    def _build_welcome_embed(self, member: discord.abc.User) -> discord.Embed:
        welcome_text = build_new_user_welcome()
        first_paragraph, _, remainder = welcome_text.partition("\n\n")
        if first_paragraph.startswith("👋 "):
            first_paragraph = first_paragraph[2:]

        description_blocks = [first_paragraph]
        if remainder:
            description_blocks.append(remainder.strip())

        embed = discord.Embed(
            title="Welcome to Devr.AI! 👋",
            description="\n\n".join(description_blocks).strip(),
            color=discord.Color.blue(),
        )
        embed.set_author(name=member.display_name if hasattr(member, "display_name") else str(member))
        embed.set_footer(text="Link expires after a short time for security.")
        return embed

    @app_commands.command(name="onboarding_test", description="DM the onboarding flow to yourself (dev only)")
    async def onboarding_test(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        status = await self._send_onboarding_flow(user)
        messages = {
            "verified": "Sent final hand-off DM (already verified).",
            "session_unavailable": "Sent fallback DMs (session unavailable).",
            "auth_unavailable": "Sent fallback DMs (no auth URL).",
            "onboarding_sent": "Sent onboarding DM to you.",
            "dm_forbidden": "I can’t DM you (DMs disabled).",
            "error": "Hit an error while sending onboarding DM.",
        }
        await interaction.followup.send(messages.get(status, "Completed."), ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # We don't need different behavior here; just run the shared flow
        await self._send_onboarding_flow(member)

    async def _send_onboarding_flow(self, user: discord.abc.User) -> str:
        """Shared onboarding flow used by both /onboarding_test and on_member_join.

        Returns a status string for telemetry/UX messages:
        - "verified": user already linked; final hand-off sent
        - "session_unavailable": could not create verification session; fallback DMs sent
        - "auth_unavailable": could not get OAuth URL; fallback DMs sent
        - "onboarding_sent": welcome DM with buttons sent
        - "dm_forbidden": cannot DM the user
        - "error": unexpected error (fallback attempted)
        """
        try:
            # Ensure DB record exists
            profile = await get_or_create_user_by_discord(
                discord_id=str(user.id),
                display_name=getattr(user, "display_name", str(user)),
                discord_username=getattr(user, "name", str(user)),
                avatar_url=str(user.avatar.url) if getattr(user, "avatar", None) else None,
            )

            # Already verified: send final hand-off and finish
            if getattr(profile, "is_verified", False) and getattr(profile, "github_id", None):
                try:
                    await user.send(build_verified_welcome(profile.github_username))
                    await user.send(build_verified_capabilities_intro(profile.github_username))
                    await user.send(embed=build_final_handoff_embed())
                except Exception:
                    pass
                return "verified"

            # Determine whether to show OAuth button
            show_oauth_button = getattr(settings, 'onboarding_show_oauth_button', True)
            auth_url = None

            if show_oauth_button:
                # Create verification session
                session_id = await create_verification_session(str(user.id))
                if not session_id:
                    try:
                        await user.send("I couldn't start verification right now. You can use /verify_github anytime.")
                        await user.send(build_encourage_verification_message(reminder_count=1))
                        await user.send(embed=build_final_handoff_embed())
                    except Exception:
                        pass
                    return "session_unavailable"

                # Generate GitHub OAuth URL via Supabase
                callback_url = f"{settings.backend_url}/v1/auth/callback?session={session_id}"
                auth = await login_with_github(redirect_to=callback_url)
                auth_url = auth.get("url")
                if not auth_url:
                    try:
                        await user.send("Couldn't generate a verification link. Please use /verify_github.")
                        await user.send(build_encourage_verification_message(reminder_count=1))
                        await user.send(embed=build_final_handoff_embed())
                    except Exception:
                        pass
                    return "auth_unavailable"

            # Send welcome DM with actions (auth_url may be None when button disabled)
            embed = self._build_welcome_embed(user)
            await user.send(embed=embed, view=OnboardingView(auth_url))
            return "onboarding_sent"
        except discord.Forbidden:
            return "dm_forbidden"
        except Exception as e:
            logger.error(f"onboarding flow error: {e}")
            try:
                await user.send("I hit an error. You can still run /verify_github and /help.")
                await user.send(build_encourage_verification_message(reminder_count=1))
            except Exception:
                pass
            return "error"
