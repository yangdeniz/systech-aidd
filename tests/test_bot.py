import pytest

from src.bot.bot import TelegramBot


@pytest.mark.asyncio
async def test_bot_initialization(mock_bot_token, message_handler, command_handler):
    """Тест инициализации TelegramBot"""
    bot = TelegramBot(mock_bot_token, message_handler, command_handler)

    assert bot.message_handler == message_handler
    assert bot.command_handler == command_handler
    assert bot.bot is not None
    assert bot.dp is not None


@pytest.mark.asyncio
async def test_cmd_start(mock_bot_token, message_handler, command_handler, mock_message):
    """Тест команды /start"""
    bot = TelegramBot(mock_bot_token, message_handler, command_handler)

    await bot.cmd_start(mock_message)

    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "AI-ассистент" in args[0]


@pytest.mark.asyncio
async def test_cmd_help(mock_bot_token, message_handler, command_handler, mock_message):
    """Тест команды /help"""
    bot = TelegramBot(mock_bot_token, message_handler, command_handler)

    await bot.cmd_help(mock_message)

    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "Справка" in args[0]


@pytest.mark.asyncio
async def test_cmd_reset(
    mock_bot_token, message_handler, command_handler, dialogue_manager, mock_message
):
    """Тест команды /reset"""
    bot = TelegramBot(mock_bot_token, message_handler, command_handler)

    # Добавляем историю
    dialogue_manager.add_message(12345, "user", "test")

    await bot.cmd_reset(mock_message)

    # Проверяем что история очищена
    history = dialogue_manager.get_history(12345)
    assert len(history) == 0
    mock_message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_success(
    mock_bot_token,
    message_handler,
    command_handler,
    dialogue_manager,
    mock_llm_client,
    mock_message,
):
    """Тест успешной обработки сообщения"""
    bot = TelegramBot(mock_bot_token, message_handler, command_handler)

    await bot.handle_message(mock_message)

    # Проверяем что сообщение добавлено в историю
    history = dialogue_manager.get_history(12345)
    assert len(history) == 2  # user + assistant

    # Проверяем что LLM был вызван
    mock_llm_client.get_response.assert_called_once()

    # Проверяем что ответ отправлен
    assert mock_message.answer.call_count == 1


@pytest.mark.asyncio
async def test_handle_message_error(
    mock_bot_token, mock_llm_client, message_handler, command_handler, mock_message
):
    """Тест обработки ошибки при обработке сообщения"""
    # Заставляем LLM выбросить ошибку
    mock_llm_client.get_response.side_effect = Exception("LLM Error")

    bot = TelegramBot(mock_bot_token, message_handler, command_handler)

    await bot.handle_message(mock_message)

    # Проверяем что отправлено сообщение об ошибке
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "ошибка" in args[0].lower()


@pytest.mark.asyncio
async def test_cmd_start_no_user(mock_bot_token, message_handler, command_handler, mock_message):
    """Тест команды /start без пользователя"""
    bot = TelegramBot(mock_bot_token, message_handler, command_handler)
    mock_message.from_user = None

    await bot.cmd_start(mock_message)

    # Не должно быть вызовов answer
    mock_message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_no_text(
    mock_bot_token, message_handler, command_handler, mock_message
):
    """Тест обработки сообщения без текста"""
    bot = TelegramBot(mock_bot_token, message_handler, command_handler)
    mock_message.text = None

    await bot.handle_message(mock_message)

    # Ответ не должен быть отправлен
    mock_message.answer.assert_not_called()
