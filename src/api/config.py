"""
Конфигурация API и фабрика для создания StatCollector.

Поддерживает переключение между Mock и Real реализациями через environment variables.
"""

import os
from enum import Enum

from .collectors import MockStatCollector, RealStatCollector
from .interfaces import StatCollector


class CollectorMode(str, Enum):
    """
    Режимы работы сборщика статистики.

    MOCK: Генерирует тестовые данные (для разработки frontend)
    REAL: Использует реальные данные из PostgreSQL (production)
    """

    MOCK = "mock"
    REAL = "real"


class APIConfig:
    """
    Конфигурация API сервера.

    Читает настройки из environment variables:
    - COLLECTOR_MODE: режим работы collector ("mock" или "real")
    - DATABASE_URL: URL для подключения к PostgreSQL (только для REAL режима)
    """

    def __init__(self) -> None:
        """Инициализация конфигурации из environment variables."""
        # Режим сборщика статистики (по умолчанию mock для обратной совместимости)
        mode_str = os.getenv("COLLECTOR_MODE", "mock").lower()
        try:
            self.collector_mode = CollectorMode(mode_str)
        except ValueError:
            raise ValueError(
                f"Invalid COLLECTOR_MODE: {mode_str}. Must be 'mock' or 'real'"
            ) from None

        # Database URL (требуется только для REAL режима)
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://homeguru:homeguru_dev@localhost:5432/homeguru",
        )


def create_collector(config: APIConfig) -> StatCollector:
    """
    Фабрика для создания нужного StatCollector на основе конфигурации.

    Args:
        config: Конфигурация API с выбранным режимом

    Returns:
        StatCollector (MockStatCollector или RealStatCollector)

    Raises:
        ValueError: Если режим не поддерживается
    """
    if config.collector_mode == CollectorMode.MOCK:
        return MockStatCollector()

    elif config.collector_mode == CollectorMode.REAL:
        # Создаем database engine и session factory для RealStatCollector
        from ..bot.database import create_engine, create_session_factory

        # Создаем временную конфигурацию для database
        # (в реальности можно использовать существующую Config из bot.config)
        class _DBConfig:
            def __init__(self, database_url: str):
                self.database_url = database_url

        db_config = _DBConfig(config.database_url)
        engine = create_engine(db_config)
        session_factory = create_session_factory(engine)

        return RealStatCollector(session_factory)

    else:
        raise ValueError(f"Unsupported collector mode: {config.collector_mode}")


# Глобальный экземпляр конфигурации
_config: APIConfig | None = None


def get_config() -> APIConfig:
    """
    Получить глобальный экземпляр конфигурации (singleton pattern).

    Returns:
        APIConfig с настройками из environment
    """
    global _config
    if _config is None:
        _config = APIConfig()
    return _config


def get_collector() -> StatCollector:
    """
    Получить StatCollector на основе текущей конфигурации.

    Это основная функция для использования в FastAPI dependency injection.

    Returns:
        StatCollector (Mock или Real в зависимости от COLLECTOR_MODE)
    """
    config = get_config()
    return create_collector(config)
