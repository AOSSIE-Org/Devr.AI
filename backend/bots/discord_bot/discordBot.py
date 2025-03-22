import discord
from discord.ext import commands
import dotenv
import os
import logging
import asyncio

from app.core.handler.pr_handler import PRHandler
from app.core.handler.issue_handler import IssueHandler
from app.core.handler.onboarding_handler import OnboardingHandler
from app.core.handler.message_handler import MessageHandler
from app.core.handler.faq_handler import FAQHandler
from app.core.events.discord_event import DiscordEvent
from app.core.events.enums import EventType, PlatformType
from app.core.events.event_bus import EventBus
from app.core.handler.handler_registry import HandlerRegistry
from app.core.handler.base import BaseHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.reactions = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

handler_registry = HandlerRegistry()
event_bus = EventBus(handler_registry)

faq_handler = FAQHandler(bot)
# Register event handlers
event_bus.register_handler(EventType.USER_JOINED, OnboardingHandler().handle, platform=PlatformType.DISCORD)
event_bus.register_handler(EventType.MESSAGE_CREATED, MessageHandler().handle, platform=PlatformType.DISCORD)
event_bus.register_handler(EventType.MESSAGE_UPDATED, MessageHandler().handle, platform=PlatformType.DISCORD)
event_bus.register_handler(EventType.MESSAGE_DELETED, MessageHandler().handle, platform=PlatformType.DISCORD)
event_bus.register_handler(EventType.FAQ_REQUESTED, faq_handler.handle, platform=PlatformType.DISCORD)

# Track dispatched event IDs to avoid duplicate dispatching
processed_events = set()

async def dispatch_event(event: DiscordEvent):
    event_key = (event.id, event.event_type)

    """Dispatches an event only if it hasn't been processed before with the same event type."""
    if event_key in processed_events:
        logger.info(f"Skipping duplicate event: {event.event_type} (ID: {event.id})")
        return

    processed_events.add(event_key)
    await event_bus.dispatch(event)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    """Handles user joining"""
    logger.info(f"New member joined: {member.name}")

    event = DiscordEvent(
        id=str(member.id),
        event_type=EventType.USER_JOINED,
        platform=PlatformType.DISCORD,
        actor_id=str(member.id),
        guild_id=str(member.guild.id),
        channel_id=None,
        data={"username": member.name}
    )
    await dispatch_event(event)

@bot.event
async def on_message(message):
    """Handles new messages"""
    if message.author == bot.user:
        return

    logger.info(f"Message received: {message.content} from {message.author.name}")
    logger.info(f"Dispatching event with channel_id: {str(message.channel.id)}")
    channel_id = str(message.channel.id)

    is_faq, faq_response = await faq_handler.is_faq(message.content)
    event_type = EventType.FAQ_REQUESTED if is_faq else EventType.MESSAGE_CREATED

    event = DiscordEvent(
        id=str(message.id),
        event_type=event_type,
        platform=PlatformType.DISCORD,
        actor_id=str(message.author.id),
        actor_name=message.author.name,
        guild_id=str(message.guild.id) if message.guild else None,
        channel_id=(channel_id),
        message_id=str(message.id),
        raw_data={
            "id": str(message.id),
            "content": message.content,
            "actor_id": str(message.author.id),
            "attachments": [attachment.url for attachment in message.attachments],
            "mentions": [user.id for user in message.mentions],
        },
    )

    await dispatch_event(event)
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    """Handles edited messages"""
    if before.author == bot.user:
        return

    logger.info(f"Message edited by {before.author.name}: {before.content} → {after.content}")

    event = DiscordEvent(
        id=str(after.id),
        event_type=EventType.MESSAGE_UPDATED,
        platform=PlatformType.DISCORD,
        actor_id=str(after.author.id),
        guild_id=str(after.guild.id) if after.guild else None,
        channel_id=str(after.channel.id),
        data={"before": before.content, "after": after.content, "author": after.author.name}
    )

    await dispatch_event(event)

@bot.event
async def on_message_delete(message):
    """Handles deleted messages"""
    if message.author == bot.user:
        return

    logger.info(f" Message deleted by {message.author.name}: {message.content}")

    event = DiscordEvent(
        id=str(message.id),
        event_type=EventType.MESSAGE_DELETED,
        platform=PlatformType.DISCORD,
        actor_id=str(message.author.id),
        guild_id=str(message.guild.id) if message.guild else None,
        channel_id=str(message.channel.id),
        data={"content": message.content, "author": message.author.name}
    )

    await dispatch_event(event)

@bot.event
async def on_raw_reaction_add(payload):
    """Handles reactions even for uncached messages"""
    logger.info(f" Reaction detected: {payload.emoji.name} by user ID {payload.user_id}")

    if payload.user_id == bot.user.id:
        logger.info("Bot reacted, ignoring...")
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        logger.error(f"Guild {payload.guild_id} not found.")
        return

    channel = guild.get_channel(payload.channel_id)
    if not channel:
        logger.error(f"Channel {payload.channel_id} not found.")
        return

    user = await bot.fetch_user(payload.user_id)
    emoji = payload.emoji.name

    if not channel:
        logger.error(" Channel not found!")
        return

    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        logger.error(" Message not found!")
        return

    actor_id = user.id if user else None

    event = DiscordEvent(
        id=str(message.id),
        event_type=EventType.REACTION_ADDED,
        platform=PlatformType.DISCORD,
        actor_id=str(actor_id),
        guild_id=str(payload.guild_id),
        channel_id=str(payload.channel_id),
        data={"emoji": str(emoji), "message_id": str(message.id), "user_id": str(user.id)}
    )

    await dispatch_event(event)

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
