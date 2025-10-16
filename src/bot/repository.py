"""
Repository для работы с сообщениями в БД.

Реализует паттерн Repository для абстракции доступа к данным.
"""

import logging
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Message

logger = logging.getLogger(__name__)


class MessageRepository:
    """
    Репозиторий для работы с сообщениями диалогов.

    Предоставляет методы для:
    - Добавления сообщений
    - Получения истории диалогов
    - Soft delete истории
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy
        """
        self.session = session

    async def add_message(
        self, user_id: int, role: str, content: dict[str, Any] | str | list[dict[str, Any]]
    ) -> Message:
        """
        Добавить сообщение в БД.

        Args:
            user_id: ID пользователя Telegram
            role: Роль отправителя ("user" или "assistant")
            content: Содержимое сообщения (текст или мультимодальный контент)

        Returns:
            Созданное сообщение
        """
        # Нормализуем content к dict или оставляем list для мультимодального контента
        if isinstance(content, str):
            content_dict: dict[str, Any] | list[dict[str, Any]] = {"text": content}
        elif isinstance(content, list):
            # Для мультимодального контента сохраняем list как есть
            content_dict = content
        else:
            content_dict = content

        char_length = self._calculate_char_length(content_dict)

        message = Message(
            user_id=user_id,
            role=role,
            content=content_dict,
            char_length=char_length,
        )

        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        logger.debug(f"Added message for user {user_id}: role={role}, char_length={char_length}")
        return message

    async def get_history(self, user_id: int, limit: int) -> list[dict[str, Any]]:
        """
        Получить историю сообщений пользователя (только не удаленные).

        Args:
            user_id: ID пользователя Telegram
            limit: Максимальное количество сообщений

        Returns:
            Список сообщений в формате [{"role": "user", "content": "..."}]
        """
        stmt = (
            select(Message)
            .where(Message.user_id == user_id, Message.is_deleted == False)  # noqa: E712
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        messages = result.scalars().all()

        # Возвращаем в прямом порядке (от старых к новым)
        # Распаковываем текст из {"text": "..."} обратно в строку для LLM API
        history = []
        for msg in reversed(messages):
            content = msg.content
            # Если это простое текстовое сообщение в формате {"text": "..."}
            if isinstance(content, dict) and "text" in content and len(content) == 1:
                content = content["text"]
            # Иначе (список для мультимодального) оставляем как есть
            history.append({"role": msg.role, "content": content})

        logger.debug(f"Retrieved {len(history)} messages for user {user_id}")
        return history

    async def clear_history(self, user_id: int) -> None:
        """
        Soft delete всех сообщений пользователя.

        Args:
            user_id: ID пользователя Telegram
        """
        stmt = (
            update(Message)
            .where(Message.user_id == user_id, Message.is_deleted == False)  # noqa: E712
            .values(is_deleted=True)
        )

        result = await self.session.execute(stmt)
        rows_affected = result.rowcount  # type: ignore[attr-defined]
        await self.session.commit()

        logger.info(f"Soft deleted {rows_affected} messages for user {user_id}")

    def _calculate_char_length(self, content: dict[str, Any] | list[dict[str, Any]]) -> int:
        """
        Вычислить длину контента в символах.

        Для текстовых сообщений - длина текста.
        Для мультимодальных - сумма длин всех текстовых частей.

        Args:
            content: Содержимое сообщения (dict или list)

        Returns:
            Длина в символах
        """
        # Простое текстовое сообщение
        if isinstance(content, dict) and "text" in content:
            return len(str(content["text"]))

        # Мультимодальное сообщение (список с type: text и type: image_url)
        if isinstance(content, list):
            text_parts = [item.get("text", "") for item in content if item.get("type") == "text"]
            return sum(len(text) for text in text_parts)

        # Fallback: считаем длину строкового представления
        return len(str(content))
