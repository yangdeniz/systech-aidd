from unittest.mock import Mock, patch

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
