"""
In-memory кэширование для API с TTL.

Простая реализация кэша для уменьшения нагрузки на базу данных.
В будущем может быть заменена на Redis для distributed caching.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, cast

from .models import StatsResponse


class SimpleCache:
    """
    Простой in-memory кэш с TTL (Time To Live).

    Особенности:
    - Хранение в памяти (словарь)
    - Автоматическая инвалидация по времени
    - Поддержка асинхронных операций
    - Thread-safe операции через asyncio.Lock

    Использование:
        cache = SimpleCache(ttl_seconds=60)
        await cache.set("key", value)
        value = await cache.get("key")
    """

    def __init__(self, ttl_seconds: int = 60) -> None:
        """
        Инициализация кэша.

        Args:
            ttl_seconds: Время жизни записи в секундах (по умолчанию 60)
        """
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> StatsResponse | None:  # noqa: ANN401
        """
        Получить значение из кэша.

        Args:
            key: Ключ для поиска

        Returns:
            Значение из кэша или None если не найдено или истекло TTL
        """
        async with self._lock:
            if key not in self._cache:
                return None

            value, expires_at = self._cache[key]

            # Проверяем не истекло ли TTL
            if datetime.now() >= expires_at:
                # Удаляем устаревшую запись
                del self._cache[key]
                return None

            # Type casting для mypy
            return cast(StatsResponse, value)

    async def set(self, key: str, value: StatsResponse) -> None:
        """
        Сохранить значение в кэш.

        Args:
            key: Ключ для сохранения
            value: Значение для кэширования
        """
        async with self._lock:
            expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)
            self._cache[key] = (value, expires_at)

    async def clear(self) -> None:
        """Очистить весь кэш."""
        async with self._lock:
            self._cache.clear()

    async def delete(self, key: str) -> None:
        """
        Удалить конкретную запись из кэша.

        Args:
            key: Ключ для удаления
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def cleanup_expired(self) -> int:
        """
        Удалить все истекшие записи из кэша.

        Returns:
            Количество удаленных записей
        """
        async with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, (_, expires_at) in self._cache.items() if now >= expires_at
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    def get_size(self) -> int:
        """
        Получить размер кэша (количество записей).

        Returns:
            Количество записей в кэше
        """
        return len(self._cache)


# Глобальный экземпляр кэша (singleton)
_cache: SimpleCache | None = None


def get_cache(ttl_seconds: int = 60) -> SimpleCache:
    """
    Получить глобальный экземпляр кэша (singleton pattern).

    Args:
        ttl_seconds: TTL в секундах (используется только при первом вызове)

    Returns:
        SimpleCache instance
    """
    global _cache
    if _cache is None:
        _cache = SimpleCache(ttl_seconds=ttl_seconds)
    return _cache
