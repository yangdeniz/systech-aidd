import pytest

from src.bot.interfaces import DialogueStorage


@pytest.mark.asyncio
async def test_dialogue_manager_initialization(dialogue_manager: DialogueStorage) -> None:
    """Тест инициализации DialogueManager"""
    # DialogueManager успешно инициализирован (проверяем интерфейс)
    assert hasattr(dialogue_manager, "add_message")
    assert hasattr(dialogue_manager, "get_history")
    assert hasattr(dialogue_manager, "clear_history")


@pytest.mark.asyncio
async def test_add_message(
    dialogue_manager: DialogueStorage, test_users_mapping: dict[int, int]
) -> None:
    """Тест добавления сообщения в историю"""
    user_id = test_users_mapping[123]  # Получаем внутренний user.id
    await dialogue_manager.add_message(user_id, "user", "Hello")

    history = await dialogue_manager.get_history(user_id)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"  # Теперь простая строка для LLM API


@pytest.mark.asyncio
async def test_get_history_empty(dialogue_manager: DialogueStorage, test_session_factory) -> None:
    """Тест получения пустой истории"""
    from src.bot.repository import UserRepository

    # Создаем нового пользователя с telegram_id=999
    async with test_session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_or_create_user(
            telegram_id=999,
            username="emptyuser",
            first_name="Empty",
            last_name="User",
            language_code="en",
        )
        user_id = user.id

    history = await dialogue_manager.get_history(user_id)
    assert history == []


@pytest.mark.asyncio
async def test_max_history_limit(test_session_factory) -> None:  # type: ignore[no-untyped-def]
    """Тест ограничения количества сообщений"""
    from src.bot.dialogue_manager import DialogueManager
    from src.bot.repository import UserRepository

    # Создаем пользователя перед тестом и получаем его user.id
    async with test_session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_or_create_user(
            telegram_id=123,
            username="testuser123",
            first_name="Test",
            last_name="User",
            language_code="en",
        )
        user_id = user.id

    # Создаем DialogueManager с max_history=3
    dm = DialogueManager(session_factory=test_session_factory, max_history=3)

    # Добавляем 5 сообщений
    for i in range(5):
        await dm.add_message(user_id, "user", f"Message {i}")

    history = await dm.get_history(user_id)
    # Должны остаться только последние 3
    assert len(history) == 3
    assert history[0]["content"] == "Message 2"  # Простые строки
    assert history[2]["content"] == "Message 4"


@pytest.mark.asyncio
async def test_clear_history(
    dialogue_manager: DialogueStorage, test_users_mapping: dict[int, int]
) -> None:
    """Тест очистки истории (soft delete)"""
    user_id = test_users_mapping[123]
    await dialogue_manager.add_message(user_id, "user", "Hello")
    await dialogue_manager.add_message(user_id, "assistant", "Hi")

    await dialogue_manager.clear_history(user_id)
    history = await dialogue_manager.get_history(user_id)
    assert history == []


@pytest.mark.asyncio
async def test_multiple_users(
    dialogue_manager: DialogueStorage, test_users_mapping: dict[int, int]
) -> None:
    """Тест работы с несколькими пользователями"""
    user_id_1 = test_users_mapping[111]
    user_id_2 = test_users_mapping[222]

    await dialogue_manager.add_message(user_id_1, "user", "User 1 message")
    await dialogue_manager.add_message(user_id_2, "user", "User 2 message")

    history_1 = await dialogue_manager.get_history(user_id_1)
    history_2 = await dialogue_manager.get_history(user_id_2)

    assert len(history_1) == 1
    assert len(history_2) == 1
    assert history_1[0]["content"] == "User 1 message"  # Простые строки
    assert history_2[0]["content"] == "User 2 message"


@pytest.mark.asyncio
async def test_add_multimodal_message(
    dialogue_manager: DialogueStorage, test_users_mapping: dict[int, int]
) -> None:
    """Тест: добавление мультимодального сообщения с изображением."""
    from typing import Any

    user_id = test_users_mapping[123]

    # Мультимодальное сообщение с изображением
    multimodal_content: list[dict[str, Any]] = [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,fake_data"}},
    ]

    await dialogue_manager.add_message(user_id, "user", multimodal_content)

    history = await dialogue_manager.get_history(user_id)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert isinstance(history[0]["content"], list)
    assert history[0]["content"][0]["type"] == "text"
    assert history[0]["content"][1]["type"] == "image_url"


@pytest.mark.asyncio
async def test_mixed_text_and_multimodal_history(
    dialogue_manager: DialogueStorage, test_users_mapping: dict[int, int]
) -> None:
    """Тест: смешанная история с текстовыми и мультимодальными сообщениями."""
    from typing import Any

    user_id = test_users_mapping[123]

    # Обычное текстовое сообщение
    await dialogue_manager.add_message(user_id, "user", "Hello")
    await dialogue_manager.add_message(user_id, "assistant", "Hi there!")

    # Мультимодальное сообщение
    multimodal_content: list[dict[str, Any]] = [
        {"type": "text", "text": "Look at this photo"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,photo_data"}},
    ]
    await dialogue_manager.add_message(user_id, "user", multimodal_content)
    await dialogue_manager.add_message(user_id, "assistant", "Nice photo!")

    history = await dialogue_manager.get_history(user_id)
    assert len(history) == 4
    assert history[0]["content"] == "Hello"  # Простая строка
    assert history[1]["content"] == "Hi there!"  # Простая строка
    assert isinstance(history[2]["content"], list)  # Список для мультимодального
    assert history[3]["content"] == "Nice photo!"  # Простая строка
