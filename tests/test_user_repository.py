"""Тесты для UserRepository."""

from typing import Any

import pytest

from src.bot.models import User
from src.bot.repository import UserRepository


@pytest.mark.asyncio
async def test_get_or_create_user_creates_new_user(test_session_factory: Any) -> None:
    """Тест: get_or_create_user создает нового пользователя."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        user = await repo.get_or_create_user(
            telegram_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            language_code="en",
        )

        assert user.id is not None
        assert user.telegram_id == 12345
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.language_code == "en"
        assert user.is_active is True
        assert user.first_seen is not None
        assert user.last_seen is not None


@pytest.mark.asyncio
async def test_get_or_create_user_returns_existing_user(test_session_factory: Any) -> None:
    """Тест: get_or_create_user возвращает существующего пользователя."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Создаем пользователя первый раз
        user1 = await repo.get_or_create_user(
            telegram_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
        )
        user1_id = user1.id
        user1_first_seen = user1.first_seen

    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Получаем того же пользователя второй раз
        user2 = await repo.get_or_create_user(
            telegram_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
        )

        # Проверяем, что это тот же пользователь
        assert user2.id == user1_id
        assert user2.telegram_id == 12345
        # first_seen не должен измениться
        assert user2.first_seen == user1_first_seen


@pytest.mark.asyncio
async def test_get_or_create_user_updates_last_seen(test_session_factory: Any) -> None:
    """Тест: get_or_create_user обновляет last_seen при каждом вызове."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Создаем пользователя
        user1 = await repo.get_or_create_user(telegram_id=12345, username="testuser")
        last_seen1 = user1.last_seen

    # Ждем немного, чтобы время изменилось
    import asyncio

    await asyncio.sleep(0.1)

    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Получаем пользователя снова
        user2 = await repo.get_or_create_user(telegram_id=12345, username="testuser")
        last_seen2 = user2.last_seen

        # last_seen должен обновиться
        assert last_seen2 > last_seen1


@pytest.mark.asyncio
async def test_get_or_create_user_updates_username(test_session_factory: Any) -> None:
    """Тест: get_or_create_user обновляет username если он изменился."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Создаем пользователя с одним username
        await repo.get_or_create_user(telegram_id=12345, username="old_username")

    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Обновляем username
        user = await repo.get_or_create_user(telegram_id=12345, username="new_username")

        assert user.username == "new_username"


@pytest.mark.asyncio
async def test_get_or_create_user_updates_names(test_session_factory: Any) -> None:
    """Тест: get_or_create_user обновляет first_name и last_name если они изменились."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Создаем пользователя
        await repo.get_or_create_user(telegram_id=12345, first_name="OldFirst", last_name="OldLast")

    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Обновляем имена
        user = await repo.get_or_create_user(
            telegram_id=12345, first_name="NewFirst", last_name="NewLast"
        )

        assert user.first_name == "NewFirst"
        assert user.last_name == "NewLast"


@pytest.mark.asyncio
async def test_get_or_create_user_with_none_values(test_session_factory: Any) -> None:
    """Тест: get_or_create_user работает с None значениями."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        user = await repo.get_or_create_user(
            telegram_id=12345,
            username=None,
            first_name=None,
            last_name=None,
            language_code=None,
        )

        assert user.telegram_id == 12345
        assert user.username is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.language_code is None
        assert user.is_active is True


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_returns_user(test_session_factory: Any) -> None:
    """Тест: get_user_by_telegram_id возвращает пользователя."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Создаем пользователя
        await repo.get_or_create_user(telegram_id=12345, username="testuser")

    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Получаем пользователя
        user = await repo.get_user_by_telegram_id(12345)

        assert user is not None
        assert user.telegram_id == 12345
        assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_returns_none(test_session_factory: Any) -> None:
    """Тест: get_user_by_telegram_id возвращает None если пользователь не найден."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        user = await repo.get_user_by_telegram_id(99999)

        assert user is None


@pytest.mark.asyncio
async def test_update_last_seen(test_session_factory: Any) -> None:
    """Тест: update_last_seen обновляет время последнего взаимодействия."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Создаем пользователя
        user = await repo.get_or_create_user(telegram_id=12345, username="testuser")
        original_last_seen = user.last_seen

    # Ждем немного
    import asyncio

    await asyncio.sleep(0.1)

    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Обновляем last_seen
        await repo.update_last_seen(12345)

    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Проверяем, что last_seen обновился
        updated_user = await repo.get_user_by_telegram_id(12345)
        assert updated_user is not None
        assert updated_user.last_seen > original_last_seen


@pytest.mark.asyncio
async def test_get_active_users_count(test_session_factory: Any) -> None:
    """Тест: get_active_users_count возвращает количество активных пользователей."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Создаем несколько пользователей
        await repo.get_or_create_user(telegram_id=1, username="user1")
        await repo.get_or_create_user(telegram_id=2, username="user2")
        await repo.get_or_create_user(telegram_id=3, username="user3")

    async with test_session_factory() as session:
        repo = UserRepository(session)

        count = await repo.get_active_users_count()

        assert count == 3


@pytest.mark.asyncio
async def test_get_active_users_count_only_active(test_session_factory: Any) -> None:
    """Тест: get_active_users_count считает только активных пользователей."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        # Создаем активного пользователя
        await repo.get_or_create_user(telegram_id=1, username="user1")

        # Создаем неактивного пользователя вручную
        user2 = User(
            telegram_id=2,
            username="user2",
            is_active=False,
        )
        session.add(user2)
        await session.commit()

    async with test_session_factory() as session:
        repo = UserRepository(session)

        count = await repo.get_active_users_count()

        # Должен считать только активного пользователя
        assert count == 1


@pytest.mark.asyncio
async def test_get_active_users_count_empty(test_session_factory: Any) -> None:
    """Тест: get_active_users_count возвращает 0 если нет пользователей."""
    async with test_session_factory() as session:
        repo = UserRepository(session)

        count = await repo.get_active_users_count()

        assert count == 0
