"""
Настройка подключения к базе данных.

Использует async engine и session factory для работы с PostgreSQL.
"""

import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import Config

logger = logging.getLogger(__name__)


def create_engine(config: Config) -> AsyncEngine:
    """
    Создать async engine для подключения к базе данных.

    Args:
        config: Конфигурация приложения с database_url

    Returns:
        AsyncEngine для работы с БД
    """
    engine = create_async_engine(
        config.database_url,
        echo=False,  # Не логировать SQL запросы (можно включить для отладки)
        pool_size=5,  # Размер пула соединений
        max_overflow=10,  # Максимальное количество дополнительных соединений
    )
    logger.info(f"Database engine created for {config.database_url.split('@')[1]}")
    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Создать фабрику сессий для работы с БД.

    Args:
        engine: AsyncEngine

    Returns:
        async_sessionmaker для создания сессий
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Не сбрасывать объекты после commit
    )
