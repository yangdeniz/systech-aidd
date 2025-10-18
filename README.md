# HomeGuru - ИИ-дизайнер интерьеров 🏠

Специализированный ИИ-ассистент для дизайна интерьеров на базе больших языковых моделей с Telegram-ботом и современным веб-интерфейсом.

## 📋 О проекте

HomeGuru — это полноценная система для консультаций по дизайну и оформлению интерьеров, включающая Telegram-бота для пользователей и веб-интерфейс для администрирования. Система специализируется на консультациях по стилям, подборе цветовых решений, рекомендациях по мебели и декору, а также предоставляет аналитический дашборд и веб-чат с поддержкой text2sql запросов.

### Ключевые возможности

**Telegram Bot:**
- 🎨 **ИИ-дизайнер интерьеров** - специализированная роль через системный промпт
- 🤖 **Telegram-бот** - удобный интерфейс взаимодействия
- 💬 **Контекстный диалог** - поддержка истории сообщений
- 📸 **Анализ фотографий** - поддержка Vision API для дизайна интерьеров
- 🎤 **Голосовые сообщения** - распознавание речи через Faster-Whisper (локально)
- 💾 **Персистентное хранение** - PostgreSQL для сохранения диалогов

**Web Interface:**
- 🌐 **Современный веб-интерфейс** - Next.js 14+ с адаптивным дизайном
- 🔐 **Аутентификация и RBAC** - JWT токены, роли user/administrator
- 📊 **Дашборд статистики** - метрики, графики активности, таблицы (только для admin)
- 💬 **Веб-чат** - Normal режим (HomeGuru) и Admin режим (text2sql)
- 🔍 **Text2SQL** - вопросы на естественном языке → SQL → данные → ответ
- 🎨 **Light/Dark темы** - переключатель тем для комфортной работы

**Backend & Infrastructure:**
- 🚀 **REST API** - FastAPI с автоматической документацией
- 🧠 **Мультимодальная LLM** - работа с языковыми моделями через OpenRouter API
- ⚡ **Кэширование** - in-memory cache с TTL для производительности
- 📈 **Мониторинг LangSmith** - трейсинг качества ответов LLM
- 🗄️ **Единая база данных** - Telegram и веб-пользователи в одной таблице

## 🏗️ Архитектура

Проект следует принципам KISS, SOLID и чистой архитектуры с акцентом на качество кода:

**Telegram Bot (src/bot/):**
- **TelegramBot** - инфраструктура Telegram (aiogram, polling)
- **MessageHandler** - бизнес-логика обработки сообщений
- **CommandHandler** - обработка команд бота (/start, /reset, /help, /role)
- **DialogueManager** - управление контекстом диалогов (персистентное хранение в PostgreSQL)
- **MessageRepository** - Repository pattern для работы с сообщениями
- **UserRepository** - Repository pattern для работы с пользователями (telegram + web)
- **LLMClient** - интеграция с OpenRouter API (Vision API для фото)
- **MediaProcessor** - обработка фотографий и голосовых (Faster-Whisper)
- **Config** - управление конфигурацией из .env
- **Interfaces** - Protocol для Dependency Inversion (SOLID DIP)
- **Models** - SQLAlchemy ORM модели (Message, User с двумя типами)
- **Database** - async engine и session factory для PostgreSQL

**REST API (src/api/):**
- **FastAPI Application** - REST API сервер с автодокументацией
- **AuthService** - веб-аутентификация (регистрация, вход, JWT токены)
- **RBAC Middleware** - контроль доступа по ролям (user/administrator)
- **ChatService** - веб-чат с LLM (Normal и Admin режимы)
- **StatCollector** - сбор статистики (Mock/Real реализации с Factory pattern)
- **Cache** - in-memory кэширование статистики с TTL 60 секунд
- **Text2SQL** - преобразование вопросов в SQL запросы для админ режима
- **Models** - Pydantic модели для API контрактов

**Frontend (frontend/app/):**
- **Next.js 14+ App Router** - SSR, оптимизация производительности
- **Pages** - login, register, admin/dashboard, admin/chat, user/chat
- **Dashboard Components** - MetricCard, ActivityChart, RecentDialogues, TopUsers
- **Chat Components** - ChatButton, ChatWindow, MessageList, Message, ModeToggle
- **AuthContext** - управление аутентификацией (JWT в localStorage)
- **React Query** - управление server state и кэширование
- **shadcn/ui** - современные UI компоненты с Tailwind CSS
- **API Client** - HTTP клиент с автоматическим добавлением JWT токенов

**Shared Components:**
- **Database Layer** - PostgreSQL с Alembic миграциями
- **Models (ORM)** - единая таблица users для telegram и web пользователей
- **LLMClient** - используется как ботом, так и веб-чатом

## 🛠️ Технологии

**Backend:**
- **Python 3.11+** - язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API
- **FastAPI** - современный веб-фреймворк для REST API
- **openai** - клиент для работы с OpenRouter (мультимодальные модели)
- **faster-whisper** - локальная транскрибация аудио (Speech-to-Text)
- **python-dotenv** - управление переменными окружения
- **PostgreSQL 16** - персистентное хранение диалогов
- **SQLAlchemy 2.0+ ORM** - async ORM для работы с БД
- **Alembic** - миграции базы данных
- **bcrypt** - хеширование паролей
- **PyJWT** - JWT токены для аутентификации
- **Docker** - контейнеризация PostgreSQL

**Frontend:**
- **Next.js 14+** - React фреймворк с App Router и SSR
- **React 19** - библиотека для построения UI
- **TypeScript** - статическая типизация для JavaScript
- **Tailwind CSS** - utility-first CSS фреймворк
- **shadcn/ui** - современная UI библиотека компонентов
- **React Query (TanStack Query)** - управление server state
- **Recharts** - библиотека для графиков и визуализации
- **pnpm** - быстрый пакетный менеджер

**Качество кода (Backend):**
- **ruff** - форматтер и линтер (заменяет Black + Flake8 + isort)
- **mypy** - статическая проверка типов (strict mode)
- **pytest** - фреймворк для тестирования
- **pytest-cov** - измерение покрытия кода
- **pytest-asyncio** - тестирование async кода
- **Make** - автоматизация задач проверки качества

**Качество кода (Frontend):**
- **TypeScript** - type safety на фронтенде
- **ESLint** - линтер для JavaScript/TypeScript
- **Prettier** - форматтер кода
- **Jest** - фреймворк для тестирования
- **React Testing Library** - тестирование React компонентов

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
   
   # Database (PostgreSQL)
   DATABASE_URL=postgresql+asyncpg://homeguru:homeguru_dev@localhost:5432/homeguru
   
   # OpenRouter (мультимодальная модель)
   OPENROUTER_API_KEY=ваш_openrouter_ключ
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   
   # Dialogue Settings
   MAX_HISTORY_MESSAGES=20
   
   # Faster-Whisper (Speech-to-Text, локальная обработка)
   WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
   WHISPER_DEVICE=cpu  # Options: cpu, cuda
   
   # API Settings
   COLLECTOR_MODE=real  # Options: mock, real
   ADMIN_PASSWORD=admin123  # Пароль для Admin режима чата
   
   # Web Auth Settings
   JWT_SECRET_KEY=your-secret-key-here  # Секрет для JWT токенов
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_DAYS=30
   
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
   
   Системные промпты хранятся в файлах:
   - `src/bot/system_prompt.txt` - промпт для HomeGuru (дизайнер интерьеров)
   - `src/api/text2sql_prompt.txt` - промпт для text2sql режима
   
   При необходимости отредактируйте их для изменения роли и поведения.

6. **Запуск приложений**
   
   **Telegram Bot:**
   ```bash
   make run
   ```
   
   **REST API (в отдельном терминале):**
   ```bash
   make api-run-real  # Запуск с реальной статистикой из БД
   # или
   make api-run-mock  # Запуск с фейковой статистикой (для разработки)
   ```
   API будет доступно на http://localhost:8000
   Документация API: http://localhost:8000/docs
   
   **Frontend (в отдельном терминале):**
   ```bash
   cd frontend/app
   pnpm install  # Первый раз
   pnpm dev
   ```
   Веб-интерфейс будет доступен на http://localhost:3000

7. **Создание администратора**
   
   Для доступа к дашборду создайте администратора через миграцию или зарегистрируйтесь на странице /register и обновите роль в БД:
   ```sql
   UPDATE users SET role = 'administrator' WHERE username = 'your_username';
   ```

### Доступные команды Make

**Разработка:**
- `make install` - установка всех зависимостей (включая dev)
- `make run` - запуск Telegram бота
- `make api-run-real` - запуск API с реальной статистикой
- `make api-run-mock` - запуск API с фейковой статистикой

**Проверка качества (Backend):**
- `make format` - автоформатирование кода (Ruff)
- `make lint` - проверка стиля и автоисправление (Ruff)
- `make typecheck` - проверка типов (Mypy strict mode)
- `make test` - запуск тестов с покрытием (Pytest + coverage)
- `make quality` - все проверки качества вместе

**Проверка качества (Frontend):**
```bash
cd frontend/app
pnpm lint        # ESLint проверка
pnpm format      # Prettier форматирование
pnpm type-check  # TypeScript проверка
pnpm test        # Jest тесты
pnpm test:coverage  # Тесты с покрытием
```

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

## 🎯 Применение и возможности

**Для пользователей (Telegram Bot):**
- **Консультации по стилям интерьера** - помощь в выборе стиля (скандинавский, лофт, минимализм, классика и др.)
- **Подбор цветовых решений** - рекомендации по цветовым палитрам для помещений
- **Анализ фотографий интерьеров** - оценка дизайна на фото и предложения по улучшению с помощью Vision API
- **Рекомендации по мебели и декору** - советы по выбору и расположению предметов интерьера
- **Планирование пространства** - идеи по оптимизации использования помещений
- **Голосовые консультации** - распознавание речи через Faster-Whisper (локальная модель, без внешних API)

**Для администраторов (Web Interface):**
- **Дашборд статистики** - мониторинг использования бота (метрики, графики, таблицы)
- **Аналитика пользователей** - топ пользователей, активность по периодам
- **Веб-чат с HomeGuru** - консультации через браузер (Normal режим)
- **Text2SQL запросы** - вопросы о статистике на естественном языке (Admin режим)
- **Управление пользователями** - просмотр и анализ активности

**Для обычных веб-пользователей:**
- **Веб-чат с HomeGuru** - доступ к ИИ-дизайнеру через браузер
- **История диалогов** - сохранение и продолжение разговоров
- **Адаптивный интерфейс** - удобная работа с любого устройства

## 📝 Принципы разработки

- **KISS** - максимальная простота реализации
- **TDD** - тесты перед кодом (RED-GREEN-REFACTOR)
- **SOLID** - применяем разумно (SRP, DIP через Protocol)
- **Type Safety** - type hints обязательны (mypy strict mode + TypeScript)
- **Clean Architecture** - четкое разделение: bot/, api/, frontend/
- **ООП** - правило "1 класс = 1 файл" для backend
- **Component-Based** - компонентный подход для frontend
- **Качество кода** - автоматизированные проверки (Ruff, Mypy, ESLint, Prettier)
- **High Coverage** - backend ≥80%, frontend ≥75%
- **Repository Pattern** - для работы с данными
- **Async Everywhere** - асинхронность на всех уровнях

## 📊 Статус разработки

**Backend (Telegram Bot):**
| Спринт | Задача | Статус |
|----------|--------|--------|
| Sprint-0 | Базовая функциональность (бот + LLM + диалоги) | ✅ Завершено |
| Sprint-1 | Персистентное хранение (PostgreSQL + SQLAlchemy + Alembic) | ✅ Завершено |
| Sprint-2 | User management и Repository pattern | ✅ Завершено |
| Sprint-3 | Системный промпт HomeGuru | ✅ Завершено |
| Sprint-4 | Обработка фотографий (Vision API) | ✅ Завершено |
| Sprint-5 | Обработка аудио (Faster-Whisper) | ✅ Завершено |

**Backend (REST API):**
| Спринт | Задача | Статус |
|----------|--------|--------|
| F-Sprint-1 | Mock API для статистики | ✅ Завершено |
| F-Sprint-4 | Chat API (Normal/Admin режимы, text2sql) | ✅ Завершено |
| F-Sprint-5 | Real API с PostgreSQL и кэшированием | ✅ Завершено |
| F-Sprint-6 | Аутентификация и RBAC | ✅ Завершено |

**Frontend:**
| Спринт | Задача | Статус |
|----------|--------|--------|
| F-Sprint-2 | Инициализация Next.js проекта | ✅ Завершено |
| F-Sprint-3 | Dashboard со статистикой | ✅ Завершено |
| F-Sprint-4 | Веб-чат с LLM | ✅ Завершено |
| F-Sprint-6 | Login/Register, RBAC роутинг | ✅ Завершено |

**Tech Debt (улучшение качества):**
| Итерация | Задача | Статус |
|----------|--------|--------|
| TD-1 до TD-5 | Качество кода (Ruff, Mypy, Coverage, SOLID) | ✅ Завершено |

**Метрики качества:**

*Backend:*
- ✅ Test Coverage: **85-90%** (цель ≥80%)
- ✅ Mypy Strict: **0 errors**
- ✅ Ruff: **All checks passed**
- ✅ Tests: **150+ passed** (bot + API)

*Frontend:*
- ✅ Test Coverage: **79%** (цель ≥75%)
- ✅ TypeScript: **0 errors**
- ✅ ESLint: **All checks passed**
- ✅ Tests: **29+ passed**

**Roadmaps:**
- Backend: [`docs/roadmap.md`](docs/roadmap.md)
- Frontend: [`frontend/doc/frontend-roadmap.md`](frontend/doc/frontend-roadmap.md)
- Планы спринтов: [`docs/plans/`](docs/plans/)

## 📄 Лицензия

Этот проект разрабатывается для внутреннего использования.

---

**Проект:** HomeGuru - ИИ-дизайнер интерьеров  
**Статус:** Production Ready - полноценная система с Telegram ботом, REST API и веб-интерфейсом  
**Возможности:** Telegram бот (текст + фото + аудио) • Веб-дашборд • Веб-чат • Text2SQL • RBAC
