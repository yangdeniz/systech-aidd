from unittest.mock import patch

import pytest

from src.bot.config import Config


def test_config_loads_env_variables():
    with patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "OPENROUTER_API_KEY": "test_key",
            "OPENROUTER_MODEL": "test_model",
            "SYSTEM_PROMPT": "Test prompt",
            "MAX_HISTORY_MESSAGES": "10",
        },
    ):
        config = Config()
        assert config.telegram_token == "test_token"
        assert config.openrouter_api_key == "test_key"
        assert config.openrouter_model == "test_model"
        assert config.system_prompt == "Test prompt"
        assert config.max_history == 10


def test_config_default_max_history():
    with patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "OPENROUTER_API_KEY": "test_key",
            "OPENROUTER_MODEL": "test_model",
            "SYSTEM_PROMPT": "Test prompt",
        },
        clear=True,
    ):
        config = Config()
        assert config.max_history == 20


@patch("src.bot.config.load_dotenv")
def test_config_missing_telegram_token(mock_load_dotenv):
    """Тест отсутствия TELEGRAM_BOT_TOKEN"""
    with patch.dict(
        "os.environ",
        {"OPENROUTER_API_KEY": "test_key", "OPENROUTER_MODEL": "test_model"},
        clear=True,
    ), pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
        Config()


@patch("src.bot.config.load_dotenv")
def test_config_missing_api_key(mock_load_dotenv):
    """Тест отсутствия OPENROUTER_API_KEY"""
    with patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "test_token", "OPENROUTER_MODEL": "test_model"},
        clear=True,
    ), pytest.raises(ValueError, match="OPENROUTER_API_KEY is required"):
        Config()


@patch("src.bot.config.load_dotenv")
def test_config_missing_model(mock_load_dotenv):
    """Тест отсутствия OPENROUTER_MODEL"""
    with patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "test_token", "OPENROUTER_API_KEY": "test_key"},
        clear=True,
    ), pytest.raises(ValueError, match="OPENROUTER_MODEL is required"):
        Config()


@patch("src.bot.config.load_dotenv")
def test_config_default_system_prompt(mock_load_dotenv):
    """Тест дефолтного значения system_prompt"""
    with patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "OPENROUTER_API_KEY": "test_key",
            "OPENROUTER_MODEL": "test_model",
        },
        clear=True,
    ):
        config = Config()
        assert config.system_prompt == "You are a helpful assistant."
