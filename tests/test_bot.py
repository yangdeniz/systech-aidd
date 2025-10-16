import pytest

from src.bot.bot import TelegramBot


@pytest.mark.asyncio
async def test_bot_initialization(telegram_bot, message_handler, command_handler) -> None:
    """Тест инициализации TelegramBot"""
    assert telegram_bot.message_handler == message_handler
    assert telegram_bot.command_handler == command_handler
    assert telegram_bot.bot is not None
    assert telegram_bot.dp is not None
    assert telegram_bot.session_factory is not None


@pytest.mark.asyncio
async def test_cmd_start(telegram_bot, mock_message) -> None:
    """Тест команды /start"""
    await telegram_bot.cmd_start(mock_message)

    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "HomeGuru" in args[0]


@pytest.mark.asyncio
async def test_cmd_help(telegram_bot, mock_message) -> None:
    """Тест команды /help"""
    await telegram_bot.cmd_help(mock_message)

    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "Справка" in args[0]


@pytest.mark.asyncio
async def test_cmd_role(telegram_bot, mock_message) -> None:
    """Тест команды /role"""
    await telegram_bot.cmd_role(mock_message)

    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "HomeGuru" in args[0]
    assert "дизайн" in args[0] or "интерьер" in args[0]


@pytest.mark.asyncio
async def test_cmd_reset(telegram_bot, dialogue_manager, mock_message) -> None:
    """Тест команды /reset"""
    # Добавляем историю
    await dialogue_manager.add_message(12345, "user", "test")

    await telegram_bot.cmd_reset(mock_message)

    # Проверяем что история очищена
    history = await dialogue_manager.get_history(12345)
    assert len(history) == 0
    mock_message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_success(
    telegram_bot,
    dialogue_manager,
    mock_llm_client,
    mock_message,
) -> None:
    """Тест успешной обработки сообщения"""
    await telegram_bot.handle_message(mock_message)

    # Проверяем что сообщение добавлено в историю
    history = await dialogue_manager.get_history(12345)
    assert len(history) == 2  # user + assistant

    # Проверяем что LLM был вызван
    mock_llm_client.get_response.assert_called_once()

    # Проверяем что ответ отправлен
    assert mock_message.answer.call_count == 1


@pytest.mark.asyncio
async def test_handle_message_error(telegram_bot, mock_llm_client, mock_message) -> None:
    """Тест обработки ошибки при обработке сообщения"""
    # Заставляем LLM выбросить ошибку
    mock_llm_client.get_response.side_effect = Exception("LLM Error")

    await telegram_bot.handle_message(mock_message)

    # Проверяем что отправлено сообщение об ошибке
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "ошибка" in args[0].lower()


@pytest.mark.asyncio
async def test_cmd_start_no_user(telegram_bot, mock_message) -> None:
    """Тест команды /start без пользователя"""
    mock_message.from_user = None

    await telegram_bot.cmd_start(mock_message)

    # Не должно быть вызовов answer
    mock_message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_no_text(telegram_bot, mock_message) -> None:
    """Тест обработки сообщения без текста"""
    mock_message.text = None

    await telegram_bot.handle_message(mock_message)

    # Ответ не должен быть отправлен
    mock_message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_photo(telegram_bot, message_handler_with_media, mock_message) -> None:
    """Тест обработки фото от пользователя."""
    from unittest.mock import AsyncMock, Mock

    # Create a new bot with media-enabled handler

    bot = TelegramBot(
        telegram_bot.bot.token,
        message_handler_with_media,
        telegram_bot.command_handler,
        telegram_bot.session_factory,
    )

    # Arrange - мок сообщения с фото
    mock_photo_message = AsyncMock()
    mock_photo_message.from_user = Mock()
    mock_photo_message.from_user.id = 12345
    mock_photo_message.from_user.username = "testuser"
    mock_photo_message.from_user.first_name = "Test"
    mock_photo_message.from_user.last_name = "User"
    mock_photo_message.from_user.language_code = "en"

    # Мок фото (список размеров, берем последнее - самое большое)
    mock_photo = Mock()
    mock_photo.file_id = "photo_file_id_123"
    mock_photo_message.photo = [mock_photo]
    mock_photo_message.caption = "Что на этом фото?"
    mock_photo_message.answer = AsyncMock()

    # Act
    await bot.handle_photo(mock_photo_message)

    # Assert - проверяем что ответ был отправлен
    mock_photo_message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_photo_without_caption(telegram_bot, message_handler_with_media) -> None:
    """Тест обработки фото без подписи."""
    from unittest.mock import AsyncMock, Mock


    bot = TelegramBot(
        telegram_bot.bot.token,
        message_handler_with_media,
        telegram_bot.command_handler,
        telegram_bot.session_factory,
    )

    # Arrange - фото без caption
    mock_photo_message = AsyncMock()
    mock_photo_message.from_user = Mock()
    mock_photo_message.from_user.id = 12345
    mock_photo_message.from_user.username = "testuser"
    mock_photo_message.from_user.first_name = "Test"
    mock_photo_message.from_user.last_name = "User"
    mock_photo_message.from_user.language_code = "en"

    mock_photo = Mock()
    mock_photo.file_id = "photo_file_id_456"
    mock_photo_message.photo = [mock_photo]
    mock_photo_message.caption = None
    mock_photo_message.answer = AsyncMock()

    # Act
    await bot.handle_photo(mock_photo_message)

    # Assert
    mock_photo_message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_photo_no_user(telegram_bot, message_handler_with_media) -> None:
    """Тест обработки фото без пользователя."""
    from unittest.mock import AsyncMock, Mock


    bot = TelegramBot(
        telegram_bot.bot.token,
        message_handler_with_media,
        telegram_bot.command_handler,
        telegram_bot.session_factory,
    )

    # Arrange - сообщение без from_user
    mock_photo_message = AsyncMock()
    mock_photo_message.from_user = None
    mock_photo_message.photo = [Mock(file_id="test")]
    mock_photo_message.answer = AsyncMock()

    # Act
    await bot.handle_photo(mock_photo_message)

    # Assert - не должно быть ответа
    mock_photo_message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_photo_error(telegram_bot, message_handler_with_media) -> None:
    """Тест обработки ошибки при обработке фото."""
    from unittest.mock import AsyncMock, Mock


    # Arrange - message_handler выбросит ошибку
    message_handler_with_media.handle_photo_message = AsyncMock(
        side_effect=Exception("Photo processing error")
    )

    bot = TelegramBot(
        telegram_bot.bot.token,
        message_handler_with_media,
        telegram_bot.command_handler,
        telegram_bot.session_factory,
    )

    mock_photo_message = AsyncMock()
    mock_photo_message.from_user = Mock()
    mock_photo_message.from_user.id = 12345
    mock_photo_message.from_user.username = "testuser"
    mock_photo_message.from_user.first_name = "Test"
    mock_photo_message.from_user.last_name = "User"
    mock_photo_message.from_user.language_code = "en"
    mock_photo_message.photo = [Mock(file_id="photo_id")]
    mock_photo_message.caption = "Test"
    mock_photo_message.answer = AsyncMock()

    # Act
    await bot.handle_photo(mock_photo_message)

    # Assert - должно быть отправлено сообщение об ошибке
    mock_photo_message.answer.assert_called_once()
    args = mock_photo_message.answer.call_args[0]
    assert "ошибка" in args[0].lower()


@pytest.mark.asyncio
async def test_handle_voice(telegram_bot, message_handler_with_media) -> None:
    """Тест обработки голосового сообщения от пользователя."""
    from unittest.mock import AsyncMock, Mock


    bot = TelegramBot(
        telegram_bot.bot.token,
        message_handler_with_media,
        telegram_bot.command_handler,
        telegram_bot.session_factory,
    )

    # Arrange - мок сообщения с голосовым
    mock_voice_message = AsyncMock()
    mock_voice_message.from_user = Mock()
    mock_voice_message.from_user.id = 12345
    mock_voice_message.from_user.username = "testuser"
    mock_voice_message.from_user.first_name = "Test"
    mock_voice_message.from_user.last_name = "User"
    mock_voice_message.from_user.language_code = "en"

    # Мок голосового сообщения
    mock_voice = Mock()
    mock_voice.file_id = "voice_file_id_123"
    mock_voice_message.voice = mock_voice
    mock_voice_message.answer = AsyncMock()

    # Act
    await bot.handle_voice(mock_voice_message)

    # Assert - проверяем что ответ был отправлен
    mock_voice_message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_voice_no_user(telegram_bot, message_handler_with_media) -> None:
    """Тест обработки голосового сообщения без пользователя."""
    from unittest.mock import AsyncMock, Mock


    bot = TelegramBot(
        telegram_bot.bot.token,
        message_handler_with_media,
        telegram_bot.command_handler,
        telegram_bot.session_factory,
    )

    # Arrange - сообщение без from_user
    mock_voice_message = AsyncMock()
    mock_voice_message.from_user = None
    mock_voice_message.voice = Mock(file_id="test")
    mock_voice_message.answer = AsyncMock()

    # Act
    await bot.handle_voice(mock_voice_message)

    # Assert - не должно быть ответа
    mock_voice_message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_voice_error(telegram_bot, message_handler_with_media) -> None:
    """Тест обработки ошибки при обработке голосового сообщения."""
    from unittest.mock import AsyncMock, Mock


    # Arrange - message_handler выбросит ошибку
    message_handler_with_media.handle_voice_message = AsyncMock(
        side_effect=Exception("Voice processing error")
    )

    bot = TelegramBot(
        telegram_bot.bot.token,
        message_handler_with_media,
        telegram_bot.command_handler,
        telegram_bot.session_factory,
    )

    mock_voice_message = AsyncMock()
    mock_voice_message.from_user = Mock()
    mock_voice_message.from_user.id = 12345
    mock_voice_message.from_user.username = "testuser"
    mock_voice_message.from_user.first_name = "Test"
    mock_voice_message.from_user.last_name = "User"
    mock_voice_message.from_user.language_code = "en"
    mock_voice_message.voice = Mock(file_id="voice_id")
    mock_voice_message.answer = AsyncMock()

    # Act
    await bot.handle_voice(mock_voice_message)

    # Assert - должно быть отправлено сообщение об ошибке
    mock_voice_message.answer.assert_called_once()
    args = mock_voice_message.answer.call_args[0]
    assert "ошибка" in args[0].lower()
