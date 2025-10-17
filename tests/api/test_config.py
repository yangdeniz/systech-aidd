"""
Тесты для модуля конфигурации и factory pattern.

Проверяем APIConfig и создание collectors.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.api.collectors import MockStatCollector, RealStatCollector
from src.api.config import APIConfig, CollectorMode, create_collector, get_config


@pytest.fixture
def mock_env_mock():
    """Мокаем environment для MOCK режима."""
    with patch.dict(os.environ, {"COLLECTOR_MODE": "mock"}, clear=False):
        yield


@pytest.fixture
def mock_env_real():
    """Мокаем environment для REAL режима."""
    with patch.dict(
        os.environ,
        {
            "COLLECTOR_MODE": "real",
            "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
        },
        clear=False,
    ):
        yield


def test_collector_mode_enum():
    """Тест CollectorMode enum."""
    assert CollectorMode.MOCK.value == "mock"
    assert CollectorMode.REAL.value == "real"


def test_api_config_default():
    """Тест конфигурации по умолчанию (mock режим)."""
    with patch.dict(os.environ, {}, clear=True):
        config = APIConfig()
        assert config.collector_mode == CollectorMode.MOCK
        assert "postgresql" in config.database_url.lower()


def test_api_config_mock_mode(mock_env_mock):
    """Тест конфигурации в MOCK режиме."""
    config = APIConfig()
    assert config.collector_mode == CollectorMode.MOCK


def test_api_config_real_mode(mock_env_real):
    """Тест конфигурации в REAL режиме."""
    config = APIConfig()
    assert config.collector_mode == CollectorMode.REAL
    assert config.database_url == "postgresql+asyncpg://test:test@localhost/test"


def test_api_config_invalid_mode():
    """Тест обработки некорректного режима."""
    with patch.dict(os.environ, {"COLLECTOR_MODE": "invalid"}, clear=False):
        with pytest.raises(ValueError, match="Invalid COLLECTOR_MODE"):
            APIConfig()


def test_create_collector_mock(mock_env_mock):
    """Тест создания MockStatCollector."""
    config = APIConfig()
    collector = create_collector(config)

    assert isinstance(collector, MockStatCollector)


@patch("src.bot.database.create_engine")
@patch("src.bot.database.create_session_factory")
def test_create_collector_real(mock_session_factory, mock_create_engine, mock_env_real):
    """Тест создания RealStatCollector."""
    # Мокаем database setup
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_factory = MagicMock()
    mock_session_factory.return_value = mock_factory

    config = APIConfig()
    collector = create_collector(config)

    assert isinstance(collector, RealStatCollector)
    mock_create_engine.assert_called_once()
    mock_session_factory.assert_called_once_with(mock_engine)


def test_get_config_singleton():
    """Тест singleton pattern для get_config."""
    # Сбрасываем глобальный _config
    import src.api.config

    src.api.config._config = None

    config1 = get_config()
    config2 = get_config()

    # Должны вернуть один и тот же экземпляр
    assert config1 is config2
