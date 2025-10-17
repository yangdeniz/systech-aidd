"""
FastAPI dependencies для всего API.

Централизованное место для общих dependencies.
"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Global database session factory (инициализируется в main.py)
db_session_factory = None


async def get_db_session():
    """
    Dependency для получения database session.

    Yields:
        AsyncSession: Database session

    Raises:
        HTTPException 503: Если database недоступна
    """
    if db_session_factory is not None:
        async with db_session_factory() as session:
            yield session
    else:
        raise HTTPException(
            status_code=503,
            detail="Database not available. Ensure COLLECTOR_MODE=real and DATABASE_URL is set.",
        )
