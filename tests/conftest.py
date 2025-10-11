from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.dialogue_manager import DialogueManager
from src.bot.llm_client import LLMClient


@pytest.fixture
def dialogue_manager() -> DialogueManager:
    """Создает DialogueManager для тестов"""
    return DialogueManager(max_history=20)


@pytest.fixture
def mock_llm_client() -> Mock:
    """Создает мокированный LLMClient"""
    mock = Mock(spec=LLMClient)
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
