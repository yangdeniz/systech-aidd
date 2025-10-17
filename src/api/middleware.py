"""
RBAC Middleware для защиты endpoints.

Предоставляет FastAPI dependencies для:
- Извлечения текущего пользователя из JWT токена
- Проверки роли администратора
"""

import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.models import User, UserRole, UserType

from .auth_service import verify_session_token
from .dependencies import get_db_session

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_web_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """
    Dependency для извлечения текущего веб-пользователя из JWT токена.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        session: Database session

    Returns:
        User объект

    Raises:
        HTTPException 401: Токен невалидный или истек
        HTTPException 404: Пользователь не найден
    """
    token = credentials.credentials

    try:
        # Верифицируем токен
        payload = verify_session_token(token)

        # Получаем user_id из payload
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")

        # Загружаем пользователя из БД
        stmt = select(User).where(
            User.id == user_id,
            User.user_type == UserType.web,
            User.is_active == True,  # noqa: E712
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User not found for user_id={user_id} from token")
            raise HTTPException(
                status_code=401,
                detail="User not found or inactive. Please login again.",
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting current user: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid token") from e


async def require_admin(user: Annotated[User, Depends(get_current_web_user)]) -> User:
    """
    Dependency для проверки что пользователь - администратор.

    Args:
        user: Текущий пользователь (из get_current_web_user)

    Returns:
        User объект если роль администратора

    Raises:
        HTTPException 403: Пользователь не имеет прав администратора
    """
    if user.role != UserRole.administrator:
        logger.warning(
            f"Access denied for user {user.username}: role={user.role}, required=administrator"
        )
        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )

    return user


async def get_current_user_optional(
    authorization: str | None = Header(None, alias="Authorization"),
    session: AsyncSession | None = None,
) -> User | None:
    """
    Dependency для опциональной аутентификации.

    Возвращает User если токен валидный, None если токена нет или он невалидный.

    Args:
        authorization: Authorization header
        session: Database session

    Returns:
        User объект или None
    """
    if authorization is None or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")

    try:
        payload = verify_session_token(token)
        user_id = payload.get("user_id")

        if user_id is None or session is None:
            return None

        stmt = select(User).where(
            User.id == user_id,
            User.user_type == UserType.web,
            User.is_active == True,  # noqa: E712
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    except Exception:
        return None
