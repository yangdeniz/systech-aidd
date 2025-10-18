# Локальная сборка Frontend для Production

**Цель:** Собрать frontend образ локально с правильным `NEXT_PUBLIC_API_URL` и развернуть на сервере без копирования исходников.

---

## Преимущества локальной сборки

✅ Не нужно копировать исходники на сервер  
✅ Быстрее развертывание (уже собранный образ)  
✅ Можно протестировать образ локально перед развертыванием  
✅ Меньше зависимостей на сервере (не нужен Node.js для сборки)

---

## Способ 1: Загрузка образа файлом (рекомендуется для быстрого деплоя)

### Шаг 1: Соберите образ локально

**Важно:** API URL (`http://92.255.78.249:8003`) уже захардкожен в `Dockerfile.frontend`, поэтому build-arg не нужен.

**Windows PowerShell:**
```powershell
cd c:\DEV\systech-aidd\systech-aidd

# Соберите frontend (API URL уже захардкожен в Dockerfile)
docker build `
  -t homeguru-frontend:production `
  -f Dockerfile.frontend `
  ./frontend/app

# Проверьте, что образ создан
docker images | Select-String "homeguru-frontend"
```

**Linux/macOS:**
```bash
cd /path/to/systech-aidd

docker build \
  -t homeguru-frontend:production \
  -f Dockerfile.frontend \
  ./frontend/app

docker images | grep homeguru-frontend
```

**Ожидаемое время сборки:** 5-10 минут (зависит от мощности компьютера)

---

### Шаг 2: Сохраните образ в файл

```powershell
# Сохраните образ в .tar файл
docker save homeguru-frontend:production -o homeguru-frontend-production.tar

# Проверьте размер файла (обычно 500-800 MB)
Get-Item homeguru-frontend-production.tar
```

---

### Шаг 3: Скопируйте образ на сервер

```powershell
# Замените на ваш путь к SSH ключу
scp -i <путь_к_SSH_ключу> homeguru-frontend-production.tar systech@92.255.78.249:/opt/systech/sunko/
```

**Ожидаемое время:** 5-15 минут (зависит от скорости интернета)

---

### Шаг 4: Загрузите образ на сервере

```bash
# Подключитесь к серверу
ssh -i <путь_к_ключу> systech@92.255.78.249

cd /opt/systech/sunko

# Загрузите образ в Docker
docker load -i homeguru-frontend-production.tar

# Должны увидеть:
# Loaded image: homeguru-frontend:production

# Проверьте образ
docker images | grep homeguru-frontend

# Удалите .tar файл (опционально, для освобождения места)
rm homeguru-frontend-production.tar
```

---

### Шаг 5: Скопируйте docker-compose.prod.production.yml

**Локально:**
```powershell
scp -i <путь_к_ключу> docker-compose.prod.production.yml systech@92.255.78.249:/opt/systech/sunko/
```

**Или создайте на сервере вручную:**
```bash
# На сервере
nano docker-compose.prod.production.yml
```

Скопируйте содержимое из `docker-compose.prod.production.yml` (файл создан в проекте).

---

### Шаг 6: Запустите сервисы

```bash
# На сервере
cd /opt/systech/sunko

# Остановите старые контейнеры (если есть)
docker compose -f docker-compose.prod.yml down

# Запустите с новым compose файлом
docker compose -f docker-compose.prod.production.yml pull bot api postgres
docker compose -f docker-compose.prod.production.yml up -d

# Проверьте статус
docker compose -f docker-compose.prod.production.yml ps

# Проверьте логи
docker compose -f docker-compose.prod.production.yml logs -f frontend
```

---

### Шаг 7: Проверка работоспособности

**В браузере:**
1. Откройте http://92.255.78.249:3003
2. Нажмите F12 → Network
3. Попробуйте залогиниться
4. Убедитесь, что запросы идут на `http://92.255.78.249:8003`

**Тестовый запрос:**
```bash
curl http://92.255.78.249:8003/
```

---

## Способ 2: Через GitHub Container Registry (для постоянного использования)

### Преимущества
- Образ доступен из любого места
- Версионирование образов
- Интеграция с CI/CD

### Шаг 1: Настройте GitHub Personal Access Token

1. Перейдите: https://github.com/settings/tokens
2. Создайте новый token (Classic)
3. Выберите scope: `write:packages`, `read:packages`, `delete:packages`
4. Скопируйте токен

### Шаг 2: Логин в GHCR

**Windows PowerShell:**
```powershell
# Замените YOUR_TOKEN и YOUR_USERNAME
$env:CR_PAT = "ghp_ваш_токен_здесь"
echo $env:CR_PAT | docker login ghcr.io -u ваш_github_username --password-stdin
```

**Linux/macOS:**
```bash
export CR_PAT=ghp_ваш_токен_здесь
echo $CR_PAT | docker login ghcr.io -u ваш_github_username --password-stdin
```

### Шаг 3: Соберите и тегируйте образ

```powershell
cd c:\DEV\systech-aidd\systech-aidd

# Измените yangdeniz на ваш GitHub username
# API URL уже захардкожен в Dockerfile.frontend
docker build `
  -t ghcr.io/yangdeniz/homeguru-frontend:production `
  -f Dockerfile.frontend `
  ./frontend/app
```

### Шаг 4: Запушьте образ в GHCR

```powershell
docker push ghcr.io/yangdeniz/homeguru-frontend:production
```

### Шаг 5: Настройте видимость образа (опционально)

1. Перейдите: https://github.com/users/ваш_username/packages/container/homeguru-frontend
2. Package Settings → Change visibility → Public (если хотите публичный доступ)

### Шаг 6: На сервере используйте образ из GHCR

В `docker-compose.prod.production.yml` измените:

```yaml
frontend:
  image: ghcr.io/yangdeniz/homeguru-frontend:production
```

Затем запустите:

```bash
# На сервере
docker compose -f docker-compose.prod.production.yml pull
docker compose -f docker-compose.prod.production.yml up -d
```

---

## Способ 3: Обновить GitHub Actions для автоматической сборки

**Хорошая новость:** API URL уже захардкожен в `Dockerfile.frontend`, поэтому GitHub Actions уже будет собирать frontend с правильным URL `http://92.255.78.249:8003` без дополнительных изменений!

Текущий `.github/workflows/build.yml` уже работает корректно. Каждый push в main будет собирать frontend с правильным URL.

**Опционально:** Если в будущем понадобится гибкость, можно добавить build-args:

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: ${{ matrix.context }}
    file: ${{ matrix.dockerfile }}
    push: ${{ github.event_name == 'push' }}
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
    # build-args можно добавить для переопределения URL
    # build-args: |
    #   NEXT_PUBLIC_API_URL=${{ secrets.PROD_API_URL }}
    cache-from: type=gha,scope=${{ matrix.service }}
    cache-to: type=gha,mode=max,scope=${{ matrix.service }}
```

---

## Сравнение способов

| Способ | Время | Сложность | Когда использовать |
|--------|-------|-----------|-------------------|
| **Файл .tar** | ~20 мин | Низкая | Быстрый деплой, разовая задача |
| **GHCR** | ~30 мин | Средняя | Постоянное использование, версионирование |
| **GitHub Actions** | ~15 мин | Средняя | Автоматизация CI/CD |

---

## Troubleshooting

### Ошибка: "Cannot connect to Docker daemon"

```powershell
# Убедитесь, что Docker Desktop запущен
docker ps
```

### Образ слишком большой (>1GB)

Это нормально для Next.js приложения с зависимостями. Можно оптимизировать используя multi-stage build, но для MVP текущий размер приемлем.

### Долгая загрузка на сервер

Используйте сжатие:
```powershell
docker save homeguru-frontend:production | gzip > homeguru-frontend-production.tar.gz
scp -i <ключ> homeguru-frontend-production.tar.gz systech@92.255.78.249:/opt/systech/sunko/
```

На сервере:
```bash
gunzip homeguru-frontend-production.tar.gz
docker load -i homeguru-frontend-production.tar
```

---

## Заключение

**Рекомендуемый подход для D-Sprint-2:**
- Используйте **Способ 1** (файл .tar) для быстрого деплоя

**Для D-Sprint-3 и далее:**
- Настройте **GitHub Actions** для автоматической сборки с production URL
- Используйте **GHCR** для хранения версионированных образов

---

**Время выполнения Способа 1:**
- Сборка локально: 5-10 мин
- Сохранение в файл: 1-2 мин
- Копирование на сервер: 5-15 мин
- Загрузка и запуск: 2-3 мин
- **Итого: 15-30 минут**

Это быстрее, чем копировать исходники и собирать на сервере (~10-20 минут сборка на сервере).

