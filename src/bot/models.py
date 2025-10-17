"""
Модели базы данных для хранения истории диалогов.

Используем SQLAlchemy 2.0+ async ORM с DeclarativeBase для type safety.
"""

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass


class UserType(str, enum.Enum):
    """Тип пользователя в системе."""

    telegram = "telegram"
    web = "web"


class UserRole(str, enum.Enum):
    """Роль веб-пользователя для RBAC."""

    user = "user"
    administrator = "administrator"


class User(Base):
    """
    Модель пользователя системы.

    Поддерживает два типа пользователей:
    1. Telegram пользователи (user_type='telegram'):
       - Имеют telegram_id (NOT NULL)
       - Данные из Telegram API
       - Нет password_hash и role

    2. Веб пользователи (user_type='web'):
       - Имеют username и password_hash (NOT NULL)
       - Имеют role для RBAC (user/administrator)
       - telegram_id = NULL

    Общие поля для обоих типов:
    - Метрики активности (first_seen, last_seen)
    - Статус активности (is_active)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Тип пользователя (telegram или web)
    user_type: Mapped[UserType] = mapped_column(
        Enum(UserType, name="user_type_enum", native_enum=True),
        nullable=False,
        server_default="telegram",
        doc="Тип пользователя: telegram или web",
    )

    # Telegram-специфичные поля
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        doc="Telegram user ID (только для telegram пользователей)",
    )
    language_code: Mapped[str | None] = mapped_column(String(10), doc="Telegram language code")

    # Общие поля
    username: Mapped[str | None] = mapped_column(String(255), doc="Username (telegram или web)")
    first_name: Mapped[str | None] = mapped_column(String(255), doc="Имя пользователя")
    last_name: Mapped[str | None] = mapped_column(String(255), doc="Фамилия пользователя")

    # Веб-специфичные поля
    password_hash: Mapped[str | None] = mapped_column(
        String(255), doc="Bcrypt hash пароля (только для web пользователей)"
    )
    role: Mapped[UserRole | None] = mapped_column(
        Enum(UserRole, name="user_role_enum", native_enum=True),
        doc="Роль веб-пользователя для RBAC",
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), doc="Последний логин (для web пользователей)"
    )

    # Метрики активности
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
        if self.user_type == UserType.telegram:
            return (
                f"User(id={self.id}, type=telegram, telegram_id={self.telegram_id}, "
                f"username={self.username})"
            )
        else:
            return f"User(id={self.id}, type=web, username={self.username}, role={self.role})"


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
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        doc="User ID (foreign key to users.id)",
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
