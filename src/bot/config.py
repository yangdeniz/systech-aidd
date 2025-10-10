from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        load_dotenv()
        
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL")
        self.system_prompt = os.getenv("SYSTEM_PROMPT")
        self.max_history = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

