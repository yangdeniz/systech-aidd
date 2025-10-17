"""
Тесты для RealStatCollector.

Проверяем работу сборщика статистики с реальной базой данных.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.api.collectors import RealStatCollector
from src.api.models import DialogueInfo, MetricCard, TimeSeriesPoint, TopUser
from src.bot.models import Message, User


@pytest.fixture
def mock_session_factory():
    """Создать mock session factory для тестов."""
    factory = MagicMock()
    factory.return_value = AsyncMock()
    return factory


@pytest.fixture
def real_collector(mock_session_factory):
    """Создать RealStatCollector для тестов."""
    return RealStatCollector(mock_session_factory)


@pytest.mark.asyncio
async def test_real_collector_initialization(mock_session_factory):
    """Тест инициализации RealStatCollector."""
    collector = RealStatCollector(mock_session_factory)
    assert collector.session_factory == mock_session_factory


@pytest.mark.asyncio
async def test_get_stats_invalid_period(real_collector):
    """Тест обработки некорректного периода."""
    with pytest.raises(ValueError, match="Invalid period"):
        await real_collector.get_stats("invalid")


@pytest.mark.asyncio
async def test_calculate_change_percent(real_collector):
    """Тест расчета процента изменения."""
    # Положительное изменение
    assert real_collector._calculate_change_percent(120, 100) == 20.0

    # Отрицательное изменение
    assert real_collector._calculate_change_percent(80, 100) == -20.0

    # Нулевое предыдущее значение
    assert real_collector._calculate_change_percent(100, 0) == 100.0

    # Оба нуля
    assert real_collector._calculate_change_percent(0, 0) == 0.0


@pytest.mark.asyncio
async def test_get_trend_description(real_collector):
    """Тест генерации описания тренда."""
    # Strong growth
    desc = real_collector._get_trend_description(20, "dialogues")
    assert "growth" in desc.lower() or "strong" in desc.lower()

    # Steady increase
    desc = real_collector._get_trend_description(7, "users")
    assert "stable" in desc.lower() or "steady" in desc.lower()

    # Stable
    desc = real_collector._get_trend_description(0, "engagement")
    assert "stable" in desc.lower() or "consistent" in desc.lower()

    # Decline
    desc = real_collector._get_trend_description(-10, "activity")
    assert "decline" in desc.lower() or "below" in desc.lower() or "attention" in desc.lower()

    # Significant drop
    desc = real_collector._get_trend_description(-20, "dialogues")
    assert "drop" in desc.lower() or "attention" in desc.lower() or "declining" in desc.lower()


@pytest.mark.asyncio
async def test_get_stats_day_period_structure(real_collector, mock_session_factory):
    """Тест структуры данных для периода 'day'."""
    # Мокаем сессию
    mock_session = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    # Используем return_value для всех вызовов
    mock_session.scalar = AsyncMock(return_value=10)
    mock_session.execute = AsyncMock(return_value=MagicMock(all=lambda: []))

    result = await real_collector.get_stats("day")

    # Проверяем структуру
    assert isinstance(result.metrics, list)
    assert len(result.metrics) == 4
    assert all(isinstance(m, MetricCard) for m in result.metrics)
    assert isinstance(result.time_series, list)
    assert len(result.time_series) == 24  # 24 часа для day
    assert isinstance(result.recent_dialogues, list)
    assert isinstance(result.top_users, list)


@pytest.mark.asyncio
async def test_get_stats_week_period_structure(real_collector, mock_session_factory):
    """Тест структуры данных для периода 'week'."""
    mock_session = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_session.scalar = AsyncMock(return_value=50)
    mock_session.execute = AsyncMock(return_value=MagicMock(all=lambda: []))

    result = await real_collector.get_stats("week")

    assert len(result.metrics) == 4
    assert isinstance(result.time_series, list)
    assert len(result.time_series) == 7  # 7 дней для week


@pytest.mark.asyncio
async def test_get_stats_month_period_structure(real_collector, mock_session_factory):
    """Тест структуры данных для периода 'month'."""
    mock_session = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_session.scalar = AsyncMock(return_value=200)
    mock_session.execute = AsyncMock(return_value=MagicMock(all=lambda: []))

    result = await real_collector.get_stats("month")

    assert len(result.metrics) == 4
    assert isinstance(result.time_series, list)
    assert len(result.time_series) == 30  # 30 дней для month


@pytest.mark.asyncio
async def test_metrics_titles(real_collector, mock_session_factory):
    """Тест что метрики имеют правильные заголовки."""
    mock_session = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_session.scalar = AsyncMock(return_value=100)
    mock_session.execute = AsyncMock(return_value=MagicMock(all=lambda: []))

    result = await real_collector.get_stats("week")

    titles = [m.title for m in result.metrics]
    assert "Total Dialogues" in titles
    assert "Active Users" in titles
    assert "Avg Messages per Dialogue" in titles
    assert "Messages Today" in titles
