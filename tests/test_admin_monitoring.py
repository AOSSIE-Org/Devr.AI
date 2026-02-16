import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))


async def test_stats_service():
    from app.services.admin.bot_stats_service import BotStatsService

    mock_bot = Mock()
    mock_bot.guilds = [Mock(member_count=100), Mock(member_count=200)]
    mock_bot.active_threads = {"1": "thread1"}
    mock_bot.latency = 0.05

    service = BotStatsService(mock_bot, None)

    with patch.object(service, 'get_message_stats', new_callable=AsyncMock) as mock_msg, \
            patch.object(service, 'get_queue_stats', new_callable=AsyncMock) as mock_queue:
        mock_msg.return_value = {"today": 10, "week": 50}
        mock_queue.return_value = {"high": 1, "medium": 2, "low": 3}

        stats = await service.get_all_stats()

        assert stats.guild_count == 2
        assert stats.total_members == 300
        assert stats.active_threads == 1
        assert stats.messages_today == 10
        print("PASS: test_stats_service")


async def test_stats_handles_errors():
    from app.services.admin.bot_stats_service import BotStatsService

    mock_bot = Mock()
    mock_bot.guilds = []
    mock_bot.active_threads = {}
    mock_bot.latency = 0.1

    service = BotStatsService(mock_bot, None)

    with patch('app.services.admin.bot_stats_service.get_supabase_client') as mock_supa:
        mock_supa.side_effect = Exception("Database error")
        stats = await service.get_all_stats()
        assert stats.messages_today == 0
        print("PASS: test_stats_handles_errors")


async def test_health_all_healthy():
    from app.services.admin.health_check_service import HealthCheckService, ServiceHealth

    service = HealthCheckService(None)

    with patch.object(service, 'check_supabase', new_callable=AsyncMock) as m1, \
            patch.object(service, 'check_rabbitmq', new_callable=AsyncMock) as m2, \
            patch.object(service, 'check_weaviate', new_callable=AsyncMock) as m3, \
            patch.object(service, 'check_falkordb', new_callable=AsyncMock) as m4, \
            patch.object(service, 'check_gemini_api', new_callable=AsyncMock) as m5:

        m1.return_value = ServiceHealth("Supabase", "healthy", 10)
        m2.return_value = ServiceHealth("RabbitMQ", "healthy", 5)
        m3.return_value = ServiceHealth("Weaviate", "healthy", 15)
        m4.return_value = ServiceHealth("FalkorDB", "healthy", 12)
        m5.return_value = ServiceHealth("Gemini", "healthy", 100)

        health = await service.get_all_health()

        assert health.overall_status == "healthy"
        assert len(health.services) == 5
        print("PASS: test_health_all_healthy")


async def test_health_service_down():
    from app.services.admin.health_check_service import HealthCheckService, ServiceHealth

    service = HealthCheckService(None)

    with patch.object(service, 'check_supabase', new_callable=AsyncMock) as m1, \
            patch.object(service, 'check_rabbitmq', new_callable=AsyncMock) as m2, \
            patch.object(service, 'check_weaviate', new_callable=AsyncMock) as m3, \
            patch.object(service, 'check_falkordb', new_callable=AsyncMock) as m4, \
            patch.object(service, 'check_gemini_api', new_callable=AsyncMock) as m5:

        m1.return_value = ServiceHealth("Supabase", "unhealthy", 0, "Connection failed")
        m2.return_value = ServiceHealth("RabbitMQ", "healthy", 5)
        m3.return_value = ServiceHealth("Weaviate", "healthy", 15)
        m4.return_value = ServiceHealth("FalkorDB", "healthy", 12)
        m5.return_value = ServiceHealth("Gemini", "healthy", 100)

        health = await service.get_all_health()

        assert health.overall_status == "unhealthy"
        print("PASS: test_health_service_down")


async def test_user_info_verified():
    from app.services.admin.user_info_service import UserInfoService

    mock_bot = Mock()
    mock_bot.active_threads = {"123456": "thread1"}

    service = UserInfoService(mock_bot)

    mock_user = Mock()
    mock_user.id = 123456
    mock_user.name = "testuser"
    mock_user.display_name = "Test User"
    mock_user.avatar = Mock()
    mock_user.avatar.url = "https://example.com/avatar.png"
    mock_user.created_at = Mock()
    mock_user.created_at.strftime = Mock(return_value="2020-01-01")

    mock_member = Mock()
    mock_member.roles = [Mock(), Mock(), Mock()]

    with patch.object(service, 'get_user_profile', new_callable=AsyncMock) as m1, \
            patch.object(service, 'get_user_message_count', new_callable=AsyncMock) as m2, \
            patch.object(service, 'get_last_message', new_callable=AsyncMock) as m3:

        m1.return_value = {"is_verified": True, "github_username": "testuser_gh"}
        m2.return_value = 42
        m3.return_value = "2024-01-15T10:00:00"

        info = await service.get_full_user_info(mock_user, mock_member)

        assert info.is_verified is True
        assert info.github_username == "testuser_gh"
        assert info.message_count == 42
        assert info.has_active_thread is True
        print("PASS: test_user_info_verified")


async def test_user_info_unverified():
    from app.services.admin.user_info_service import UserInfoService

    mock_bot = Mock()
    mock_bot.active_threads = {}

    service = UserInfoService(mock_bot)

    mock_user = Mock()
    mock_user.id = 999999
    mock_user.name = "newuser"
    mock_user.display_name = "New User"
    mock_user.avatar = None
    mock_user.created_at = Mock()
    mock_user.created_at.strftime = Mock(return_value="2024-01-01")

    with patch.object(service, 'get_user_profile', new_callable=AsyncMock) as m1, \
            patch.object(service, 'get_user_message_count', new_callable=AsyncMock) as m2, \
            patch.object(service, 'get_last_message', new_callable=AsyncMock) as m3:

        m1.return_value = None
        m2.return_value = 0
        m3.return_value = None

        info = await service.get_full_user_info(mock_user, None)

        assert info.is_verified is False
        assert info.github_username is None
        assert info.message_count == 0
        print("PASS: test_user_info_unverified")


async def run_all_tests():
    print("\n" + "=" * 60)
    print("Running Admin Monitoring Tests")
    print("=" * 60 + "\n")

    passed = 0
    failed = 0

    tests = [
        test_stats_service,
        test_stats_handles_errors,
        test_health_all_healthy,
        test_health_service_down,
        test_user_info_verified,
        test_user_info_unverified,
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
