from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.command_handler import CommandHandler
from src.bot.dialogue_manager import DialogueManager
from src.bot.interfaces import DialogueStorage, LLMProvider, MediaProvider
from src.bot.message_handler import MessageHandler


@pytest.fixture
def dialogue_manager() -> DialogueStorage:
    """Создает DialogueManager для тестов"""
    return DialogueManager(max_history=20)


@pytest.fixture
def mock_llm_client() -> LLMProvider:
    """Создает мокированный LLMProvider"""
    mock = Mock(spec=LLMProvider)
    mock.get_response.return_value = "Test response from LLM"
    return mock


@pytest.fixture
def message_handler(
    mock_llm_client: LLMProvider, dialogue_manager: DialogueStorage
) -> MessageHandler:
    """Создает MessageHandler для тестов"""
    return MessageHandler(mock_llm_client, dialogue_manager)


@pytest.fixture
def command_handler(dialogue_manager: DialogueStorage) -> CommandHandler:
    """Создает CommandHandler для тестов"""
    return CommandHandler(dialogue_manager)


@pytest.fixture
def mock_message() -> AsyncMock:
    """Создает мокированное Telegram Message"""
    message = AsyncMock()
    message.from_user = Mock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.text = "Test message"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_bot_token() -> str:
    """Возвращает тестовый токен бота"""
    return "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"


@pytest.fixture
def mock_media_provider() -> MediaProvider:
    """Создает мокированный MediaProvider"""
    mock = AsyncMock(spec=MediaProvider)
    mock.download_photo.return_value = b"fake_image_bytes"
    mock.photo_to_base64.return_value = "fake_base64_string"
    mock.download_audio.return_value = b"fake_audio_bytes"
    mock.transcribe_audio.return_value = "Fake transcribed text"
    return mock


@pytest.fixture
def message_handler_with_media(
    mock_llm_client: LLMProvider,
    dialogue_manager: DialogueStorage,
    mock_media_provider: MediaProvider,
) -> MessageHandler:
    """Создает MessageHandler с MediaProvider для тестов"""
    return MessageHandler(mock_llm_client, dialogue_manager, media_provider=mock_media_provider)
