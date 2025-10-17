"""
Тесты для аутентификации админ режима чата.

Тестируем проверку паролей, генерацию JWT токенов,
валидацию токенов и проверку админских прав.
"""

from datetime import datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.api.auth import (
    ADMIN_PASSWORD,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    verify_admin_password,
    verify_admin_token,
    verify_token,
)


class TestPasswordVerification:
    """Тесты для проверки паролей."""

    def test_verify_correct_password(self):
        """Тестируем проверку корректного пароля."""
        assert verify_admin_password(ADMIN_PASSWORD) is True

    def test_verify_incorrect_password(self):
        """Тестируем отклонение неверного пароля."""
        assert verify_admin_password("wrong_password") is False

    def test_verify_empty_password(self):
        """Тестируем отклонение пустого пароля."""
        assert verify_admin_password("") is False


class TestTokenCreation:
    """Тесты для создания JWT токенов."""

    def test_create_access_token(self):
        """Тестируем создание токена."""
        data = {"role": "admin", "user": "test"}
        token, expires_at = create_access_token(data)

        # Проверяем что токен - строка
        assert isinstance(token, str)
        assert len(token) > 0

        # Проверяем что время истечения в будущем
        assert expires_at > datetime.utcnow()

        # Декодируем и проверяем payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["role"] == "admin"
        assert payload["user"] == "test"
        assert "exp" in payload

    def test_token_expiry_time(self):
        """Тестируем что время истечения токена корректное (1 час)."""
        data = {"role": "admin"}
        token, expires_at = create_access_token(data)

        # Проверяем что срок действия около 1 часа
        now = datetime.utcnow()
        time_diff = expires_at - now
        # Допускаем разницу в несколько секунд
        assert timedelta(hours=0, minutes=59) < time_diff < timedelta(hours=1, minutes=1)


class TestTokenVerification:
    """Тесты для проверки токенов."""

    def test_verify_valid_token(self):
        """Тестируем проверку валидного токена."""
        data = {"role": "admin", "user": "test"}
        token, _ = create_access_token(data)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
        )

        payload = verify_token(credentials)
        assert payload["role"] == "admin"
        assert payload["user"] == "test"

    def test_verify_expired_token(self):
        """Тестируем отклонение истекшего токена."""
        # Создаем токен с прошедшим сроком действия
        expired_time = datetime.utcnow() - timedelta(hours=2)
        payload = {"role": "admin", "exp": expired_time}
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=expired_token,
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_verify_invalid_token(self):
        """Тестируем отклонение невалидного токена."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here",
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()

    def test_verify_token_with_wrong_secret(self):
        """Тестируем отклонение токена подписанного неверным секретом."""
        payload = {"role": "admin", "exp": datetime.utcnow() + timedelta(hours=1)}
        wrong_token = jwt.encode(payload, "wrong_secret", algorithm=ALGORITHM)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=wrong_token,
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401


class TestAdminTokenVerification:
    """Тесты для проверки админских токенов."""

    def test_verify_admin_token_with_admin_role(self):
        """Тестируем проверку токена с админской ролью."""
        data = {"role": "admin"}
        token, _ = create_access_token(data)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
        )

        payload = verify_admin_token(credentials)
        assert payload["role"] == "admin"

    def test_verify_admin_token_without_admin_role(self):
        """Тестируем отклонение токена без админской роли."""
        data = {"role": "user"}
        token, _ = create_access_token(data)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_admin_token(credentials)

        assert exc_info.value.status_code == 403
        assert "admin" in exc_info.value.detail.lower()

    def test_verify_admin_token_with_no_role(self):
        """Тестируем отклонение токена без поля role."""
        data = {"user": "test"}
        token, _ = create_access_token(data)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_admin_token(credentials)

        assert exc_info.value.status_code == 403
