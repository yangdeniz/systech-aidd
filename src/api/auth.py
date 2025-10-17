"""
Аутентификация для админ режима чата.

Простая JWT-based аутентификация с проверкой пароля из environment variable.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError

logger = logging.getLogger(__name__)

# Настройки JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

# Пароль администратора из environment
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Security scheme для FastAPI
security = HTTPBearer()


def verify_admin_password(password: str) -> bool:
    """
    Проверка пароля администратора.

    Args:
        password: Пароль для проверки

    Returns:
        True если пароль верный, False иначе
    """
    is_valid = password == ADMIN_PASSWORD
    if not is_valid:
        logger.warning("Failed admin authentication attempt")
    return is_valid


def create_access_token(data: dict[str, Any]) -> tuple[str, datetime]:
    """
    Создание JWT токена.

    Args:
        data: Данные для включения в payload токена

    Returns:
        Tuple (token, expires_at)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Created access token")

    return encoded_jwt, expire


def verify_token(credentials: HTTPAuthorizationCredentials) -> dict[str, Any]:
    """
    Проверка JWT токена.

    Используется как dependency в FastAPI endpoints.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        Payload токена если валидный

    Raises:
        HTTPException 401: Если токен невалидный или истек
    """
    token = credentials.credentials

    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired") from None
    except (DecodeError, InvalidSignatureError) as e:
        logger.warning("Invalid token: %s", e)
        raise HTTPException(status_code=401, detail="Invalid token") from e


def verify_admin_token(credentials: HTTPAuthorizationCredentials) -> dict[str, Any]:
    """
    Проверка токена администратора.

    Проверяет наличие role=admin в payload.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        Payload токена если валидный и role=admin

    Raises:
        HTTPException 403: Если нет прав администратора
    """
    payload = verify_token(credentials)

    if payload.get("role") != "admin":
        logger.warning("Attempted admin access without admin role")
        raise HTTPException(status_code=403, detail="Admin access required")

    return payload
