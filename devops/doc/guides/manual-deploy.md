# Руководство по ручному развертыванию на production сервере

**Версия:** 1.0  
**Дата создания:** 2025-10-18  
**Спринт:** D-Sprint-2

## Содержание

1. [Требования](#требования)
2. [Подготовка локально](#подготовка-локально)
3. [Подключение к серверу](#подключение-к-серверу)
4. [Копирование файлов](#копирование-файлов)
5. [Загрузка образов](#загрузка-образов)
6. [Запуск сервисов](#запуск-сервисов)
7. [Проверка работоспособности](#проверка-работоспособности)
8. [Управление сервисами](#управление-сервисами)
9. [Troubleshooting](#troubleshooting)

---

## Требования

### Предустановленное ПО на сервере

Сервер должен иметь предустановленное следующее ПО:

- **Docker** версии 20.10 или выше
- **Docker Compose** версии 2.0 или выше (команда `docker compose`, не `docker-compose`)
- **SSH сервер** для удаленного доступа

### Что нужно иметь локально

- **SSH ключ** для доступа к серверу (файл `.pem` или `.key`)
- Доступ к репозиторию проекта
- Файлы для копирования (см. раздел "Подготовка локально")

### Информация о сервере

| Параметр | Значение |
|----------|----------|
| IP адрес | `92.255.78.249` |
| Пользователь | `systech` |
| Рабочая директория | `/opt/systech/sunko` |
| Порт API | `8003` |
| Порт Frontend | `3003` |

---

## Подготовка локально

### 1. Перейдите в директорию проекта

```bash
cd c:\DEV\systech-aidd\systech-aidd
```

### 2. Создайте .env файл на основе шаблона

```bash
# Windows PowerShell
Copy-Item env.production .env

# Linux/macOS
cp env.production .env
```

### 3. Отредактируйте .env файл

Откройте файл `.env` в текстовом редакторе и заполните все значения:

**Обязательные параметры для изменения:**

```env
# Сгенерируйте сильный пароль администратора
ADMIN_PASSWORD=VeryStr0ngP@ssw0rd2024!

# Сгенерируйте случайный JWT секретный ключ (минимум 32 символа)
# Используйте: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=ваш_случайный_секретный_ключ_min_32_chars

# Укажите ваш OpenRouter API ключ
OPENROUTER_API_KEY=sk-or-v1-ваш_ключ_здесь

# Укажите ваш Telegram Bot токен (если используется бот)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwXYz
```

**Параметры, которые можно оставить без изменений:**

```env
DATABASE_URL=postgresql+asyncpg://homeguru:homeguru_dev@postgres:5432/homeguru
COLLECTOR_MODE=real
ADMIN_USERNAME=admin
JWT_ACCESS_TOKEN_EXPIRE_DAYS=30
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
LLM_MODEL=anthropic/claude-3.5-sonnet
NEXT_PUBLIC_API_URL=http://92.255.78.249:8003
```

### 4. Проверьте файлы для копирования

Убедитесь, что в директории проекта есть следующие файлы:

- ✅ `docker-compose.prod.yml` - конфигурация Docker Compose
- ✅ `.env` - переменные окружения (только что созданный)

---

## Подключение к серверу

### 1. Проверьте SSH ключ

Убедитесь, что у вас есть SSH ключ и правильные права доступа:

```bash
# Windows PowerShell (если требуется, установите права)
# Обычно в Windows проблем с правами не возникает

# Linux/macOS
chmod 600 /path/to/your/ssh-key.pem
```

### 2. Подключитесь к серверу

```bash
# Замените /path/to/your/ssh-key.pem на путь к вашему ключу
ssh -i /path/to/your/ssh-key.pem systech@92.255.78.249
```

**Пример для Windows:**
```powershell
ssh -i C:\Users\YourName\.ssh\systech-key.pem systech@92.255.78.249
```

**Пример для Linux/macOS:**
```bash
ssh -i ~/.ssh/systech-key.pem systech@92.255.78.249
```

### 3. Проверьте установленное ПО

После подключения выполните проверку:

```bash
# Проверка Docker
docker --version
# Ожидается: Docker version 20.10.x или выше

# Проверка Docker Compose
docker compose version
# Ожидается: Docker Compose version v2.x.x или выше
```

### 4. Создайте рабочую директорию

```bash
mkdir -p /opt/systech/sunko
cd /opt/systech/sunko
```

### 5. Оставайтесь подключенными

Не закрывайте это SSH соединение - оно понадобится для следующих шагов.

---

## Копирование файлов

Откройте **новый терминал** на вашем локальном компьютере (не закрывая SSH сессию).

### 1. Перейдите в директорию проекта

```bash
cd c:\DEV\systech-aidd\systech-aidd
```

### 2. Скопируйте docker-compose.prod.yml

```bash
scp -i /path/to/your/ssh-key.pem docker-compose.prod.yml systech@92.255.78.249:/opt/systech/sunko/
```

**Пример для Windows PowerShell:**
```powershell
scp -i C:\Users\YourName\.ssh\systech-key.pem docker-compose.prod.yml systech@92.255.78.249:/opt/systech/sunko/
```

### 3. Скопируйте .env файл

```bash
scp -i /path/to/your/ssh-key.pem .env systech@92.255.78.249:/opt/systech/sunko/.env
```

**Пример для Windows PowerShell:**
```powershell
scp -i C:\Users\YourName\.ssh\systech-key.pem .env systech@92.255.78.249:/opt/systech/sunko/.env
```

### 4. Скопируйте исходники проекта (для сборки Frontend)

**Важно:** Frontend нужно собрать на сервере с правильным `NEXT_PUBLIC_API_URL`, так как это build-time переменная.

**Windows PowerShell (используйте scp -r для директорий):**
```powershell
# Копирование всей директории проекта
scp -i C:\Users\YourName\.ssh\systech-key.pem -r frontend systech@92.255.78.249:/opt/systech/sunko/
scp -i C:\Users\YourName\.ssh\systech-key.pem -r src systech@92.255.78.249:/opt/systech/sunko/
scp -i C:\Users\YourName\.ssh\systech-key.pem -r migrations systech@92.255.78.249:/opt/systech/sunko/
scp -i C:\Users\YourName\.ssh\systech-key.pem Dockerfile.* systech@92.255.78.249:/opt/systech/sunko/
scp -i C:\Users\YourName\.ssh\systech-key.pem alembic.ini systech@92.255.78.249:/opt/systech/sunko/
scp -i C:\Users\YourName\.ssh\systech-key.pem pyproject.toml systech@92.255.78.249:/opt/systech/sunko/
scp -i C:\Users\YourName\.ssh\systech-key.pem uv.lock systech@92.255.78.249:/opt/systech/sunko/
scp -i C:\Users\YourName\.ssh\systech-key.pem docker-entrypoint-api.sh systech@92.255.78.249:/opt/systech/sunko/
```

**Linux/macOS:**
```bash
scp -i ~/.ssh/systech-key.pem -r frontend src migrations Dockerfile.* alembic.ini pyproject.toml uv.lock docker-entrypoint-api.sh systech@92.255.78.249:/opt/systech/sunko/
```

### 5. Проверьте, что файлы скопированы

Вернитесь в **SSH терминал** на сервере и выполните:

```bash
cd /opt/systech/sunko
ls -la
```

Вы должны увидеть:
```
-rw-r--r-- 1 systech systech  xxxx дата docker-compose.prod.yml
-rw-r--r-- 1 systech systech  xxxx дата .env
drwxr-xr-x 3 systech systech  xxxx дата frontend
drwxr-xr-x 3 systech systech  xxxx дата src
drwxr-xr-x 2 systech systech  xxxx дата migrations
-rw-r--r-- 1 systech systech  xxxx дата Dockerfile.api
-rw-r--r-- 1 systech systech  xxxx дата Dockerfile.bot
-rw-r--r-- 1 systech systech  xxxx дата Dockerfile.frontend
...
```

---

## Загрузка образов и сборка Frontend

Все следующие команды выполняются на **сервере** (в SSH терминале).

### 1. Загрузите Docker образы для Bot и API из GitHub Container Registry

```bash
cd /opt/systech/sunko
docker compose -f docker-compose.prod.yml pull bot api postgres
```

**Примечание:** Образы публичные, поэтому `docker login` не требуется.

Вы должны увидеть загрузку следующих образов:
- `postgres:16-alpine`
- `ghcr.io/yangdeniz/homeguru-bot:latest`
- `ghcr.io/yangdeniz/homeguru-api:latest`

**Ожидаемое время:** 2-5 минут в зависимости от скорости интернет соединения.

### 2. Соберите Frontend с правильным NEXT_PUBLIC_API_URL

**Важно:** Frontend собирается локально, чтобы переменная `NEXT_PUBLIC_API_URL` была правильно установлена на этапе сборки.

```bash
docker compose -f docker-compose.prod.yml build frontend
```

**Ожидаемое время:** 3-7 минут (зависит от мощности сервера).

**Что происходит:**
- Устанавливается Node.js и pnpm
- Устанавливаются зависимости frontend
- Собирается Next.js приложение с `NEXT_PUBLIC_API_URL=http://92.255.78.249:8003`

### 3. Проверьте созданные образы

```bash
docker images | grep homeguru
```

Вы должны увидеть:
- `ghcr.io/yangdeniz/homeguru-bot:latest` (из GHCR)
- `ghcr.io/yangdeniz/homeguru-api:latest` (из GHCR)
- `sunko-frontend` или `homeguru-frontend` (собран локально)

---

## Запуск сервисов

### 1. Запустите все сервисы в фоновом режиме

```bash
cd /opt/systech/sunko
docker compose -f docker-compose.prod.yml up -d
```

**Что происходит:**
1. Создается Docker network `homeguru-network`
2. Создается volume `postgres_data` для базы данных
3. Запускается PostgreSQL контейнер
4. После healthcheck PostgreSQL запускаются Bot и API
5. После запуска API запускается Frontend

**Ожидаемое время:** 30-60 секунд для полного запуска всех сервисов.

### 2. Проверьте статус контейнеров

```bash
docker compose -f docker-compose.prod.yml ps
```

**Ожидаемый результат:**

```
NAME                 COMMAND                  SERVICE    STATUS         PORTS
homeguru-api         "./docker-entrypoint…"   api        Up 30 seconds  0.0.0.0:8003->8000/tcp
homeguru-bot         "uv run python -m sr…"   bot        Up 30 seconds  
homeguru-frontend    "docker-entrypoint.s…"   frontend   Up 20 seconds  0.0.0.0:3003->3000/tcp
homeguru-postgres    "docker-entrypoint.s…"   postgres   Up 40 seconds  0.0.0.0:5432->5432/tcp
```

Все сервисы должны иметь статус `Up`.

### 3. Проверьте логи API (миграции БД)

Миграции базы данных выполняются автоматически при старте API контейнера через `docker-entrypoint-api.sh`.

```bash
docker compose -f docker-compose.prod.yml logs api
```

**Ожидаемые строки в логах:**

```
homeguru-api  | Running database migrations...
homeguru-api  | INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
homeguru-api  | INFO  [alembic.runtime.migration] Will assume transactional DDL.
homeguru-api  | INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, migration_name
homeguru-api  | Starting API server...
homeguru-api  | INFO:     Started server process [1]
homeguru-api  | INFO:     Waiting for application startup.
homeguru-api  | INFO:     Application startup complete.
homeguru-api  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Проверка работоспособности

### 1. Проверьте статус всех контейнеров

```bash
docker compose -f docker-compose.prod.yml ps
```

Все сервисы должны быть в статусе `Up` (не `Restarting`, не `Exited`).

### 2. Проверьте логи каждого сервиса

**PostgreSQL:**
```bash
docker compose -f docker-compose.prod.yml logs postgres
```
Должна быть строка: `database system is ready to accept connections`

**API:**
```bash
docker compose -f docker-compose.prod.yml logs api
```
Должна быть строка: `Uvicorn running on http://0.0.0.0:8000`

**Frontend:**
```bash
docker compose -f docker-compose.prod.yml logs frontend
```
Должна быть строка: `Ready in` или `Compiled successfully`

**Bot:**
```bash
docker compose -f docker-compose.prod.yml logs bot
```
Должна быть строка с успешным подключением к Telegram API.

### 3. Проверьте API изнутри сервера

```bash
curl http://localhost:8003/
```

**Ожидаемый ответ:**
```json
{"message":"HomeGuru API is running","version":"1.0.0"}
```

### 4. Проверьте API снаружи (с локального компьютера)

Откройте новый терминал на **вашем локальном компьютере** и выполните:

```bash
curl http://92.255.78.249:8003/
```

**Ожидаемый ответ:**
```json
{"message":"HomeGuru API is running","version":"1.0.0"}
```

### 5. Проверьте Frontend в браузере

Откройте браузер и перейдите по адресу:

```
http://92.255.78.249:3003
```

Вы должны увидеть главную страницу приложения HomeGuru.

### 6. Проверьте healthcheck API

```bash
# На сервере
docker inspect homeguru-api | grep -A 10 Health
```

Должен показывать `"Status": "healthy"`.

### 7. Проверьте подключение к базе данных

```bash
# Подключитесь к PostgreSQL контейнеру
docker exec -it homeguru-postgres psql -U homeguru -d homeguru

# Внутри psql выполните:
\dt
```

Вы должны увидеть таблицы: `users`, `messages`, `alembic_version`.

Для выхода из psql:
```
\q
```

---

## Управление сервисами

### Просмотр логов

**Все сервисы (live tail):**
```bash
docker compose -f docker-compose.prod.yml logs -f
```

**Конкретный сервис:**
```bash
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f bot
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f postgres
```

**Последние N строк:**
```bash
docker compose -f docker-compose.prod.yml logs --tail=100 api
```

### Перезапуск сервисов

**Все сервисы:**
```bash
docker compose -f docker-compose.prod.yml restart
```

**Конкретный сервис:**
```bash
docker compose -f docker-compose.prod.yml restart api
docker compose -f docker-compose.prod.yml restart bot
docker compose -f docker-compose.prod.yml restart frontend
```

### Остановка сервисов

**Остановить все сервисы (сохранить данные):**
```bash
docker compose -f docker-compose.prod.yml stop
```

**Остановить и удалить контейнеры (сохранить данные в volumes):**
```bash
docker compose -f docker-compose.prod.yml down
```

**Остановить и удалить ВСЁ включая volumes (ДАННЫЕ БУДУТ УДАЛЕНЫ!):**
```bash
docker compose -f docker-compose.prod.yml down -v
```

### Запуск после остановки

```bash
docker compose -f docker-compose.prod.yml up -d
```

### Обновление на новую версию

```bash
# 1. Загрузите новые образы
docker compose -f docker-compose.prod.yml pull

# 2. Пересоздайте контейнеры
docker compose -f docker-compose.prod.yml up -d

# 3. Проверьте логи
docker compose -f docker-compose.prod.yml logs -f
```

---

## Troubleshooting

### Проблема: Контейнер постоянно перезапускается

**Диагностика:**
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs <service_name>
```

**Возможные причины:**
1. Ошибки в `.env` файле (неверные переменные)
2. Проблемы с подключением к базе данных
3. Отсутствие обязательных переменных окружения

**Решение:**
1. Проверьте логи сервиса
2. Проверьте `.env` файл на наличие всех переменных
3. Убедитесь, что PostgreSQL запустился успешно

### Проблема: API недоступен снаружи

**Диагностика:**
```bash
# На сервере проверьте, что API слушает на всех интерфейсах
curl http://localhost:8003/
netstat -tlnp | grep 8003
```

**Возможные причины:**
1. Firewall блокирует порт 8003
2. Docker неправильно пробросил порт

**Решение:**
```bash
# Проверьте firewall (если используется)
sudo ufw status
sudo ufw allow 8003/tcp

# Проверьте проброс портов Docker
docker port homeguru-api
```

### Проблема: Frontend показывает ошибку подключения к API

**Ошибка в браузере:**
```
POST http://localhost:8000/api/auth/login net::ERR_CONNECTION_REFUSED
```

**Причина:**
Frontend пытается обратиться к `http://localhost:8000` вместо `http://92.255.78.249:8003`. Это происходит потому, что `NEXT_PUBLIC_API_URL` - это build-time переменная Next.js, которая встраивается в код при сборке.

**Решение:**
Frontend необходимо пересобрать с правильным `NEXT_PUBLIC_API_URL`:

1. Убедитесь, что в `docker-compose.prod.yml` указан правильный build arg:
```yaml
frontend:
  build:
    context: ./frontend/app
    dockerfile: ../../Dockerfile.frontend
    args:
      NEXT_PUBLIC_API_URL: http://92.255.78.249:8003
```

2. Пересоберите frontend контейнер:
```bash
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

3. Проверьте логи frontend:
```bash
docker compose -f docker-compose.prod.yml logs frontend | grep API
```

4. Откройте DevTools в браузере (F12) → Network → проверьте, что запросы идут на `92.255.78.249:8003`

### Проблема: Миграции БД не выполнились

**Диагностика:**
```bash
docker compose -f docker-compose.prod.yml logs api | grep migration
```

**Решение:**
Выполните миграции вручную:
```bash
docker exec -it homeguru-api uv run alembic upgrade head
```

### Проблема: PostgreSQL не запускается

**Диагностика:**
```bash
docker compose -f docker-compose.prod.yml logs postgres
```

**Возможные причины:**
1. Порт 5432 занят другим процессом
2. Проблемы с volume

**Решение:**
```bash
# Проверьте, что порт свободен
sudo netstat -tlnp | grep 5432

# Если нужно пересоздать БД (ДАННЫЕ БУДУТ УДАЛЕНЫ!)
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d
```

### Проблема: Нет места на диске

**Диагностика:**
```bash
df -h
docker system df
```

**Решение:**
Очистите неиспользуемые Docker ресурсы:
```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить всё неиспользуемое (images, containers, networks, volumes)
docker system prune -a --volumes
```

### Проблема: Bot не подключается к Telegram

**Диагностика:**
```bash
docker compose -f docker-compose.prod.yml logs bot
```

**Возможные причины:**
1. Неверный `TELEGRAM_BOT_TOKEN`
2. Нет доступа к интернету

**Решение:**
1. Проверьте токен в `.env` файле
2. Проверьте интернет соединение:
```bash
ping api.telegram.org
```
3. Перезапустите bot:
```bash
docker compose -f docker-compose.prod.yml restart bot
```

### Проблема: Ошибка "OPENROUTER_MODEL is required in .env"

**Диагностика:**
```bash
docker compose -f docker-compose.prod.yml logs api
# Видите: ValueError("OPENROUTER_MODEL is required in .env")
```

**Причина:**
В `.env` файле отсутствует переменная `OPENROUTER_MODEL`. Обратите внимание, что для работы нужны **обе** переменные: `OPENROUTER_MODEL` (для бота) и `LLM_MODEL` (для API chat).

**Решение:**
1. Проверьте наличие обеих переменных в `.env`:
```bash
cat .env | grep -E "OPENROUTER_MODEL|LLM_MODEL"
```
2. Если переменных нет, добавьте их:
```bash
echo "OPENROUTER_MODEL=anthropic/claude-3.5-sonnet" >> .env
echo "LLM_MODEL=anthropic/claude-3.5-sonnet" >> .env
```
3. Скопируйте обновленный .env на сервер:
```bash
# Локально
scp -i <путь_к_ключу> .env systech@92.255.78.249:/opt/systech/sunko/.env
```
4. Перезапустите сервисы на сервере:
```bash
# На сервере
docker compose -f docker-compose.prod.yml restart
```

### Получение детальной информации

**Информация о контейнере:**
```bash
docker inspect homeguru-api
```

**Статистика использования ресурсов:**
```bash
docker stats
```

**Войти в контейнер для отладки:**
```bash
docker exec -it homeguru-api /bin/bash
```

---

## Чек-лист успешного развертывания

Проверьте все пункты после развертывания:

- [ ] Все 4 контейнера запущены (`docker compose ps` показывает статус `Up`)
- [ ] PostgreSQL принимает подключения
- [ ] Миграции базы данных выполнены успешно
- [ ] API доступен локально: `curl http://localhost:8003/`
- [ ] API доступен снаружи: `curl http://92.255.78.249:8003/`
- [ ] Frontend открывается в браузере: `http://92.255.78.249:3003`
- [ ] Bot подключился к Telegram (если используется)
- [ ] Нет ошибок в логах сервисов
- [ ] Healthcheck API возвращает `healthy`
- [ ] В базе данных созданы таблицы и администратор

---

## Полезные команды (шпаргалка)

```bash
# Статус всех сервисов
docker compose -f docker-compose.prod.yml ps

# Логи в реальном времени
docker compose -f docker-compose.prod.yml logs -f

# Перезапуск всех сервисов
docker compose -f docker-compose.prod.yml restart

# Остановка всех сервисов
docker compose -f docker-compose.prod.yml down

# Запуск всех сервисов
docker compose -f docker-compose.prod.yml up -d

# Обновление на новую версию
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Проверка API
curl http://localhost:8003/

# Статистика контейнеров
docker stats

# Очистка неиспользуемых образов
docker image prune
```

---

## Что дальше?

После успешного развертывания:

1. **Настройте регулярные бэкапы базы данных**
2. **Настройте мониторинг сервисов**
3. **Изучите спринт D-Sprint-3** для автоматизации развертывания через GitHub Actions
4. **Настройте SSL сертификаты** для HTTPS (опционально)
5. **Настройте домен** вместо использования IP адреса (опционально)

---

## Поддержка

Если возникли проблемы:

1. Проверьте раздел [Troubleshooting](#troubleshooting)
2. Посмотрите логи сервисов
3. Обратитесь к документации проекта
4. Создайте issue в репозитории проекта

---

**Конец руководства**

