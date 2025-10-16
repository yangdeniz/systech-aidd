# HomeGuru - ИИ-дизайнер интерьеров 🏠

Специализированный ИИ-ассистент для дизайна интерьеров на базе больших языковых моделей, реализованный в виде Telegram-бота.

## 📋 О проекте

HomeGuru — это MVP (Minimum Viable Product) Telegram-бота, который помогает пользователям в вопросах дизайна и оформления интерьеров. Бот специализируется на консультациях по стилям, подборе цветовых решений, рекомендациях по мебели и декору.

### Ключевые особенности

- 🎨 **ИИ-дизайнер интерьеров** - специализированная роль через системный промпт
- 🤖 **Telegram-бот** - удобный интерфейс взаимодействия
- 🧠 **Мультимодальная LLM** - работа с языковыми моделями через OpenRouter API
- 💬 **Контекстный диалог** - поддержка истории сообщений
- ⚡ **Простая архитектура** - минималистичный MVP-подход
- 💾 **Персистентное хранение** - PostgreSQL для сохранения диалогов между перезапусками
- 📸 **Анализ фотографий** - поддержка Vision API для дизайна интерьеров
- 🎤 **Голосовые сообщения** - распознавание речи через Faster-Whisper (локально)
- 📊 **Мониторинг LangSmith** - трейсинг качества ответов (в разработке)

## 🏗️ Архитектура

Проект следует принципам KISS, SOLID и MVP-подхода с акцентом на качество кода:

**Текущая реализация:**
- **TelegramBot** - инфраструктура Telegram (aiogram, polling)
- **MessageHandler** - бизнес-логика обработки сообщений
- **CommandHandler** - обработка команд бота
- **DialogueManager** - управление контекстом диалогов (персистентное хранение в PostgreSQL)
- **MessageRepository** - Repository pattern для работы с сообщениями
- **UserRepository** - Repository pattern для работы с пользователями
- **LLMClient** - интеграция с OpenRouter API (Vision API для фото)
- **MediaProcessor** - обработка фотографий и голосовых (Faster-Whisper)
- **Config** - управление конфигурацией из .env
- **Interfaces** - Protocol для Dependency Inversion (SOLID DIP)
- **Models** - SQLAlchemy ORM модели (Message, User с relationships)
- **Database** - engine и session factory для PostgreSQL

**В разработке (Sprint-3):**
- **LangSmith Integration** - мониторинг и трейсинг запросов к LLM

## 🛠️ Технологии

**Основные:**
- **Python 3.11+** - язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API
- **openai** - клиент для работы с OpenRouter (мультимодальные модели)
- **faster-whisper** - локальная транскрибация аудио (Speech-to-Text)
- **python-dotenv** - управление переменными окружения
- **PostgreSQL 16** - персистентное хранение диалогов
- **SQLAlchemy 2.0+ ORM** - async ORM для работы с БД
- **Alembic** - миграции базы данных
- **Docker** - контейнеризация PostgreSQL

**Качество кода:**
- **ruff** - форматтер и линтер (заменяет Black + Flake8 + isort)
- **mypy** - статическая проверка типов (strict mode)
- **pytest** - фреймворк для тестирования
- **pytest-cov** - измерение покрытия кода
- **pytest-asyncio** - тестирование async кода
- **Make** - автоматизация задач проверки качества

## 📚 Документация

Подробная документация проекта находится в директории `docs/`:

**Практические гайды:** [`docs/guides/`](docs/guides/)
- 🚀 [Getting Started](docs/guides/01-getting-started.md) - установка и запуск за 15 минут
- 👨‍💻 [Developer Quickstart](docs/guides/02-developer-quickstart.md) - первый день разработчика
- 🏗 [Architecture Overview](docs/guides/03-architecture-overview.md) - обзор архитектуры с диаграммами
- 📊 [Visual System Overview](docs/guides/04-visual-system-overview.md) - 13 диаграмм системы
- ⚙️ [Configuration Guide](docs/guides/07-configuration.md) - настройка и секреты

**Основные документы:**
- [`docs/idea.md`](docs/idea.md) - концепция HomeGuru и основные идеи
- [`docs/vision.md`](docs/vision.md) - техническое видение и детальная спецификация
- [`docs/roadmap.md`](docs/roadmap.md) - roadmap проекта по спринтам
- [`docs/conventions.md`](docs/conventions.md) - соглашения и принципы разработки
- [`docs/workflow.md`](docs/workflow.md) - процесс выполнения работ

**Подпапки:**
- [`docs/tasklists/`](docs/tasklists/) - тасклисты спринтов (Sprint-0, Sprint-1, ...)
- [`docs/reports/`](docs/reports/) - отчеты о выполненных работах (tech debt)
- [`docs/reviews/`](docs/reviews/) - результаты code review проекта
- [`docs/addrs/`](docs/addrs/) - архитектурные решения (Architecture Decision Records)
  - [ADR-01: Архитектура HomeGuru MVP](docs/addrs/ADR-01.md) - монолитная архитектура с мультимодальностью
  - [ADR-02: Выбор Faster-Whisper для распознавания речи](docs/addrs/ADR-02.md) - локальное Speech-to-Text
  - [ADR-03: PostgreSQL + SQLAlchemy ORM для персистентного хранения](docs/addrs/ADR-03.md) - база данных для диалогов

## ⚙️ Установка и запуск

### Предварительные требования

- Python 3.11 или выше
- [uv](https://github.com/astral-sh/uv) - менеджер пакетов и зависимостей
- [Docker](https://www.docker.com/) - для запуска PostgreSQL
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- OpenRouter API Key (получить на [openrouter.ai](https://openrouter.ai))
- LangSmith API Key (опционально, для мониторинга - получить на [smith.langchain.com](https://smith.langchain.com))

### Быстрый старт

1. **Клонирование репозитория**
   ```bash
   git clone <repository-url>
   cd systech-aidd
   ```

2. **Установка зависимостей**
   ```bash
   make install
   ```

3. **Настройка переменных окружения**
   
   Создайте файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```
   
   Заполните необходимые переменные в `.env`:
   ```env
   # Telegram Bot
   TELEGRAM_BOT_TOKEN=ваш_telegram_токен
   
   # OpenRouter (мультимодальная модель)
   OPENROUTER_API_KEY=ваш_openrouter_ключ
   OPENROUTER_MODEL=google/gemini-pro-1.5
   
   # Dialogue Settings
   MAX_HISTORY_MESSAGES=20
   
   # Faster-Whisper (Speech-to-Text, локальная обработка)
   WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
   WHISPER_DEVICE=cpu  # Options: cpu, cuda
   
   # Database (PostgreSQL)
   DATABASE_URL=postgresql+asyncpg://homeguru:homeguru_dev@localhost:5432/homeguru
   
   # LangSmith (опционально, для мониторинга)
   LANGSMITH_API_KEY=ваш_langsmith_ключ
   LANGSMITH_PROJECT=homeguru
   ```

4. **Запуск PostgreSQL**
   
   Запустите PostgreSQL в Docker:
   ```bash
   make db-up
   ```
   
   Примените миграции базы данных:
   ```bash
   make db-migrate
   ```

5. **Настройка системного промпта**
   
   Системный промпт HomeGuru хранится в файле `src/bot/system_prompt.txt`.
   При необходимости отредактируйте его для изменения роли и поведения бота.

6. **Запуск бота**
   ```bash
   make run
   ```

### Доступные команды Make

**Разработка:**
- `make install` - установка всех зависимостей (включая dev)
- `make run` - запуск бота

**Проверка качества:**
- `make format` - автоформатирование кода (Ruff)
- `make lint` - проверка стиля и автоисправление (Ruff)
- `make typecheck` - проверка типов (Mypy strict mode)
- `make test` - запуск тестов с покрытием (Pytest + coverage)
- `make quality` - все проверки качества вместе

**Управление базой данных:**
- `make db-up` - запустить PostgreSQL в Docker
- `make db-down` - остановить PostgreSQL
- `make db-migrate` - применить миграции
- `make db-revision MSG="description"` - создать новую миграцию
- `make db-reset` - сбросить БД и применить миграции заново

## 🚀 Команды бота

- `/start` - запуск бота и приветствие от HomeGuru
- `/role` - информация о роли и специализации ИИ-дизайнера
- `/reset` - очистка истории диалога
- `/help` - справка о командах и возможностях

## 🎯 Применение

HomeGuru специализируется на дизайне интерьеров и предоставляет:

- **Консультации по стилям интерьера** - помощь в выборе стиля (скандинавский, лофт, минимализм, классика и др.)
- **Подбор цветовых решений** - рекомендации по цветовым палитрам для помещений
- **Анализ фотографий интерьеров** - оценка дизайна на фото и предложения по улучшению с помощью Vision API
- **Рекомендации по мебели и декору** - советы по выбору и расположению предметов интерьера
- **Планирование пространства** - идеи по оптимизации использования помещений
- **Голосовые консультации** - распознавание речи через Faster-Whisper (локальная модель, без внешних API)

## 📝 Принципы разработки

- **KISS** - максимальная простота
- **MVP** - только необходимый функционал
- **SOLID** - применяем разумно (SRP, DIP через Protocol)
- **Type Safety** - type hints обязательны, mypy strict mode
- **ООП** - правило "1 класс = 1 файл"
- **Без оверинжиниринга** - не решаем проблемы, которых еще нет
- **Качество кода** - автоматизированные проверки (Ruff, Mypy, Coverage ≥80%)

## 📊 Статус разработки

**Основная функциональность:**
| Итерация | Задача | Статус |
|----------|--------|--------|
| 1-5 | Базовая функциональность (бот + LLM + диалоги + логирование) | ✅ Завершено |
| 6 | Системный промпт HomeGuru | ✅ Завершено |
| 7 | Обработка фотографий (Vision API) | ✅ Завершено |
| 8 | Обработка аудио (Faster-Whisper) | ✅ Завершено |
| 9 | Мониторинг LangSmith | ⏳ В планах |

**Tech Debt (улучшение качества):**
| Итерация | Задача | Статус |
|----------|--------|--------|
| TD-1 | Автоматизация контроля качества (Ruff, Mypy, Pytest) | ✅ Завершено |
| TD-2 | Type hints и статическая типизация | ✅ Завершено |
| TD-3 | Расширение покрытия тестами (98%) | ✅ Завершено |
| TD-4 | Protocol для Dependency Inversion (SOLID DIP) | ✅ Завершено |
| TD-5 | Рефакторинг по Single Responsibility (SOLID SRP) | ✅ Завершено |

**Метрики качества:**
- ✅ Test Coverage: **98%** (цель ≥80%)
- ✅ Mypy Strict: **0 errors**
- ✅ Ruff: **All checks passed**
- ✅ Tests: **66 passed**

Подробные планы спринтов см. в [`docs/tasklists/`](docs/tasklists/)  
Отчет о выполненных улучшениях см. в [`docs/reports/tech_debt_report.md`](docs/reports/tech_debt_report.md)

## 📄 Лицензия

Этот проект разрабатывается для внутреннего использования.

---

**Проект:** HomeGuru - ИИ-дизайнер интерьеров  
**Статус:** MVP - мультимодальная функциональность готова (текст + фото + аудио)
