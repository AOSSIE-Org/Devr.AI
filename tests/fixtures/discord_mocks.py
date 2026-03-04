# tests/fixtures/discord_mocks.py
"""
Mock Discord objects for testing.

Provides mock Discord.py objects for unit testing without needing
a real Discord bot or connection.

Includes:
- Mock channels, messages, embeds
- Mock bot and client
- Mock Discord API responses
- Utility functions for creating test data
"""

from unittest.mock import AsyncMock, MagicMock, Mock
from typing import Optional, List, Dict, Any
import discord
from discord import TextChannel, Message, Embed, Guild, Member, User


# ============================================================================
# BASIC MOCK OBJECTS
# ============================================================================

def create_mock_user(
    user_id: int = 123456789,
    username: str = "TestUser",
    discriminator: str = "0001"
) -> User:
    """
    Create a mock Discord user.
    
    Args:
        user_id: User ID (unique identifier)
        username: Username display name
        discriminator: User discriminator (deprecated in new Discord)
        
    Returns:
        Mock User object
    """
    user = MagicMock(spec=User)
    user.id = user_id
    user.name = username
    user.username = username
    user.discriminator = discriminator
    user.mention = f"<@{user_id}>"
    user.bot = False
    user.system = False
    
    return user


def create_mock_member(
    user_id: int = 123456789,
    username: str = "TestMember",
    guild_id: int = 987654321,
    roles: Optional[List] = None,
    nick: Optional[str] = None
) -> Member:
    """
    Create a mock Discord guild member.
    
    Args:
        user_id: User ID
        username: Username
        guild_id: Guild ID member belongs to
        roles: List of role objects
        nick: Nickname in guild (optional)
        
    Returns:
        Mock Member object
    """
    member = MagicMock(spec=Member)
    member.id = user_id
    member.name = username
    member.username = username
    member.mention = f"<@{user_id}>"
    member.nick = nick
    member.display_name = nick or username
    member.guild = MagicMock(id=guild_id)
    member.roles = roles or []
    member.bot = False
    
    return member


def create_mock_guild(
    guild_id: int = 987654321,
    name: str = "TestGuild",
    member_count: int = 100
) -> Guild:
    """
    Create a mock Discord guild (server).
    
    Args:
        guild_id: Guild ID
        name: Guild name
        member_count: Number of members
        
    Returns:
        Mock Guild object
    """
    guild = MagicMock(spec=Guild)
    guild.id = guild_id
    guild.name = name
    guild.member_count = member_count
    guild.owner = create_mock_user(user_id=1, username="GuildOwner")
    guild.roles = []
    guild.channels = []
    
    return guild


def create_mock_channel(
    channel_id: int = 111222333,
    name: str = "test-channel",
    guild_id: int = 987654321,
    topic: Optional[str] = None,
    is_nsfw: bool = False
) -> TextChannel:
    """
    Create a mock Discord text channel.
    
    Args:
        channel_id: Channel ID
        name: Channel name
        guild_id: Guild ID channel belongs to
        topic: Channel topic/description
        is_nsfw: Whether channel is NSFW
        
    Returns:
        Mock TextChannel object with async send/edit methods
    """
    channel = MagicMock(spec=TextChannel)
    channel.id = channel_id
    channel.name = name
    channel.guild = MagicMock(id=guild_id)
    channel.topic = topic
    channel.nsfw = is_nsfw
    channel.mention = f"<#{channel_id}>"
    
    # Make send/edit async
    channel.send = AsyncMock(return_value=create_mock_message(channel_id=channel_id))
    channel.edit = AsyncMock()
    channel.delete = AsyncMock()
    channel.purge = AsyncMock()
    
    return channel


def create_mock_message(
    message_id: int = 555666777,
    content: str = "Test message",
    channel_id: int = 111222333,
    author_id: int = 123456789,
    author_name: str = "TestUser",
    embeds: Optional[List[Embed]] = None,
    attachments: Optional[List] = None
) -> Message:
    """
    Create a mock Discord message.
    
    Args:
        message_id: Message ID
        content: Message content/text
        channel_id: Channel ID message is in
        author_id: Author user ID
        author_name: Author username
        embeds: List of embeds in message
        attachments: List of attachments
        
    Returns:
        Mock Message object with async edit/delete methods
    """
    message = MagicMock(spec=Message)
    message.id = message_id
    message.content = content
    message.channel = create_mock_channel(channel_id=channel_id)
    message.author = create_mock_user(user_id=author_id, username=author_name)
    message.embeds = embeds or []
    message.attachments = attachments or []
    message.mention_everyone = False
    message.mentions = []
    message.reactions = []
    
    # Make async methods
    message.edit = AsyncMock(return_value=message)
    message.delete = AsyncMock()
    message.add_reaction = AsyncMock()
    message.remove_reaction = AsyncMock()
    message.clear_reactions = AsyncMock()
    
    return message


def create_mock_embed(
    title: str = "Test Embed",
    description: str = "This is a test embed",
    color: int = 0x00FF00
) -> Embed:
    """
    Create a mock Discord embed.
    
    Args:
        title: Embed title
        description: Embed description
        color: Embed color (RGB int)
        
    Returns:
        Mock Embed object
    """
    embed = MagicMock(spec=Embed)
    embed.title = title
    embed.description = description
    embed.color = color
    embed.fields = []
    embed.footer = None
    embed.author = None
    embed.image = None
    embed.thumbnail = None
    
    # Add field method
    embed.add_field = MagicMock(return_value=embed)
    embed.set_footer = MagicMock(return_value=embed)
    embed.set_author = MagicMock(return_value=embed)
    embed.set_image = MagicMock(return_value=embed)
    
    return embed


# ============================================================================
# BOT AND CLIENT MOCKS
# ============================================================================

def create_mock_bot(
    bot_id: int = 999888777,
    bot_name: str = "TestBot",
    command_prefix: str = "!"
) -> discord.ext.commands.Bot:
    """
    Create a mock Discord bot.
    
    Args:
        bot_id: Bot user ID
        bot_name: Bot username
        command_prefix: Command prefix
        
    Returns:
        Mock Bot object
    """
    bot = MagicMock(spec=discord.ext.commands.Bot)
    bot.user = create_mock_user(user_id=bot_id, username=bot_name)
    bot.command_prefix = command_prefix
    bot.guilds = []
    bot.cogs = {}
    bot.latency = 0.05
    
    # Async methods
    bot.load_cog = AsyncMock()
    bot.unload_cog = AsyncMock()
    bot.add_cog = AsyncMock()
    bot.remove_cog = AsyncMock()
    bot.wait_until_ready = AsyncMock()
    
    return bot


def create_mock_interaction(
    interaction_id: int = 444555666,
    user_id: int = 123456789,
    user_name: str = "TestUser",
    channel_id: int = 111222333,
    guild_id: int = 987654321,
    command_name: str = "test_command"
) -> discord.Interaction:
    """
    Create a mock Discord interaction (slash command).
    
    Args:
        interaction_id: Interaction ID
        user_id: User ID who triggered interaction
        user_name: Username
        channel_id: Channel ID interaction was in
        guild_id: Guild ID
        command_name: Name of command triggered
        
    Returns:
        Mock Interaction object
    """
    interaction = MagicMock(spec=discord.Interaction)
    interaction.id = interaction_id
    interaction.user = create_mock_user(user_id=user_id, username=user_name)
    interaction.channel = create_mock_channel(channel_id=channel_id)
    interaction.guild = MagicMock(id=guild_id)
    interaction.command_name = command_name
    
    # Response object
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.response.is_done = MagicMock(return_value=False)
    
    # Followup messages
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    
    return interaction


# ============================================================================
# DISCORD API ERROR MOCKS
# ============================================================================

class MockDiscordError(Exception):
    """Base mock Discord error."""
    pass


class MockNotFound(MockDiscordError):
    """Mock 404 Not Found error."""
    def __init__(self, message: str = "Resource not found"):
        self.status = 404
        super().__init__(message)


class MockForbidden(MockDiscordError):
    """Mock 403 Forbidden error."""
    def __init__(self, message: str = "Forbidden"):
        self.status = 403
        super().__init__(message)


class MockRateLimitError(MockDiscordError):
    """Mock 429 Too Many Requests error (rate limit)."""
    def __init__(self, retry_after: float = 1.0):
        self.status = 429
        self.retry_after = retry_after
        super().__init__(f"429 Too Many Requests - Retry after {retry_after}s")


class MockServerError(MockDiscordError):
    """Mock 5xx Server error."""
    def __init__(self, message: str = "Server error"):
        self.status = 500
        super().__init__(message)


# ============================================================================
# FIXTURE FACTORIES
# ============================================================================

class DiscordMockFactory:
    """Factory for creating Discord test fixtures."""
    
    @staticmethod
    def create_test_scenario(
        num_users: int = 3,
        num_channels: int = 2,
        num_messages: int = 5
    ) -> Dict[str, Any]:
        """
        Create a complete test scenario with users, channels, and messages.
        
        Args:
            num_users: Number of users to create
            num_channels: Number of channels to create
            num_messages: Number of messages per channel
            
        Returns:
            Dictionary with:
            - 'bot': Mock bot
            - 'guild': Mock guild
            - 'users': List of mock users
            - 'channels': List of mock channels
            - 'messages': Dict of channel_id -> List[messages]
        """
        # Create bot and guild
        bot = create_mock_bot()
        guild = create_mock_guild()
        
        # Create users
        users = [
            create_mock_user(
                user_id=100 + i,
                username=f"TestUser{i}"
            )
            for i in range(num_users)
        ]
        
        # Create channels and messages
        channels = []
        messages = {}
        
        for ch in range(num_channels):
            channel = create_mock_channel(
                channel_id=1000 + ch,
                name=f"test-channel-{ch}"
            )
            channels.append(channel)
            
            # Create messages in channel
            channel_messages = []
            for msg in range(num_messages):
                message = create_mock_message(
                    message_id=10000 + ch * 100 + msg,
                    content=f"Test message {msg}",
                    channel_id=channel.id,
                    author_id=users[msg % len(users)].id,
                    author_name=users[msg % len(users)].name
                )
                channel_messages.append(message)
            
            messages[channel.id] = channel_messages
        
        return {
            'bot': bot,
            'guild': guild,
            'users': users,
            'channels': channels,
            'messages': messages
        }
    
    @staticmethod
    def create_rate_limit_response(retry_after: float = 1.0) -> Exception:
        """
        Create a mock rate limit error response.
        
        Args:
            retry_after: Seconds to wait before retry
            
        Returns:
            Mock rate limit error
        """
        return MockRateLimitError(retry_after=retry_after)
    
    @staticmethod
    def create_error_response(error_type: str = "not_found") -> Exception:
        """
        Create a mock error response.
        
        Args:
            error_type: Type of error ('not_found', 'forbidden', 'server', etc.)
            
        Returns:
            Mock error object
        """
        error_map = {
            'not_found': MockNotFound(),
            'forbidden': MockForbidden(),
            'rate_limit': MockRateLimitError(),
            'server': MockServerError(),
        }
        
        return error_map.get(error_type, MockDiscordError("Unknown error"))


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

import pytest


@pytest.fixture
def mock_user():
    """Fixture: Create a mock Discord user."""
    return create_mock_user()


@pytest.fixture
def mock_channel():
    """Fixture: Create a mock Discord channel."""
    return create_mock_channel()


@pytest.fixture
def mock_message(mock_channel):
    """Fixture: Create a mock Discord message."""
    return create_mock_message(channel_id=mock_channel.id)


@pytest.fixture
def mock_embed():
    """Fixture: Create a mock Discord embed."""
    return create_mock_embed()


@pytest.fixture
def mock_bot():
    """Fixture: Create a mock Discord bot."""
    return create_mock_bot()


@pytest.fixture
def mock_guild():
    """Fixture: Create a mock Discord guild."""
    return create_mock_guild()


@pytest.fixture
def mock_interaction():
    """Fixture: Create a mock Discord interaction."""
    return create_mock_interaction()


@pytest.fixture
def discord_scenario():
    """Fixture: Create a complete Discord test scenario."""
    factory = DiscordMockFactory()
    return factory.create_test_scenario()


@pytest.fixture
def rate_limit_error():
    """Fixture: Create a mock rate limit error."""
    factory = DiscordMockFactory()
    return factory.create_rate_limit_response(retry_after=0.5)


# ============================================================================
# HELPER FUNCTIONS FOR TESTS
# ============================================================================

def assert_channel_mentioned(message: Message, channel: TextChannel) -> None:
    """
    Assert that a message mentions a channel.
    
    Args:
        message: Mock message to check
        channel: Mock channel that should be mentioned
    """
    assert f"<#{channel.id}>" in (message.content or "")


def assert_user_mentioned(message: Message, user: User) -> None:
    """
    Assert that a message mentions a user.
    
    Args:
        message: Mock message to check
        user: Mock user that should be mentioned
    """
    assert f"<@{user.id}>" in (message.content or "")


def assert_message_has_embed(message: Message, title: str = None) -> None:
    """
    Assert that a message has an embed.
    
    Args:
        message: Mock message to check
        title: Expected embed title (optional)
    """
    assert len(message.embeds) > 0
    if title:
        assert message.embeds[0].title == title


def create_message_with_reactions(
    message_id: int = 555666777,
    reactions: Optional[List[str]] = None
) -> Message:
    """
    Create a mock message with reactions.
    
    Args:
        message_id: Message ID
        reactions: List of emoji reactions (e.g., ["👍", "❌"])
        
    Returns:
        Mock message with reactions
    """
    message = create_mock_message(message_id=message_id)
    
    if reactions:
        # Create mock reaction objects
        message.reactions = [
            MagicMock(emoji=emoji, count=1)
            for emoji in reactions
        ]
    
    return message


def create_message_with_mentions(
    content: str = "Hello @user1 and <#channel>",
    mentioned_users: Optional[List[User]] = None,
    mentioned_channels: Optional[List[TextChannel]] = None
) -> Message:
    """
    Create a mock message with mentions.
    
    Args:
        content: Message content
        mentioned_users: List of mentioned users
        mentioned_channels: List of mentioned channels
        
    Returns:
        Mock message with mentions
    """
    message = create_mock_message(content=content)
    message.mentions = mentioned_users or []
    message.channel_mentions = mentioned_channels or []
    
    return message


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """Example of how to use the mock factory in tests."""
    
    # Create individual mocks
    user = create_mock_user(username="Alice")
    channel = create_mock_channel(name="general")
    message = create_mock_message(content="Hello!", channel_id=channel.id)
    
    # Create complete scenario
    factory = DiscordMockFactory()
    scenario = factory.create_test_scenario(num_users=5, num_channels=3)
    
    # Access scenario data
    bot = scenario['bot']
    guild = scenario['guild']
    users = scenario['users']
    channels = scenario['channels']
    messages = scenario['messages']
    
    # Create error responses
    rate_limit_error = factory.create_rate_limit_response(retry_after=0.5)
    not_found_error = factory.create_error_response('not_found')


if __name__ == "__main__":
    example_usage()
    print("✅ Discord mocks loaded successfully")
