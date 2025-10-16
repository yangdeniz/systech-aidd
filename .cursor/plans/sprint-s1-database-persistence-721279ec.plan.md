<!-- 721279ec-8920-4173-9d14-7f8d076f0700 82416bf9-65d1-4142-8cf2-18fbd47064a3 -->
# Sprint S1: Персистентное хранение данных

## Выбранный стек

**PostgreSQL + SQLAlchemy ORM + Alembic**

- PostgreSQL 16 в Docker
- SQLAlchemy 2.0+ async ORM (DeclarativeBase)
- asyncpg драйвер
- Alembic для миграций

## Этапы реализации

### 1. ADR-03: Документирование технологического выбора

Создать `docs/addrs/ADR-03.md` с обоснованием выбора PostgreSQL + SQLAlchemy ORM:

- Контекст: необходимость персистентного хранения
- Рассмотренные варианты (SQLite vs PostgreSQL, Core vs ORM)
- Решение: PostgreSQL + async ORM для production-ready решения
- Последствия и риски

### 2. Docker setup

Создать `docker-compose.yml` в корне проекта:

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

volumes:
  postgres_data:
```

Добавить в `.gitignore`: `.env.local`, `data/`

### 3. Зависимости

Обновить `pyproject.toml`:

```toml
[project.dependencies]
sqlalchemy = ">=2.0.0"
asyncpg = ">=0.29.0"
alembic = ">=1.13.0"
```

### 4. Конфигурация БД

Обновить `src/bot/config.py`:

- Добавить `database_url: str` (из env: `DATABASE_URL`)
- Значение по умолчанию: `postgresql+asyncpg://homeguru:homeguru_dev@localhost:5432/homeguru`

Обновить `.env.example` с новой переменной.

### 5. Модели БД

Создать `src/bot/models.py`:

```python
from datetime import datetime, timezone
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
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')
    
    __table_args__ = (
        Index('ix_messages_user_id_created_at', 'user_id', 'created_at'),
    )
```

**Изменения:**

- Используем `server_default=func.now()` вместо Python-side default для created_at
- Добавлен `timezone=True` для DateTime
- Добавлен `server_default='false'` для is_deleted

### 6. Database engine

Создать `src/bot/database.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.bot.config import Config

def create_engine(config: Config):
    return create_async_engine(config.database_url, echo=False)

def create_session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### 7. Alembic setup

Инициализировать Alembic:

```bash
alembic init migrations
```

Настроить `alembic.ini`:

- Удалить жестко заданный `sqlalchemy.url`

Настроить `migrations/env.py`:

- Импортировать `Config` и `Base`
- Использовать `config.database_url` вместо статического URL
- Настроить async режим

### 8. Initial migration

Создать первую миграцию:

```bash
alembic revision --autogenerate -m "Add messages table"
```

Проверить и отредактировать сгенерированную миграцию.

### 9. Repository layer

Создать `src/bot/repository.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.bot.models import Message

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_message(
        self, user_id: int, role: str, content: dict
    ) -> Message:
        """Добавить сообщение в БД"""
        char_length = self._calculate_char_length(content)
        message = Message(
            user_id=user_id,
            role=role,
            content=content,
            char_length=char_length
        )
        self.session.add(message)
        await self.session.commit()
        return message
    
    async def get_history(
        self, user_id: int, limit: int
    ) -> list[dict]:
        """Получить историю сообщений (только не удаленные)"""
        stmt = (
            select(Message)
            .where(Message.user_id == user_id, Message.is_deleted == False)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
    
    async def clear_history(self, user_id: int) -> None:
        """Soft delete всех сообщений пользователя"""
        stmt = (
            update(Message)
            .where(Message.user_id == user_id)
            .values(is_deleted=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()
    
    def _calculate_char_length(self, content: dict | str) -> int:
        """Вычислить длину контента в символах"""
        if isinstance(content, str):
            return len(content)
        # Для мультимодального контента считаем только текст
        if isinstance(content, list):
            text_parts = [
                item["text"] for item in content
                if item.get("type") == "text"
            ]
            return sum(len(text) for text in text_parts)
        return 0
```

### 10. Обновление DialogueManager

Рефакторить `src/bot/dialogue_manager.py`:

- Добавить `MessageRepository` как зависимость
- Убрать in-memory `self.dialogues`
- Использовать repository для всех операций
- Сохранить тот же интерфейс (соответствие `DialogueStorage` Protocol)

### 11. Обновление main.py

Обновить `src/bot/main.py`:

- Создать database engine и session factory
- Передать session в DialogueManager
- Добавить graceful shutdown для закрытия соединений

### 12. Makefile команды

Добавить в `Makefile`:

```makefile
db-up:
	docker-compose up -d postgres

db-down:
	docker-compose down

db-migrate:
	alembic upgrade head

db-reset:
	docker-compose down -v
	docker-compose up -d postgres
	sleep 2
	alembic upgrade head
```

### 13. Тесты

Создать/обновить тесты:

- `tests/test_models.py` - тесты моделей SQLAlchemy
- `tests/test_repository.py` - тесты MessageRepository (с test DB)
- Обновить `tests/test_dialogue_manager.py` - интеграционные тесты
- Обновить `tests/conftest.py` - добавить фикстуры для test DB

Использовать отдельную test database для изоляции.

### 14. Документация

Обновить:

- `README.md` - добавить инструкции по Docker и миграциям
- `docs/guides/01-getting-started.md` - обновить quickstart
- `docs/guides/07-configuration.md` - добавить DATABASE_URL

## Ключевые файлы

**Новые:**

- `docs/addrs/ADR-03.md`
- `docker-compose.yml`
- `src/bot/models.py`
- `src/bot/database.py`
- `src/bot/repository.py`
- `migrations/` (Alembic)
- `tests/test_models.py`
- `tests/test_repository.py`

**Изменяемые:**

- `pyproject.toml`
- `src/bot/config.py`
- `src/bot/dialogue_manager.py`
- `src/bot/main.py`
- `Makefile`
- `README.md`
- `.env.example`
- `tests/conftest.py`
- `tests/test_dialogue_manager.py`

## Критерии приемки

- ✅ PostgreSQL запускается через Docker
- ✅ Alembic миграции применяются успешно
- ✅ Сообщения сохраняются в БД с created_at и char_length
- ✅ Реализован soft delete (is_deleted = true)
- ✅ История диалогов сохраняется между перезапусками
- ✅ Все тесты проходят (coverage ≥ 98%)
- ✅ Mypy strict: 0 errors
- ✅ Ruff: 0 errors
- ✅ ADR-03 документирует принятое решение

### To-dos

- [ ] Создать ADR-03 с обоснованием выбора PostgreSQL + SQLAlchemy ORM
- [ ] Создать docker-compose.yml для PostgreSQL
- [ ] Добавить sqlalchemy, asyncpg, alembic в pyproject.toml
- [ ] Обновить Config для DATABASE_URL и .env.example
- [ ] Создать models.py с Message model (SQLAlchemy ORM)
- [ ] Создать database.py с async engine и session factory
- [ ] Настроить Alembic для async миграций
- [ ] Создать initial migration для messages table
- [ ] Создать MessageRepository с add_message, get_history, clear_history
- [ ] Рефакторить DialogueManager для использования MessageRepository
- [ ] Обновить main.py для инициализации БД и graceful shutdown
- [ ] Добавить db-up, db-down, db-migrate, db-reset в Makefile
- [ ] Создать тесты для models, repository и обновить тесты DialogueManager
- [ ] Обновить README.md и guides с инструкциями по БД