"""
Модели базы данных для хранения истории диалогов.

Используем SQLAlchemy 2.0+ async ORM с DeclarativeBase для type safety.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass


class User(Base):
    """
    Модель пользователя бота.

    Хранит информацию о пользователях Telegram:
    - Данные из Telegram API (username, first/last name, language_code)
    - Метрики активности (first_seen, last_seen)
    - Статус активности (is_active)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, doc="Telegram user ID"
    )
    username: Mapped[str | None] = mapped_column(String(255), doc="Telegram username")
    first_name: Mapped[str | None] = mapped_column(String(255), doc="Telegram first name")
    last_name: Mapped[str | None] = mapped_column(String(255), doc="Telegram last name")
    language_code: Mapped[str | None] = mapped_column(String(10), doc="Telegram language code")
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), doc="Первое взаимодействие"
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        doc="Последнее взаимодействие",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", doc="Флаг активности пользователя"
    )

    # Relationship to messages
    messages: Mapped[list["Message"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, telegram_id={self.telegram_id}, "
            f"username={self.username}, is_active={self.is_active})"
        )


class Message(Base):
    """
    Модель сообщения в диалоге.

    Хранит историю диалогов пользователей с поддержкой:
    - Мультимодального контента (текст + изображения) в JSONB
    - Soft delete стратегии (is_deleted)
    - Метаданных (created_at, char_length)
    - Связи с пользователем (foreign key)
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        index=True,
        doc="Telegram user ID (foreign key)",
    )
    role: Mapped[str] = mapped_column(String(20), doc="user или assistant")
    content: Mapped[Any] = mapped_column(
        JSONB, doc="Текстовое или мультимодальное содержимое сообщения (dict или list)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), doc="Время создания сообщения"
    )
    char_length: Mapped[int] = mapped_column(Integer, doc="Длина сообщения в символах")
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", doc="Флаг soft delete"
    )

    # Relationship to user
    user: Mapped["User"] = relationship(back_populates="messages")

    __table_args__ = (Index("ix_messages_user_id_created_at", "user_id", "created_at"),)

    def __repr__(self) -> str:
        return (
            f"Message(id={self.id}, user_id={self.user_id}, role={self.role}, "
            f"char_length={self.char_length}, is_deleted={self.is_deleted})"
        )
