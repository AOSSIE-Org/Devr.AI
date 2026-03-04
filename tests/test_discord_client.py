"""
Tests for EnhancedDiscordClient.
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
import discord
from discord.ext import commands

from discord_client import EnhancedDiscordClient, create_enhanced_client
from rate_limiter import DiscordRateLimiter


class TestEnhancedDiscordClient:
    """Test EnhancedDiscordClient functionality."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock Discord bot."""
        bot = AsyncMock(spec=commands.Bot)
        bot.get_channel = Mock(return_value=None)
        bot.fetch_channel = AsyncMock()
        return bot

    @pytest.fixture
    def rate_limiter(self):
        """Create a rate limiter instance."""
        return DiscordRateLimiter(max_retries=2, base_delay=0.01)

    @pytest.fixture
    def client(self, mock_bot, rate_limiter):
        """Create an enhanced Discord client."""
        return EnhancedDiscordClient(mock_bot, rate_limiter)

    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_bot, rate_limiter):
        """Test client initializes correctly."""
        client = EnhancedDiscordClient(mock_bot, rate_limiter)

        assert client.bot is mock_bot
        assert client.rate_limiter is rate_limiter

    @pytest.mark.asyncio
    async def test_send_message_with_retry_success(self, client):
        """Test successful message sending."""
        mock_channel = AsyncMock(spec=discord.TextChannel)
        mock_message = Mock(spec=discord.Message)
        mock_channel.send = AsyncMock(return_value=mock_message)

        result = await client.send_message_with_retry(
            mock_channel,
            content="Hello!",
        )

        assert result is mock_message
        mock_channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_with_retry_channel_id(self, client, mock_bot):
        """Test message sending with channel ID."""
        mock_channel = AsyncMock(spec=discord.TextChannel)
        mock_message = Mock(spec=discord.Message)
        mock_channel.send = AsyncMock(return_value=mock_message)

        mock_bot.get_channel = Mock(return_value=mock_channel)

        result = await client.send_message_with_retry(
            12345,  # Channel ID
            content="Hello!",
        )

        assert result is mock_message
        mock_bot.get_channel.assert_called_with(12345)

    @pytest.mark.asyncio
    async def test_send_message_with_embed(self, client):
        """Test message sending with embed."""
        mock_channel = AsyncMock(spec=discord.TextChannel)
        mock_message = Mock(spec=discord.Message)
        mock_channel.send = AsyncMock(return_value=mock_message)

        embed = discord.Embed(title="Test")

        result = await client.send_message_with_retry(
            mock_channel,
            embed=embed,
        )

        assert result is mock_message
        call_args = mock_channel.send.call_args
        assert call_args[1]["embed"] is embed

    @pytest.mark.asyncio
    async def test_edit_message_with_retry_success(self, client):
        """Test successful message editing."""
        mock_message = AsyncMock(spec=discord.Message)
        mock_edited = Mock(spec=discord.Message)
        mock_message.edit = AsyncMock(return_value=mock_edited)

        result = await client.edit_message_with_retry(
            mock_message,
            content="Edited!",
        )

        assert result is mock_edited
        mock_message.edit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_message_with_retry(self, client):
        """Test message deletion."""
        mock_message = AsyncMock(spec=discord.Message)
        mock_message.delete = AsyncMock()

        await client.delete_message_with_retry(mock_message)

        mock_message.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_reaction_with_retry(self, client):
        """Test adding reaction to message."""
        mock_message = AsyncMock(spec=discord.Message)
        mock_message.add_reaction = AsyncMock()

        await client.add_reaction_with_retry(mock_message, "👍")

        mock_message.add_reaction.assert_called_once_with("👍")

    @pytest.mark.asyncio
    async def test_create_thread_with_retry_from_message(self, client):
        """Test creating thread from message."""
        mock_message = AsyncMock(spec=discord.Message)
        mock_thread = Mock(spec=discord.Thread)
        mock_message.create_thread = AsyncMock(return_value=mock_thread)

        result = await client.create_thread_with_retry(
            AsyncMock(spec=discord.TextChannel),
            name="Test Thread",
            message=mock_message,
        )

        assert result is mock_thread
        mock_message.create_thread.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_thread_with_retry_from_channel(self, client):
        """Test creating thread from channel."""
        mock_channel = AsyncMock(spec=discord.TextChannel)
        mock_thread = Mock(spec=discord.Thread)
        mock_channel.create_thread = AsyncMock(return_value=mock_thread)

        result = await client.create_thread_with_retry(
            mock_channel,
            name="Test Thread",
        )

        assert result is mock_thread
        mock_channel.create_thread.assert_called_once()

    def test_get_rate_limit_status(self, client):
        """Test getting rate limit status."""
        status = client.get_rate_limit_status()

        assert "total_buckets" in status or "status" in status

    def test_get_rate_limit_status_specific_endpoint(self, client):
        """Test getting status for specific endpoint."""
        # Create a bucket first
        client.rate_limiter._get_bucket("test_endpoint")

        status = client.get_rate_limit_status("test_endpoint")

        assert status["endpoint"] == "test_endpoint"

    def test_reset_rate_limits(self, client):
        """Test resetting rate limits."""
        # Add some buckets
        client.rate_limiter._get_bucket("endpoint1")
        client.rate_limiter._get_bucket("endpoint2")

        # Set them to rate limited
        client.rate_limiter.buckets["endpoint1"].remaining = 0
        client.rate_limiter.buckets["endpoint2"].remaining = 0

        client.reset_rate_limits()

        assert client.rate_limiter.buckets["endpoint1"].remaining > 0
        assert client.rate_limiter.buckets["endpoint2"].remaining > 0


class TestCreateEnhancedClient:
    """Test create_enhanced_client factory function."""

    def test_create_with_default_rate_limiter(self):
        """Test creation with default rate limiter."""
        mock_bot = Mock(spec=commands.Bot)

        client = create_enhanced_client(mock_bot)

        assert isinstance(client, EnhancedDiscordClient)
        assert client.bot is mock_bot

    def test_create_with_custom_rate_limiter(self):
        """Test creation with custom rate limiter."""
        mock_bot = Mock(spec=commands.Bot)
        limiter = DiscordRateLimiter(max_retries=5)

        client = create_enhanced_client(mock_bot, limiter)

        assert client.rate_limiter is limiter


class TestMessageSendingScenarios:
    """Test various message sending scenarios."""

    @pytest.fixture
    def setup(self):
        """Setup test fixtures."""
        mock_bot = AsyncMock(spec=commands.Bot)
        limiter = DiscordRateLimiter(max_retries=2, base_delay=0.01)
        client = EnhancedDiscordClient(mock_bot, limiter)
        return mock_bot, limiter, client

    @pytest.mark.asyncio
    async def test_send_with_all_parameters(self, setup):
        """Test sending message with all parameters."""
        mock_bot, _, client = setup

        mock_channel = AsyncMock(spec=discord.TextChannel)
        mock_message = Mock(spec=discord.Message)
        mock_message.id = 123
        mock_channel.send = AsyncMock(return_value=mock_message)

        embed = discord.Embed(title="Test")
        view = Mock()

        result = await client.send_message_with_retry(
            mock_channel,
            content="Test message",
            embed=embed,
            delete_after=10.0,
            view=view,
        )

        assert result is mock_message
        call_kwargs = mock_channel.send.call_args[1]
        assert call_kwargs["content"] == "Test message"
        assert call_kwargs["embed"] is embed
        assert call_kwargs["delete_after"] == 10.0
        assert call_kwargs["view"] is view

    @pytest.mark.asyncio
    async def test_edit_with_all_parameters(self, setup):
        """Test editing message with all parameters."""
        mock_bot, _, client = setup

        mock_message = AsyncMock(spec=discord.Message)
        mock_edited = Mock(spec=discord.Message)
        mock_message.edit = AsyncMock(return_value=mock_edited)

        embed = discord.Embed(title="Updated")
        view = Mock()

        result = await client.edit_message_with_retry(
            mock_message,
            content="Updated message",
            embed=embed,
            view=view,
        )

        assert result is mock_edited
        call_kwargs = mock_message.edit.call_args[1]
        assert call_kwargs["content"] == "Updated message"
        assert call_kwargs["embed"] is embed
        assert call_kwargs["view"] is view
