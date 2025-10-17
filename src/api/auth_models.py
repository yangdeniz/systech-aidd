"""
Pydantic модели для Auth API endpoints.
"""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Запрос на регистрацию нового пользователя."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (минимум 8 символов)")
    first_name: str | None = Field(None, description="Имя пользователя")


class LoginRequest(BaseModel):
    """Запрос на вход в систему."""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    """Ответ после успешной регистрации или логина."""

    token: str = Field(..., description="JWT токен")
    expires_at: str = Field(..., description="Дата истечения токена (ISO format)")
    user_id: int = Field(..., description="ID пользователя")
    username: str = Field(..., description="Username пользователя")
    role: str = Field(..., description="Роль пользователя (user или administrator)")


class VerifyResponse(BaseModel):
    """Ответ на проверку токена."""

    valid: bool = Field(..., description="Валиден ли токен")
    user_id: int | None = Field(None, description="ID пользователя")
    username: str | None = Field(None, description="Username пользователя")
    role: str | None = Field(None, description="Роль пользователя")


class LogoutResponse(BaseModel):
    """Ответ на logout."""

    status: str = Field(..., description="Статус операции")
    message: str = Field(..., description="Сообщение")
