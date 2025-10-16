# Sprint S2: User Management & Profiles

## Overview

Add full user profile management to track user interactions with the bot. Store user data from Telegram API (username, first/last name, language_code) and activity metrics (first_seen, last_seen).

## Architecture Approach

Follow existing patterns from Sprint-1:

- SQLAlchemy ORM models (like `Message` model)
- Repository pattern (like `MessageRepository`)
- Async operations throughout
- Protocol interface for DIP
- Session factory pattern from `main.py`

## Implementation Steps

### 1. Database Model (`src/bot/models.py`)

Add `User` model next to existing `Message` model:

- `id`: Primary key (auto-increment)
- `telegram_id`: BigInteger, unique, indexed (Telegram user ID)
- `username`: String(255), nullable (can be None)
- `first_name`: String(255), nullable
- `last_name`: String(255), nullable
- `language_code`: String(10), nullable
- `first_seen`: DateTime with timezone (first interaction)
- `last_seen`: DateTime with timezone (last interaction, auto-update)
- `is_active`: Boolean (default True)

**Reference:** `21:54:src/bot/models.py` - existing Message model pattern

### 2. Foreign Key Relationship

Update `Message` model to add foreign key:

- Add `user_id` foreign key to `users.id`
- Keep `user_id` as BigInteger (Telegram ID for backward compatibility)
- Add `user` relationship via SQLAlchemy relationship()

**Note:** Migration will handle existing data by creating users first

### 3. User Repository (`src/bot/repository.py`)

Add `UserRepository` class with async methods:

- `get_or_create_user(telegram_id, username, first_name, last_name, language_code)` -> User
  - Find by telegram_id or create new user
  - Update last_seen on every call
  - Update username/names if changed
- `get_user_by_telegram_id(telegram_id)` -> User | None
- `update_last_seen(telegram_id)` -> None
- `get_active_users_count()` -> int

**Reference:** `18:154:src/bot/repository.py` - MessageRepository pattern

### 4. Protocol Interface (`src/bot/interfaces.py`)

Add `UserStorage` Protocol for dependency inversion:

- `get_or_create_user()` method signature
- `update_last_seen()` method signature

**Reference:** `40:88:src/bot/interfaces.py` - DialogueStorage protocol

### 5. Integration Point (`src/bot/bot.py`)

Update message handlers to collect user data:

- Extract user data from `message.from_user` (aiogram provides username, first_name, last_name, language_code)
- Call `user_repository.get_or_create_user()` at the start of:
  - `handle_message()`
  - `handle_photo()`
  - `handle_voice()`
  - Command handlers (`cmd_start`, `cmd_reset`, etc.)

**Reference:** `102:122:src/bot/bot.py` - existing handler pattern

### 6. Dependency Injection (`src/bot/main.py`)

Update initialization:

- Create `UserRepository` instance
- Pass to `TelegramBot` constructor
- Store as instance variable

**Reference:** `46:100:src/bot/main.py` - existing DI pattern

### 7. Alembic Migration

Create migration `add_users_table`:

```python
# Create users table
# Add foreign key to messages.user_id -> users.telegram_id
# Backfill users from existing messages (distinct user_id values)
# Add index on users.telegram_id
```

**Reference:** `migrations/versions/5b38e2158d23_dd_messages_table_with.py`

### 8. Tests

Create `tests/test_user_repository.py`:

- Test `get_or_create_user()` creates new user
- Test `get_or_create_user()` returns existing user
- Test `last_seen` updates on every call
- Test username/name updates when changed
- Test `get_active_users_count()`
- Use in-memory SQLite for testing (like existing tests)

**Reference:** Check existing test patterns in `tests/test_*.py`

## Key Design Decisions (KISS)

1. **No middleware** - Direct calls in handlers (simpler, more explicit)
2. **get_or_create pattern** - Single method instead of separate get/create
3. **Soft relationship** - Keep user_id as BigInteger for backward compatibility, add FK separately
4. **Auto-update last_seen** - Happens in get_or_create (no separate tracking needed)
5. **No user sessions** - Simply track first_seen/last_seen timestamps

## Files to Create/Modify

**New files:**

- `tests/test_user_repository.py`

**Modified files:**

- `src/bot/models.py` - Add User model, update Message model
- `src/bot/repository.py` - Add UserRepository class
- `src/bot/interfaces.py` - Add UserStorage protocol
- `src/bot/bot.py` - Add user tracking to all handlers
- `src/bot/main.py` - Initialize UserRepository, pass to TelegramBot
- `migrations/versions/[new]_add_users_table.py` - Create via alembic

## Success Criteria

- ✅ User data automatically collected from all Telegram interactions
- ✅ User profiles persisted in PostgreSQL
- ✅ Foreign key relationship User ↔ Message established
- ✅ Activity metrics (first_seen, last_seen) tracked
- ✅ Tests pass with 95%+ coverage
- ✅ Type safety maintained (mypy strict passes)
- ✅ Zero linter errors (ruff)

