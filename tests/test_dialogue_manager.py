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
async def test_add_message(dialogue_manager: DialogueStorage) -> None:
    """Тест добавления сообщения в историю"""
    await dialogue_manager.add_message(123, "user", "Hello")

    history = await dialogue_manager.get_history(123)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"  # Теперь простая строка для LLM API


@pytest.mark.asyncio
async def test_get_history_empty(dialogue_manager: DialogueStorage) -> None:
    """Тест получения пустой истории"""
    history = await dialogue_manager.get_history(999)
    assert history == []


@pytest.mark.asyncio
async def test_max_history_limit(test_session_factory) -> None:  # type: ignore[no-untyped-def]
    """Тест ограничения количества сообщений"""
    from src.bot.dialogue_manager import DialogueManager

    # Создаем DialogueManager с max_history=3
    dm = DialogueManager(session_factory=test_session_factory, max_history=3)

    # Добавляем 5 сообщений
    for i in range(5):
        await dm.add_message(123, "user", f"Message {i}")

    history = await dm.get_history(123)
    # Должны остаться только последние 3
    assert len(history) == 3
    assert history[0]["content"] == "Message 2"  # Простые строки
    assert history[2]["content"] == "Message 4"


@pytest.mark.asyncio
async def test_clear_history(dialogue_manager: DialogueStorage) -> None:
    """Тест очистки истории (soft delete)"""
    await dialogue_manager.add_message(123, "user", "Hello")
    await dialogue_manager.add_message(123, "assistant", "Hi")

    await dialogue_manager.clear_history(123)
    history = await dialogue_manager.get_history(123)
    assert history == []


@pytest.mark.asyncio
async def test_multiple_users(dialogue_manager: DialogueStorage) -> None:
    """Тест работы с несколькими пользователями"""
    await dialogue_manager.add_message(111, "user", "User 1 message")
    await dialogue_manager.add_message(222, "user", "User 2 message")

    history_1 = await dialogue_manager.get_history(111)
    history_2 = await dialogue_manager.get_history(222)

    assert len(history_1) == 1
    assert len(history_2) == 1
    assert history_1[0]["content"] == "User 1 message"  # Простые строки
    assert history_2[0]["content"] == "User 2 message"


@pytest.mark.asyncio
async def test_add_multimodal_message(dialogue_manager: DialogueStorage) -> None:
    """Тест: добавление мультимодального сообщения с изображением."""
    from typing import Any

    # Мультимодальное сообщение с изображением
    multimodal_content: list[dict[str, Any]] = [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,fake_data"}},
    ]

    await dialogue_manager.add_message(123, "user", multimodal_content)

    history = await dialogue_manager.get_history(123)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert isinstance(history[0]["content"], list)
    assert history[0]["content"][0]["type"] == "text"
    assert history[0]["content"][1]["type"] == "image_url"


@pytest.mark.asyncio
async def test_mixed_text_and_multimodal_history(dialogue_manager: DialogueStorage) -> None:
    """Тест: смешанная история с текстовыми и мультимодальными сообщениями."""
    from typing import Any

    # Обычное текстовое сообщение
    await dialogue_manager.add_message(123, "user", "Hello")
    await dialogue_manager.add_message(123, "assistant", "Hi there!")

    # Мультимодальное сообщение
    multimodal_content: list[dict[str, Any]] = [
        {"type": "text", "text": "Look at this photo"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,photo_data"}},
    ]
    await dialogue_manager.add_message(123, "user", multimodal_content)
    await dialogue_manager.add_message(123, "assistant", "Nice photo!")

    history = await dialogue_manager.get_history(123)
    assert len(history) == 4
    assert history[0]["content"] == "Hello"  # Простая строка
    assert history[1]["content"] == "Hi there!"  # Простая строка
    assert isinstance(history[2]["content"], list)  # Список для мультимодального
    assert history[3]["content"] == "Nice photo!"  # Простая строка
