# Быстрое исправление: Frontend не подключается к API

**Проблема:** Frontend пытается обратиться к `http://localhost:8000` вместо `http://92.255.78.249:8003`

**Причина:** `NEXT_PUBLIC_API_URL` - это build-time переменная Next.js, встраивается в код при сборке.

---

## Решение: Пересборка Frontend на сервере

### Шаг 1: Скопируйте обновленные файлы на сервер

**Локально (Windows PowerShell):**

```powershell
cd c:\DEV\systech-aidd\systech-aidd

# Скопируйте обновленные файлы
scp -i <путь_к_SSH_ключу> docker-compose.prod.yml systech@92.255.78.249:/opt/systech/sunko/
scp -i <путь_к_SSH_ключу> Dockerfile.frontend systech@92.255.78.249:/opt/systech/sunko/
scp -i <путь_к_SSH_ключу> .env systech@92.255.78.249:/opt/systech/sunko/

# Скопируйте директорию frontend (важно сохранить структуру frontend/app)
scp -i <путь_к_SSH_ключу> -r frontend systech@92.255.78.249:/opt/systech/sunko/

# Проверьте на сервере, что путь frontend/app существует:
# ssh -i <путь_к_ключу> systech@92.255.78.249 "ls -la /opt/systech/sunko/frontend/app"
```

### Шаг 2: Пересоберите Frontend на сервере

**На сервере (SSH):**

```bash
ssh -i <путь_к_ключу> systech@92.255.78.249
cd /opt/systech/sunko

# Остановите текущий frontend
docker compose -f docker-compose.prod.yml stop frontend

# Пересоберите frontend с правильным API URL
docker compose -f docker-compose.prod.yml build --no-cache frontend

# Запустите frontend
docker compose -f docker-compose.prod.yml up -d frontend

# Проверьте логи
docker compose -f docker-compose.prod.yml logs -f frontend
```

### Шаг 3: Проверка

1. **Откройте браузер:** http://92.255.78.249:3003
2. **Откройте DevTools (F12)** → Network
3. **Попробуйте залогиниться**
4. **Проверьте URL запросов** - они должны идти на `92.255.78.249:8003`

---

## Альтернативное решение: Копирование всего проекта

Если не хватает каких-то файлов, скопируйте весь проект:

```powershell
# Локально (Windows PowerShell)
cd c:\DEV\systech-aidd\systech-aidd

scp -i <путь_к_ключу> -r frontend src migrations systech@92.255.78.249:/opt/systech/sunko/
scp -i <путь_к_ключу> Dockerfile.* docker-compose.prod.yml .env alembic.ini pyproject.toml uv.lock docker-entrypoint-api.sh systech@92.255.78.249:/opt/systech/sunko/
```

---

## Что изменилось

### В `docker-compose.prod.yml`:

```yaml
frontend:
  build:  # Вместо image
    context: ./frontend/app
    dockerfile: ../../Dockerfile.frontend
    args:
      NEXT_PUBLIC_API_URL: http://92.255.78.249:8003
  environment:
    NEXT_PUBLIC_API_URL: http://92.255.78.249:8003
```

### В `Dockerfile.frontend`:

```dockerfile
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN pnpm run build
```

---

## Проверка успешной сборки

После сборки в логах frontend должны появиться строки:

```
✓ Compiled successfully
✓ Generating static pages
✓ Collecting page data
✓ Finalizing page optimization
```

И frontend должен запуститься на порту 3000 (внешний 3003).

---

## Время выполнения

- Копирование файлов: ~1-2 минуты
- Сборка frontend: ~3-7 минут
- **Общее время:** ~5-10 минут

---

**После выполнения этих шагов frontend будет обращаться к правильному API URL.**

