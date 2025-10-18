# Настройка GitHub Container Registry (GHCR)

## Что такое GitHub Container Registry?

**GitHub Container Registry (ghcr.io)** — это встроенный в GitHub сервис для хранения и публикации Docker образов, тесно интегрированный с репозиториями и GitHub Actions.

### Ключевые преимущества:

- ✅ Бесплатное хранение для публичных репозиториев
- ✅ Интеграция с GitHub Packages
- ✅ Автоматическая связь с исходным кодом
- ✅ Удобное управление через GitHub UI
- ✅ Поддержка OCI-совместимых образов

---

## Формат имен образов

### Структура URL образа:
```
ghcr.io/{owner}/{image-name}:{tag}
```

### Примеры для нашего проекта:

```bash
# Bot
ghcr.io/your-username/homeguru-bot:latest
ghcr.io/your-username/homeguru-bot:sha-abc1234

# API
ghcr.io/your-username/homeguru-api:latest
ghcr.io/your-username/homeguru-api:sha-abc1234

# Frontend
ghcr.io/your-username/homeguru-frontend:latest
ghcr.io/your-username/homeguru-frontend:sha-abc1234
```

**Где:**
- `your-username` — GitHub username или organization
- `homeguru-bot/api/frontend` — имя образа
- `latest` — тег (может быть любой: версия, sha, дата)

---

## Первая публикация образа

### Через GitHub Actions (рекомендуется)

Workflow автоматически публикует образы при push в main:

```yaml
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.repository_owner }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: ghcr.io/${{ github.repository_owner }}/homeguru-api:latest
```

### Через локальный Docker (для тестирования)

```bash
# 1. Создать Personal Access Token (PAT)
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# Permissions: write:packages, read:packages, delete:packages

# 2. Авторизоваться
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 3. Собрать образ
docker build -t ghcr.io/your-username/homeguru-api:latest -f Dockerfile.api .

# 4. Опубликовать
docker push ghcr.io/your-username/homeguru-api:latest
```

---

## Настройка видимости пакетов

### Public vs Private

**После первой публикации образ по умолчанию PRIVATE!**

### Как сделать образ публичным (Public):

#### Способ 1: Через GitHub UI (рекомендуется)

1. Перейти на главную страницу репозитория
2. Справа найти **Packages** → выбрать нужный пакет
3. Нажать **Package settings** (справа вверху)
4. Прокрутить вниз до **Danger Zone**
5. Нажать **Change visibility**
6. Выбрать **Public**
7. Ввести название пакета для подтверждения
8. Нажать **I understand, change package visibility**

#### Способ 2: При создании пакета (в будущих версиях GitHub)

В настройках репозитория можно задать дефолтную видимость для новых пакетов.

### Зачем делать образы публичными?

**Преимущества Public образов:**
- ✅ Можно скачивать **без авторизации**: `docker pull ghcr.io/.../app:latest`
- ✅ Упрощает развертывание на production сервере
- ✅ Не нужно создавать и хранить токены на сервере
- ✅ Подходит для open-source проектов

**Когда использовать Private:**
- Коммерческие проекты с закрытым кодом
- Образы содержат чувствительную информацию
- Нужен контроль доступа к образам

---

## Управление токенами и permissions

### GITHUB_TOKEN (для CI/CD)

**Используется в GitHub Actions автоматически:**

```yaml
permissions:
  contents: read      # Чтение кода репозитория
  packages: write     # Публикация в GHCR
```

Этот токен:
- ✅ Автоматически генерируется для каждого workflow run
- ✅ Ротируется после завершения workflow
- ✅ Имеет ограниченные права только для текущего репозитория
- ✅ **Не требует ручной настройки**

### Personal Access Token (PAT)

**Используется для локальной работы:**

#### Создание PAT:

1. GitHub → **Settings** (ваш профиль, не репозиторий)
2. **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. **Generate new token (classic)**
4. Настройки:
   - **Note:** `GHCR Access for Docker`
   - **Expiration:** выберите срок (30/60/90 days или custom)
   - **Scopes:**
     - ✅ `write:packages` (публикация образов)
     - ✅ `read:packages` (скачивание приватных образов)
     - ✅ `delete:packages` (удаление образов, опционально)
5. **Generate token**
6. **Скопировать токен** (показывается один раз!)

#### Использование PAT:

```bash
# Авторизация
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Проверка
docker pull ghcr.io/your-username/homeguru-api:latest
```

#### Безопасное хранение PAT:

```bash
# Linux/macOS - сохранить в ~/.docker/config.json
docker login ghcr.io

# Windows - Docker Desktop сохраняет в Credential Manager
```

⚠️ **Важно:** PAT — это как пароль, не коммитьте его в git!

---

## Скачивание образов

### Public образы (без авторизации)

```bash
docker pull ghcr.io/username/homeguru-bot:latest
docker pull ghcr.io/username/homeguru-api:latest
docker pull ghcr.io/username/homeguru-frontend:latest
```

### Private образы (требуется авторизация)

```bash
# Авторизоваться с PAT
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Скачать образ
docker pull ghcr.io/username/homeguru-api:latest
```

### В docker-compose.prod.yml

```yaml
services:
  api:
    image: ghcr.io/username/homeguru-api:latest
    # Если образ публичный - авторизация не нужна
    # Если приватный - сначала docker login ghcr.io
```

---

## Просмотр и управление пакетами

### Где найти опубликованные образы?

**Вариант 1: В репозитории**
1. Главная страница репозитория
2. Справа → **Packages**
3. Список всех опубликованных образов

**Вариант 2: Профиль/Organization**
1. GitHub → Ваш профиль → **Packages**
2. Все пакеты всех репозиториев

### Информация о пакете:

- 📊 **Статистика скачиваний**
- 📝 **Список тегов** (latest, sha-xxx, версии)
- 🔗 **Ссылка на репозиторий** (автоматически)
- 👥 **Кто опубликовал** (через Actions или вручную)
- 📅 **Дата публикации**

### Удаление образа:

1. Packages → выбрать пакет
2. Package settings → Danger Zone
3. Delete this package
4. Подтверждение

---

## Лучшие практики

### 1. Используйте описательные имена
```
✅ homeguru-api
✅ homeguru-bot
❌ app
❌ backend
```

### 2. Тегируйте образы правильно
```bash
# Хорошо
ghcr.io/user/app:latest           # Последняя версия
ghcr.io/user/app:v1.2.3           # Версия
ghcr.io/user/app:sha-abc1234      # Коммит
ghcr.io/user/app:2024-10-18       # Дата

# Плохо
ghcr.io/user/app:test
ghcr.io/user/app:123
```

### 3. Делайте open-source образы публичными
Упрощает использование и развертывание.

### 4. Используйте GITHUB_TOKEN в CI/CD
Не создавайте PAT для GitHub Actions - используйте встроенный токен.

### 5. Регулярно ротируйте PAT
Обновляйте Personal Access Tokens каждые 60-90 дней.

### 6. Связывайте пакеты с репозиторием
При публикации GHCR автоматически связывает образ с репозиторием.

---

## Troubleshooting

### Ошибка: "denied: permission_denied"

**Причина:** Нет прав на публикацию.

**Решение:**
```yaml
# Добавить в workflow
permissions:
  packages: write
```

### Ошибка: "unauthorized: authentication required"

**Причина:** Не выполнен `docker login`.

**Решение:**
```bash
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### Образ не появляется в Packages

**Причина:** Образ опубликован, но не связан с репозиторием.

**Решение:**
1. Packages → Package settings
2. Connect repository → выбрать репозиторий

### Не могу скачать public образ

**Причина:** Образ всё ещё private.

**Решение:**
1. Проверить видимость: Package settings → Danger Zone → Change visibility
2. Сделать Public

---

## Пример для нашего проекта HomeGuru

### После настройки CI/CD у нас будет:

**Автоматическая публикация:**
- Push в main → автоматическая сборка и публикация
- Образы доступны в ghcr.io

**Публичные образы:**
```bash
# Скачать (без авторизации)
docker pull ghcr.io/your-username/homeguru-bot:latest
docker pull ghcr.io/your-username/homeguru-api:latest
docker pull ghcr.io/your-username/homeguru-frontend:latest

# Запустить
docker compose -f docker-compose.prod.yml up
```

**Готовность к deployment:**
- Образы готовы для развертывания на production
- Не нужна авторизация на production сервере
- Простой pull и запуск

---

## Полезные ссылки

- [GHCR Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Managing packages visibility](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)
- [Authenticating to GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)

---

## Следующие шаги

1. ✅ Создать GitHub Actions workflow для автоматической публикации
2. ✅ После первого push проверить появление образов в Packages
3. ✅ Сделать все образы публичными
4. ✅ Протестировать pull образов без авторизации
5. ✅ Обновить README с ссылками на образы

