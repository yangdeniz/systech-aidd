<!-- 0e3b1789-8fd3-48f9-ab68-6f8af52335ad 1e23f7f1-3171-45b7-814d-420b2f6323c3 -->
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
COPY frontend/app/package.json frontend/app/pnpm-lock.yaml ./

# Установка зависимостей
RUN pnpm install

# Копирование остальных файлов
COPY frontend/app/ ./

EXPOSE 3000

# Development режим с hot reload
CMD ["pnpm", "run", "dev"]
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
      context: .
      dockerfile: Dockerfile.frontend
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
    volumes:
      - ./frontend/app:/app
      - /app/node_modules
      - /app/.next

networks:
  homeguru-network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
```

### 7. Обновление README.md

Добавить секцию "Запуск через Docker":

````markdown
## Запуск через Docker

### Быстрый старт

1. Убедитесь, что установлены Docker и Docker Compose v2
2. Создайте файл `.env` на основе `env.example`
3. Запустите все сервисы:

```bash
docker compose up
````

Сервисы будут доступны по адресам:

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Управление контейнерами

**Запуск в фоновом режиме:**

```bash
docker compose up -d
```

**Остановка:**

```bash
docker compose down
```

**Просмотр логов:**

```bash
docker compose logs -f
docker compose logs -f bot    # Только бот
docker compose logs -f api    # Только API
```

**Пересборка образов:**

```bash
docker compose build
docker compose up --build
```

**Очистка (с удалением данных БД):**

```bash
docker compose down -v
```

### Первый запуск

При первом запуске API автоматически выполнит миграции базы данных. Это может занять несколько секунд.

### Требования

- Docker 20.10+
- Docker Compose v2.0+
- Минимум 4 GB RAM
- Минимум 10 GB свободного места на диске

```

### 8. Создание директории devops/doc/plans/

Создать файл `devops/doc/plans/d0-basic-docker-plan.md` с этим планом после реализации.

## Порядок выполнения

1. Создать `.dockerignore` файлы (корневой и для frontend)
2. Создать `Dockerfile.bot`
3. Создать `Dockerfile.api`
4. Создать `docker-entrypoint-api.sh` и сделать executable
5. Создать `Dockerfile.frontend`
6. Обновить `docker-compose.yml`
7. Обновить `README.md` с инструкциями по Docker
8. Протестировать: `docker compose up --build`
9. Проверить работу всех 4 сервисов
10. Обновить `devops/doc/devops-roadmap.md` - добавить ссылку на план

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
- Frontend стартует в dev режиме на порту 3000 с hot reload

Все сервисы работают в одной Docker сети, видят друг друга по именам сервисов.

### To-dos

- [ ] Создать .dockerignore файлы для оптимизации сборки (корневой и frontend)
- [ ] Создать Dockerfile.bot для Telegram бота (Python + UV)
- [ ] Создать docker-entrypoint-api.sh для автоматических миграций
- [ ] Создать Dockerfile.api для FastAPI сервиса с entrypoint
- [ ] Создать Dockerfile.frontend для Next.js (dev режим с hot reload)
- [ ] Обновить docker-compose.yml - добавить bot, api, frontend с health checks
- [ ] Протестировать docker-compose up --build и проверить работу всех сервисов
- [ ] Обновить README.md с инструкциями по запуску через Docker
- [ ] Обновить devops-roadmap.md - добавить ссылку на план спринта