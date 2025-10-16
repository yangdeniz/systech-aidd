# ADR-03: Выбор PostgreSQL + SQLAlchemy ORM для персистентного хранения диалогов

**Дата:** 2025-10-16  
**Статус:** Принято (Accepted)  
**Авторы:** Команда разработки  

---

## Контекст

После завершения Sprint-0 (MVP) HomeGuru работает с in-memory хранением истории диалогов (ADR-01). Это означает, что при перезапуске бота все диалоги пользователей теряются.

### Текущая ситуация

**Проблемы текущего подхода:**
- История диалогов теряется при перезапуске приложения
- Невозможность восстановления контекста после сбоя
- Отсутствие долгосрочного хранения данных о взаимодействии с пользователями
- Ограничения по масштабируемости (нельзя запустить несколько экземпляров бота)

**Требования к решению:**
- Персистентное хранение истории диалогов между перезапусками
- Поддержка мультимодальных сообщений (текст + изображения в формате JSONB)
- Soft delete стратегия (физически не удаляем данные)
- Метаданные сообщений: дата создания, длина в символах
- Следование принципу KISS (Keep It Simple, Stupid)
- Production-ready решение
- Система миграций для управления схемой данных

### Рассмотренные варианты

Проведен анализ трех основных подходов к реализации персистентного хранения.

## Вариант 1: SQLite + SQLAlchemy Core

**Стек:**
- SQLite 3 (встроенный файл-based)
- SQLAlchemy Core 2.0+ (async)
- aiosqlite драйвер
- Alembic для миграций

**Плюсы:**
- ✅ Максимальная простота (KISS)
- ✅ Нет необходимости в Docker/внешних сервисах
- ✅ Один файл БД (легкий бэкап)
- ✅ Быстрая настройка окружения
- ✅ Нулевые операционные издержки
- ✅ Достаточно для Telegram бота (один user = один write)

**Минусы:**
- ⚠️ Ограничения concurrent writes (блокировки)
- ⚠️ JSON вместо JSONB (нет индексов по JSON полям)
- ⚠️ Ограничения масштабируемости
- ⚠️ Меньше возможностей для production нагрузок

**Оценка трудоемкости:** ~8 часов

---

## Вариант 2: PostgreSQL + SQLAlchemy Core

**Стек:**
- PostgreSQL 16 (Docker)
- SQLAlchemy Core 2.0+ (async)
- asyncpg драйвер
- Alembic для миграций
- docker-compose

**Плюсы:**
- ✅ Production-ready СУБД
- ✅ JSONB с возможностью индексирования
- ✅ Отличная поддержка concurrent writes
- ✅ Горизонтальное масштабирование
- ✅ Прямой контроль над SQL запросами
- ✅ Легко мигрировать между БД (только connection string)

**Минусы:**
- ⚠️ Docker добавляет сложности в development
- ⚠️ SQL builder требует больше кода
- ⚠️ Менее выразительный код по сравнению с ORM

**Оценка трудоемкости:** ~8.5 часов

---

## Вариант 3: PostgreSQL + SQLAlchemy ORM ⭐

**Стек:**
- PostgreSQL 16 (Docker)
- SQLAlchemy ORM 2.0+ (async, DeclarativeBase)
- asyncpg драйвер
- Alembic для миграций
- docker-compose

**Плюсы:**
- ✅ Production-ready СУБД
- ✅ JSONB с возможностью индексирования
- ✅ Отличная поддержка concurrent writes
- ✅ Горизонтальное масштабирование
- ✅ Декларативные модели (читаемый код)
- ✅ Отличная интеграция ORM + Alembic (автогенерация миграций)
- ✅ Меньше boilerplate кода
- ✅ Отличная type safety с Mapped аннотациями (mypy strict)
- ✅ Легко мигрировать между БД (только connection string)

**Минусы:**
- ⚠️ Docker добавляет сложности в development
- ⚠️ ORM добавляет абстракцию (меньше контроля)
- ⚠️ "Магия" ORM может быть менее понятной

**Оценка трудоемкости:** ~6.5 часов

---

## Сравнительная таблица

| Критерий | SQLite + Core | PostgreSQL + Core | PostgreSQL + ORM |
|----------|--------------|-------------------|------------------|
| **KISS принцип** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Production-ready** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Масштабируемость** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Type safety** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Размер кода** | ~150-200 строк | ~150-200 строк | ~100-120 строк |
| **JSONB поддержка** | ❌ Только JSON | ✅ JSONB | ✅ JSONB |
| **Concurrent writes** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Автогенерация миграций** | ⚠️ Частично | ⚠️ Частично | ✅ Полная |
| **Трудоемкость** | ~8ч | ~8.5ч | ~6.5ч |

---

## Решение

Выбран **Вариант 3: PostgreSQL + SQLAlchemy ORM** для реализации персистентного хранения.

### Обоснование выбора

#### 1. Production-ready подход
PostgreSQL - индустриальный стандарт, который используется в production приложениях любого масштаба. Это дает уверенность в надежности и стабильности решения.

#### 2. Оптимальный баланс простоты и функциональности
SQLAlchemy ORM 2.0+ с DeclarativeBase предоставляет:
- Декларативное определение моделей (читаемо и понятно)
- Автоматическая генерация миграций через Alembic
- Меньше boilerplate кода по сравнению с Core
- Отличная type safety через `Mapped` аннотации (mypy strict совместимость)

#### 3. JSONB для мультимодальных сообщений
Поддержка JSONB критична для хранения мультимодальных сообщений (текст + изображения). PostgreSQL предоставляет:
- Эффективное хранение JSON структур
- Возможность индексирования полей (при необходимости в будущем)
- Запросы по содержимому JSON

#### 4. Готовность к масштабированию
PostgreSQL позволяет:
- Запускать несколько экземпляров бота
- Горизонтальное масштабирование при росте нагрузки
- Connection pooling для оптимизации

#### 5. Меньше кода и времени
ORM подход сокращает объем кода на ~30-40% по сравнению с Core, что означает:
- Быстрее реализация (~6.5ч vs ~8.5ч)
- Меньше потенциальных багов
- Проще поддержка

#### 6. Отличная интеграция с Alembic
Alembic был создан тем же автором, что и SQLAlchemy, что обеспечивает:
- Автогенерацию миграций из моделей ORM
- Минимальную ручную работу
- Безопасное управление схемой БД

### Технические детали решения

#### Схема БД

Одна таблица `messages`:

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    char_length INTEGER NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    INDEX ix_messages_user_id (user_id),
    INDEX ix_messages_user_id_created_at (user_id, created_at)
);
```

**Поля:**
- `id` - автоинкремент primary key
- `user_id` - Telegram user ID (bigint для больших ID)
- `role` - роль отправителя ("user" или "assistant")
- `content` - JSONB с текстом или мультимодальным контентом
- `created_at` - timestamp создания сообщения (с timezone)
- `char_length` - длина сообщения в символах
- `is_deleted` - флаг soft delete (boolean)

**Индексы:**
- `ix_messages_user_id` - для быстрого поиска по пользователю
- `ix_messages_user_id_created_at` - композитный для сортировки истории

#### Модель SQLAlchemy ORM

```python
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Integer, String, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    char_length: Mapped[int] = mapped_column(Integer)
    is_deleted: Mapped[bool] = mapped_column(Boolean, server_default='false')
    
    __table_args__ = (
        Index('ix_messages_user_id_created_at', 'user_id', 'created_at'),
    )
```

**Преимущества подхода:**
- Type hints через `Mapped` (полная type safety)
- Server-side defaults для created_at и is_deleted
- Декларативный стиль (понятно с первого взгляда)

#### Repository Pattern

Слой доступа к данным через Repository:

```python
class MessageRepository:
    async def add_message(self, user_id: int, role: str, content: dict) -> Message
    async def get_history(self, user_id: int, limit: int) -> list[dict]
    async def clear_history(self, user_id: int) -> None  # soft delete
```

#### Docker setup

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: homeguru
      POSTGRES_USER: homeguru
      POSTGRES_PASSWORD: homeguru_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

#### Alembic migrations

Система миграций с автогенерацией:

```bash
# Создать миграцию автоматически из моделей
alembic revision --autogenerate -m "Add messages table"

# Применить миграции
alembic upgrade head
```

### Архитектурные решения

#### 1. Soft Delete стратегия
Вместо физического удаления используем флаг `is_deleted = true`:
- Сохраняется история для аналитики
- Возможность восстановления данных
- Соответствие GDPR (данные можно "удалить" для пользователя)

#### 2. Метаданные сообщений
Каждое сообщение содержит:
- `created_at` - для временной сортировки и аналитики
- `char_length` - для быстрого определения размера без парсинга JSONB

#### 3. Async throughout
Полностью асинхронная работа с БД:
- `create_async_engine` - async engine
- `AsyncSession` - async сессии
- `async_sessionmaker` - фабрика сессий
- Все методы repository - async

#### 4. Protocol соответствие
`DialogueManager` продолжает реализовывать `DialogueStorage` Protocol, меняется только внутренняя реализация с in-memory на database-backed.

---

## Последствия

### Положительные

#### Production-ready решение
- PostgreSQL выдержит любую нагрузку от Telegram бота
- Concurrent writes без проблем
- Надежность и стабильность

#### Персистентность данных
- История диалогов сохраняется между перезапусками
- Возможность восстановления после сбоев
- Долгосрочное хранение данных для аналитики

#### Масштабируемость
- Возможность запуска нескольких экземпляров бота
- Горизонтальное масштабирование
- Connection pooling

#### JSONB возможности
- Эффективное хранение мультимодальных сообщений
- Возможность индексирования полей при необходимости
- Гибкость структуры данных

#### Простота кода
- Меньше boilerplate по сравнению с Core
- Декларативные модели (читаемо)
- Автогенерация миграций

#### Type Safety
- Полная поддержка mypy strict mode
- `Mapped` аннотации для всех полей
- Ошибки типов отлавливаются на этапе разработки

#### Soft Delete
- Данные не теряются физически
- Возможность восстановления
- Аналитика на исторических данных

### Отрицательные

#### Дополнительная инфраструктура
- Требуется Docker для PostgreSQL
- Необходимость управления БД (backup, мониторинг)
- **Митигация:** docker-compose упрощает setup; PostgreSQL стабилен и требует минимального обслуживания

#### Увеличение сложности development
- Необходимо запускать PostgreSQL локально
- Дополнительный шаг в setup процессе
- **Митигация:** Makefile команды (db-up, db-down) упрощают работу

#### Миграции требуют внимания
- Необходимо проверять автогенерированные миграции
- Управление версиями схемы
- **Митигация:** Alembic хорошо работает; миграции генерируются автоматически

#### Зависимость от внешнего сервиса
- PostgreSQL должен быть запущен для работы бота
- **Митигация:** Docker обеспечивает надежный запуск; возможность fallback на SQLite в будущем

#### Абстракция ORM
- Меньше контроля над SQL запросами
- "Магия" ORM может быть непонятной
- **Митигация:** SQLAlchemy хорошо документирован; можно использовать raw SQL при необходимости

### Риски и их митигация

#### Риск: Сложность настройки для новых разработчиков
**Митигация:**
- Документация в README и guides
- Makefile команды для автоматизации
- docker-compose для одной команды setup

#### Риск: Проблемы с миграциями
**Митигация:**
- Всегда проверять автогенерированные миграции
- Тестировать миграции на test database
- Версионирование миграций в Git

#### Риск: Performance issues
**Митигация:**
- PostgreSQL более чем достаточно для Telegram бота
- Индексы на часто используемых полях
- Connection pooling для оптимизации

#### Риск: Backup и восстановление
**Митигация:**
- Docker volumes для персистентности
- pg_dump для резервных копий
- Документация процесса backup

---

## Альтернативы для будущего

### Если потребуется упрощение:
- **SQLite + ORM** - миграция на SQLite (только connection string)
- Все модели и код остаются такими же

### Если потребуется больше производительности:
- **PostgreSQL с репликацией** - read replicas
- **Connection pooling** - pgbouncer
- **Партиционирование таблиц** - по user_id или дате

### Если потребуется больше функциональности:
- **Полнотекстовый поиск** - PostgreSQL FTS
- **JSONB индексы** - для быстрых запросов по content
- **Материализованные представления** - для аналитики

---

## Критерии успеха

Данное решение считается успешным, если:

1. ✅ История диалогов сохраняется между перезапусками бота
2. ✅ Мультимодальные сообщения корректно хранятся в JSONB
3. ✅ Soft delete работает корректно (is_deleted = true)
4. ✅ Метаданные (created_at, char_length) корректно заполняются
5. ✅ Все тесты проходят (coverage ≥ 98%)
6. ✅ Mypy strict mode: 0 ошибок
7. ✅ Ruff: 0 ошибок
8. ✅ Alembic миграции применяются без ошибок
9. ✅ Setup через docker-compose занимает < 2 минут
10. ✅ Код стал проще и понятнее

---

## Связанные решения

- [ADR-01: Архитектура HomeGuru MVP](ADR-01.md) - in-memory хранение (заменяется)
- [ADR-02: Выбор Faster-Whisper](ADR-02.md) - локальное распознавание речи
- [vision.md](../vision.md) - техническое видение проекта
- [roadmap.md](../roadmap.md) - Sprint-1 из roadmap

---

**Последнее обновление:** 2025-10-16

