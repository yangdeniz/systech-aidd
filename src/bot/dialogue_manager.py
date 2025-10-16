import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .repository import MessageRepository

logger = logging.getLogger(__name__)


class DialogueManager:
    """
    Менеджер диалогов с персистентным хранением в БД.

    Использует MessageRepository для работы с базой данных.
    Реализует интерфейс DialogueStorage Protocol.
    """

    session_factory: async_sessionmaker[AsyncSession]
    max_history: int

    def __init__(self, session_factory: async_sessionmaker[AsyncSession], max_history: int) -> None:
        """
        Инициализация менеджера диалогов.

        Args:
            session_factory: Фабрика для создания сессий БД
            max_history: Максимальное количество сообщений в истории
        """
        self.session_factory = session_factory
        self.max_history = max_history
        logger.info(f"DialogueManager initialized with max_history={max_history}")

    async def add_message(
        self, user_id: int, role: str, content: dict[str, Any] | str | list[dict[str, Any]]
    ) -> None:
        """
        Добавляет сообщение в историю диалога (БД).

        Поддерживает текстовые и мультимодальные сообщения (с изображениями).

        Args:
            user_id: ID пользователя
            role: роль отправителя ("user" или "assistant")
            content: текст сообщения или мультимодальный контент
        """
        async with self.session_factory() as session:
            repository = MessageRepository(session)
            await repository.add_message(user_id, role, content)
        logger.debug(f"Added {role} message for user {user_id} to database")

    async def get_history(self, user_id: int) -> list[dict[str, Any]]:
        """
        Возвращает историю диалога для пользователя из БД.

        Поддерживает текстовые и мультимодальные сообщения.

        Args:
            user_id: ID пользователя

        Returns:
            Список сообщений в формате [{"role": "user", "content": "..." | [...]}]
        """
        async with self.session_factory() as session:
            repository = MessageRepository(session)
            history = await repository.get_history(user_id, limit=self.max_history)
        return history

    async def clear_history(self, user_id: int) -> None:
        """
        Очищает историю диалога для пользователя (soft delete).

        Args:
            user_id: ID пользователя
        """
        async with self.session_factory() as session:
            repository = MessageRepository(session)
            await repository.clear_history(user_id)
        logger.info(f"Cleared history for user {user_id} (soft delete)")
