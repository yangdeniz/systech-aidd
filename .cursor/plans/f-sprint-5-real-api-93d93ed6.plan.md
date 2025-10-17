<!-- 93d93ed6-9574-45ce-ab26-9c838b785ed0 e150ab9b-42e8-4b6d-bd42-7fb5bf03eaee -->
# F-Sprint-5: Переход с MockAPI на реальный API

## Цель

Заменить Mock реализацию StatCollector на реальную с интеграцией PostgreSQL базы данных и переключить систему на production-ready API с кэшированием и оптимизацией производительности.

## Контекст

- **Текущее состояние**: Frontend использует Mock API из F-Sprint-1 с тестовыми данными
- **База данных**: PostgreSQL с таблицами `users` и `messages` (реализовано в спринтах S1-S2)
- **Модели**: User и Message models с repositories уже существуют
- **Интерфейс**: Protocol `StatCollector` готов для реализации

## Архитектура решения

### 1. RealStatCollector Implementation

Создать `src/api/collectors.py` → класс `RealStatCollector`:

- Использовать существующие repository (MessageRepository, UserRepository)
- SQL запросы через SQLAlchemy async ORM
- Агрегация данных для метрик, временных рядов, топ пользователей
- Соответствие интерфейсу `StatCollector` protocol

### 2. Configuration Management

Создать `src/api/config.py`:

- Enum для режимов (MOCK, REAL)
- Конфигурация через environment variables
- Factory pattern для создания нужного collector
- Поддержка dev/prod окружений

### 3. Database Queries

Оптимизированные SQL запросы для:

- **Метрики**: count dialogues, active users, avg messages, today messages
- **Time Series**: группировка по часам (day) или дням (week/month)
- **Recent Dialogues**: последние 10 с сортировкой по last_message_at
- **Top Users**: топ-5 по количеству сообщений

### 4. Caching Strategy

Добавить кэширование в `src/api/cache.py`:

- In-memory cache с TTL (60 секунд)
- Cache key по периоду (day/week/month)
- Автоматическая инвалидация по времени
- Простая реализация через словарь + asyncio

### 5. API Integration

Обновить `src/api/main.py`:

- Заменить hardcoded `MockStatCollector` на factory function
- Dependency injection для collector
- Поддержка переключения через env var

## Ключевые файлы для изменения

**Новые файлы:**

- `src/api/config.py` - конфигурация и factory
- `src/api/cache.py` - кэширование (опционально)

**Изменяемые файлы:**

- `src/api/collectors.py` - добавить RealStatCollector
- `src/api/main.py` - использовать factory вместо hardcoded Mock
- `frontend/app/.env.local` - конфигурация API URL (если нужно)

**Тесты:**

- `tests/api/test_real_collector.py` - unit тесты для RealStatCollector
- `tests/api/test_api.py` - интеграционные тесты с Real API

## Критические решения

1. **SQL запросы**: использовать SQLAlchemy Core для производительности vs ORM для читаемости

- Решение: SQLAlchemy ORM с оптимизацией (select + join где нужно)

2. **Кэширование**: простое in-memory vs Redis

- Решение: начать с in-memory (простота), мигрировать на Redis при необходимости

3. **Конфигурация**: hard switch vs градуальный rollout

- Решение: hard switch через env var (COLLECTOR_MODE=real|mock)

## План тестирования

1. **Unit тесты**: RealStatCollector с mock database session
2. **Integration тесты**: полный flow через FastAPI с тестовой БД
3. **Performance тесты**: проверка времени ответа с кэшем и без
4. **Manual тесты**: запуск frontend + backend с реальными данными

## Deployment Strategy

1. Добавить seeding скрипт для тестовых данных (если БД пустая)
2. Обновить Makefile команды для запуска с Real API
3. Документировать процесс переключения Mock ↔ Real
4. Создать ADR-05 с описанием архитектурных решений

## Success Metrics

- ✅ RealStatCollector соответствует Protocol интерфейсу
- ✅ Все тесты проходят (unit + integration)
- ✅ Frontend корректно отображает реальные данные
- ✅ Время ответа API < 500ms (с кэшем < 50ms)
- ✅ Нет SQL N+1 проблем
- ✅ Поддержка переключения Mock/Real через env var

### To-dos

- [ ] Реализовать RealStatCollector в src/api/collectors.py с интеграцией PostgreSQL
- [ ] Создать src/api/config.py с factory pattern для выбора collector (Mock/Real)
- [ ] Добавить in-memory кэширование в src/api/cache.py (опционально)
- [ ] Обновить src/api/main.py для использования factory вместо hardcoded Mock
- [ ] Написать unit и integration тесты для RealStatCollector
- [ ] Провести performance тестирование и оптимизацию SQL запросов
- [ ] Обновить документацию и создать отчет спринта