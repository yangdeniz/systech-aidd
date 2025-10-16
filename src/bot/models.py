"""
Модели базы данных для хранения истории диалогов.

Используем SQLAlchemy 2.0+ async ORM с DeclarativeBase для type safety.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass


class Message(Base):
    """
    Модель сообщения в диалоге.

    Хранит историю диалогов пользователей с поддержкой:
    - Мультимодального контента (текст + изображения) в JSONB
    - Soft delete стратегии (is_deleted)
    - Метаданных (created_at, char_length)
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, doc="Telegram user ID")
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

    __table_args__ = (Index("ix_messages_user_id_created_at", "user_id", "created_at"),)

    def __repr__(self) -> str:
        return (
            f"Message(id={self.id}, user_id={self.user_id}, role={self.role}, "
            f"char_length={self.char_length}, is_deleted={self.is_deleted})"
        )
