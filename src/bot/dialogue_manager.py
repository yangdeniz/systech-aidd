class DialogueManager:
    def __init__(self, max_history: int):
        self.dialogues = {}  # {user_id: [messages]}
        self.max_history = max_history
    
    def add_message(self, user_id: int, role: str, content: str):
        """
        Добавляет сообщение в историю диалога.
        
        Args:
            user_id: ID пользователя
            role: роль отправителя ("user" или "assistant")
            content: текст сообщения
        """
        if user_id not in self.dialogues:
            self.dialogues[user_id] = []
        
        self.dialogues[user_id].append({
            "role": role,
            "content": content
        })
        
        # Ограничиваем историю
        if len(self.dialogues[user_id]) > self.max_history:
            self.dialogues[user_id] = self.dialogues[user_id][-self.max_history:]
    
    def get_history(self, user_id: int) -> list:
        """
        Возвращает историю диалога для пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Список сообщений в формате [{"role": "user", "content": "текст"}]
        """
        return self.dialogues.get(user_id, [])
    
    def clear_history(self, user_id: int):
        """
        Очищает историю диалога для пользователя.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self.dialogues:
            self.dialogues[user_id] = []

