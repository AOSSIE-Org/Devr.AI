import asyncio
import discord
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))


class MockCog:
    def __init__(self):
        self.bot = Mock()


def create_mock_interaction(user_id=999999999, guild_id=987654321, command_name="test_command", is_admin_user=False):
    interaction = Mock()
    interaction.user = Mock()
    interaction.user.id = user_id
    interaction.user.name = "test_user"

    interaction.guild = Mock()
    interaction.guild.id = guild_id

    member = Mock()
    member.guild_permissions = Mock()
    member.guild_permissions.administrator = is_admin_user
    interaction.guild.get_member = Mock(return_value=member)

    interaction.command = Mock()
    interaction.command.name = command_name

    interaction.response = Mock()
    interaction.response.is_done = Mock(return_value=False)
    interaction.response.send_message = AsyncMock()

    interaction.followup = Mock()
    interaction.followup.send = AsyncMock()

    return interaction


async def test_admin_decorator_allows_administrator():
    from integrations.discord.permissions import require_admin

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock):

        mock_settings.bot_owner_id = 123456789
        interaction = create_mock_interaction(user_id=999999999, is_admin_user=True)
        cog = MockCog()

        called = False

        @require_admin
        async def test_command(self, interaction):
            nonlocal called
            called = True

        await test_command(cog, interaction)

        assert called, "Command should execute for admin user"
        print("PASS: test_admin_decorator_allows_administrator")


async def test_admin_decorator_allows_bot_owner():
    from integrations.discord.permissions import require_admin

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock):

        mock_settings.bot_owner_id = 123456789
        interaction = create_mock_interaction(user_id=123456789, is_admin_user=False)
        cog = MockCog()

        called = False

        @require_admin
        async def test_command(self, interaction):
            nonlocal called
            called = True

        await test_command(cog, interaction)

        assert called, "Command should execute for bot owner"
        print("PASS: test_admin_decorator_allows_bot_owner")


async def test_admin_decorator_denies_regular_user():
    from integrations.discord.permissions import require_admin

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock):

        mock_settings.bot_owner_id = 123456789
        interaction = create_mock_interaction(user_id=999999999, is_admin_user=False)
        cog = MockCog()

        called = False

        @require_admin
        async def test_command(self, interaction):
            nonlocal called
            called = True

        await test_command(cog, interaction)

        assert not called, "Command should not execute for regular user"
        assert interaction.response.send_message.called, "Should send error message"
        print("PASS: test_admin_decorator_denies_regular_user")


async def test_bot_owner_decorator_denies_admin():
    from integrations.discord.permissions import require_bot_owner

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock):

        mock_settings.bot_owner_id = 123456789
        interaction = create_mock_interaction(user_id=999999999, is_admin_user=True)
        cog = MockCog()

        called = False

        @require_bot_owner
        async def test_command(self, interaction):
            nonlocal called
            called = True

        await test_command(cog, interaction)

        assert not called, "Command should not execute for non-owner admin"
        print("PASS: test_bot_owner_decorator_denies_admin")


async def test_bot_owner_decorator_allows_owner():
    from integrations.discord.permissions import require_bot_owner

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock):

        mock_settings.bot_owner_id = 123456789
        interaction = create_mock_interaction(user_id=123456789, is_admin_user=False)
        cog = MockCog()

        called = False

        @require_bot_owner
        async def test_command(self, interaction):
            nonlocal called
            called = True

        await test_command(cog, interaction)

        assert called, "Command should execute for bot owner"
        print("PASS: test_bot_owner_decorator_allows_owner")


async def test_permission_check_logging():
    from integrations.discord.permissions import require_admin

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock) as mock_log:

        mock_settings.bot_owner_id = 123456789
        interaction = create_mock_interaction(user_id=999999999, is_admin_user=False, command_name="stats")
        cog = MockCog()

        @require_admin
        async def test_command(self, interaction):
            pass

        await test_command(cog, interaction)

        assert mock_log.called, "Should log permission check"
        call_kwargs = mock_log.call_args.kwargs
        assert call_kwargs["executor_id"] == "999999999"
        assert call_kwargs["command_name"] == "stats"
        assert call_kwargs["action_result"] == "failure"
        print("PASS: test_permission_check_logging")


def test_error_embed_generation():
    from integrations.discord.permissions import get_permission_embed

    embed = get_permission_embed()

    assert embed.title == "Permission Denied"
    assert "don't have permission" in embed.description
    assert len(embed.fields) >= 2
    print("PASS: test_error_embed_generation")


async def run_all_tests():
    print("\n" + "=" * 60)
    print("Running Admin Permissions Tests")
    print("=" * 60 + "\n")

    passed = 0
    failed = 0

    tests = [
        test_admin_decorator_allows_administrator,
        test_admin_decorator_allows_bot_owner,
        test_admin_decorator_denies_regular_user,
        test_bot_owner_decorator_denies_admin,
        test_bot_owner_decorator_allows_owner,
        test_permission_check_logging,
    ]

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"FAIL: {test.__name__}: {e}")

    try:
        test_error_embed_generation()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"FAIL: test_error_embed_generation: {e}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
