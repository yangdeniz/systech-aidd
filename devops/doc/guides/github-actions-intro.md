# Введение в GitHub Actions

## Что такое GitHub Actions?

**GitHub Actions** — это встроенная в GitHub платформа CI/CD (Continuous Integration/Continuous Deployment) для автоматизации процессов разработки, тестирования и развертывания приложений.

### Ключевые преимущества:
- ✅ Интеграция прямо в GitHub репозиторий
- ✅ Бесплатный tier для публичных репозиториев
- ✅ Огромная библиотека готовых actions
- ✅ Простая YAML-конфигурация
- ✅ Параллельное выполнение задач через matrix strategy

---

## Основные концепции

### Workflow (Рабочий процесс)
YAML-файл в директории `.github/workflows/`, который описывает автоматизированный процесс.

```yaml
name: Build Docker Images
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Hello World"
```

### Jobs (Задачи)
Набор шагов (steps), которые выполняются на одном runner'е. Jobs могут выполняться параллельно или последовательно.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
  build:
    needs: test  # Выполнится после завершения test
    runs-on: ubuntu-latest
```

### Steps (Шаги)
Отдельные команды или actions внутри job. Выполняются последовательно.

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
  
  - name: Run command
    run: echo "Building..."
```

### Matrix Strategy (Матричная стратегия)
Позволяет запускать один job с разными параметрами параллельно.

```yaml
strategy:
  matrix:
    service: [bot, api, frontend]
    
steps:
  - name: Build ${{ matrix.service }}
    run: docker build -f Dockerfile.${{ matrix.service }} .
```

**Пример для нашего проекта:**
- Один workflow собирает 3 Docker образа (bot, api, frontend) параллельно
- Каждый образ собирается независимо от других
- Ускоряет процесс в 3 раза по сравнению с последовательной сборкой

---

## Triggers (Триггеры) - когда запускается workflow

### Push - при коммите в ветку
```yaml
on:
  push:
    branches: [main, develop]
```

### Pull Request - при создании/обновлении PR
```yaml
on:
  pull_request:
    branches: [main]
```

### Workflow Dispatch - ручной запуск через UI
```yaml
on:
  workflow_dispatch:
```

### Комбинированные триггеры
```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

**Рекомендация для нашего проекта:**
- `push` на `main` — автоматическая сборка и публикация
- `pull_request` — проверка сборки без публикации (dry-run)

---

## Работа с Pull Requests

### Зачем проверять сборку в PR?

1. **Раннее обнаружение проблем** - ошибки сборки видны до merge
2. **Code review** - ревьюеры видят статус CI
3. **Защита main ветки** - можно настроить обязательную проверку

### Пример workflow для PR:

```yaml
name: PR Check
on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: docker compose build
      # Не публикуем образы - только проверяем сборку
```

### Условная публикация (только для main):

```yaml
- name: Push to registry
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  run: docker push ...
```

---

## Публикация образов в ghcr.io

### Public vs Private образы

**Public (публичные):**
- ✅ Доступны для скачивания без авторизации
- ✅ Идеально для open-source проектов
- ✅ Не требует `docker login` для pull
- ❌ Видны всем пользователям GitHub

**Private (приватные):**
- ✅ Доступны только владельцу и collaborators
- ✅ Безопасность для коммерческих проектов
- ❌ Требует авторизацию для pull
- ❌ Ограничения на бесплатном tier

**Рекомендация для нашего проекта:**
Используем **public** образы для простоты развертывания на production сервере без необходимости настройки токенов.

### Как сделать образ публичным:

1. После первой публикации перейти в **Packages** репозитория
2. Выбрать пакет (например, `homeguru-api`)
3. **Package settings** → **Danger Zone**
4. **Change visibility** → **Public**
5. Подтвердить действие

---

## Аутентификация через GITHUB_TOKEN

### Что такое GITHUB_TOKEN?

Это **автоматически генерируемый токен**, который GitHub предоставляет каждому workflow run. Не требует ручной настройки!

### Использование в workflow:

```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.repository_owner }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Permissions

По умолчанию `GITHUB_TOKEN` имеет права на чтение. Для публикации нужно добавить:

```yaml
permissions:
  contents: read
  packages: write
```

### Преимущества GITHUB_TOKEN:

- ✅ Автоматически ротируется
- ✅ Ограниченные права только для текущего workflow
- ✅ Не нужно хранить в secrets
- ✅ Безопасность из коробки

---

## Пример полного workflow для нашего проекта

```yaml
name: Build and Publish Docker Images

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, api, frontend]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GHCR
        if: github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.${{ matrix.service }}
          push: ${{ github.event_name == 'push' }}
          tags: ghcr.io/${{ github.repository_owner }}/homeguru-${{ matrix.service }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## Best Practices

### 1. Используйте кэширование
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```
Ускоряет повторные сборки в 3-5 раз.

### 2. Тегируйте образы правильно
```yaml
tags: |
  ghcr.io/owner/app:latest
  ghcr.io/owner/app:sha-${{ github.sha }}
```

### 3. Используйте matrix для параллелизма
Собирайте несколько образов одновременно.

### 4. Не публикуйте из PR
```yaml
push: ${{ github.event_name == 'push' }}
```

### 5. Добавьте badge в README
```markdown
[![Build](https://github.com/owner/repo/actions/workflows/build.yml/badge.svg)](https://github.com/owner/repo/actions/workflows/build.yml)
```

---

## Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Login Action](https://github.com/docker/login-action)

---

## Следующие шаги

1. Изучить [ghcr-setup.md](ghcr-setup.md) для настройки GitHub Container Registry
2. Создать `.github/workflows/build.yml` в вашем проекте
3. Сделать первый commit и проверить работу workflow
4. Настроить публичный доступ к образам

