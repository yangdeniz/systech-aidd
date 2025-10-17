"""
Тесты для Chat API endpoints.

Тестируем все chat endpoints: отправку сообщений,
получение истории и очистку истории.

Все эндпоинты теперь требуют JWT авторизации.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# Для тестов мы будем патчить chat_service в main модуле
@pytest.fixture
def mock_chat_service():
    """Mock ChatService."""
    mock = MagicMock()
    mock.process_message = AsyncMock(return_value=("Test response", None))
    mock.dialogue_manager = MagicMock()
    mock.dialogue_manager.get_history = AsyncMock(return_value=[])
    mock.dialogue_manager.clear_history = AsyncMock()
    return mock


@pytest.fixture
def client_with_chat(mock_chat_service, admin_user_token):
    """Test client с включенным chat service и авторизацией."""
    from src.api.main import app

    with patch("src.api.main.chat_service", mock_chat_service):
        client = TestClient(app)
        # Добавляем токен в заголовки по умолчанию
        client.headers = {"Authorization": f"Bearer {admin_user_token}"}
        yield client


class TestChatMessageEndpoint:
    """Тесты для /api/chat/message endpoint."""

    def test_send_message_normal_mode(self, client_with_chat, mock_chat_service):
        """Тестируем отправку сообщения в normal режиме."""
        mock_chat_service.process_message.return_value = ("Hello! How can I help you?", None)

        response = client_with_chat.post(
            "/api/chat/message",
            json={"message": "Hello", "mode": "normal"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello! How can I help you?"
        assert data["sql_query"] is None
        assert "timestamp" in data

        # Проверяем что ChatService был вызван
        mock_chat_service.process_message.assert_called_once()
        call_args = mock_chat_service.process_message.call_args
        assert call_args[1]["message"] == "Hello"
        assert call_args[1]["mode"] == "normal"

    def test_send_message_admin_mode(self, client_with_chat, mock_chat_service):
        """Тестируем отправку сообщения в admin режиме с SQL."""
        sql_query = "SELECT COUNT(*) FROM users"
        mock_chat_service.process_message.return_value = ("We have 42 users.", sql_query)

        response = client_with_chat.post(
            "/api/chat/message",
            json={"message": "How many users?", "mode": "admin"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "We have 42 users."
        assert data["sql_query"] == sql_query
        assert "timestamp" in data

    def test_send_message_empty(self, client_with_chat):
        """Тестируем отправку пустого сообщения (валидация)."""
        response = client_with_chat.post(
            "/api/chat/message",
            json={"message": "", "mode": "normal"},
        )

        # Pydantic должен отклонить пустую строку из-за min_length=1
        assert response.status_code == 422

    def test_send_message_invalid_mode(self, client_with_chat):
        """Тестируем отправку с невалидным режимом."""
        response = client_with_chat.post(
            "/api/chat/message",
            json={"message": "Hello", "mode": "invalid_mode"},
        )

        # Pydantic должен отклонить невалидный Literal
        assert response.status_code == 422

    def test_send_message_missing_required_fields(self, client_with_chat):
        """Тестируем отправку без обязательных полей (только mode опциональный)."""
        response = client_with_chat.post("/api/chat/message", json={})

        # Должна быть ошибка валидации, т.к. message обязателен
        assert response.status_code == 422

    def test_send_message_when_chat_service_unavailable(self, client_with_chat):
        """Тестируем ошибку когда chat service недоступен."""
        with patch("src.api.main.chat_service", None):
            response = client_with_chat.post(
                "/api/chat/message",
                json={"message": "Hello", "mode": "normal"},
            )

            assert response.status_code == 503
            assert "unavailable" in response.json()["detail"].lower()

    def test_send_message_chat_service_error(self, client_with_chat, mock_chat_service):
        """Тестируем обработку ошибки в ChatService."""
        mock_chat_service.process_message.side_effect = Exception("LLM connection failed")

        response = client_with_chat.post(
            "/api/chat/message",
            json={"message": "Hello", "mode": "normal"},
        )

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


class TestChatHistoryEndpoint:
    """Тесты для /api/chat/history endpoint."""

    def test_get_history_empty(self, client_with_chat, mock_chat_service):
        """Тестируем получение пустой истории."""
        mock_chat_service.dialogue_manager.get_history.return_value = []

        response = client_with_chat.get("/api/chat/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_history_with_messages(self, client_with_chat, mock_chat_service):
        """Тестируем получение истории с сообщениями."""
        mock_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you?"},
            {"role": "user", "content": "What is the weather?"},
            {"role": "assistant", "content": "I'm a design assistant, not a weather service."},
        ]
        mock_chat_service.dialogue_manager.get_history.return_value = mock_history

        response = client_with_chat.get("/api/chat/history")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert data[0]["role"] == "user"
        assert data[0]["content"] == "Hello"
        assert "timestamp" in data[0]

    def test_get_history_when_chat_service_unavailable(self, client_with_chat):
        """Тестируем ошибку когда chat service недоступен."""
        with patch("src.api.main.chat_service", None):
            response = client_with_chat.get("/api/chat/history")

            assert response.status_code == 503

    def test_get_history_error(self, client_with_chat, mock_chat_service):
        """Тестируем обработку ошибки при получении истории."""
        mock_chat_service.dialogue_manager.get_history.side_effect = Exception("DB error")

        response = client_with_chat.get("/api/chat/history")

        assert response.status_code == 500


class TestClearHistoryEndpoint:
    """Тесты для /api/chat/clear endpoint."""

    def test_clear_history_success(self, client_with_chat, mock_chat_service):
        """Тестируем успешную очистку истории."""
        response = client_with_chat.post("/api/chat/clear")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "history cleared"

        # Проверяем что метод был вызван
        mock_chat_service.dialogue_manager.clear_history.assert_called_once()

    def test_clear_history_when_chat_service_unavailable(self, client_with_chat):
        """Тестируем ошибку когда chat service недоступен."""
        with patch("src.api.main.chat_service", None):
            response = client_with_chat.post("/api/chat/clear")

            assert response.status_code == 503

    def test_clear_history_error(self, client_with_chat, mock_chat_service):
        """Тестируем обработку ошибки при очистке истории."""
        mock_chat_service.dialogue_manager.clear_history.side_effect = Exception("DB error")

        response = client_with_chat.post("/api/chat/clear")

        assert response.status_code == 500
