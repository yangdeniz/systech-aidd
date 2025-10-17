"""
Конфигурация тестов для API.

Использует mock режим для изоляции тестов от реальной БД.
Mock режим не требует Docker и возвращает предсказуемые тестовые данные.

ВАЖНО: COLLECTOR_MODE устанавливается на уровне модуля ДО импорта приложения.
"""

import os

# Устанавливаем COLLECTOR_MODE в 'mock' ДО импорта приложения
os.environ["COLLECTOR_MODE"] = "mock"

import pytest  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402
from testcontainers.postgres import PostgresContainer  # noqa: E402

from src.api.auth_service import create_session_token, register_web_user  # noqa: E402
from src.bot.models import Base, UserRole  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def preserve_mock_collector_mode():
    """
    Сохраняет COLLECTOR_MODE в 'mock' для всех тестов API.

    Mock режим возвращает предсказуемые тестовые данные без подключения к БД.
    """
    # COLLECTOR_MODE уже установлен на уровне модуля
    yield
    # После тестов можно удалить, если нужно
    if "COLLECTOR_MODE" in os.environ:
        del os.environ["COLLECTOR_MODE"]


@pytest.fixture(scope="session")
def postgres_container():
    """Запускает PostgreSQL контейнер для тестов."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture
async def test_engine(postgres_container):
    """Создает тестовый PostgreSQL engine через testcontainers."""
    from sqlalchemy import text

    # Конвертируем URL из psycopg2 в asyncpg
    database_url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(database_url, echo=False)

    # Создаем enum'ы и таблицы через raw SQL
    async with engine.begin() as conn:
        # Создаем enum'ы
        await conn.execute(text("CREATE TYPE user_type_enum AS ENUM ('telegram', 'web')"))
        await conn.execute(text("CREATE TYPE user_role_enum AS ENUM ('user', 'administrator')"))
        # Создаем таблицы
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очищаем таблицы и enum'ы после каждого теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("DROP TYPE IF EXISTS user_role_enum"))
        await conn.execute(text("DROP TYPE IF EXISTS user_type_enum"))

    await engine.dispose()


@pytest.fixture
async def test_session_factory(test_engine):
    """Создает session factory для тестов."""
    return async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture
async def admin_user_token(test_session_factory):
    """Создает админ-пользователя и возвращает JWT токен."""
    async with test_session_factory() as session:
        # Регистрируем админ-пользователя
        user = await register_web_user(
            session=session,
            username="testadmin",
            password="testpass123",
            first_name="Test Admin",
            role=UserRole.administrator,
        )
        await session.commit()

    # Создаем JWT токен (функция не async и принимает только user)
    token, _ = create_session_token(user)

    return token
