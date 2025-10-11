# Техническое видение проекта: HomeGuru - ИИ-дизайнер интерьеров

## 1. Технологии

### Основные технологии
- **Python 3.11+** - базовый язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API (метод polling)
- **openai** - клиент для работы с OpenRouter API (мультимодальные модели)
- **langsmith** - мониторинг и трейсинг LLM запросов
- **python-dotenv** - управление переменными окружения (.env файлы)
- **pytest** - фреймворк для юнит-тестирования
- **Make** - автоматизация задач сборки и запуска

### Обоснование выбора
- Минимальный набор зависимостей для быстрого старта MVP
- Проверенные и стабильные библиотеки
- Простота в использовании и развертывании
- Мультимодальные возможности OpenRouter для работы с изображениями
- LangSmith для мониторинга качества ответов ИИ-дизайнера

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
│       ├── llm_client.py        # LLMClient класс (мультимодальный)
│       ├── dialogue_manager.py  # DialogueManager класс
│       ├── config.py            # Config класс
│       ├── media_processor.py   # MediaProcessor класс (фото/аудио)
│       └── system_prompt.txt    # Системный промпт HomeGuru
├── tests/
│   ├── __init__.py
│   ├── test_dialogue_manager.py
│   ├── test_llm_client.py
│   ├── test_config.py
│   └── test_media_processor.py
├── docs/
│   ├── idea.md                  # Концепция HomeGuru
│   ├── vision.md                # Техническое видение
│   ├── tasklist.md              # План разработки
│   ├── conventions.md           # Соглашения
│   ├── workflow.md              # Процесс работы
│   └── addrs/
│       └── ADR-01.md            # Архитектурное решение
├── .env                         # Переменные окружения (не в git)
├── .env.example                 # Пример .env файла
├── .gitignore
├── pyproject.toml               # Конфигурация uv/проекта
├── Makefile                     # Команды для запуска
└── README.md
```

### Описание модулей
- **main.py** - точка входа, запуск приложения, настройка LangSmith
- **bot.py** - обработка Telegram сообщений: текст, фото, аудио (aiogram)
- **llm_client.py** - работа с мультимодальными моделями через OpenRouter
- **dialogue_manager.py** - управление контекстом диалогов (in-memory)
- **config.py** - загрузка конфигурации из .env и системного промпта из файла
- **media_processor.py** - обработка изображений и аудио (загрузка, конвертация)
- **system_prompt.txt** - системный промпт с ролью HomeGuru (ИИ-дизайнер)

### Принципы организации
- 1 класс = 1 файл
- Простая плоская структура без вложенных пакетов
- 6 основных модулей для MVP
- Системный промпт вынесен в отдельный файл для удобства редактирования

---

## 4. Архитектура проекта

### Основные компоненты и их взаимодействие

```
User (Telegram: текст/фото/аудио) 
    ↓
TelegramBot (aiogram)
    ↓
MediaProcessor (обработка фото/аудио)
    ↓
DialogueManager (контекст диалогов)
    ↓
LLMClient (OpenRouter API + LangSmith)
    ↓
Response → User
```

### Описание компонентов

**1. TelegramBot** (bot.py)
- Получает сообщения от пользователей: текст, фото, голосовые (polling)
- Обрабатывает команды: /start, /reset, /help, /role
- Передает в MediaProcessor для обработки медиа
- Передает в DialogueManager для формирования контекста
- Отправляет ответы обратно пользователю

**2. MediaProcessor** (media_processor.py)
- Скачивает фотографии из Telegram
- Скачивает и транскрибирует голосовые сообщения
- Конвертирует медиа в формат для отправки в LLM
- Возвращает обработанные данные

**3. DialogueManager** (dialogue_manager.py)
- Хранит историю диалогов в памяти (dict: user_id → messages)
- Формирует контекст для LLM (system prompt из файла + история + медиа)
- Вызывает LLMClient для получения ответа
- Обновляет историю диалога

**4. LLMClient** (llm_client.py)
- Отправляет мультимодальные запросы в OpenRouter API
- Использует openai client для работы с моделями, поддерживающими Vision
- Интегрирован с LangSmith для мониторинга всех запросов
- Возвращает ответ от LLM

**5. Config** (config.py)
- Загружает настройки из .env
- Загружает системный промпт из system_prompt.txt
- Предоставляет конфигурацию всем модулям

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

### Что НЕ тестируем в MVP
- TelegramBot (интеграция с aiogram)
- Реальные запросы к OpenRouter API
- Реальная транскрибация аудио
- Интеграционные тесты
- E2E тесты
- LangSmith трейсинг

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

Данный документ описывает техническое видение MVP-версии HomeGuru - ИИ-дизайнера интерьеров. Все решения направлены на максимальную простоту реализации при сохранении ключевых мультимодальных возможностей. Следование принципам KISS и отказ от оверинжиниринга позволят быстро создать рабочий прототип с конкретной специализацией и получить первый пользовательский опыт.

**Ключевые особенности MVP:**
- 🎨 Специализация на дизайне интерьеров (четкая роль через системный промпт)
- 📸 Анализ фотографий интерьеров (мультимодальная LLM)
- 🎤 Голосовые сообщения (распознавание речи)
- 📊 Мониторинг качества через LangSmith
- 🚀 Простая архитектура для быстрого запуска

