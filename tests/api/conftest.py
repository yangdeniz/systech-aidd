"""
Конфигурация тестов для API.

Использует mock режим для изоляции тестов от реальной БД.
Mock режим не требует Docker и возвращает предсказуемые тестовые данные.

ВАЖНО: COLLECTOR_MODE устанавливается на уровне модуля ДО импорта приложения.
"""

import os

# Устанавливаем COLLECTOR_MODE в 'mock' ДО импорта приложения
os.environ["COLLECTOR_MODE"] = "mock"

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def preserve_mock_collector_mode():
    """
    Сохраняет COLLECTOR_MODE в 'mock' для всех тестов API.

    Mock режим возвращает предсказуемые тестовые данные без подключения к БД.
    """
    # COLLECTOR_MODE уже установлен на уровне модуля
    yield
    # После тестов можно удалить, если нужно
    if "COLLECTOR_MODE" in os.environ:
        del os.environ["COLLECTOR_MODE"]
