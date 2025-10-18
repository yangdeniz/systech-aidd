# План D-Sprint-0: Basic Docker Setup

## Обзор

Создание Docker контейнеров для всех сервисов проекта и настройка docker-compose для локального запуска всего приложения одной командой. MVP подход - простота и скорость, без преждевременной оптимизации.

## Файлы для создания

### 1. Dockerfile.bot - Telegram бот

Простой Dockerfile для Python приложения с UV:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка UV
RUN pip install uv

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen

# Копирование исходного кода
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Команда запуска
CMD ["uv", "run", "python", "-m", "src.bot.main"]
```

### 2. Dockerfile.api - FastAPI сервис

Похожий Dockerfile с entrypoint для миграций:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./
COPY docker-entrypoint-api.sh ./

RUN chmod +x docker-entrypoint-api.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint-api.sh"]
```

### 3. docker-entrypoint-api.sh - Скрипт миграций

```bash
#!/bin/bash
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting API server..."
exec uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 4. Dockerfile.frontend - Next.js приложение

```dockerfile
FROM node:20-slim

# Установка pnpm
RUN npm install -g pnpm

WORKDIR /app

# Копирование package.json
COPY package.json pnpm-lock.yaml ./

# Установка зависимостей
RUN pnpm install --frozen-lockfile

# Копирование остальных файлов
COPY . ./

# Сборка для production
RUN pnpm run build

EXPOSE 3000

# Production режим
CMD ["pnpm", "run", "start"]
```

### 5. .dockerignore файлы

**`.dockerignore.bot`** (в корне, для Telegram бота):

```
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
.venv
*.egg-info
.mypy_cache
.ruff_cache
*.log
.env
node_modules
frontend/
tests/
docs/
devops/
.git
.gitignore
README.md
Dockerfile.api
Dockerfile.frontend
docker-entrypoint-api.sh
```

**`.dockerignore.api`** (в корне, для FastAPI):

```
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
.venv
*.egg-info
.mypy_cache
.ruff_cache
*.log
.env
node_modules
frontend/
tests/
docs/
devops/
.git
.gitignore
README.md
Dockerfile.bot
Dockerfile.frontend
src/bot/
```

**`frontend/app/.dockerignore`**:

```
node_modules
.next
out
dist
coverage
.turbo
*.log
.env*.local
.git
```

### 6. Обновление docker-compose.yml

Расширяем существующий файл, добавляя 3 новых сервиса:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: homeguru-postgres
    environment:
      POSTGRES_DB: homeguru
      POSTGRES_USER: homeguru
      POSTGRES_PASSWORD: homeguru_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U homeguru"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - homeguru-network

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    container_name: homeguru-bot
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+asyncpg://homeguru:homeguru_dev@postgres:5432/homeguru
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - homeguru-network
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: homeguru-api
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+asyncpg://homeguru:homeguru_dev@postgres:5432/homeguru
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - homeguru-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend/app
      dockerfile: ../../Dockerfile.frontend
    container_name: homeguru-frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - api
    networks:
      - homeguru-network
    restart: unless-stopped

networks:
  homeguru-network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
```

### 7. Обновление README.md

Добавлена секция "🐳 Запуск через Docker" с подробными инструкциями по:
- Быстрому старту с docker compose up
- Управлению контейнерами
- Просмотру логов
- Пересборке образов
- Требованиям к системе

## Порядок выполнения

1. ✅ Создать `.dockerignore` файлы (bot, api, frontend)
2. ✅ Создать `Dockerfile.bot`
3. ✅ Создать `Dockerfile.api`
4. ✅ Создать `docker-entrypoint-api.sh` и сделать executable
5. ✅ Создать `Dockerfile.frontend`
6. ✅ Обновить `docker-compose.yml`
7. ✅ Обновить `README.md` с инструкциями по Docker
8. ⏳ Протестировать: `docker compose up --build`
9. ⏳ Проверить работу всех 4 сервисов
10. ⏳ Обновить `devops/doc/devops-roadmap.md` - добавить ссылку на план

## Проверка работоспособности

После `docker compose up` проверить:

1. **PostgreSQL:** `docker compose logs postgres` - должен быть "ready to accept connections"
2. **API:** Открыть http://localhost:8000/docs - должна отобразиться документация
3. **Frontend:** Открыть http://localhost:3000 - должна открыться главная страница
4. **Bot:** `docker compose logs bot` - должны быть логи "Bot is starting polling..."

## Ожидаемый результат

Одна команда `docker compose up` запускает все 4 сервиса:

- PostgreSQL поднимается первым с health check
- API ждет готовности БД, запускает миграции, стартует на порту 8000
- Bot ждет готовности БД и начинает polling Telegram
- Frontend выполняет production build и стартует на порту 3000

Все сервисы работают в одной Docker сети, видят друг друга по именам сервисов.

## Результаты выполнения

### Созданные файлы

1. **Docker контейнеры:**
   - `.dockerignore` - исключения для bot и api (общий файл)
   - `frontend/app/.dockerignore` - исключения для Next.js
   - `Dockerfile.bot` - контейнер для Telegram бота
   - `Dockerfile.api` - контейнер для FastAPI с миграциями и curl
   - `Dockerfile.frontend` - контейнер для Next.js (production build)
   - `docker-entrypoint-api.sh` - скрипт автоматических миграций

2. **Оркестрация:**
   - `docker-compose.yml` - обновлен с 4 сервисами (postgres, bot, api, frontend)
   - Настроены health checks
   - Настроена сеть homeguru-network
   - Настроены зависимости между сервисами

3. **Документация:**
   - `README.md` - добавлена секция "🐳 Запуск через Docker"
   - `devops/doc/plans/d0-basic-docker-setup.md` - сохранен план спринта

### Ключевые особенности реализации

**MVP подход:**
- Single-stage Dockerfile для всех сервисов (простота)
- Production build для frontend (оптимизированный bundle)
- Автоматические миграции через entrypoint
- Простые .dockerignore файлы
- Curl установлен в API для health checks

**Оркестрация:**
- Health checks для postgres и api
- Правильные зависимости: bot/api ждут БД, frontend ждет api
- Единая Docker сеть для взаимодействия
- Volume для персистентности данных PostgreSQL

**Удобство использования:**
- Одна команда `docker compose up` запускает всё
- Логи доступны через `docker compose logs`
- Простые команды управления контейнерами

### Следующие шаги

1. Протестировать локальный запуск через `docker compose up --build`
2. Проверить работу всех 4 сервисов
3. Обновить devops-roadmap.md со ссылкой на план
4. Переходить к D-Sprint-1: Build & Publish (GitHub Actions, GHCR)

