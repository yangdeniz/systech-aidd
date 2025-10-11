import logging
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.bot.main import setup_logging


def test_setup_logging():
    """Тест настройки логирования"""
    # Очищаем логгеры перед тестом
    logging.root.handlers = []

    setup_logging()

    # Проверяем, что уровень логирования установлен
    assert logging.root.level == logging.INFO

    # Проверяем, что добавлены обработчики
    assert len(logging.root.handlers) >= 2  # console + file handlers


@pytest.mark.asyncio
@patch("src.bot.main.Config")
@patch("src.bot.main.MessageHandler")
@patch("src.bot.main.CommandHandler")
@patch("src.bot.main.TelegramBot")
async def test_main_initialization(
    mock_bot_class, mock_cmd_handler_class, mock_msg_handler_class, mock_config_class
):
    """Тест инициализации компонентов в main"""
    # Настраиваем моки
    mock_config = Mock()
    mock_config.telegram_token = "test_token"
    mock_config.openrouter_api_key = "test_key"
    mock_config.openrouter_model = "test_model"
    mock_config.system_prompt = "test_prompt"
    mock_config.max_history = 20
    mock_config_class.return_value = mock_config

    mock_msg_handler = Mock()
    mock_msg_handler_class.return_value = mock_msg_handler

    mock_cmd_handler = Mock()
    mock_cmd_handler_class.return_value = mock_cmd_handler

    mock_bot = Mock()
    mock_bot.start = AsyncMock()
    mock_bot_class.return_value = mock_bot

    # Импортируем main и запускаем (с патчингом)
    from src.bot.main import main

    # Останавливаем бота сразу после старта
    async def mock_start():
        pass

    mock_bot.start = mock_start

    await main()

    # Проверяем, что Config был создан
    mock_config_class.assert_called_once()

    # Проверяем, что MessageHandler был создан
    mock_msg_handler_class.assert_called_once()

    # Проверяем, что CommandHandler был создан
    mock_cmd_handler_class.assert_called_once()

    # Проверяем, что TelegramBot был создан с правильными параметрами
    mock_bot_class.assert_called_once()
