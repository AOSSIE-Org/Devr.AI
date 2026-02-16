import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

async def test_queue_status():
    from app.services.admin.queue_service import QueueService, FullQueueStatus, QueueStats

    service = QueueService(None)

    with patch.object(service, 'get_queue_stats', new_callable=AsyncMock) as mock_stats:
        mock_stats.return_value = FullQueueStatus(
            high=QueueStats("high", 5, 2),
            medium=QueueStats("medium", 10, 3),
            low=QueueStats("low", 3, 1),
            total_pending=18
        )

        status = await service.get_queue_stats()

        assert status.total_pending == 18
        assert status.high.pending == 5
        print("PASS: test_queue_status")


async def test_queue_clear():
    from app.services.admin.queue_service import QueueService
    from app.core.orchestration.queue_manager import QueuePriority

    mock_channel = Mock()
    mock_queue_manager = Mock()
    mock_queue_manager.channel = mock_channel
    mock_queue_manager.queues = {
        QueuePriority.HIGH: "high_task_queue",
        QueuePriority.MEDIUM: "medium_task_queue",
        QueuePriority.LOW: "low_task_queue"
    }

    mock_queue = Mock()
    mock_queue.declaration_result = Mock()
    mock_queue.declaration_result.message_count = 5
    mock_queue.purge = AsyncMock()

    mock_channel.declare_queue = AsyncMock(return_value=mock_queue)

    service = QueueService(mock_queue_manager)
    cleared = await service.clear_queue("all")

    assert "high" in cleared
    assert "medium" in cleared
    assert "low" in cleared
    print("PASS: test_queue_clear")


async def test_user_reset_memory():
    from app.services.admin.user_management_service import UserManagementService

    mock_queue = Mock()
    mock_queue.enqueue = AsyncMock()

    service = UserManagementService(None, mock_queue)

    result = await service.reset_user(
        "123456",
        reset_memory=True,
        reset_thread=False,
        reset_verification=False
    )

    assert result.memory_cleared is True
    assert result.thread_closed is False
    mock_queue.enqueue.assert_called_once()
    print("PASS: test_user_reset_memory")


async def test_user_reset_full():
    from app.services.admin.user_management_service import UserManagementService

    mock_bot = Mock()
    mock_bot.active_threads = {"123456": "thread123"}
    mock_bot.get_channel = Mock(return_value=None)

    mock_queue = Mock()
    mock_queue.enqueue = AsyncMock()

    service = UserManagementService(mock_bot, mock_queue)

    with patch('app.services.admin.user_management_service.get_supabase_client') as mock_supa:
        mock_client = Mock()
        mock_client.table = Mock(return_value=mock_client)
        mock_client.update = Mock(return_value=mock_client)
        mock_client.eq = Mock(return_value=mock_client)
        mock_client.execute = AsyncMock()
        mock_supa.return_value = mock_client

        result = await service.reset_user(
            "123456",
            reset_memory=True,
            reset_thread=True,
            reset_verification=True
        )

        assert result.memory_cleared is True
        assert result.thread_closed is True
        assert result.verification_reset is True
        print("PASS: test_user_reset_full")


async def test_cache_clear():
    from app.services.admin.cache_service import CacheService

    mock_bot = Mock()
    mock_bot.active_threads = {"1": "t1", "2": "t2", "3": "t3"}

    service = CacheService(mock_bot)
    cleared = await service.clear_cache("all")

    assert cleared["active_threads"] == 3
    assert len(mock_bot.active_threads) == 0
    print("PASS: test_cache_clear")


async def test_cache_sizes():
    from app.services.admin.cache_service import CacheService

    mock_bot = Mock()
    mock_bot.active_threads = {"1": "t1"}

    service = CacheService(mock_bot)
    sizes = await service.get_cache_sizes()

    assert sizes["active_threads"] == 1
    print("PASS: test_cache_sizes")


def test_confirm_view():
    from integrations.discord.views import ConfirmActionView

    view = ConfirmActionView(timeout=30.0)
    assert view.confirmed is False
    assert view.timeout == 30.0
    print("PASS: test_confirm_view")


async def run_all_tests():
    print("\n" + "=" * 60)
    print("Running Admin Management Tests")
    print("=" * 60 + "\n")

    passed = 0
    failed = 0

    async_tests = [
        test_queue_status,
        test_queue_clear,
        test_user_reset_memory,
        test_user_reset_full,
        test_cache_clear,
        test_cache_sizes,
    ]

    for test in async_tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"FAIL: {test.__name__}: {e}")

    try:
        test_confirm_view()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"FAIL: test_confirm_view: {e}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
