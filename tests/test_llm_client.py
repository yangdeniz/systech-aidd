from unittest.mock import Mock, patch

import pytest

from src.bot.llm_client import LLMClient


def test_llm_client_initialization():
    """Тест инициализации LLMClient"""
    client = LLMClient(api_key="test_key", model="test_model", system_prompt="Test prompt")

    assert client.model == "test_model"
    assert client.system_prompt == "Test prompt"


def test_llm_client_adds_system_prompt():
    """Тест добавления system prompt в начало сообщений"""
    with patch("src.bot.llm_client.OpenAI") as mock_openai:
        # Настраиваем мок
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Создаем клиент и вызываем метод
        client = LLMClient("key", "model", "System prompt")
        messages = [{"role": "user", "content": "Hello"}]
        response = client.get_response(messages)

        # Проверяем, что system prompt был добавлен
        call_args = mock_client.chat.completions.create.call_args
        sent_messages = call_args.kwargs["messages"]

        assert sent_messages[0]["role"] == "system"
        assert sent_messages[0]["content"] == "System prompt"
        assert sent_messages[1]["role"] == "user"
        assert sent_messages[1]["content"] == "Hello"
        assert response == "Test response"


def test_llm_client_error_handling():
    """Тест обработки ошибок API"""
    with patch("src.bot.llm_client.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        client = LLMClient("key", "model", "prompt")
        messages = [{"role": "user", "content": "test"}]

        with pytest.raises(Exception, match="API Error"):
            client.get_response(messages)


def test_llm_client_empty_response():
    """Тест пустого ответа от LLM"""
    with patch("src.bot.llm_client.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=None))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = LLMClient("key", "model", "prompt")
        messages = [{"role": "user", "content": "test"}]

        with pytest.raises(ValueError, match="empty response"):
            client.get_response(messages)


def test_llm_client_with_empty_messages():
    """Тест с пустым списком сообщений"""
    with patch("src.bot.llm_client.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = LLMClient("key", "model", "System prompt")
        messages = []
        response = client.get_response(messages)

        # Проверяем, что был отправлен только system prompt
        call_args = mock_client.chat.completions.create.call_args
        sent_messages = call_args.kwargs["messages"]
        assert len(sent_messages) == 1
        assert sent_messages[0]["role"] == "system"
        assert response == "Response"
