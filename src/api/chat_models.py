"""
Pydantic модели для Chat API.

Модели для веб-чата с поддержкой двух режимов:
- Normal: обычное общение с LLM
- Admin: вопросы по статистике через text2sql
"""

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Запрос на отправку сообщения в чат."""

    message: str = Field(..., min_length=1, description="Текст сообщения пользователя")
    mode: Literal["normal", "admin"] = Field(
        "normal", description="Режим работы чата: normal или admin"
    )
    session_id: str = Field(..., description="ID сессии для идентификации пользователя")


class ChatResponse(BaseModel):
    """Ответ от чата."""

    message: str = Field(..., description="Текст ответа от ассистента")
    sql_query: str | None = Field(None, description="SQL запрос (только для admin режима)")
    timestamp: str = Field(..., description="Timestamp ответа в ISO формате")


class ChatMessage(BaseModel):
    """Сообщение в истории чата."""

    role: Literal["user", "assistant"] = Field(..., description="Роль отправителя")
    content: str = Field(..., description="Содержимое сообщения")
    sql_query: str | None = Field(None, description="SQL запрос (если есть)")
    timestamp: str = Field(..., description="Timestamp сообщения в ISO формате")


class AuthRequest(BaseModel):
    """Запрос аутентификации для админ режима."""

    password: str = Field(..., min_length=1, description="Пароль администратора")


class AuthResponse(BaseModel):
    """Ответ аутентификации."""

    token: str = Field(..., description="JWT токен")
    expires_at: str = Field(..., description="Время истечения токена в ISO формате")


class ClearHistoryRequest(BaseModel):
    """Запрос на очистку истории чата."""

    session_id: str = Field(..., description="ID сессии для очистки истории")
