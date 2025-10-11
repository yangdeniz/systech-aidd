from unittest.mock import patch

import pytest

from src.bot.config import Config


def test_config_loads_env_variables() -> None:
    with patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "OPENROUTER_API_KEY": "test_key",
            "OPENROUTER_MODEL": "test_model",
            "MAX_HISTORY_MESSAGES": "10",
        },
    ):
        config = Config()
        assert config.telegram_token == "test_token"
        assert config.openrouter_api_key == "test_key"
        assert config.openrouter_model == "test_model"
        # system_prompt теперь загружается из файла, не из env
        assert len(config.system_prompt) > 0
        assert config.max_history == 10


def test_config_default_max_history() -> None:
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
def test_config_missing_telegram_token(mock_load_dotenv) -> None:
    """Тест отсутствия TELEGRAM_BOT_TOKEN"""
    with (
        patch.dict(
            "os.environ",
            {"OPENROUTER_API_KEY": "test_key", "OPENROUTER_MODEL": "test_model"},
            clear=True,
        ),
        pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"),
    ):
        Config()


@patch("src.bot.config.load_dotenv")
def test_config_missing_api_key(mock_load_dotenv) -> None:
    """Тест отсутствия OPENROUTER_API_KEY"""
    with (
        patch.dict(
            "os.environ",
            {"TELEGRAM_BOT_TOKEN": "test_token", "OPENROUTER_MODEL": "test_model"},
            clear=True,
        ),
        pytest.raises(ValueError, match="OPENROUTER_API_KEY is required"),
    ):
        Config()


@patch("src.bot.config.load_dotenv")
def test_config_missing_model(mock_load_dotenv) -> None:
    """Тест отсутствия OPENROUTER_MODEL"""
    with (
        patch.dict(
            "os.environ",
            {"TELEGRAM_BOT_TOKEN": "test_token", "OPENROUTER_API_KEY": "test_key"},
            clear=True,
        ),
        pytest.raises(ValueError, match="OPENROUTER_MODEL is required"),
    ):
        Config()


@patch("src.bot.config.load_dotenv")
def test_config_loads_system_prompt_from_file(mock_load_dotenv) -> None:
    """Тест загрузки system_prompt из файла (реальный файл существует)"""
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
        # Проверяем что промпт загружен из файла и содержит HomeGuru
        assert "HomeGuru" in config.system_prompt
        assert len(config.system_prompt) > 100


@patch("src.bot.config.load_dotenv")
def test_config_loads_prompt_from_file(mock_load_dotenv, tmp_path) -> None:
    """Тест загрузки системного промпта из файла"""
    # Arrange: создаем временный файл с промптом
    prompt_content = "Ты - HomeGuru, профессиональный ИИ-дизайнер интерьеров."
    prompt_file = tmp_path / "system_prompt.txt"
    prompt_file.write_text(prompt_content, encoding="utf-8")

    with (
        patch.dict(
            "os.environ",
            {
                "TELEGRAM_BOT_TOKEN": "test_token",
                "OPENROUTER_API_KEY": "test_key",
                "OPENROUTER_MODEL": "test_model",
            },
            clear=True,
        ),
        patch("src.bot.config.Config._load_system_prompt_from_file") as mock_load,
    ):
        mock_load.return_value = prompt_content

        # Act
        config = Config()

        # Assert
        assert config.system_prompt == prompt_content
        mock_load.assert_called_once()


@patch("src.bot.config.load_dotenv")
def test_config_prompt_file_not_found(mock_load_dotenv) -> None:
    """Тест fallback при отсутствии файла system_prompt.txt"""
    with (
        patch.dict(
            "os.environ",
            {
                "TELEGRAM_BOT_TOKEN": "test_token",
                "OPENROUTER_API_KEY": "test_key",
                "OPENROUTER_MODEL": "test_model",
            },
            clear=True,
        ),
        patch("builtins.open", side_effect=FileNotFoundError),
    ):
        # Act
        config = Config()

        # Assert: fallback на дефолтный промпт
        assert config.system_prompt == "You are a helpful assistant."


@patch("src.bot.config.load_dotenv")
def test_config_prompt_file_empty(mock_load_dotenv, tmp_path) -> None:
    """Тест обработки пустого файла system_prompt.txt"""
    # Arrange: создаем пустой файл
    prompt_file = tmp_path / "system_prompt.txt"
    prompt_file.write_text("   \n  ", encoding="utf-8")

    with (
        patch.dict(
            "os.environ",
            {
                "TELEGRAM_BOT_TOKEN": "test_token",
                "OPENROUTER_API_KEY": "test_key",
                "OPENROUTER_MODEL": "test_model",
            },
            clear=True,
        ),
        patch("builtins.open", return_value=prompt_file.open("r", encoding="utf-8")),
    ):
        # Act
        config = Config()

        # Assert: fallback на дефолтный промпт
        assert config.system_prompt == "You are a helpful assistant."
