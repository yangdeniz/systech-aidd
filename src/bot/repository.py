"""
Repository для работы с сообщениями и пользователями в БД.

Реализует паттерн Repository для абстракции доступа к данным.
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Message, User

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


class UserRepository:
    """
    Репозиторий для работы с пользователями.

    Предоставляет методы для:
    - Создания/получения пользователей (get_or_create)
    - Обновления информации о пользователях
    - Отслеживания активности (last_seen)
    - Получения статистики
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy
        """
        self.session = session

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> User:
        """
        Получить пользователя или создать нового.

        Автоматически обновляет last_seen и данные пользователя (username, имена) при каждом вызове.

        Args:
            telegram_id: ID пользователя Telegram
            username: Username из Telegram (может быть None)
            first_name: Имя пользователя (может быть None)
            last_name: Фамилия пользователя (может быть None)
            language_code: Код языка (может быть None)

        Returns:
            Объект User (существующий или новый)
        """
        # Ищем пользователя по telegram_id
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            # Создаем нового пользователя
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"Created new user: telegram_id={telegram_id}, username={username}")
        else:
            # Обновляем данные существующего пользователя
            updated = False
            if user.username != username:
                user.username = username
                updated = True
            if user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if user.language_code != language_code:
                user.language_code = language_code
                updated = True

            # Обновляем last_seen в любом случае
            user.last_seen = datetime.now()
            updated = True

            if updated:
                await self.session.commit()
                await self.session.refresh(user)
                logger.debug(f"Updated user data for telegram_id={telegram_id}")

        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        """
        Получить пользователя по telegram_id.

        Args:
            telegram_id: ID пользователя Telegram

        Returns:
            Объект User или None, если не найден
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_seen(self, telegram_id: int) -> None:
        """
        Обновить время последнего взаимодействия пользователя.

        Args:
            telegram_id: ID пользователя Telegram
        """
        stmt = update(User).where(User.telegram_id == telegram_id).values(last_seen=datetime.now())
        await self.session.execute(stmt)
        await self.session.commit()
        logger.debug(f"Updated last_seen for telegram_id={telegram_id}")

    async def get_active_users_count(self) -> int:
        """
        Получить количество активных пользователей.

        Returns:
            Количество активных пользователей (is_active=True)
        """
        stmt = select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count
