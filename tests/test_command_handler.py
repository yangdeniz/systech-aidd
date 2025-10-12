"""Тесты для CommandHandler."""

from unittest.mock import Mock

import pytest

from src.bot.command_handler import CommandHandler
from src.bot.interfaces import DialogueStorage


@pytest.fixture
def mock_dialogue_storage() -> DialogueStorage:
    """Мок хранилища диалогов."""
    return Mock(spec=DialogueStorage)


@pytest.fixture
def command_handler(mock_dialogue_storage: DialogueStorage) -> CommandHandler:
    """Фикстура CommandHandler."""
    return CommandHandler(mock_dialogue_storage)


def test_command_handler_get_role_message(command_handler: CommandHandler) -> None:
    """Тест получения описания роли HomeGuru."""
    # Act
    message = command_handler.get_role_message()

    # Assert
    assert "HomeGuru" in message
    assert "дизайнер" in message or "дизайн" in message
    assert "интерьер" in message
    assert len(message) > 50  # Должно быть содержательное сообщение


def test_start_message_with_homeguru_context(command_handler: CommandHandler) -> None:
    """Тест приветственного сообщения с контекстом HomeGuru."""
    # Act
    message = command_handler.get_start_message()

    # Assert
    assert "HomeGuru" in message
    assert "/role" in message
    assert "дизайн" in message or "интерьер" in message
    assert "/start" in message
    assert "/help" in message
    assert "/reset" in message


def test_help_message_includes_role_command(command_handler: CommandHandler) -> None:
    """Тест наличия команды /role в справке."""
    # Act
    message = command_handler.get_help_message()

    # Assert
    assert "/role" in message
    assert "/start" in message
    assert "/help" in message
    assert "/reset" in message


def test_help_message_includes_voice_support(command_handler: CommandHandler) -> None:
    """🔴 RED: Тест упоминания голосовых сообщений в справке."""
    # Act
    message = command_handler.get_help_message()

    # Assert - должно быть упоминание о голосовых/аудио сообщениях
    assert "голосов" in message.lower() or "аудио" in message.lower() or "voice" in message.lower()
