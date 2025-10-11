# Техническое видение проекта: HomeGuru - ИИ-дизайнер интерьеров

## 1. Технологии

### Основные технологии
- **Python 3.11+** - базовый язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API (метод polling)
- **openai** - клиент для работы с OpenRouter API (мультимодальные модели)
- **langsmith** - мониторинг и трейсинг LLM запросов
- **python-dotenv** - управление переменными окружения (.env файлы)
- **pytest** + **pytest-asyncio** + **pytest-cov** - тестирование и покрытие кода
- **ruff** - форматтер и линтер (заменяет Black + Flake8 + isort)
- **mypy** - статическая проверка типов
- **Make** - автоматизация задач сборки, запуска и проверки качества

### Обоснование выбора
- Минимальный набор зависимостей для быстрого старта MVP
- Проверенные и стабильные библиотеки
- Простота в использовании и развертывании
- Мультимодальные возможности OpenRouter для работы с изображениями
- LangSmith для мониторинга качества ответов ИИ-дизайнера
- Ruff - быстрейший форматтер/линтер на рынке (вместо множества инструментов)
- Mypy strict mode - предотвращение багов на этапе разработки
- Автоматизация через Make для единообразия проверок качества

---

## 2. Принципы разработки

### Главные принципы
- **KISS (Keep It Simple, Stupid)** - максимальная простота во всём
- **MVP-подход** - только необходимый функционал для проверки идеи
- **ООП с правилом "1 класс = 1 файл"** - чистая структура кода
- **Никакого оверинжиниринга** - не решаем проблемы, которых еще нет
- **Type Safety** - type hints обязательны, mypy strict mode
- **SOLID (разумно)** - применяем SRP и DIP через Protocol, без фанатизма

### Практическое применение
- Один модуль = одна ответственность (SRP)
- Простые и понятные имена классов и методов
- Минимум абстракций - Protocol только для ключевых зависимостей (DIP)
- Код должен быть понятен без документации (но с type hints)
- In-memory хранение данных (без БД)
- Синхронная обработка сообщений (один пользователь = один диалог)
- Все методы типизированы - параметры и возвращаемые значения
- Автоматические проверки качества через `make quality`

---

## 3. Структура проекта

### Организация файлов и директорий

> **Примечание:** Структура показана в целевом состоянии после выполнения Tech Debt итераций (TD-4, TD-5). Текущее состояние MVP (итерации 1-5) содержит 6 базовых модулей без interfaces.py, message_handler.py, command_handler.py.

```
systech-aidd/
├── src/
│   └── bot/
│       ├── __init__.py
│       ├── main.py              # Точка входа
│       ├── bot.py               # TelegramBot класс (инфраструктура)
│       ├── message_handler.py   # MessageHandler класс (бизнес-логика) [после TD-5]
│       ├── command_handler.py   # CommandHandler класс (команды) [после TD-5]
│       ├── llm_client.py        # LLMClient класс (мультимодальный)
│       ├── dialogue_manager.py  # DialogueManager класс
│       ├── config.py            # Config класс
│       ├── interfaces.py        # Protocol интерфейсы (DIP) [после TD-4]
│       ├── media_processor.py   # MediaProcessor класс (фото/аудио)
│       └── system_prompt.txt    # Системный промпт HomeGuru
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Общие фикстуры
│   ├── test_bot.py
│   ├── test_message_handler.py
│   ├── test_command_handler.py
│   ├── test_dialogue_manager.py
│   ├── test_llm_client.py
│   ├── test_config.py
│   └── test_media_processor.py
├── docs/
│   ├── idea.md                  # Концепция HomeGuru
│   ├── vision.md                # Техническое видение
│   ├── tasklist.md              # План разработки
│   ├── tasklist_tech_debt.md    # План улучшения качества
│   ├── conventions.md           # Соглашения
│   ├── workflow.md              # Процесс работы
│   ├── workflow_tech_debt.md    # Процесс для Tech Debt
│   └── addrs/
│       └── ADR-01.md            # Архитектурное решение
├── .env                         # Переменные окружения (не в git)
├── .env.example                 # Пример .env файла
├── .gitignore
├── pyproject.toml               # Конфигурация uv/проекта + инструменты качества
├── Makefile                     # Команды: run, test, format, lint, typecheck, quality
└── README.md
```

### Описание модулей

**Базовые модули MVP (итерации 1-5):**
- **main.py** - точка входа, запуск приложения, настройка LangSmith
- **bot.py** - инфраструктура Telegram (aiogram) + обработка команд и сообщений
- **llm_client.py** - работа с мультимодальными моделями через OpenRouter
- **dialogue_manager.py** - управление контекстом диалогов (in-memory)
- **config.py** - загрузка конфигурации из .env и системного промпта из файла
- **media_processor.py** - обработка изображений и аудио (загрузка, конвертация) [итерации 7-8]
- **system_prompt.txt** - системный промпт с ролью HomeGuru (ИИ-дизайнер) [итерация 6]

**Дополнительные модули после рефакторинга (Tech Debt):**
- **message_handler.py** - бизнес-логика обработки текстовых/медиа сообщений [после TD-5]
- **command_handler.py** - обработка команд бота (/start, /reset, /help, /role) [после TD-5]
- **interfaces.py** - Protocol интерфейсы для Dependency Inversion (LLMProvider, DialogueStorage) [после TD-4]

### Принципы организации
- 1 класс = 1 файл (обязательно)
- Простая плоская структура без вложенных пакетов
- **6 базовых модулей для MVP** (итерации 1-5)
- **9 модулей после рефакторинга** (с учетом разделения по SRP в TD-4, TD-5)
- Системный промпт вынесен в отдельный файл для удобства редактирования
- Protocol интерфейсы для слабой связанности - добавляются в TD-4 (DIP)
- Разделение инфраструктуры и бизнес-логики - выполняется в TD-5 (SRP)

---

## 4. Архитектура проекта

### Основные компоненты и их взаимодействие

> **Примечание:** Схема показывает целевую архитектуру после рефакторинга (TD-4, TD-5). Текущая архитектура MVP (итерации 1-5) проще: TelegramBot содержит всю логику команд и обработки сообщений, без Protocol интерфейсов.

**Целевая архитектура (после Tech Debt):**
```
User (Telegram: текст/фото/аудио) 
    ↓
TelegramBot (aiogram инфраструктура)
    ↓ (команды)          ↓ (сообщения)
CommandHandler      MessageHandler
    ↓                    ↓
    |            MediaProcessor (фото/аудио)
    |                    ↓
    |←──→ DialogueStorage (Protocol) ←── DialogueManager
                         ↓
              LLMProvider (Protocol) ←── LLMClient
                         ↓
              OpenRouter API + LangSmith
                         ↓
                    Response → User
```

**Текущая архитектура MVP (итерации 1-5):**
```
User (Telegram: текст/фото/аудио) 
    ↓
TelegramBot (aiogram) - команды + обработка сообщений
    ↓                    ↓
    |            MediaProcessor (фото/аудио) [итерации 7-8]
    |                    ↓
    |←──→ DialogueManager (управление контекстом)
                         ↓
                   LLMClient (мультимодальный)
                         ↓
              OpenRouter API + LangSmith
                         ↓
                    Response → User
```

### Описание компонентов

**Текущая архитектура (MVP):**

**1. TelegramBot** (bot.py) - Инфраструктура + Логика
- Получает сообщения от пользователей: текст, фото, голосовые (polling)
- Обрабатывает команды: /start, /reset, /help, /role (напрямую)
- Обрабатывает текстовые и мультимодальные сообщения (напрямую)
- Координирует работу DialogueManager и LLMClient
- Отправляет ответы обратно пользователю
- **Зависимости**: `LLMClient`, `DialogueManager` (прямые)

**Целевая архитектура (после TD-5):**

**1. TelegramBot** (bot.py) - Только инфраструктура
- Получает сообщения от пользователей: текст, фото, голосовые (polling)
- Делегирует команды в `CommandHandler`
- Делегирует обработку сообщений в `MessageHandler`
- Отправляет ответы обратно пользователю
- **Зависимости**: `MessageHandler`, `CommandHandler` (DIP)

**2. MessageHandler** (message_handler.py) - Бизнес-логика сообщений [после TD-5]
- Обрабатывает текстовые и мультимодальные сообщения
- Координирует работу `MediaProcessor`, `DialogueStorage`, `LLMProvider`
- Формирует контекст и получает ответ от LLM
- Возвращает текст ответа пользователю
- **Зависимости**: `LLMProvider`, `DialogueStorage` (Protocol через DIP)

**3. CommandHandler** (command_handler.py) - Обработка команд [после TD-5]
- Обрабатывает команды: /start, /reset, /help, /role
- Взаимодействует с `DialogueStorage` для очистки истории
- Формирует текст ответов на команды
- Возвращает текст ответа
- **Зависимости**: `DialogueStorage` (Protocol через DIP)

**4. MediaProcessor** (media_processor.py) - Обработка медиа
- Скачивает фотографии из Telegram
- Скачивает и транскрибирует голосовые сообщения
- Конвертирует медиа в формат для отправки в LLM
- Возвращает обработанные данные

**5. DialogueManager** (dialogue_manager.py) - Хранилище диалогов
- Хранит историю диалогов в памяти (dict: user_id → messages)
- Добавляет сообщения в историю с ограничением размера
- Предоставляет историю для формирования контекста
- Очищает историю по запросу
- **После TD-4**: Реализует `DialogueStorage` Protocol

**6. LLMClient** (llm_client.py) - Провайдер LLM
- Отправляет мультимодальные запросы в OpenRouter API
- Использует openai client для работы с моделями, поддерживающими Vision
- Интегрирован с LangSmith для мониторинга всех запросов
- Возвращает ответ от LLM
- **После TD-4**: Реализует `LLMProvider` Protocol

**7. Config** (config.py) - Конфигурация
- Загружает настройки из .env с валидацией
- Загружает системный промпт из system_prompt.txt
- Предоставляет конфигурацию всем модулям
- Выбрасывает `ValueError` при отсутствии обязательных параметров

**8. Interfaces** (interfaces.py) - Protocol интерфейсы [после TD-4]
- `LLMProvider` - контракт для провайдеров LLM
- `DialogueStorage` - контракт для хранилищ диалогов
- Обеспечивает Dependency Inversion (SOLID DIP)
- Позволяет легко заменять имплементации
- **Создается в итерации TD-4** (Technical Debt)

### Поток данных

**Текстовое сообщение:**
1. Пользователь отправляет текст в Telegram
2. TelegramBot получает сообщение
3. DialogueManager добавляет сообщение в историю
4. DialogueManager формирует запрос с контекстом
5. LLMClient отправляет запрос в OpenRouter (с трейсингом в LangSmith)
6. Ответ возвращается через цепочку обратно
7. TelegramBot отправляет ответ пользователю

**Фото:**
1. Пользователь отправляет фото интерьера
2. TelegramBot получает фото
3. MediaProcessor скачивает и обрабатывает изображение
4. DialogueManager добавляет изображение в контекст
5. LLMClient отправляет мультимодальный запрос (текст + изображение)
6. HomeGuru анализирует интерьер и дает рекомендации
7. Ответ отправляется пользователю

**Голосовое сообщение:**
1. Пользователь отправляет голосовое сообщение
2. TelegramBot получает аудио
3. MediaProcessor скачивает и транскрибирует в текст
4. Текст обрабатывается как обычное текстовое сообщение
5. Ответ отправляется пользователю

---

## 5. Модель данных

### Структуры данных

**Текстовое сообщение (Message)**
```python
{
    "role": str,      # "user" или "assistant" или "system"
    "content": str    # текст сообщения
}
```

**Мультимодальное сообщение (Message с изображением)**
```python
{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": str  # текст сообщения
        },
        {
            "type": "image_url",
            "image_url": {
                "url": str  # base64 или URL изображения
            }
        }
    ]
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
OPENROUTER_MODEL=<мультимодальная-модель>
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=homeguru
```

**Системный промпт в файле:**
- Файл `src/bot/system_prompt.txt` содержит описание роли HomeGuru
- Загружается при старте приложения через Config
- Можно легко редактировать без изменения кода

### Реализация
```python
from openai import OpenAI
from langsmith import traceable

class LLMClient:
    def __init__(self, api_key: str, model: str, system_prompt: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
        self.system_prompt = system_prompt
    
    @traceable(name="homeguru_llm_call")  # LangSmith трейсинг
    def get_response(self, messages: list) -> str:
        # Добавляем system prompt в начало
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages  # Поддержка мультимодальных сообщений
        )
        
        return response.choices[0].message.content
```

**Инициализация LangSmith в main.py:**
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = config.langsmith_api_key
os.environ["LANGCHAIN_PROJECT"] = config.langsmith_project
```

### Особенности для MVP
- Используем мультимодальную модель через OpenRouter с поддержкой Vision API
- Системный промпт загружается из файла `system_prompt.txt`
- LangSmith для автоматического трейсинга всех запросов к LLM
- Без streaming (простой синхронный запрос)
- Без обработки ошибок в первой версии
- Без настройки temperature, max_tokens и других параметров (дефолтные значения)

---

## 7. Сценарии работы

### Основные сценарии

**1. Первый запуск бота**
- Пользователь отправляет `/start`
- Бот приветствует от имени HomeGuru - ИИ-дизайнера интерьеров
- Создается новый пустой диалог для user_id

**2. Текстовый диалог по дизайну**
- Пользователь: "Какой стиль выбрать для маленькой гостиной?"
- Бот добавляет сообщение в историю
- Отправляет контекст в LLM с ролью HomeGuru
- Получает рекомендации по дизайну интерьера
- Добавляет ответ в историю

**3. Анализ фотографии интерьера**
- Пользователь отправляет фото комнаты
- MediaProcessor скачивает и обрабатывает изображение
- DialogueManager формирует мультимодальный запрос
- HomeGuru анализирует интерьер на фото
- Бот отправляет детальные рекомендации по улучшению дизайна

**4. Голосовой запрос**
- Пользователь отправляет голосовое сообщение
- MediaProcessor транскрибирует аудио в текст
- Обрабатывается как обычное текстовое сообщение
- Ответ отправляется пользователю

**5. Отображение роли**
- Пользователь отправляет `/role`
- Бот отображает информацию о роли HomeGuru (ИИ-дизайнер интерьеров)
- Перечисляет ключевые компетенции

**6. Очистка истории**
- Пользователь отправляет `/reset`
- Бот очищает историю диалога для этого пользователя
- Подтверждает очистку

### Команды бота
- `/start` - запуск бота и приветствие от HomeGuru
- `/role` - информация о роли и специализации ИИ-дизайнера
- `/reset` - очистка истории диалога
- `/help` - справка о командах и возможностях

### Возможности MVP
- ✅ Текстовые сообщения - консультации по дизайну интерьеров
- ✅ Фотографии - анализ интерьеров и рекомендации
- ✅ Голосовые сообщения - распознавание речи для удобства
- ✅ Мониторинг через LangSmith - отслеживание качества ответов
- ✅ Один активный диалог на пользователя

---

## 8. Подход к конфигурированию

### Файл .env
Все настройки в одном месте:
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# OpenRouter (мультимодальная модель)
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=<мультимодальная-модель>

# LangSmith (мониторинг)
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=homeguru

# Dialogue Settings
MAX_HISTORY_MESSAGES=20
```

**Примечание:** Системный промпт HomeGuru теперь хранится в отдельном файле `src/bot/system_prompt.txt`, а не в .env

### Класс Config
```python
from dotenv import load_dotenv
import os
from pathlib import Path

class Config:
    def __init__(self):
        load_dotenv()
        
        # Telegram
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # OpenRouter
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL")
        
        # LangSmith
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "homeguru")
        
        # System Prompt (загружается из файла)
        prompt_path = Path(__file__).parent / "system_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
        
        # Dialogue Settings
        self.max_history = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
```

### Особенности
- Один файл .env для всех настроек API
- Системный промпт в отдельном файле `system_prompt.txt` для удобства редактирования
- Никакой валидации в MVP (упадет с ошибкой, если не указано)
- Без поддержки разных окружений (dev/prod)
- .env.example в репозитории как шаблон
- .env в .gitignore
- LangSmith настраивается через переменные окружения

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
- **INFO**: Получение сообщений от пользователей (user_id, тип: текст/фото/аудио)
- **INFO**: Обработка медиа (скачивание фото, транскрибация аудио)
- **INFO**: Отправка запросов в LLM (мультимодальных)
- **INFO**: Получение ответов от LLM
- **ERROR**: Ошибки и исключения

**Дополнительно:** LangSmith автоматически логирует все запросы к LLM с детальной трейсинг информацией

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
- Загрузка системного промпта из файла
- Значения по умолчанию

**MediaProcessor** (test_media_processor.py)
- Базовая обработка изображений
- Базовая обработка аудио (моки)

**MessageHandler** (test_message_handler.py)
- Обработка текстовых сообщений
- Координация компонентов
- Обработка ошибок

**CommandHandler** (test_command_handler.py)
- Обработка всех команд
- Взаимодействие с DialogueStorage

**TelegramBot** (test_bot.py)
- Делегирование в handlers
- Отправка ответов

### Что НЕ тестируем в unit-тестах
- Реальные запросы к OpenRouter API
- Реальная транскрибация аудио
- Интеграции с Telegram API
- E2E тесты
- LangSmith трейсинг

### Запуск тестов

```bash
# Через Make (с покрытием)
make test

# Напрямую через pytest
pytest tests/ -v

# С покрытием и отчетом
pytest tests/ -v --cov=src --cov-report=html
```

### Требования к покрытию
- **Coverage ≥ 80%** - обязательная цель
- Все новые модули покрыты тестами
- Критичные пути покрыты тестами
- HTML отчет: `htmlcov/index.html`

### Использование фикстур

```python
# tests/conftest.py
import pytest

@pytest.fixture
def dialogue_manager() -> DialogueManager:
    return DialogueManager(max_history=20)

@pytest.fixture
def mock_llm_client(mocker) -> LLMClient:
    return mocker.Mock(spec=LLMClient)

# tests/test_message_handler.py
def test_process_message(dialogue_manager, mock_llm_client):
    handler = MessageHandler(mock_llm_client, dialogue_manager)
    # тест...
```

---

## 11. Качество кода

### Инструменты

**Ruff - Форматтер и Линтер:**
- Заменяет Black + Flake8 + isort
- Самый быстрый инструмент на рынке (написан на Rust)
- Автоматическое форматирование и исправление ошибок
- Конфигурация в `pyproject.toml`

**Mypy - Статическая типизация:**
- Проверка type hints в strict mode
- Предотвращает ошибки типов на этапе разработки
- Обязательная типизация всех методов и атрибутов
- Конфигурация в `pyproject.toml`

**Pytest-cov - Покрытие кода:**
- Измерение покрытия тестами
- HTML отчеты для анализа
- Цель: ≥ 80% coverage

### Конфигурация в pyproject.toml

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.3.0",
    "mypy>=1.9.0",
]

[tool.ruff]
target-version = "py311"
line-length = 100
select = ["E", "F", "I", "N", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

### Команды проверки качества

```bash
# Автоформатирование
make format

# Проверка стиля + автоисправление
make lint

# Проверка типов
make typecheck

# Запуск тестов с покрытием
make test

# Все проверки вместе
make quality
```

### Требования к качеству

**Type Hints - обязательны:**
```python
# ✅ Правильно
def get_history(self, user_id: int) -> list[dict[str, str]]:
    return self.dialogues.get(user_id, [])

# ❌ Неправильно
def get_history(self, user_id):
    return self.dialogues.get(user_id, [])
```

**SOLID Principles (разумно):**
```python
# Dependency Inversion через Protocol
from typing import Protocol

class LLMProvider(Protocol):
    def get_response(self, messages: list[dict[str, str]]) -> str: ...

class MessageHandler:
    def __init__(self, llm: LLMProvider):  # Зависимость от абстракции
        self.llm = llm
```

**Single Responsibility:**
- `TelegramBot` - только инфраструктура
- `MessageHandler` - бизнес-логика
- `CommandHandler` - команды
- Каждый класс имеет одну четкую ответственность

### Чек-лист перед коммитом

**Автоматические проверки:**
- [ ] `make format` - пройдено
- [ ] `make lint` - 0 errors
- [ ] `make typecheck` - success
- [ ] `make test` - все тесты проходят
- [ ] Coverage ≥ 80%

**Ручная проверка:**
- [ ] Код простой и понятный (KISS)
- [ ] 1 класс = 1 файл
- [ ] Все методы типизированы
- [ ] Новый код покрыт тестами
- [ ] Логирование добавлено
- [ ] Следует SOLID разумно

### Метрики качества

| Метрика | Цель | Измерение |
|---------|------|-----------|
| Test Coverage | ≥ 80% | `pytest --cov` |
| Mypy Strict | 0 errors | `mypy --strict` |
| Ruff Errors | 0 critical | `ruff check` |
| Line Length | ≤ 100 | автоматически |

---

## 12. Заключение

Данный документ описывает техническое видение MVP-версии HomeGuru - ИИ-дизайнера интерьеров. Все решения направлены на максимальную простоту реализации при сохранении ключевых мультимодальных возможностей и высокого качества кода. Следование принципам KISS, SOLID (разумно) и автоматизация проверок качества позволят быстро создать надежный прототип с конкретной специализацией.

**Ключевые особенности MVP:**
- 🎨 Специализация на дизайне интерьеров (четкая роль через системный промпт)
- 📸 Анализ фотографий интерьеров (мультимодальная LLM)
- 🎤 Голосовые сообщения (распознавание речи)
- 📊 Мониторинг качества через LangSmith
- 🚀 Простая архитектура для быстрого запуска
- ✅ Высокое качество кода (Ruff + Mypy + Coverage ≥80%)
- 🔧 Автоматизация проверок через Make
- 🧪 Type safety через strict mypy
- 🏗️ SOLID принципы (DIP через Protocol, SRP для компонентов)

**Баланс между качеством и простотой:**
- Type hints обязательны, но не усложняют код
- SOLID применяется разумно - только там, где дает реальную пользу
- Автоматические инструменты (Ruff, Mypy) освобождают от ручного контроля
- Coverage ≥80% обеспечивает уверенность в изменениях
- Простота остается главным приоритетом

