from openai import OpenAI


class LLMClient:
    def __init__(self, api_key: str, model: str, system_prompt: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
        self.system_prompt = system_prompt
    
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
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages
        )
        
        return response.choices[0].message.content

