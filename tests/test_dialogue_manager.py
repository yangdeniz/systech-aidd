from src.bot.dialogue_manager import DialogueManager


def test_dialogue_manager_initialization() -> None:
    """Тест инициализации DialogueManager"""
    dm = DialogueManager(max_history=20)
    assert dm.max_history == 20
    assert dm.dialogues == {}


def test_add_message() -> None:
    """Тест добавления сообщения в историю"""
    dm = DialogueManager(max_history=20)
    dm.add_message(123, "user", "Hello")

    history = dm.get_history(123)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"


def test_get_history_empty() -> None:
    """Тест получения пустой истории"""
    dm = DialogueManager(max_history=20)
    history = dm.get_history(999)
    assert history == []


def test_max_history_limit() -> None:
    """Тест ограничения количества сообщений"""
    dm = DialogueManager(max_history=3)

    # Добавляем 5 сообщений
    for i in range(5):
        dm.add_message(123, "user", f"Message {i}")

    history = dm.get_history(123)
    # Должны остаться только последние 3
    assert len(history) == 3
    assert history[0]["content"] == "Message 2"
    assert history[2]["content"] == "Message 4"


def test_clear_history() -> None:
    """Тест очистки истории"""
    dm = DialogueManager(max_history=20)
    dm.add_message(123, "user", "Hello")
    dm.add_message(123, "assistant", "Hi")

    dm.clear_history(123)
    history = dm.get_history(123)
    assert history == []


def test_multiple_users() -> None:
    """Тест работы с несколькими пользователями"""
    dm = DialogueManager(max_history=20)

    dm.add_message(111, "user", "User 1 message")
    dm.add_message(222, "user", "User 2 message")

    history_1 = dm.get_history(111)
    history_2 = dm.get_history(222)

    assert len(history_1) == 1
    assert len(history_2) == 1
    assert history_1[0]["content"] == "User 1 message"
    assert history_2[0]["content"] == "User 2 message"


def test_add_multimodal_message() -> None:
    """Тест: добавление мультимодального сообщения с изображением."""
    dm = DialogueManager(max_history=20)

    # Мультимодальное сообщение с изображением
    multimodal_content = [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,fake_data"}},
    ]

    dm.add_message(123, "user", multimodal_content)

    history = dm.get_history(123)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert isinstance(history[0]["content"], list)
    assert history[0]["content"][0]["type"] == "text"
    assert history[0]["content"][1]["type"] == "image_url"


def test_mixed_text_and_multimodal_history() -> None:
    """Тест: смешанная история с текстовыми и мультимодальными сообщениями."""
    dm = DialogueManager(max_history=20)

    # Обычное текстовое сообщение
    dm.add_message(123, "user", "Hello")
    dm.add_message(123, "assistant", "Hi there!")

    # Мультимодальное сообщение
    multimodal_content = [
        {"type": "text", "text": "Look at this photo"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,photo_data"}},
    ]
    dm.add_message(123, "user", multimodal_content)
    dm.add_message(123, "assistant", "Nice photo!")

    history = dm.get_history(123)
    assert len(history) == 4
    assert history[0]["content"] == "Hello"
    assert history[1]["content"] == "Hi there!"
    assert isinstance(history[2]["content"], list)
    assert history[3]["content"] == "Nice photo!"
