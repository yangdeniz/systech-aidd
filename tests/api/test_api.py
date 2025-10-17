"""
Тесты для FastAPI endpoints.

Проверяет работу REST API для получения статистики дашборда.
Использует testcontainers для изоляции от реальной БД.
Требует запущенный Docker Desktop на Windows.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app


class TestStatsAPI:
    """Тесты для Stats API endpoints."""

    @pytest.fixture
    async def client(self) -> AsyncClient:
        """Создает тестовый async клиент FastAPI."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test", timeout=30.0
        ) as client:
            yield client

    async def test_root_endpoint(self, client: AsyncClient) -> None:
        """Тест корневого endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "HomeGuru Stats API"
        assert data["version"] == "0.2.0"
        assert "mode" in data
        assert data["mode"] == "mock"  # Тесты используют mock режим (без БД)
        assert data["docs"] == "/docs"

    async def test_health_check(self, client: AsyncClient) -> None:
        """Тест health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_get_stats_default_period(self, client: AsyncClient) -> None:
        """Тест получения статистики с периодом по умолчанию (week)."""
        response = await client.get("/stats")
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
        # Mock генерирует 10 диалогов и 5 пользователей
        assert len(data["recent_dialogues"]) == 10
        assert len(data["top_users"]) == 5

    async def test_get_stats_day_period(self, client: AsyncClient) -> None:
        """Тест получения статистики за день."""
        response = await client.get("/stats?period=day")
        assert response.status_code == 200
        data = response.json()

        assert len(data["metrics"]) == 4
        assert len(data["time_series"]) == 24  # day = 24 часа

    async def test_get_stats_week_period(self, client: AsyncClient) -> None:
        """Тест получения статистики за неделю."""
        response = await client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        assert len(data["metrics"]) == 4
        assert len(data["time_series"]) == 7  # week = 7 дней

    async def test_get_stats_month_period(self, client: AsyncClient) -> None:
        """Тест получения статистики за месяц."""
        response = await client.get("/stats?period=month")
        assert response.status_code == 200
        data = response.json()

        assert len(data["metrics"]) == 4
        assert len(data["time_series"]) == 30  # month = 30 дней

    async def test_get_stats_invalid_period(self, client: AsyncClient) -> None:
        """Тест с некорректным периодом."""
        response = await client.get("/stats?period=invalid")
        assert response.status_code == 422  # Validation error

    async def test_metrics_structure(self, client: AsyncClient) -> None:
        """Тест структуры метрик в ответе."""
        response = await client.get("/stats?period=week")
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

    async def test_time_series_structure(self, client: AsyncClient) -> None:
        """Тест структуры временного ряда в ответе."""
        response = await client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        for point in data["time_series"]:
            assert "date" in point
            assert "value" in point
            assert isinstance(point["value"], int)
            assert point["value"] >= 0

    async def test_recent_dialogues_structure(self, client: AsyncClient) -> None:
        """Тест структуры последних диалогов в ответе."""
        response = await client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        # Mock генерирует 10 диалогов
        assert len(data["recent_dialogues"]) == 10

        for dialogue in data["recent_dialogues"]:
            assert "user_id" in dialogue
            assert "username" in dialogue
            assert "message_count" in dialogue
            assert "last_message_at" in dialogue
            assert isinstance(dialogue["message_count"], int)
            assert dialogue["message_count"] > 0

    async def test_top_users_structure(self, client: AsyncClient) -> None:
        """Тест структуры топ пользователей в ответе."""
        response = await client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        # Mock генерирует 5 пользователей
        assert len(data["top_users"]) == 5

        for user in data["top_users"]:
            assert "user_id" in user
            assert "username" in user
            assert "total_messages" in user
            assert "dialogue_count" in user
            assert isinstance(user["total_messages"], int)
            assert isinstance(user["dialogue_count"], int)

    async def test_response_content_type(self, client: AsyncClient) -> None:
        """Тест корректного content-type в ответе."""
        response = await client.get("/stats")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    async def test_openapi_docs_available(self, client: AsyncClient) -> None:
        """Тест доступности OpenAPI документации."""
        response = await client.get("/docs")
        assert response.status_code == 200

        response = await client.get("/openapi.json")
        assert response.status_code == 200
        openapi_schema = response.json()
        assert openapi_schema["info"]["title"] == "HomeGuru API"
        assert openapi_schema["info"]["version"] == "0.3.0"
