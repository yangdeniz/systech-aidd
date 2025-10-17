"""
Тесты для FastAPI endpoints.

Проверяет работу REST API для получения статистики дашборда.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


class TestStatsAPI:
    """Тесты для Stats API endpoints."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Создает тестовый клиент FastAPI."""
        return TestClient(app)

    def test_root_endpoint(self, client: TestClient) -> None:
        """Тест корневого endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "HomeGuru Stats API"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"

    def test_health_check(self, client: TestClient) -> None:
        """Тест health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_get_stats_default_period(self, client: TestClient) -> None:
        """Тест получения статистики с периодом по умолчанию (week)."""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()

        # Проверяем структуру ответа
        assert "metrics" in data
        assert "time_series" in data
        assert "recent_dialogues" in data
        assert "top_users" in data

        # Проверяем количество элементов
        assert len(data["metrics"]) == 4
        assert len(data["time_series"]) == 7  # week = 7 дней
        assert len(data["recent_dialogues"]) == 10
        assert len(data["top_users"]) == 5

    def test_get_stats_day_period(self, client: TestClient) -> None:
        """Тест получения статистики за день."""
        response = client.get("/stats?period=day")
        assert response.status_code == 200
        data = response.json()

        assert len(data["metrics"]) == 4
        assert len(data["time_series"]) == 24  # day = 24 часа

    def test_get_stats_week_period(self, client: TestClient) -> None:
        """Тест получения статистики за неделю."""
        response = client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        assert len(data["metrics"]) == 4
        assert len(data["time_series"]) == 7  # week = 7 дней

    def test_get_stats_month_period(self, client: TestClient) -> None:
        """Тест получения статистики за месяц."""
        response = client.get("/stats?period=month")
        assert response.status_code == 200
        data = response.json()

        assert len(data["metrics"]) == 4
        assert len(data["time_series"]) == 30  # month = 30 дней

    def test_get_stats_invalid_period(self, client: TestClient) -> None:
        """Тест с некорректным периодом."""
        response = client.get("/stats?period=invalid")
        assert response.status_code == 422  # Validation error

    def test_metrics_structure(self, client: TestClient) -> None:
        """Тест структуры метрик в ответе."""
        response = client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        for metric in data["metrics"]:
            assert "title" in metric
            assert "value" in metric
            assert "change_percent" in metric
            assert "description" in metric

        # Проверяем наличие всех ожидаемых метрик
        titles = [m["title"] for m in data["metrics"]]
        assert "Total Dialogues" in titles
        assert "Active Users" in titles
        assert "Avg Messages per Dialogue" in titles
        assert "Messages Today" in titles

    def test_time_series_structure(self, client: TestClient) -> None:
        """Тест структуры временного ряда в ответе."""
        response = client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        for point in data["time_series"]:
            assert "date" in point
            assert "value" in point
            assert isinstance(point["value"], int)
            assert point["value"] >= 0

    def test_recent_dialogues_structure(self, client: TestClient) -> None:
        """Тест структуры последних диалогов в ответе."""
        response = client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        assert len(data["recent_dialogues"]) == 10

        for dialogue in data["recent_dialogues"]:
            assert "user_id" in dialogue
            assert "username" in dialogue
            assert "message_count" in dialogue
            assert "last_message_at" in dialogue
            assert isinstance(dialogue["message_count"], int)
            assert dialogue["message_count"] > 0

    def test_top_users_structure(self, client: TestClient) -> None:
        """Тест структуры топ пользователей в ответе."""
        response = client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        assert len(data["top_users"]) == 5

        for user in data["top_users"]:
            assert "user_id" in user
            assert "username" in user
            assert "total_messages" in user
            assert "dialogue_count" in user
            assert isinstance(user["total_messages"], int)
            assert isinstance(user["dialogue_count"], int)

    def test_response_content_type(self, client: TestClient) -> None:
        """Тест корректного content-type в ответе."""
        response = client.get("/stats")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_openapi_docs_available(self, client: TestClient) -> None:
        """Тест доступности OpenAPI документации."""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_schema = response.json()
        assert openapi_schema["info"]["title"] == "HomeGuru Stats API"
        assert openapi_schema["info"]["version"] == "0.1.0"
