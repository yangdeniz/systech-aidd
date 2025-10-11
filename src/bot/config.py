import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    telegram_token: str
    openrouter_api_key: str
    openrouter_model: str
    system_prompt: str
    max_history: int

    def __init__(self) -> None:
        load_dotenv()

        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required in .env")
        self.telegram_token = telegram_token

        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required in .env")
        self.openrouter_api_key = openrouter_api_key

        openrouter_model = os.getenv("OPENROUTER_MODEL")
        if not openrouter_model:
            raise ValueError("OPENROUTER_MODEL is required in .env")
        self.openrouter_model = openrouter_model

        self.system_prompt = self._load_system_prompt_from_file()
        self.max_history = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

    def _load_system_prompt_from_file(self) -> str:
        """
        Загрузить системный промпт из файла system_prompt.txt.

        Returns:
            Содержимое файла или дефолтный промпт при ошибке
        """
        prompt_file = "src/bot/system_prompt.txt"
        try:
            with open(prompt_file, encoding="utf-8") as f:
                prompt = f.read().strip()
                if not prompt:
                    logger.warning(f"System prompt file is empty: {prompt_file}. Using default.")
                    return "You are a helpful assistant."
                logger.info(f"System prompt loaded from {prompt_file}")
                return prompt
        except FileNotFoundError:
            logger.warning(f"System prompt file not found: {prompt_file}. Using default.")
            return "You are a helpful assistant."
