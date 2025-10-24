import discord

from app.agents.devrel.onboarding.messages import (
    CAPABILITIES_INTRO_TEXT,
    CAPABILITIES_OUTRO_TEXT,
    CAPABILITY_SECTIONS,
)
from app.services.auth.management import get_or_create_user_by_discord


def build_final_handoff_embed() -> discord.Embed:
    """Create the final hand-off embed describing capabilities."""
    embed = discord.Embed(
        title="You're all set!",
        description=CAPABILITIES_INTRO_TEXT,
        color=discord.Color.green(),
    )
    for section in CAPABILITY_SECTIONS:
        examples = "\n".join(f"• {example}" for example in section["examples"])
        embed.add_field(name=section["title"], value=examples, inline=False)

    embed.add_field(name="Ready when you are", value=CAPABILITIES_OUTRO_TEXT, inline=False)
    embed.set_footer(text="Use /help anytime to see commands.")
    return embed


async def send_final_handoff_dm(user: discord.abc.User):
    """Send the final hand-off message to a user via DM."""
    try:
        embed = build_final_handoff_embed()
        await user.send(embed=embed)
    except Exception:
        # Fail silently to avoid crashing flows if DMs are closed or similar
        pass

class OAuthView(discord.ui.View):
    """View with OAuth button."""

    def __init__(self, oauth_url: str, provider_name: str):
        super().__init__(timeout=300)
        self.oauth_url = oauth_url
        self.provider_name = provider_name

        button = discord.ui.Button(
            label=f"Connect {provider_name}",
            style=discord.ButtonStyle.link,
            url=oauth_url
        )
        self.add_item(button)


class OnboardingView(discord.ui.View):
    """View shown in onboarding DM with optional GitHub connect link and Skip button."""

    def __init__(self, oauth_url: str | None):
        super().__init__(timeout=300)
        # Link button to start GitHub OAuth (optional)
        if oauth_url:
            self.add_item(
                discord.ui.Button(
                    label="Connect GitHub",
                    style=discord.ButtonStyle.link,
                    url=oauth_url,
                )
            )

    @discord.ui.button(
        label="I've verified",
        style=discord.ButtonStyle.primary,
        custom_id="onboarding_check_verified",
    )
    async def check_verified(  # type: ignore[override]
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True, thinking=False)

        try:
            profile = await get_or_create_user_by_discord(
                discord_id=str(interaction.user.id),
                display_name=getattr(interaction.user, "display_name", str(interaction.user)),
                discord_username=getattr(interaction.user, "name", str(interaction.user)),
                avatar_url=str(interaction.user.avatar.url) if getattr(interaction.user, "avatar", None) else None,
            )
        except Exception:
            await interaction.followup.send(
                "❌ I couldn't confirm right now. Please use `/verification_status` to check manually.",
                ephemeral=True,
            )
            return

        if getattr(profile, "is_verified", False) and getattr(profile, "github_id", None):
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.style != discord.ButtonStyle.link:
                    item.disabled = True
            await interaction.followup.send(
                "✅ Your GitHub connection is confirmed! I've sent over the capability menu.",
                ephemeral=True,
            )
            await send_final_handoff_dm(interaction.user)
            try:
                await interaction.message.edit(view=self)
            except Exception:
                pass
        else:
            await interaction.followup.send(
                "I still don't see a linked GitHub account. Run `/verify_github` and try again in a moment.",
                ephemeral=True,
            )

    @discord.ui.button(label="Skip for now", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):  # type: ignore[override]
        # Send the final hand-off DM and disable the view buttons
        await send_final_handoff_dm(interaction.user)
        for item in self.children:
            item.disabled = True
        try:
            await interaction.response.edit_message(view=self)
        except Exception:
            # If edit fails (e.g., message deleted), ignore
            pass
