import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))


async def test_full_workflow():
    from app.services.admin.bot_stats_service import BotStatsService
    from app.services.admin.health_check_service import HealthCheckService, ServiceHealth
    from app.services.admin.queue_service import QueueService, FullQueueStatus, QueueStats

    mock_bot = Mock()
    mock_bot.guilds = [Mock(member_count=100)]
    mock_bot.active_threads = {}
    mock_bot.latency = 0.05

    stats_service = BotStatsService(mock_bot, None)
    health_service = HealthCheckService(None)
    queue_service = QueueService(None)

    with patch.object(stats_service, 'get_message_stats', new_callable=AsyncMock) as m1, \
            patch.object(stats_service, 'get_queue_stats', new_callable=AsyncMock) as m2:
        m1.return_value = {"today": 5, "week": 20}
        m2.return_value = {"high": 0, "medium": 0, "low": 0}

        stats = await stats_service.get_all_stats()
        assert stats.guild_count == 1

    with patch.object(health_service, 'check_supabase', new_callable=AsyncMock) as h1, \
            patch.object(health_service, 'check_rabbitmq', new_callable=AsyncMock) as h2, \
            patch.object(health_service, 'check_weaviate', new_callable=AsyncMock) as h3, \
            patch.object(health_service, 'check_falkordb', new_callable=AsyncMock) as h4, \
            patch.object(health_service, 'check_gemini_api', new_callable=AsyncMock) as h5:

        h1.return_value = ServiceHealth("Supabase", "healthy", 10)
        h2.return_value = ServiceHealth("RabbitMQ", "healthy", 5)
        h3.return_value = ServiceHealth("Weaviate", "healthy", 15)
        h4.return_value = ServiceHealth("FalkorDB", "healthy", 12)
        h5.return_value = ServiceHealth("Gemini", "healthy", 100)

        health = await health_service.get_all_health()
        assert health.overall_status == "healthy"

    with patch.object(queue_service, 'get_queue_stats', new_callable=AsyncMock) as q1:
        q1.return_value = FullQueueStatus(
            high=QueueStats("high", 0, 1),
            medium=QueueStats("medium", 0, 1),
            low=QueueStats("low", 0, 1),
            total_pending=0
        )

        status = await queue_service.get_queue_stats()
        assert status.total_pending == 0

    print("PASS: test_full_workflow")


async def test_permission_denies_regular_user():
    from integrations.discord.permissions import require_admin

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock):

        mock_settings.bot_owner_id = 123456789

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 999999999
        interaction.user.name = "regular_user"
        interaction.guild = Mock()
        interaction.guild.id = 1234567890

        member = Mock()
        member.guild_permissions = Mock()
        member.guild_permissions.administrator = False
        interaction.guild.get_member = Mock(return_value=member)

        interaction.command = Mock()
        interaction.command.name = "stats"

        interaction.response = Mock()
        interaction.response.is_done = Mock(return_value=False)
        interaction.response.send_message = AsyncMock()

        called = False

        class Cog:
            pass

        @require_admin
        async def cmd(self, interaction):
            nonlocal called
            called = True

        await cmd(Cog(), interaction)

        assert not called
        assert interaction.response.send_message.called
        print("PASS: test_permission_denies_regular_user")


async def test_permission_allows_admin():
    from integrations.discord.permissions import require_admin

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock):

        mock_settings.bot_owner_id = 123456789

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 999999999
        interaction.user.name = "admin_user"
        interaction.guild = Mock()
        interaction.guild.id = 1234567890

        member = Mock()
        member.guild_permissions = Mock()
        member.guild_permissions.administrator = True
        interaction.guild.get_member = Mock(return_value=member)

        interaction.command = Mock()
        interaction.command.name = "stats"

        interaction.response = Mock()
        interaction.response.is_done = Mock(return_value=False)

        called = False

        class Cog:
            pass

        @require_admin
        async def cmd(self, interaction):
            nonlocal called
            called = True

        await cmd(Cog(), interaction)

        assert called
        print("PASS: test_permission_allows_admin")


async def test_logging_works():
    from integrations.discord.permissions import require_admin

    with patch("integrations.discord.permissions.settings") as mock_settings, \
            patch("integrations.discord.permissions.log_admin_action", new_callable=AsyncMock) as mock_log:

        mock_settings.bot_owner_id = 123456789

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 123456789
        interaction.user.name = "bot_owner"
        interaction.guild = Mock()
        interaction.guild.id = 1234567890

        member = Mock()
        member.guild_permissions = Mock()
        member.guild_permissions.administrator = False
        interaction.guild.get_member = Mock(return_value=member)

        interaction.command = Mock()
        interaction.command.name = "queue_clear"

        interaction.response = Mock()
        interaction.response.is_done = Mock(return_value=False)

        class Cog:
            pass

        @require_admin
        async def cmd(self, interaction, priority="all"):
            pass

        await cmd(Cog(), interaction, priority="high")

        assert mock_log.called
        kwargs = mock_log.call_args.kwargs
        assert kwargs["executor_id"] == "123456789"
        assert kwargs["command_name"] == "queue_clear"
        print("PASS: test_logging_works")


async def run_all_tests():
    print("\n" + "=" * 60)
    print("Running Admin Integration Tests")
    print("=" * 60 + "\n")

    passed = 0
    failed = 0

    tests = [
        test_full_workflow,
        test_permission_denies_regular_user,
        test_permission_allows_admin,
        test_logging_works,
    ]

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"FAIL: {test.__name__}: {e}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
