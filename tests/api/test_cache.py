"""
Тесты для модуля кэширования.

Проверяем работу SimpleCache с TTL.
"""

import asyncio
from datetime import datetime

import pytest

from src.api.cache import SimpleCache, get_cache
from src.api.models import MetricCard, StatsResponse


@pytest.fixture
def cache():
    """Создать новый экземпляр кэша для каждого теста."""
    return SimpleCache(ttl_seconds=1)


@pytest.fixture
def sample_stats():
    """Создать пример StatsResponse для тестов."""
    return StatsResponse(
        metrics=[
            MetricCard(
                title="Test Metric",
                value=100,
                change_percent=10.5,
                description="Test description",
            )
        ],
        time_series=[],
        recent_dialogues=[],
        top_users=[],
    )


@pytest.mark.asyncio
async def test_cache_set_and_get(cache, sample_stats):
    """Тест базовой работы set/get."""
    await cache.set("test_key", sample_stats)
    result = await cache.get("test_key")

    assert result is not None
    assert result.metrics[0].title == "Test Metric"
    assert result.metrics[0].value == 100


@pytest.mark.asyncio
async def test_cache_miss(cache):
    """Тест cache miss для несуществующего ключа."""
    result = await cache.get("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_ttl_expiration(cache, sample_stats):
    """Тест истечения TTL."""
    # Устанавливаем с TTL 1 секунда
    await cache.set("test_key", sample_stats)

    # Сразу доступно
    result = await cache.get("test_key")
    assert result is not None

    # Ждем больше TTL
    await asyncio.sleep(1.1)

    # Теперь должно быть None
    result = await cache.get("test_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_clear(cache, sample_stats):
    """Тест очистки всего кэша."""
    await cache.set("key1", sample_stats)
    await cache.set("key2", sample_stats)

    assert cache.get_size() == 2

    await cache.clear()

    assert cache.get_size() == 0
    assert await cache.get("key1") is None
    assert await cache.get("key2") is None


@pytest.mark.asyncio
async def test_cache_delete(cache, sample_stats):
    """Тест удаления конкретной записи."""
    await cache.set("key1", sample_stats)
    await cache.set("key2", sample_stats)

    await cache.delete("key1")

    assert await cache.get("key1") is None
    assert await cache.get("key2") is not None
    assert cache.get_size() == 1


@pytest.mark.asyncio
async def test_cache_cleanup_expired(cache, sample_stats):
    """Тест очистки истекших записей."""
    await cache.set("key1", sample_stats)
    await cache.set("key2", sample_stats)

    # Ждем истечения TTL
    await asyncio.sleep(1.1)

    # Добавляем новую запись (она не истечет)
    await cache.set("key3", sample_stats)

    # Очищаем истекшие
    cleaned = await cache.cleanup_expired()

    # Должны удалить 2 истекшие записи
    assert cleaned == 2
    assert cache.get_size() == 1
    assert await cache.get("key3") is not None


@pytest.mark.asyncio
async def test_cache_get_size(cache, sample_stats):
    """Тест получения размера кэша."""
    assert cache.get_size() == 0

    await cache.set("key1", sample_stats)
    assert cache.get_size() == 1

    await cache.set("key2", sample_stats)
    assert cache.get_size() == 2

    await cache.delete("key1")
    assert cache.get_size() == 1


@pytest.mark.asyncio
async def test_cache_overwrite(cache, sample_stats):
    """Тест перезаписи значения."""
    await cache.set("key", sample_stats)

    # Создаем новый StatsResponse
    new_stats = StatsResponse(
        metrics=[
            MetricCard(
                title="New Metric",
                value=200,
                change_percent=20.0,
                description="New description",
            )
        ],
        time_series=[],
        recent_dialogues=[],
        top_users=[],
    )

    await cache.set("key", new_stats)

    result = await cache.get("key")
    assert result.metrics[0].value == 200


@pytest.mark.asyncio
async def test_get_cache_singleton():
    """Тест singleton pattern для get_cache."""
    cache1 = get_cache(ttl_seconds=60)
    cache2 = get_cache(ttl_seconds=120)  # TTL должен игнорироваться

    # Должны вернуть один и тот же экземпляр
    assert cache1 is cache2
