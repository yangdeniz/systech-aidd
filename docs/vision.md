# Техническое видение проекта: LLM-ассистент

## 1. Технологии

### Основные технологии
- **Python 3.11+** - базовый язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API (метод polling)
- **openai** - клиент для работы с OpenRouter API
- **python-dotenv** - управление переменными окружения (.env файлы)
- **pytest** - фреймворк для юнит-тестирования
- **Make** - автоматизация задач сборки и запуска

### Обоснование выбора
- Минимальный набор зависимостей для быстрого старта MVP
- Проверенные и стабильные библиотеки
- Простота в использовании и развертывании

---

## 2. Принципы разработки

### Главные принципы
- **KISS (Keep It Simple, Stupid)** - максимальная простота во всём
- **MVP-подход** - только необходимый функционал для проверки идеи
- **ООП с правилом "1 класс = 1 файл"** - чистая структура кода
- **Никакого оверинжиниринга** - не решаем проблемы, которых еще нет

### Практическое применение
- Один модуль = одна ответственность
- Простые и понятные имена классов и методов
- Минимум абстракций на старте
- Код должен быть понятен без документации
- In-memory хранение данных (без БД)
- Синхронная обработка сообщений (один пользователь = один диалог)

---

## 3. Структура проекта

### Организация файлов и директорий

```
systech-aidd/
├── src/
│   └── bot/
│       ├── __init__.py
│       ├── main.py              # Точка входа
│       ├── bot.py               # TelegramBot класс
│       ├── llm_client.py        # LLMClient класс
│       ├── dialogue_manager.py  # DialogueManager класс
│       └── config.py            # Config класс
├── tests/
│   ├── __init__.py
│   ├── test_dialogue_manager.py
│   ├── test_llm_client.py
│   └── test_config.py
├── .env                         # Переменные окружения (не в git)
├── .env.example                 # Пример .env файла
├── .gitignore
├── pyproject.toml               # Конфигурация uv/проекта
├── Makefile                     # Команды для запуска
└── README.md
```

### Описание модулей
- **main.py** - точка входа, запуск приложения
- **bot.py** - обработка Telegram сообщений (aiogram)
- **llm_client.py** - работа с OpenRouter через openai client
- **dialogue_manager.py** - управление контекстом диалогов (in-memory)
- **config.py** - загрузка конфигурации из .env

### Принципы организации
- 1 класс = 1 файл
- Простая плоская структура без вложенных пакетов
- Всего 5 основных модулей для MVP

---

## 4. Архитектура проекта

### Основные компоненты и их взаимодействие

```
User (Telegram) 
    ↓
TelegramBot (aiogram)
    ↓
DialogueManager (контекст диалогов)
    ↓
LLMClient (OpenRouter API)
    ↓
Response → User
```

### Описание компонентов

**1. TelegramBot** (bot.py)
- Получает сообщения от пользователей (polling)
- Передает в DialogueManager
- Отправляет ответы обратно пользователю

**2. DialogueManager** (dialogue_manager.py)
- Хранит историю диалогов в памяти (dict: user_id → messages)
- Формирует контекст для LLM (system prompt + история)
- Вызывает LLMClient для получения ответа
- Обновляет историю диалога

**3. LLMClient** (llm_client.py)
- Отправляет запросы в OpenRouter API
- Использует openai client
- Возвращает ответ от LLM

**4. Config** (config.py)
- Загружает настройки из .env
- Предоставляет конфигурацию всем модулям

### Поток данных
1. Пользователь отправляет сообщение в Telegram
2. TelegramBot получает сообщение
3. DialogueManager добавляет сообщение в историю
4. DialogueManager формирует запрос с контекстом
5. LLMClient отправляет запрос в OpenRouter
6. Ответ возвращается через цепочку обратно
7. TelegramBot отправляет ответ пользователю

---

## 5. Модель данных

### Структуры данных

**Сообщение (Message)**
```python
{
    "role": str,      # "user" или "assistant" или "system"
    "content": str    # текст сообщения
}
```

**Диалог (Dialogue)**
```python
{
    user_id: int → [Message]  # список сообщений для каждого пользователя
}
```

### Хранение в DialogueManager
```python
class DialogueManager:
    def __init__(self):
        self.dialogues = {}  # {user_id: [messages]}
```

### Особенности
- Хранение **только в памяти** (dict)
- При перезапуске бота история теряется
- Формат совместим с OpenAI API (role + content)
- Никаких дополнительных полей (timestamp, id и т.д.)

### Ограничения для MVP
- Максимум последних 10 пар вопрос-ответ (20 сообщений) на пользователя
- Простое усечение старых сообщений при превышении лимита

---

## 6. Работа с LLM

### Конфигурация LLMClient

**Параметры в .env:**
```env
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
SYSTEM_PROMPT=Ты полезный AI-ассистент...
```

### Реализация
```python
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
        # Добавляем system prompt в начало
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages
        )
        
        return response.choices[0].message.content
```

### Особенности для MVP
- Используем стандартный openai client с base_url на OpenRouter
- Один системный промпт для всех пользователей
- Без streaming (простой синхронный запрос)
- Без обработки ошибок в первой версии
- Без настройки temperature, max_tokens и других параметров (дефолтные значения)

---

## 7. Сценарии работы

### Основные сценарии

**1. Первый запуск бота**
- Пользователь отправляет `/start`
- Бот приветствует пользователя
- Создается новый пустой диалог для user_id

**2. Обычный диалог**
- Пользователь отправляет текстовое сообщение
- Бот добавляет сообщение в историю
- Отправляет контекст в LLM
- Получает ответ и отправляет пользователю
- Добавляет ответ в историю

**3. Очистка истории**
- Пользователь отправляет `/reset`
- Бот очищает историю диалога для этого пользователя
- Подтверждает очистку

### Команды бота
- `/start` - запуск бота и приветствие
- `/reset` - очистка истории диалога
- `/help` - справка о командах

### Ограничения MVP
- Только текстовые сообщения (без изображений, документов)
- Один активный диалог на пользователя
- Никаких дополнительных команд для настройки

---

## 8. Подход к конфигурированию

### Файл .env
Все настройки в одном месте:
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# OpenRouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# System Prompt
SYSTEM_PROMPT=Ты полезный AI-ассистент, который помогает пользователям...

# Dialogue Settings
MAX_HISTORY_MESSAGES=20
```

### Класс Config
```python
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
```

### Особенности
- Один файл .env для всех настроек
- Никакой валидации в MVP (упадет с ошибкой, если не указано)
- Без поддержки разных окружений (dev/prod)
- .env.example в репозитории как шаблон
- .env в .gitignore

---

## 9. Подход к логгированию

### Использование стандартного logging

```python
import logging

# Настройка в main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()  # Также выводим в консоль
    ]
)

logger = logging.getLogger(__name__)
```

### Что логируем
- **INFO**: Старт/остановка бота
- **INFO**: Получение сообщений от пользователей (user_id, текст)
- **INFO**: Отправка запросов в LLM
- **INFO**: Получение ответов от LLM
- **ERROR**: Ошибки и исключения

### Пример использования в коде
```python
class TelegramBot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def handle_message(self, message):
        self.logger.info(f"Received message from user {message.from_user.id}")
        try:
            # ...
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
```

### Особенности для MVP
- Логи в файл `bot.log` + вывод в консоль
- Уровень INFO для информационных сообщений
- Уровень ERROR для ошибок
- Простой формат сообщений
- Без ротации логов на старте
- Файл bot.log в .gitignore

---

## 10. Тестирование

### Подход к тестированию

Минимальный набор юнит-тестов для проверки базовой функциональности основных компонентов.

### Что тестируем

**DialogueManager** (test_dialogue_manager.py)
- Добавление сообщения в историю
- Получение истории диалога
- Очистка истории
- Ограничение количества сообщений (20 сообщений)

**LLMClient** (test_llm_client.py)
- Корректность формирования запроса
- Добавление system prompt в начало
- Мок-тестирование без реальных запросов к API

**Config** (test_config.py)
- Корректная загрузка параметров из .env
- Значения по умолчанию

### Что НЕ тестируем в MVP
- TelegramBot (интеграция с aiogram)
- Реальные запросы к OpenRouter API
- Интеграционные тесты
- E2E тесты

### Запуск тестов

```bash
# Через Make
make test

# Напрямую через pytest
pytest tests/ -v
```

### Особенности для MVP
- Только самые базовые юнит-тесты
- Использование моков для внешних зависимостей
- Без измерения покрытия кода
- Без CI/CD на старте
- Простая структура тестов (один тестовый файл на модуль)

---

## Заключение

Данный документ описывает техническое видение MVP-версии LLM-ассистента. Все решения направлены на максимальную простоту реализации и быструю проверку идеи. Следование принципам KISS и отказ от оверинжиниринга позволят быстро создать рабочий прототип и получить первый пользовательский опыт.

