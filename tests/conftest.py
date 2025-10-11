from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.dialogue_manager import DialogueManager
from src.bot.interfaces import DialogueStorage, LLMProvider


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
