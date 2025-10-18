# Техническое видение проекта: HomeGuru - ИИ-дизайнер интерьеров

## 1. Технологии

### Backend технологии
- **Python 3.11+** - базовый язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API (метод polling)
- **FastAPI** - современный веб-фреймворк для REST API
- **PostgreSQL** + **SQLAlchemy 2.0+** - персистентное хранение данных с async ORM
- **Alembic** - миграции базы данных
- **openai** - клиент для работы с OpenRouter API (мультимодальные модели)
- **faster-whisper** - локальная модель распознавания речи (base модель)
- **langsmith** - мониторинг и трейсинг LLM запросов
- **python-dotenv** - управление переменными окружения (.env файлы)
- **pytest** + **pytest-asyncio** + **pytest-cov** - тестирование и покрытие кода
- **ruff** - форматтер и линтер (заменяет Black + Flake8 + isort)
- **mypy** - статическая проверка типов
- **Make** - автоматизация задач сборки, запуска и проверки качества

### Frontend технологии
- **Next.js 14+** - React фреймворк с App Router
- **TypeScript** - статическая типизация для JavaScript
- **React Query (TanStack Query)** - управление server state
- **shadcn/ui** - современная UI библиотека с Tailwind CSS
- **Tailwind CSS** - utility-first CSS фреймворк
- **Jest** + **React Testing Library** - тестирование компонентов
- **ESLint** + **Prettier** - форматтер и линтер
- **pnpm** - быстрый пакетный менеджер

### Обоснование выбора
- **Backend**: проверенные и стабильные библиотеки для быстрой разработки
- **FastAPI**: высокая производительность, автоматическая документация API
- **PostgreSQL**: надежная СУБД с поддержкой JSONB для мультимодального контента
- **Next.js**: SSR, оптимизация производительности, отличный DX
- **TypeScript**: type safety на фронтенде для предотвращения ошибок
- **React Query**: декларативное управление асинхронным состоянием
- **shadcn/ui**: гибкие, кастомизируемые компоненты с современным дизайном
- Мультимодальные возможности OpenRouter для работы с изображениями
- Faster-Whisper base - быстрая и точная локальная транскрибация без внешних API
- LangSmith для мониторинга качества ответов ИИ-дизайнера
- Ruff - быстрейший форматтер/линтер на рынке (вместо множества инструментов)
- Mypy strict mode - предотвращение багов на этапе разработки
- Автоматизация через Make для единообразия проверок качества

---

## 2. Принципы разработки

### Главные принципы
- **KISS (Keep It Simple, Stupid)** - максимальная простота во всём
- **TDD (Test-Driven Development)** - тесты перед кодом, RED-GREEN-REFACTOR циклы
- **MVP-подход** - только необходимый функционал для проверки идеи
- **ООП с правилом "1 класс = 1 файл"** - чистая структура кода
- **Никакого оверинжиниринга** - не решаем проблемы, которых еще нет
- **Type Safety** - type hints обязательны, mypy strict mode
- **SOLID (разумно)** - применяем SRP и DIP через Protocol, без фанатизма

### Практическое применение
- **TDD обязателен** - тесты пишутся ПЕРЕД кодом (RED → GREEN → REFACTOR)
- Каждая итерация начинается с согласования архитектуры и плана тестов
- Один модуль = одна ответственность (SRP)
- Простые и понятные имена классов и методов
- Минимум абстракций - Protocol только для ключевых зависимостей (DIP)
- Код должен быть понятен без документации (но с type hints)
- Персистентное хранение (PostgreSQL + SQLAlchemy ORM + Alembic)
- Асинхронная обработка через aiogram, async SQLAlchemy и FastAPI
- Все методы типизированы - параметры и возвращаемые значения
- Автоматические проверки качества через `make quality`
- REST API с автоматической документацией (FastAPI)
- Современный веб-интерфейс с адаптивным дизайном (Next.js + Tailwind CSS)

---

## 3. Структура проекта

### Организация файлов и директорий

> **Примечание:** Структура отражает текущее состояние после завершения всех спринтов, включая фронтенд (обновлено 2025-10-18).

```
systech-aidd/
├── src/
│   ├── bot/                     # Telegram Bot приложение
│   │   ├── __init__.py
│   │   ├── main.py              # Точка входа
│   │   ├── bot.py               # TelegramBot класс (инфраструктура)
│   │   ├── message_handler.py   # MessageHandler класс (бизнес-логика) 
│   │   ├── command_handler.py   # CommandHandler класс (команды)
│   │   ├── llm_client.py        # LLMClient класс (мультимодальный)
│   │   ├── dialogue_manager.py  # DialogueManager класс
│   │   ├── repository.py        # Repository pattern (MessageRepository, UserRepository)
│   │   ├── models.py            # SQLAlchemy ORM модели (User, Message)
│   │   ├── database.py          # Фабрика engine и session
│   │   ├── config.py            # Config класс
│   │   ├── interfaces.py        # Protocol интерфейсы (DIP)
│   │   ├── media_processor.py   # MediaProcessor класс (фото/аудио)
│   │   └── system_prompt.txt    # Системный промпт HomeGuru
│   └── api/                     # FastAPI REST API
│       ├── __init__.py
│       ├── main.py              # FastAPI приложение (точка входа)
│       ├── models.py            # Pydantic модели для статистики
│       ├── auth_models.py       # Pydantic модели для аутентификации
│       ├── chat_models.py       # Pydantic модели для чата
│       ├── auth.py              # JWT аутентификация для чата
│       ├── auth_service.py      # Сервис веб-аутентификации
│       ├── middleware.py        # RBAC middleware
│       ├── chat_service.py      # Сервис веб-чата с LLM
│       ├── collectors.py        # StatCollector интерфейс и реализации
│       ├── cache.py             # In-memory кэширование
│       ├── config.py            # Конфигурация API
│       ├── dependencies.py      # Dependency injection для FastAPI
│       ├── text2sql_prompt.txt  # Промпт для text2sql режима
│       └── examples.http        # HTTP примеры запросов
├── frontend/
│   └── app/                     # Next.js приложение
│       ├── src/
│       │   ├── app/             # App Router (страницы)
│       │   │   ├── layout.tsx   # Root layout
│       │   │   ├── page.tsx     # Главная страница (routing logic)
│       │   │   ├── login/       # Страница входа
│       │   │   ├── register/    # Страница регистрации
│       │   │   ├── admin/       # Админ интерфейс
│       │   │   │   ├── dashboard/  # Дашборд статистики
│       │   │   │   └── chat/       # Админ чат
│       │   │   └── user/        # Пользовательский интерфейс
│       │   │       └── chat/    # Чат пользователя
│       │   ├── components/      # React компоненты
│       │   │   ├── dashboard/   # Компоненты дашборда
│       │   │   ├── chat/        # Компоненты чата
│       │   │   ├── layout/      # Layout компоненты
│       │   │   ├── providers/   # Context провайдеры
│       │   │   └── ui/          # shadcn/ui компоненты
│       │   ├── contexts/        # React contexts
│       │   │   └── AuthContext.tsx  # Аутентификация
│       │   ├── hooks/           # Custom React hooks
│       │   ├── lib/             # Утилиты и API клиент
│       │   └── types/           # TypeScript типы
│       ├── public/              # Статические файлы
│       ├── package.json         # npm зависимости
│       ├── tsconfig.json        # TypeScript конфигурация
│       ├── tailwind.config.js   # Tailwind CSS конфигурация
│       ├── jest.config.js       # Jest конфигурация
│       └── next.config.ts       # Next.js конфигурация
├── tests/
│   ├── bot/                     # Тесты Telegram бота
│   │   ├── conftest.py
│   │   ├── test_bot.py
│   │   ├── test_message_handler.py
│   │   ├── test_command_handler.py
│   │   ├── test_dialogue_manager.py
│   │   ├── test_llm_client.py
│   │   ├── test_config.py
│   │   ├── test_media_processor.py
│   │   └── test_user_repository.py
│   └── api/                     # Тесты REST API
│       ├── conftest.py
│       ├── test_api.py
│       ├── test_auth.py
│       ├── test_chat_endpoints.py
│       ├── test_chat_service.py
│       ├── test_collectors.py
│       ├── test_cache.py
│       ├── test_config.py
│       └── test_real_collector.py
├── migrations/                  # Alembic миграции
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── docs/
│   ├── idea.md                  # Концепция HomeGuru
│   ├── vision.md                # Техническое видение
│   ├── roadmap.md               # Roadmap проекта
│   ├── conventions.md           # Соглашения
│   ├── workflow.md              # Процесс работы
│   ├── plans/                   # Планы спринтов
│   ├── reports/                 # Отчеты о выполненных работах
│   ├── reviews/                 # Результаты code review
│   └── addrs/                   # Архитектурные решения (ADR)
├── .env                         # Переменные окружения (не в git)
├── .env.example                 # Пример .env файла
├── .gitignore
├── alembic.ini                  # Конфигурация Alembic
├── docker-compose.yml           # Docker Compose для PostgreSQL
├── pyproject.toml               # Конфигурация uv/проекта + инструменты качества
├── Makefile                     # Команды: run, test, format, lint, typecheck, quality
└── README.md
```

### Описание модулей

**Backend (Telegram Bot):**
- **main.py** - точка входа Telegram бота, запуск приложения, создание компонентов
- **bot.py** - инфраструктура Telegram (aiogram), делегирование в handlers
- **message_handler.py** - бизнес-логика обработки сообщений
- **command_handler.py** - обработка команд бота (/start, /reset, /help, /role)
- **llm_client.py** - работа с мультимодальными моделями через OpenRouter
- **dialogue_manager.py** - управление контекстом диалогов через Repository
- **repository.py** - Repository pattern (MessageRepository, UserRepository)
- **models.py** - SQLAlchemy ORM модели (Message, User с relationships)
- **database.py** - фабрика engine и session для PostgreSQL
- **config.py** - загрузка конфигурации из .env с валидацией
- **interfaces.py** - Protocol интерфейсы (LLMProvider, DialogueStorage, MediaProvider, UserStorage)
- **media_processor.py** - обработка фотографий и аудио через Faster-Whisper
- **system_prompt.txt** - системный промпт с ролью HomeGuru (ИИ-дизайнер)

**Backend (REST API):**
- **api/main.py** - FastAPI приложение, точка входа REST API
- **api/models.py** - Pydantic модели для статистики (StatsResponse, MetricCard, TimeSeriesPoint и др.)
- **api/auth_models.py** - Pydantic модели для аутентификации (RegisterRequest, LoginRequest, AuthResponse)
- **api/chat_models.py** - Pydantic модели для веб-чата (ChatRequest, ChatResponse)
- **api/auth.py** - JWT аутентификация для чата (создание и проверка токенов)
- **api/auth_service.py** - сервис веб-аутентификации (регистрация, вход, проверка токена)
- **api/middleware.py** - RBAC middleware для защиты endpoints по ролям
- **api/chat_service.py** - сервис веб-чата с LLM (Normal и Admin режимы, text2sql)
- **api/collectors.py** - интерфейс StatCollector и реализации (MockStatCollector, RealStatCollector)
- **api/cache.py** - in-memory кэширование статистики с TTL
- **api/config.py** - конфигурация API (режим collector, настройки)
- **api/dependencies.py** - dependency injection для FastAPI
- **api/text2sql_prompt.txt** - промпт для преобразования вопросов в SQL

**Frontend (Next.js):**
- **app/layout.tsx** - корневой layout с провайдерами (Query, Theme, Auth)
- **app/page.tsx** - главная страница с роутингом по ролям
- **app/login/page.tsx** - страница входа
- **app/register/page.tsx** - страница регистрации
- **app/admin/dashboard/page.tsx** - дашборд статистики для администраторов
- **app/admin/chat/page.tsx** - страница чата для администраторов (опционально)
- **app/user/chat/page.tsx** - страница чата для пользователей
- **components/dashboard/** - компоненты дашборда (MetricCard, ActivityChart, RecentDialogues, TopUsers)
- **components/chat/** - компоненты чата (ChatButton, ChatWindow, MessageList, Message, ModeToggle, AuthModal)
- **components/layout/ThemeToggle.tsx** - переключатель Light/Dark темы
- **components/ui/** - переиспользуемые UI компоненты (shadcn/ui)
- **contexts/AuthContext.tsx** - React Context для управления аутентификацией
- **hooks/** - custom React hooks (useAuth, useChat, useChatAuth)
- **lib/api.ts** - API клиент для взаимодействия с backend
- **types/** - TypeScript типы и интерфейсы

### Принципы организации

**Backend:**
- 1 класс = 1 файл (обязательно)
- Простая плоская структура без вложенных пакетов
- Разделение на модули: bot/ для Telegram, api/ для REST API
- Системный промпт вынесен в отдельные файлы (system_prompt.txt, text2sql_prompt.txt)
- ✅ Protocol интерфейсы для слабой связанности
- ✅ Разделение инфраструктуры и бизнес-логики
- ✅ SOLID принципы применены: SRP и DIP
- ✅ Repository pattern для работы с БД
- ✅ Type hints обязательны, mypy strict mode
- ✅ Автоматизированные проверки качества (Ruff, Mypy, Pytest)

**Frontend:**
- Компонентный подход (React)
- Feature-based организация компонентов (dashboard/, chat/, layout/, ui/)
- Разделение concerns: app/ (страницы), components/ (UI), hooks/ (логика), contexts/ (состояние)
- TypeScript для type safety на всех уровнях
- Адаптивный дизайн (mobile-first)
- ✅ Автоматические проверки (TypeScript, ESLint, Prettier)
- ✅ Unit и integration тесты (Jest + React Testing Library)

---

## 4. Архитектура проекта

### Основные компоненты и их взаимодействие

> **Примечание:** Схема показывает полную архитектуру системы с Telegram ботом, REST API и веб-интерфейсом (обновлено 2025-10-18). Применены SOLID принципы: SRP для разделения ответственностей, DIP через Protocol интерфейсы, Repository pattern для работы с БД.

**Полная архитектура:**
```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTS (Пользователи)                      │
├─────────────────────────────────┬───────────────────────────────────┤
│   Telegram Users                │   Web Users (Browser)             │
│   (текст/фото/аудио)            │   (admin/user интерфейс)          │
└────────────┬────────────────────┴──────────────┬────────────────────┘
             │                                   │
             ↓                                   ↓
┌────────────────────────┐         ┌────────────────────────────────┐
│   Telegram Bot         │         │   Frontend (Next.js)           │
│   (aiogram)            │         │   - Pages: login, register,    │
│                        │         │     admin/dashboard, chat      │
│   CommandHandler       │         │   - Components: Dashboard,     │
│   MessageHandler       │         │     Chat, UI                   │
│   MediaProcessor       │         │   - AuthContext, React Query   │
│   LLMClient            │         │   - shadcn/ui, Tailwind CSS    │
└─────────┬──────────────┘         └───────────┬────────────────────┘
          │                                    │
          │                                    │ HTTP/REST
          │                                    ↓
          │                        ┌────────────────────────────────┐
          │                        │   FastAPI REST API             │
          │                        │   - /stats (admin only)        │
          │                        │   - /api/auth/* (reg, login)   │
          │                        │   - /api/chat/* (web chat)     │
          │                        │   - JWT auth, RBAC middleware  │
          │                        │   - StatCollector (Mock/Real)  │
          │                        │   - ChatService (text2sql)     │
          │                        └───────────┬────────────────────┘
          │                                    │
          └─────────────┬──────────────────────┘
                        │
                        ↓
          ┌────────────────────────────────┐
          │   Shared Business Logic        │
          │   - DialogueManager            │
          │   - LLMClient                  │
          │   - Repository Pattern         │
          │     (Message, User)            │
          └────────────┬───────────────────┘
                       │
                       ↓
          ┌────────────────────────────────┐
          │   Data Layer                   │
          │   - Models (SQLAlchemy ORM)    │
          │   - Database (async engine)    │
          │   - Alembic (migrations)       │
          └────────────┬───────────────────┘
                       │
                       ↓
          ┌────────────────────────────────┐
          │   PostgreSQL Database          │
          │   - users (telegram + web)     │
          │   - messages (JSONB content)   │
          └────────────────────────────────┘
                       ↑
                       │
          ┌────────────┴───────────────────┐
          │   External Services            │
          │   - OpenRouter API (LLM)       │
          │   - LangSmith (monitoring)     │
          └────────────────────────────────┘
```

### Описание компонентов

**Telegram Bot компоненты:**

**1. TelegramBot** (bot.py) - Инфраструктура Telegram
- Получает сообщения от пользователей: текст, фото, голосовые (polling)
- Делегирует команды в `CommandHandler`
- Делегирует обработку сообщений в `MessageHandler`
- Отправляет ответы обратно пользователю
- **Зависимости**: `MessageHandler`, `CommandHandler` (DIP)

**2. MessageHandler** (message_handler.py) - Бизнес-логика сообщений
- Обрабатывает текстовые и мультимодальные сообщения
- Координирует работу `MediaProcessor`, `DialogueStorage`, `LLMProvider`
- Формирует контекст и получает ответ от LLM
- Возвращает текст ответа пользователю
- **Зависимости**: `LLMProvider`, `DialogueStorage` (Protocol через DIP)

**3. CommandHandler** (command_handler.py) - Обработка команд
- Обрабатывает команды: /start, /reset, /help, /role
- Взаимодействует с `DialogueStorage` для очистки истории
- Формирует текст ответов на команды
- Возвращает текст ответа
- **Зависимости**: `DialogueStorage` (Protocol через DIP)

**4. MediaProcessor** (media_processor.py) - Обработка медиа
- Скачивает фотографии из Telegram
- Скачивает и транскрибирует голосовые сообщения через Faster-Whisper (base модель)
- Конвертирует медиа в формат для отправки в LLM
- Локальная обработка аудио без внешних API вызовов
- Возвращает обработанные данные

**REST API компоненты:**

**5. FastAPI Application** (api/main.py) - REST API сервер
- Предоставляет HTTP endpoints для веб-интерфейса
- `/stats` - статистика дашборда (защищен RBAC, только admin)
- `/api/auth/*` - регистрация, вход, проверка токена, выход
- `/api/chat/*` - веб-чат с LLM (Normal и Admin режимы)
- CORS middleware для фронтенда
- Автоматическая документация (Swagger UI)

**6. AuthService** (api/auth_service.py) - Веб-аутентификация
- Регистрация новых веб-пользователей (username, password, role)
- Аутентификация пользователей (проверка пароля через bcrypt)
- Создание JWT токенов с TTL 30 дней
- Проверка и валидация токенов
- Работа с UserRepository для web пользователей

**7. RBAC Middleware** (api/middleware.py) - Контроль доступа
- Извлечение и проверка JWT токенов из заголовков
- Проверка роли пользователя (user/administrator)
- Защита endpoints по ролям (require_admin decorator)
- Возврат 401/403 при отсутствии доступа

**8. ChatService** (api/chat_service.py) - Веб-чат с LLM
- Обработка сообщений в Normal режиме (обычный чат с HomeGuru)
- Обработка сообщений в Admin режиме (text2sql для статистики)
- Text2SQL pipeline: вопрос → SQL → выполнение → LLM → ответ
- Валидация SQL (только SELECT)
- Использует DialogueManager и LLMClient

**9. StatCollector** (api/collectors.py) - Сбор статистики
- Интерфейс для сбора статистики дашборда
- MockStatCollector - генерация фейковых данных для разработки
- RealStatCollector - реальная статистика из PostgreSQL
- Factory pattern для переключения Mock ↔ Real (env var)
- Оптимизированные SQL запросы с агрегациями

**10. Cache** (api/cache.py) - Кэширование
- In-memory кэширование статистики
- TTL 60 секунд для свежести данных
- Ускорение API в 50-200x
- Простая реализация без внешних зависимостей

**Shared компоненты:**

**11. DialogueManager** (dialogue_manager.py) - Управление диалогами
- Координирует работу с MessageRepository для персистентного хранения
- Добавляет сообщения в историю через Repository
- Предоставляет историю для формирования контекста из БД
- Очищает историю через soft delete
- Реализует `DialogueStorage` Protocol

**12. MessageRepository / UserRepository** (repository.py) - Repository pattern
- Инкапсулирует работу с базой данных (async SQLAlchemy)
- MessageRepository: add_message, get_history, clear_history (soft delete)
- UserRepository: get_or_create_user (для telegram и web), update_last_seen, get_active_users_count
- Управление async session и транзакциями
- Возвращает бизнес-объекты, скрывает детали ORM

**13. Models** (models.py) - ORM модели
- `User` модель с двумя типами пользователей:
  - Telegram: telegram_id, username, language_code
  - Web: username, password_hash, role (user/administrator), last_login
- `Message` модель: user_id, role, content (JSONB), created_at, char_length, is_deleted
- SQLAlchemy DeclarativeBase с relationships
- Поддержка мультимодального контента через JSONB
- Индексы для оптимизации запросов

**14. Database** (database.py) - Слой базы данных
- Создание async engine для PostgreSQL
- Session factory с async_sessionmaker
- Управление соединениями и транзакциями
- Интеграция с Alembic для миграций

**15. LLMClient** (llm_client.py) - Провайдер LLM
- Отправляет мультимодальные запросы в OpenRouter API
- Использует openai client для работы с моделями, поддерживающими Vision
- Интегрирован с LangSmith для мониторинга всех запросов
- Возвращает ответ от LLM
- Реализует `LLMProvider` Protocol
- Используется как Telegram ботом, так и веб-чатом

**16. Config** (config.py) - Конфигурация
- Загружает настройки из .env с валидацией
- Загружает системный промпт из system_prompt.txt
- Предоставляет конфигурацию всем модулям
- Выбрасывает `ValueError` при отсутствии обязательных параметров

**17. Interfaces** (interfaces.py) - Protocol интерфейсы
- `LLMProvider` - контракт для провайдеров LLM
- `DialogueStorage` - контракт для хранилищ диалогов
- `MediaProvider` - контракт для обработки медиа
- `UserStorage` - контракт для работы с пользователями
- Обеспечивает Dependency Inversion (SOLID DIP)
- Позволяет легко заменять имплементации

**Frontend компоненты:**

**18. Next.js Application** - Веб-интерфейс
- Server-side rendering (SSR) для оптимизации производительности
- App Router для роутинга
- Страницы: login, register, admin/dashboard, admin/chat, user/chat
- Автоматическое перенаправление по ролям

**19. Dashboard Components** - Визуализация статистики
- MetricCard - карточки с ключевыми метриками и трендами
- ActivityChart - график активности (Line chart с Recharts)
- RecentDialogues - таблица последних диалогов
- TopUsers - таблица топ пользователей по активности
- ThemeToggle - переключатель Light/Dark темы

**20. Chat Components** - Компоненты чата
- ChatButton - плавающая кнопка для открытия чата
- ChatWindow - окно чата с сообщениями и input
- MessageList - список сообщений с автопрокруткой
- Message - отдельное сообщение (user/assistant)
- ModeToggle - переключатель режимов (Normal/Admin)
- AuthModal - модальное окно для админ аутентификации

**21. AuthContext** - Управление аутентификацией
- React Context для глобального состояния аутентификации
- Хранение JWT токена в localStorage
- Автоматическая проверка токена при загрузке
- Предоставление user, isLoading, login, logout, register методов

**22. API Client** (lib/api.ts) - HTTP клиент
- Обертка над fetch API
- Автоматическое добавление JWT токена в заголовки
- Методы для всех API endpoints (stats, auth, chat)
- Обработка ошибок и HTTP статусов

### Поток данных

**Telegram Bot - Текстовое сообщение:**
1. Пользователь отправляет текст в Telegram
2. TelegramBot получает сообщение
3. UserRepository регистрирует/обновляет пользователя (get_or_create_user, last_seen)
4. MessageHandler получает сообщение для обработки
5. DialogueManager через MessageRepository сохраняет сообщение в БД
6. MessageRepository загружает историю из PostgreSQL (последние 20 сообщений)
7. LLMClient отправляет запрос с контекстом в OpenRouter (с трейсингом в LangSmith)
8. Ответ от LLM сохраняется в БД через MessageRepository
9. TelegramBot отправляет ответ пользователю

**Telegram Bot - Фото:**
1. Пользователь отправляет фото интерьера
2. TelegramBot получает фото
3. UserRepository обновляет метрики пользователя
4. MediaProcessor скачивает и обрабатывает изображение в base64
5. DialogueManager через MessageRepository сохраняет мультимодальное сообщение в БД (JSONB)
6. LLMClient отправляет мультимодальный запрос (текст + изображение) в OpenRouter
7. HomeGuru анализирует интерьер и дает рекомендации
8. Ответ сохраняется в БД и отправляется пользователю

**Telegram Bot - Голосовое сообщение:**
1. Пользователь отправляет голосовое сообщение
2. TelegramBot получает аудио
3. UserRepository обновляет активность пользователя
4. MediaProcessor скачивает и транскрибирует в текст через Faster-Whisper (локально)
5. Транскрибированный текст обрабатывается как обычное текстовое сообщение
6. Сообщение и ответ сохраняются в PostgreSQL
7. Ответ отправляется пользователю

**Web - Регистрация и вход:**
1. Пользователь открывает страницу регистрации
2. Заполняет форму (username, password, first_name)
3. Frontend отправляет POST /api/auth/register
4. AuthService создает нового web пользователя (bcrypt hash пароля)
5. UserRepository сохраняет пользователя в БД (user_type='web', role='user')
6. Backend возвращает JWT токен с TTL 30 дней
7. Frontend сохраняет токен в localStorage
8. AuthContext обновляется, пользователь перенаправляется в чат

**Web - Дашборд статистики (Admin):**
1. Администратор входит в систему (роль 'administrator')
2. Открывается страница admin/dashboard
3. Frontend отправляет GET /stats с JWT токеном
4. RBAC middleware проверяет роль (require_admin)
5. StatCollector (Real) собирает статистику из PostgreSQL
6. Cache проверяет наличие данных (TTL 60 сек)
7. Backend возвращает StatsResponse (metrics, time_series, dialogues, top_users)
8. React Query кэширует данные на клиенте
9. Dashboard компоненты отображают графики и таблицы

**Web - Веб-чат (Normal режим):**
1. Пользователь отправляет сообщение в веб-чате
2. Frontend отправляет POST /api/chat/message (mode='normal')
3. ChatService обрабатывает сообщение
4. DialogueManager сохраняет сообщение в БД (для виртуального web-пользователя)
5. LLMClient отправляет запрос в OpenRouter с системным промптом HomeGuru
6. Ответ сохраняется в БД
7. Backend возвращает ChatResponse (answer, session_id)
8. Frontend отображает ответ в чате

**Web - Веб-чат (Admin режим, text2sql):**
1. Администратор переключается в Admin режим (проходит аутентификацию)
2. Задает вопрос: "Сколько сообщений отправлено за сегодня?"
3. Frontend отправляет POST /api/chat/message (mode='admin')
4. ChatService использует text2sql_prompt.txt для генерации SQL
5. LLMClient генерирует SQL запрос: `SELECT COUNT(*) FROM messages WHERE created_at::date = CURRENT_DATE`
6. ChatService валидирует SQL (только SELECT)
7. SQL выполняется на PostgreSQL, результат получен
8. LLMClient формирует естественный ответ на основе данных
9. Ответ с SQL и результатом возвращается клиенту
10. Frontend отображает ответ с expandable SQL блоком

---

## 5. Модель данных

### База данных (PostgreSQL)

**User модель** (таблица `users`) - Поддержка двух типов пользователей
```python
class User(Base):
    id: int                       # Primary key
    user_type: UserType           # Enum: 'telegram' или 'web'
    
    # Telegram-специфичные поля (для user_type='telegram')
    telegram_id: int | None       # Telegram user ID (unique, indexed)
    language_code: str | None     # Язык интерфейса (ru, en, etc.)
    
    # Общие поля
    username: str | None          # Username (telegram @username или web username)
    first_name: str | None        # Имя пользователя
    last_name: str | None         # Фамилия пользователя
    
    # Web-специфичные поля (для user_type='web')
    password_hash: str | None     # Bcrypt hash пароля (только для web)
    role: UserRole | None         # Enum: 'user' или 'administrator' (только для web)
    last_login: datetime | None   # Последний вход (только для web)
    
    # Метрики активности (для обоих типов)
    first_seen: datetime          # Первое взаимодействие
    last_seen: datetime           # Последнее взаимодействие
    is_active: bool               # Активен ли пользователь
```

**Message модель** (таблица `messages`)
```python
class Message(Base):
    id: int                       # Primary key
    user_id: int                  # Foreign key to users.id (indexed)
    role: str                     # "user" или "assistant"
    content: dict                 # JSONB - текст или мультимодальный контент
    created_at: datetime          # Timestamp (UTC with timezone)
    char_length: int              # Длина контента в символах
    is_deleted: bool              # Soft delete флаг
```

### Структуры данных в приложении

**Текстовое сообщение**
```python
{
    "role": str,      # "user" или "assistant" или "system"
    "content": str    # текст сообщения
}
```

**Мультимодальное сообщение (с изображением)**
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
                "url": str  # base64 data URL изображения
            }
        }
    ]
}
```

### Особенности модели данных
- **Персистентное хранение** в PostgreSQL
- **Единая таблица users** для Telegram и веб-пользователей
- **RBAC через роли**: user и administrator для веб-пользователей
- История диалогов сохраняется между перезапусками
- Soft delete для сохранения данных при очистке истории
- Формат совместим с OpenAI API (role + content)
- Мультимодальный контент хранится в JSONB
- Индексы для быстрых запросов по user_id и created_at
- Async операции через SQLAlchemy 2.0+
- Миграции через Alembic для версионирования схемы

### Текущие ограничения
- Максимум последних 20 сообщений на пользователя при загрузке истории
- Soft delete вместо физического удаления (для возможного восстановления)
- JWT токены с TTL 30 дней (не поддерживается refresh token)

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

### Особенности работы с LLM
- Используем мультимодальную модель через OpenRouter с поддержкой Vision API
- Системные промпты загружаются из файлов (`system_prompt.txt`, `text2sql_prompt.txt`)
- LangSmith для автоматического трейсинга всех запросов к LLM
- Text2SQL режим для админ чата (естественный язык → SQL → данные → ответ)
- Без streaming (простой синхронный запрос)
- Используется единый LLMClient для Telegram бота и веб-чата
- Дефолтные параметры моделей (temperature, max_tokens)

---

## 7. Сценарии работы

### Telegram Bot сценарии

**1. Первый запуск бота**
- Пользователь отправляет `/start`
- Бот приветствует от имени HomeGuru - ИИ-дизайнера интерьеров
- Создается новый Telegram пользователь в БД (user_type='telegram')
- Создается новый диалог для user

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
- MediaProcessor транскрибирует аудио в текст через Faster-Whisper base модель (локально)
- Обрабатывается как обычное текстовое сообщение
- Ответ отправляется пользователю

**5. Команды бота**
- `/start` - запуск бота и приветствие от HomeGuru
- `/role` - информация о роли и специализации ИИ-дизайнера
- `/reset` - очистка истории диалога
- `/help` - справка о командах и возможностях

### Web интерфейс сценарии

**6. Регистрация нового пользователя**
- Пользователь открывает /register
- Заполняет форму (username, password, first_name)
- Система создает веб-пользователя (user_type='web', role='user')
- Выдается JWT токен, сохраняется в localStorage
- Перенаправление на страницу чата

**7. Вход существующего пользователя**
- Пользователь открывает /login
- Вводит username и password
- Система проверяет пароль (bcrypt)
- Выдается JWT токен
- Перенаправление по роли: admin → dashboard, user → chat

**8. Просмотр дашборда (Administrator)**
- Администратор входит в систему
- Открывается admin/dashboard
- Отображаются метрики:
  - Total Dialogues с трендом
  - Active Users с изменением
  - Avg Messages per Dialogue
  - Messages Today
- График активности за период (Day/Week/Month)
- Таблица последних диалогов
- Таблица топ-5 пользователей

**9. Веб-чат в Normal режиме (User)**
- Пользователь открывает страницу чата
- Отправляет сообщения HomeGuru
- Получает консультации по дизайну интерьеров
- История сохраняется в БД
- Можно очистить историю (Clear History)

**10. Веб-чат в Admin режиме (Administrator)**
- Администратор переключается в Admin режим
- Проходит дополнительную аутентификацию (admin password)
- Задает вопросы о статистике естественным языком
- Система генерирует SQL, выполняет запрос
- Получает ответ с данными и SQL кодом
- SQL блок можно развернуть для просмотра

### Возможности системы
- ✅ **Telegram Bot** - текстовые, фото, голосовые сообщения
- ✅ **Веб-интерфейс** - современный UI с адаптивным дизайном
- ✅ **Аутентификация** - JWT токены, bcrypt пароли
- ✅ **RBAC** - роли user и administrator
- ✅ **Дашборд статистики** - графики, метрики, таблицы (только admin)
- ✅ **Веб-чат** - Normal режим (HomeGuru) и Admin режим (text2sql)
- ✅ **Text2SQL** - вопросы на естественном языке → SQL → данные
- ✅ **Мониторинг LLM** - LangSmith трейсинг
- ✅ **Кэширование** - in-memory cache с TTL для статистики

---

## 8. Подход к конфигурированию

### Файл .env
Все настройки в одном месте:
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/homeguru

# OpenRouter (мультимодальная модель)
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# LangSmith (мониторинг)
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=homeguru

# Dialogue Settings
MAX_HISTORY_MESSAGES=20

# Speech Recognition (Faster-Whisper)
WHISPER_MODEL=base
WHISPER_DEVICE=cpu

# API Settings
COLLECTOR_MODE=real  # 'mock' или 'real'
ADMIN_PASSWORD=admin123  # Пароль для Admin режима чата

# Web Auth Settings
JWT_SECRET_KEY=your-secret-key-here  # Секрет для JWT токенов
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=30
```

**Примечание:** 
- Системные промпты хранятся в отдельных файлах (`system_prompt.txt`, `text2sql_prompt.txt`), а не в .env
- DATABASE_URL используется как Telegram ботом, так и REST API
- COLLECTOR_MODE переключает Mock/Real режимы для StatCollector

### Класс Config (Bot)
```python
from dotenv import load_dotenv
import os
from pathlib import Path

class Config:
    def __init__(self):
        load_dotenv()
        
        # Telegram
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Database
        self.database_url = os.getenv("DATABASE_URL")
        
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
        
        # Speech Recognition
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.whisper_device = os.getenv("WHISPER_DEVICE", "cpu")
```

### API Config
```python
from enum import Enum

class CollectorMode(str, Enum):
    mock = "mock"
    real = "real"

class APIConfig:
    def __init__(self):
        load_dotenv()
        
        # Database (для Real collector)
        self.database_url = os.getenv("DATABASE_URL")
        
        # Collector mode
        mode = os.getenv("COLLECTOR_MODE", "mock")
        self.collector_mode = CollectorMode(mode)
        
        # Admin password для чата
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        # JWT Settings
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_days = int(os.getenv("JWT_EXPIRATION_DAYS", "30"))
```

### Особенности
- Один файл .env для всех настроек (bot + API)
- Системные промпты в отдельных файлах для удобства редактирования
- Валидация обязательных параметров (ValueError при отсутствии)
- Factory pattern для переключения Mock/Real режимов
- .env.example в репозитории как шаблон
- .env в .gitignore
- LangSmith настраивается через переменные окружения
- Разделение конфигураций: bot/config.py и api/config.py

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

**Telegram Bot:**
- **INFO**: Старт/остановка бота
- **INFO**: Получение сообщений от пользователей (user_id, тип: текст/фото/аудио)
- **INFO**: Обработка медиа (скачивание фото, транскрибация аудио)
- **INFO**: Отправка запросов в LLM (мультимодальных)
- **INFO**: Получение ответов от LLM
- **ERROR**: Ошибки и исключения

**REST API:**
- **INFO**: Старт/остановка API сервера
- **INFO**: HTTP запросы (method, path, status_code, duration)
- **INFO**: Аутентификация (успех/неудача)
- **INFO**: RBAC проверки (доступ разрешен/запрещен)
- **INFO**: StatCollector режим (Mock/Real)
- **INFO**: Cache hits/misses
- **ERROR**: Ошибки валидации, SQL ошибки, исключения

**Дополнительно:** LangSmith автоматически логирует все запросы к LLM с детальной трейсинг информацией

### Пример использования в коде

**Bot:**
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

**API:**
```python
@app.get("/stats")
async def get_stats(user: User = Depends(require_admin)):
    logger.info(f"Stats requested by admin user_id={user.id}")
    try:
        stats = await collector.collect_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to collect stats: {e}", exc_info=True)
        raise HTTPException(status_code=500)
```

### Особенности
- Логи в файл `bot.log` + вывод в консоль
- FastAPI автоматически логирует все HTTP запросы (uvicorn)
- Уровень INFO для информационных сообщений
- Уровень ERROR для ошибок
- Простой формат сообщений с timestamp
- Без ротации логов
- Файл bot.log в .gitignore

---

## 10. Тестирование

### TDD-подход (Test-Driven Development)

**Обязательный процесс разработки:**
1. **RED** - пишем падающий тест для нового функционала
2. **GREEN** - реализуем минимум кода для прохождения теста
3. **REFACTOR** - улучшаем код, тесты остаются зелеными

**Правила TDD:**
- ✅ Тесты пишутся ПЕРЕД кодом (не после!)
- ✅ Один тест = одно поведение
- ✅ Маленькие циклы (RED-GREEN-REFACTOR < 10 минут)
- ✅ Тесты должны быть простыми и понятными (AAA: Arrange-Act-Assert)
- ✅ Моки только для внешних зависимостей (не для своего кода)

**Процесс итерации:**
1. Согласовать архитектуру и план тестов
2. Для каждого компонента: RED → GREEN → REFACTOR циклы
3. Проверка качества: `make quality`
4. Coverage ≥ 80%
5. Коммит только после прохождения всех проверок

**Примеры TDD-цикла:**
```python
# RED: тест для нового функционала (тест падает)
def test_add_message():
    dm = DialogueManager(max_history=20)
    dm.add_message(123, "user", "Hello")
    
    history = dm.get_history(123)
    assert len(history) == 1
    assert history[0]["content"] == "Hello"

# GREEN: минимальная реализация (тест проходит)
def add_message(self, user_id: int, role: str, content: str) -> None:
    if user_id not in self.dialogues:
        self.dialogues[user_id] = []
    self.dialogues[user_id].append({"role": role, "content": content})

# REFACTOR: улучшение кода (тесты остаются зелеными)
# Добавляем ограничение истории, оптимизируем, улучшаем читаемость
```

**Документация:**
- Детальное описание TDD процесса: [workflow_tdd.mdc](.cursor/rules/workflow_tdd.mdc)
- Соглашения по тестированию: [qa_conventions.mdc](.cursor/rules/qa_conventions.mdc)

---

### Подход к тестированию (Unit Tests)

Минимальный набор юнит-тестов для проверки базовой функциональности основных компонентов.

### Что тестируем

**Backend (Telegram Bot) - tests/bot/**

- **DialogueManager** (test_dialogue_manager.py)
- Добавление сообщения в историю
- Получение истории диалога
- Очистка истории
- Ограничение количества сообщений (20 сообщений)

- **LLMClient** (test_llm_client.py)
- Корректность формирования запроса
- Добавление system prompt в начало
- Мок-тестирование без реальных запросов к API

- **Config** (test_config.py)
- Корректная загрузка параметров из .env
- Загрузка системного промпта из файла
- Значения по умолчанию

- **MediaProcessor** (test_media_processor.py)
- Базовая обработка изображений
- Транскрибация аудио через Faster-Whisper (моки для изоляции тестов)

- **MessageHandler** (test_message_handler.py)
- Обработка текстовых сообщений
- Координация компонентов
- Обработка ошибок

- **CommandHandler** (test_command_handler.py)
- Обработка всех команд
- Взаимодействие с DialogueStorage

- **TelegramBot** (test_bot.py)
- Делегирование в handlers
- Отправка ответов

- **UserRepository** (test_user_repository.py)
  - Создание и получение пользователей
  - Обновление метрик активности

**Backend (REST API) - tests/api/**

- **StatCollector** (test_collectors.py, test_real_collector.py)
  - MockStatCollector: генерация фейковых данных
  - RealStatCollector: реальные SQL запросы
  - Factory pattern для переключения режимов

- **Cache** (test_cache.py)
  - Кэширование данных с TTL
  - Очистка устаревших данных
  - Thread-safe операции

- **Auth** (test_auth.py)
  - Регистрация веб-пользователей
  - Аутентификация (bcrypt)
  - JWT токены (создание, проверка)
  - RBAC middleware

- **ChatService** (test_chat_service.py)
  - Normal режим (обычный чат)
  - Admin режим (text2sql)
  - SQL валидация
  - Обработка ошибок

- **API Endpoints** (test_api.py, test_chat_endpoints.py)
  - GET /stats (с RBAC)
  - POST /api/auth/register, /login
  - POST /api/chat/message
  - Все HTTP статусы и ошибки

- **Config** (test_config.py)
  - Загрузка конфигурации API
  - CollectorMode enum
  - Валидация параметров

**Frontend - frontend/app/src/**

- **Components** (*.test.tsx)
  - MetricCard: отображение метрик
  - ActivityChart: график активности
  - RecentDialogues: таблица диалогов
  - TopUsers: таблица пользователей
  - ThemeToggle: переключение темы
  - Page: роутинг по ролям

- **Integration Tests**
  - React Query интеграция
  - API клиент
  - AuthContext

### Что НЕ тестируем в unit-тестах
- Реальные запросы к OpenRouter API
- Реальная транскрибация аудио
- Интеграции с Telegram API
- E2E тесты
- LangSmith трейсинг
- Real PostgreSQL (используем моки в тестах)

### Запуск тестов

**Backend:**
```bash
# Все тесты backend через Make (с покрытием)
make test

# Только тесты бота
uv run pytest tests/bot/ -v

# Только тесты API
uv run pytest tests/api/ -v

# С покрытием и отчетом
uv run pytest tests/ -v --cov=src --cov-report=html
```

**Frontend:**
```bash
# Из директории frontend/app
pnpm test

# С покрытием
pnpm test:coverage

# Watch mode
pnpm test:watch
```

### Требования к покрытию
- **Backend Coverage ≥ 80%** - обязательная цель (текущий: ~85-90%)
- **Frontend Coverage ≥ 75%** - цель (текущий: ~79%)
- Все новые модули покрыты тестами
- Критичные пути покрыты тестами
- HTML отчет backend: `htmlcov/index.html`
- HTML отчет frontend: `frontend/app/coverage/lcov-report/index.html`

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

**TDD-процесс:**
- [ ] План тестов согласован для итерации
- [ ] Тесты написаны ПЕРЕД кодом
- [ ] RED-GREEN-REFACTOR циклы соблюдены
- [ ] Все новые компоненты покрыты тестами

**Автоматические проверки:**
- [ ] `make format` - пройдено
- [ ] `make lint` - 0 errors
- [ ] `make typecheck` - success (mypy strict)
- [ ] `make test` - все тесты проходят
- [ ] Coverage ≥ 80%

**Ручная проверка:**
- [ ] Код простой и понятный (KISS)
- [ ] 1 класс = 1 файл
- [ ] Все методы типизированы
- [ ] Логирование добавлено
- [ ] Следует SOLID разумно
- [ ] Protocol интерфейсы применены где нужно (DIP)

### Метрики качества

| Метрика | Цель | Измерение |
|---------|------|-----------|
| **TDD Compliance** | **100%** | **Ревью процесса** |
| Test Coverage | ≥ 80% | `pytest --cov` |
| Mypy Strict | 0 errors | `mypy --strict` |
| Ruff Errors | 0 critical | `ruff check` |
| Line Length | ≤ 100 | автоматически |
| **TDD Cycle Time** | **< 10 мин** | **RED-GREEN-REFACTOR** |

---

## 12. Заключение

Данный документ описывает техническое видение проекта HomeGuru - ИИ-дизайнера интерьеров. Система реализована как полноценный продукт с Telegram ботом, REST API и современным веб-интерфейсом. Все решения направлены на баланс между простотой реализации и профессиональным качеством кода.

**Текущее состояние системы:**

**Backend (Telegram Bot + REST API):**
- ✅ **85-90% test coverage** (превышено требование ≥80%)
- ✅ **0 ошибок mypy** strict mode
- ✅ **150+ автоматических тестов** (bot + API)
- ✅ **SOLID принципы** применены (SRP, DIP через Protocol)
- ✅ **Чистая архитектура** с разделением ответственностей
- ✅ **Автоматизированный контроль качества** (Ruff, Mypy, Pytest)
- ✅ **PostgreSQL** с Alembic миграциями
- ✅ **FastAPI** с автоматической документацией

**Frontend (Next.js + React):**
- ✅ **79% test coverage** (приближено к цели ≥75%)
- ✅ **0 ошибок TypeScript**
- ✅ **29+ компонентных тестов**
- ✅ **Адаптивный дизайн** (mobile/tablet/desktop)
- ✅ **Light/Dark темы**
- ✅ **shadcn/ui компоненты**
- ✅ **React Query** для server state

**Ключевые возможности:**
- 🤖 **Telegram Bot** - текстовые диалоги, анализ фото интерьеров, голосовые сообщения
- 🌐 **Веб-интерфейс** - современный UI с адаптивным дизайном
- 🔐 **Аутентификация и RBAC** - JWT токены, bcrypt, роли user/administrator
- 📊 **Дашборд статистики** - метрики, графики, таблицы (только для admin)
- 💬 **Веб-чат** - Normal режим (HomeGuru) и Admin режим (text2sql)
- 🔍 **Text2SQL** - естественный язык → SQL → данные → ответ
- 📈 **Мониторинг LLM** - LangSmith автоматический трейсинг
- ⚡ **Кэширование** - in-memory cache с TTL для производительности
- 🗄️ **Единая база данных** - Telegram и веб-пользователи в одной таблице

**Архитектурные достижения:**
- 🧪 **TDD-подход** - тесты перед кодом, RED-GREEN-REFACTOR
- 🎨 **Специализация** на дизайне интерьеров (системный промпт HomeGuru)
- 🚀 **Модульная архитектура** - четкое разделение bot/, api/, frontend/
- ✅ **Высокое качество кода** (Ruff + Mypy + ESLint + Prettier)
- 🔧 **Автоматизация** проверок через Make и npm scripts
- 🧪 **Type safety** - mypy strict mode и TypeScript
- 🏗️ **SOLID принципы** (DIP через Protocol, SRP для компонентов)
- 🔄 **Расширяемая архитектура** (Factory pattern, Protocol интерфейсы)

**Технологическое совершенство:**
- Backend: Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy 2.0+, Alembic
- Frontend: Next.js 14+, React, TypeScript, Tailwind CSS, shadcn/ui
- Infrastructure: Docker Compose, Alembic миграции, async everywhere
- Testing: Pytest, Jest, React Testing Library, 85-90% backend, 79% frontend coverage
- Quality: Ruff, Mypy, ESLint, Prettier - 0 errors в production

**Баланс между качеством и простотой:**
- TDD обеспечивает качество без избыточности - тесты определяют минимум кода
- Type hints и TypeScript обязательны, но не усложняют код
- SOLID применяется разумно - только там, где дает реальную пользу
- Автоматические инструменты освобождают от ручного контроля
- Высокий coverage обеспечивает уверенность в изменениях
- Простота остается главным приоритетом

**Документация:**
- [`docs/roadmap.md`](roadmap.md) - roadmap проекта по спринтам (bot + frontend)
- [`docs/plans/`](plans/) - детальные планы всех спринтов (Sprint-0 до F-Sprint-6)
- [`frontend/doc/frontend-roadmap.md`](../frontend/doc/frontend-roadmap.md) - roadmap frontend разработки
- [`docs/reports/`](reports/) - отчеты о выполненных работах
- [`docs/addrs/`](addrs/) - архитектурные решения (ADR)

