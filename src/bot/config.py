import os

from dotenv import load_dotenv


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

        self.system_prompt = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")
        self.max_history = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
