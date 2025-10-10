import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, api_key: str, model: str, system_prompt: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
        self.system_prompt = system_prompt
        logger.info(f"LLMClient initialized with model: {model}")
    
    def get_response(self, messages: list) -> str:
        """
        Отправляет запрос в OpenRouter и возвращает ответ LLM.
        
        Args:
            messages: список сообщений в формате [{"role": "user", "content": "текст"}]
        
        Returns:
            Текст ответа от LLM
        """
        # Добавляем system prompt в начало
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages
        
        logger.info(f"Sending request to LLM: model={self.model}, messages_count={len(messages)}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"Received response from LLM: length={len(response_text)} chars")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error getting response from LLM: {e}", exc_info=True)
            raise

