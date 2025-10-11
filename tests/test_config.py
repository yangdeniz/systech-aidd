from unittest.mock import patch

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
