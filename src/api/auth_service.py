"""
Auth Service для веб-аутентификации.

Предоставляет функции для:
- Хеширования и проверки паролей (bcrypt)
- Создания и валидации JWT токенов (30 дней TTL)
- Аутентификации веб-пользователей
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.models import User, UserRole, UserType

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", "30"))

# Password hashing configuration
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """
    Хеширует пароль с помощью bcrypt.

    Args:
        password: Пароль в открытом виде

    Returns:
        Хеш пароля в виде строки
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return password_hash.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Проверяет пароль против хеша.

    Args:
        password: Пароль в открытом виде
        password_hash: Хеш пароля

    Returns:
        True если пароль верный, False иначе
    """
    try:
        password_bytes = password.encode("utf-8")
        password_hash_bytes = password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, password_hash_bytes)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


async def authenticate_web_user(username: str, password: str, session: AsyncSession) -> User | None:
    """
    Аутентифицирует веб-пользователя по username и паролю.

    Args:
        username: Имя пользователя
        password: Пароль
        session: Async database session

    Returns:
        User объект если аутентификация успешна, None иначе
    """
    # Получаем пользователя из БД
    stmt = select(User).where(
        User.user_type == UserType.web,
        User.username == username,
        User.is_active == True,  # noqa: E712
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(f"Login attempt for non-existent user: {username}")
        return None

    # Проверяем пароль
    if user.password_hash is None:
        logger.error(f"User {username} has no password_hash")
        return None

    if not verify_password(password, user.password_hash):
        logger.warning(f"Failed login attempt for user: {username}")
        return None

    # Обновляем last_login
    user.last_login = datetime.utcnow()
    await session.commit()

    logger.info(f"Successful login for user: {username}")
    return user


def create_session_token(user: User) -> tuple[str, datetime]:
    """
    Создает JWT токен для пользователя.

    Args:
        user: User объект

    Returns:
        Tuple (token, expires_at)
    """
    expires_at = datetime.utcnow() + timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)

    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role.value if user.role else None,
        "user_type": user.user_type.value,
        "exp": expires_at,
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    logger.info(
        f"Created session token for user {user.username} "
        f"(expires in {JWT_ACCESS_TOKEN_EXPIRE_DAYS} days)"
    )

    return token, expires_at


def verify_session_token(token: str) -> dict[str, Any]:
    """
    Проверяет и декодирует JWT токен.

    Args:
        token: JWT токен

    Returns:
        Payload токена если валидный

    Raises:
        ExpiredSignatureError: Если токен истек
        DecodeError, InvalidSignatureError: Если токен невалидный
    """
    try:
        payload: dict[str, Any] = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        logger.warning("Token expired")
        raise
    except (DecodeError, InvalidSignatureError) as e:
        logger.warning(f"Invalid token: {e}")
        raise


async def register_web_user(
    username: str,
    password: str,
    first_name: str | None,
    session: AsyncSession,
    role: UserRole = UserRole.user,
) -> User:
    """
    Регистрирует нового веб-пользователя.

    Args:
        username: Имя пользователя (должно быть уникальным)
        password: Пароль (минимум 8 символов)
        first_name: Имя (опционально)
        session: Async database session
        role: Роль пользователя (по умолчанию USER)

    Returns:
        Созданный User объект

    Raises:
        ValueError: Если username уже занят или пароль слабый
    """
    # Валидация
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not username or len(username) < 3 or len(username) > 50:
        raise ValueError("Username must be between 3 and 50 characters")

    # Проверка уникальности username
    stmt = select(User).where(User.user_type == UserType.web, User.username == username)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise ValueError(f"Username {username} is already taken")

    # Создаем пользователя
    password_hash_str = hash_password(password)

    new_user = User(
        user_type=UserType.web,
        username=username,
        first_name=first_name,
        password_hash=password_hash_str,
        role=role,
        is_active=True,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info(f"Registered new web user: {username} with role {role.value}")

    return new_user
