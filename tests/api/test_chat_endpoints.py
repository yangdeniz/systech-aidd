"""
Тесты для Chat API endpoints.

Тестируем все chat endpoints: аутентификацию, отправку сообщений,
получение истории и очистку истории.
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
def client_with_chat(mock_chat_service):
    """Test client с включенным chat service."""
    from src.api.main import app

    with patch("src.api.main.chat_service", mock_chat_service):
        client = TestClient(app)
        yield client


class TestAuthEndpoint:
    """Тесты для /api/chat/auth endpoint."""

    def test_auth_with_correct_password(self, client_with_chat):
        """Тестируем аутентификацию с корректным паролем."""
        response = client_with_chat.post(
            "/api/chat/auth",
            json={"password": "admin123"},  # default ADMIN_PASSWORD
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "expires_at" in data
        assert len(data["token"]) > 0

    def test_auth_with_incorrect_password(self, client_with_chat):
        """Тестируем отклонение неверного пароля."""
        response = client_with_chat.post("/api/chat/auth", json={"password": "wrong_password"})

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_auth_with_empty_password(self, client_with_chat):
        """Тестируем отклонение пустого пароля."""
        response = client_with_chat.post("/api/chat/auth", json={"password": ""})

        # Pydantic валидация отклоняет пустую строку (min_length=1)
        assert response.status_code == 422

    def test_auth_missing_password_field(self, client_with_chat):
        """Тестируем ошибку при отсутствии поля password."""
        response = client_with_chat.post("/api/chat/auth", json={})

        assert response.status_code == 422  # Validation error


class TestChatMessageEndpoint:
    """Тесты для /api/chat/message endpoint."""

    def test_send_message_normal_mode(self, client_with_chat, mock_chat_service):
        """Тестируем отправку сообщения в normal режиме."""
        mock_chat_service.process_message.return_value = ("Hello! How can I help you?", None)

        response = client_with_chat.post(
            "/api/chat/message",
            json={"message": "Hello", "mode": "normal", "session_id": "test-session-123"},
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
            json={"message": "How many users?", "mode": "admin", "session_id": "test-session-456"},
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
            json={"message": "", "mode": "normal", "session_id": "test-session-789"},
        )

        # Pydantic должен отклонить пустую строку из-за min_length=1
        assert response.status_code == 422

    def test_send_message_invalid_mode(self, client_with_chat):
        """Тестируем отправку с невалидным режимом."""
        response = client_with_chat.post(
            "/api/chat/message",
            json={"message": "Hello", "mode": "invalid_mode", "session_id": "test-session"},
        )

        # Pydantic должен отклонить невалидный Literal
        assert response.status_code == 422

    def test_send_message_missing_required_fields(self, client_with_chat):
        """Тестируем отправку без обязательных полей."""
        response = client_with_chat.post("/api/chat/message", json={"message": "Hello"})

        assert response.status_code == 422

    def test_send_message_when_chat_service_unavailable(self, client_with_chat):
        """Тестируем ошибку когда chat service недоступен."""
        with patch("src.api.main.chat_service", None):
            response = client_with_chat.post(
                "/api/chat/message",
                json={"message": "Hello", "mode": "normal", "session_id": "test"},
            )

            assert response.status_code == 503
            assert "unavailable" in response.json()["detail"].lower()

    def test_send_message_chat_service_error(self, client_with_chat, mock_chat_service):
        """Тестируем обработку ошибки в ChatService."""
        mock_chat_service.process_message.side_effect = Exception("LLM connection failed")

        response = client_with_chat.post(
            "/api/chat/message",
            json={"message": "Hello", "mode": "normal", "session_id": "test"},
        )

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


class TestChatHistoryEndpoint:
    """Тесты для /api/chat/history endpoint."""

    def test_get_history_empty(self, client_with_chat, mock_chat_service):
        """Тестируем получение пустой истории."""
        mock_chat_service.dialogue_manager.get_history.return_value = []

        response = client_with_chat.get("/api/chat/history?session_id=test-session")

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

        response = client_with_chat.get("/api/chat/history?session_id=test-session")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert data[0]["role"] == "user"
        assert data[0]["content"] == "Hello"
        assert "timestamp" in data[0]

    def test_get_history_missing_session_id(self, client_with_chat):
        """Тестируем ошибку при отсутствии session_id."""
        response = client_with_chat.get("/api/chat/history")

        assert response.status_code == 422

    def test_get_history_when_chat_service_unavailable(self, client_with_chat):
        """Тестируем ошибку когда chat service недоступен."""
        with patch("src.api.main.chat_service", None):
            response = client_with_chat.get("/api/chat/history?session_id=test")

            assert response.status_code == 503

    def test_get_history_error(self, client_with_chat, mock_chat_service):
        """Тестируем обработку ошибки при получении истории."""
        mock_chat_service.dialogue_manager.get_history.side_effect = Exception("DB error")

        response = client_with_chat.get("/api/chat/history?session_id=test")

        assert response.status_code == 500


class TestClearHistoryEndpoint:
    """Тесты для /api/chat/clear endpoint."""

    def test_clear_history_success(self, client_with_chat, mock_chat_service):
        """Тестируем успешную очистку истории."""
        response = client_with_chat.post("/api/chat/clear", json={"session_id": "test-session"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "history cleared"
        assert data["session_id"] == "test-session"

        # Проверяем что метод был вызван
        mock_chat_service.dialogue_manager.clear_history.assert_called_once()

    def test_clear_history_missing_session_id(self, client_with_chat):
        """Тестируем ошибку при отсутствии session_id."""
        response = client_with_chat.post("/api/chat/clear", json={})

        assert response.status_code == 422

    def test_clear_history_when_chat_service_unavailable(self, client_with_chat):
        """Тестируем ошибку когда chat service недоступен."""
        with patch("src.api.main.chat_service", None):
            response = client_with_chat.post("/api/chat/clear", json={"session_id": "test"})

            assert response.status_code == 503

    def test_clear_history_error(self, client_with_chat, mock_chat_service):
        """Тестируем обработку ошибки при очистке истории."""
        mock_chat_service.dialogue_manager.clear_history.side_effect = Exception("DB error")

        response = client_with_chat.post("/api/chat/clear", json={"session_id": "test"})

        assert response.status_code == 500


class TestSessionIdMapping:
    """Тесты для маппинга session_id → user_id."""

    def test_consistent_user_id_for_session(self, client_with_chat, mock_chat_service):
        """Тестируем что один session_id всегда получает один user_id."""
        session_id = "consistent-session"

        # Отправляем несколько сообщений
        for i in range(3):
            client_with_chat.post(
                "/api/chat/message",
                json={"message": f"Message {i}", "mode": "normal", "session_id": session_id},
            )

        # Проверяем что все вызовы использовали один user_id
        calls = mock_chat_service.process_message.call_args_list
        user_ids = [call[1]["user_id"] for call in calls]

        # Все user_id должны быть одинаковыми
        assert len(set(user_ids)) == 1
        # И должны быть отрицательными (веб-пользователи)
        assert user_ids[0] < 0

    def test_different_user_ids_for_different_sessions(self, client_with_chat, mock_chat_service):
        """Тестируем что разные session_id получают разные user_id."""
        session_ids = ["session-1", "session-2", "session-3"]

        for session_id in session_ids:
            client_with_chat.post(
                "/api/chat/message",
                json={"message": "Test", "mode": "normal", "session_id": session_id},
            )

        # Проверяем что все вызовы использовали разные user_id
        calls = mock_chat_service.process_message.call_args_list
        user_ids = [call[1]["user_id"] for call in calls]

        # Все user_id должны быть уникальными
        assert len(set(user_ids)) == 3
