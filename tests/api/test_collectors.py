"""
Тесты для MockStatCollector.

Проверяет корректность генерации тестовых данных для дашборда.
"""

import pytest

from src.api.collectors import MockStatCollector
from src.api.models import StatsResponse


class TestMockStatCollector:
    """Тесты для MockStatCollector."""

    @pytest.fixture
    def collector(self) -> MockStatCollector:
        """Создает экземпляр MockStatCollector."""
        return MockStatCollector()

    @pytest.mark.asyncio
    async def test_get_stats_day(self, collector: MockStatCollector) -> None:
        """Тест получения статистики за день."""
        stats = await collector.get_stats("day")

        assert isinstance(stats, StatsResponse)
        assert len(stats.metrics) == 4
        assert len(stats.time_series) == 24  # 24 часа
        assert len(stats.recent_dialogues) == 10
        assert len(stats.top_users) == 5

    @pytest.mark.asyncio
    async def test_get_stats_week(self, collector: MockStatCollector) -> None:
        """Тест получения статистики за неделю."""
        stats = await collector.get_stats("week")

        assert isinstance(stats, StatsResponse)
        assert len(stats.metrics) == 4
        assert len(stats.time_series) == 7  # 7 дней
        assert len(stats.recent_dialogues) == 10
        assert len(stats.top_users) == 5

    @pytest.mark.asyncio
    async def test_get_stats_month(self, collector: MockStatCollector) -> None:
        """Тест получения статистики за месяц."""
        stats = await collector.get_stats("month")

        assert isinstance(stats, StatsResponse)
        assert len(stats.metrics) == 4
        assert len(stats.time_series) == 30  # 30 дней
        assert len(stats.recent_dialogues) == 10
        assert len(stats.top_users) == 5

    @pytest.mark.asyncio
    async def test_get_stats_invalid_period(self, collector: MockStatCollector) -> None:
        """Тест с некорректным периодом."""
        with pytest.raises(ValueError, match="Invalid period"):
            await collector.get_stats("invalid")

    @pytest.mark.asyncio
    async def test_metrics_structure(self, collector: MockStatCollector) -> None:
        """Тест структуры метрик."""
        stats = await collector.get_stats("week")

        for metric in stats.metrics:
            assert metric.title
            assert metric.value is not None
            assert isinstance(metric.change_percent, float)
            assert metric.description

        # Проверяем наличие всех ожидаемых метрик
        titles = [m.title for m in stats.metrics]
        assert "Total Dialogues" in titles
        assert "Active Users" in titles
        assert "Avg Messages per Dialogue" in titles
        assert "Messages Today" in titles

    @pytest.mark.asyncio
    async def test_time_series_structure(self, collector: MockStatCollector) -> None:
        """Тест структуры временного ряда."""
        stats = await collector.get_stats("week")

        for point in stats.time_series:
            assert point.date
            assert isinstance(point.value, int)
            assert point.value >= 0

    @pytest.mark.asyncio
    async def test_recent_dialogues_structure(self, collector: MockStatCollector) -> None:
        """Тест структуры последних диалогов."""
        stats = await collector.get_stats("week")

        for dialogue in stats.recent_dialogues:
            assert isinstance(dialogue.user_id, int)
            assert dialogue.username is None or isinstance(dialogue.username, str)
            assert isinstance(dialogue.message_count, int)
            assert dialogue.message_count > 0
            assert dialogue.last_message_at is not None

    @pytest.mark.asyncio
    async def test_top_users_structure(self, collector: MockStatCollector) -> None:
        """Тест структуры топ пользователей."""
        stats = await collector.get_stats("week")

        for user in stats.top_users:
            assert isinstance(user.user_id, int)
            assert user.username is None or isinstance(user.username, str)
            assert isinstance(user.total_messages, int)
            assert user.total_messages > 0
            assert isinstance(user.dialogue_count, int)
            assert user.dialogue_count > 0

    @pytest.mark.asyncio
    async def test_top_users_sorted(self, collector: MockStatCollector) -> None:
        """Тест сортировки топ пользователей по убыванию сообщений."""
        stats = await collector.get_stats("week")

        messages_counts = [user.total_messages for user in stats.top_users]
        assert messages_counts == sorted(messages_counts, reverse=True)

    @pytest.mark.asyncio
    async def test_different_periods_different_data(self, collector: MockStatCollector) -> None:
        """Тест различия данных для разных периодов."""
        # Сбрасываем seed для каждого периода
        stats_day = await collector.get_stats("day")
        stats_week = await collector.get_stats("week")
        stats_month = await collector.get_stats("month")

        # Проверяем, что длина временных рядов различается
        assert len(stats_day.time_series) == 24
        assert len(stats_week.time_series) == 7
        assert len(stats_month.time_series) == 30

        # Проверяем, что значения метрик различаются
        day_dialogues = stats_day.metrics[0].value
        week_dialogues = stats_week.metrics[0].value
        month_dialogues = stats_month.metrics[0].value

        # Значения должны быть разные (так как используется random)
        assert not (day_dialogues == week_dialogues == month_dialogues)
