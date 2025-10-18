# План D-Sprint-1: Build & Publish

## Обзор

Автоматизация сборки и публикации Docker образов в GitHub Container Registry через GitHub Actions с поддержкой локального и production режимов.

**Статус:** 🚧 In Progress  
**Дата начала:** 2025-10-18

---

## 1. Создание документации по GitHub Actions

### devops/doc/guides/github-actions-intro.md

Создать краткую инструкцию, включающую:

- Что такое GitHub Actions и workflow
- Основные концепции: jobs, steps, matrix strategy
- Принципы работы с Pull Requests и triggers
- События: `push`, `pull_request`, `workflow_dispatch`
- Публикация образов: public vs private в ghcr.io
- Аутентификация через `GITHUB_TOKEN`

### devops/doc/guides/ghcr-setup.md

Инструкция по GitHub Container Registry:

- Как работает ghcr.io
- Настройка видимости пакетов (public/private)
- Как сделать образы публичными для скачивания без авторизации
- Управление токенами и permissions

---

## 2. Создание GitHub Actions Workflow

### .github/workflows/build.yml

Создать workflow со следующей структурой:

**Triggers:**
- `push` на ветку `main`
- `pull_request` для проверки сборки

**Matrix Strategy:**
- Параллельная сборка 3 образов: `bot`, `api`, `frontend`
- Конфигурация для каждого образа: имя, dockerfile, context

**Steps:**
1. Checkout кода
2. Docker meta - генерация тегов (latest + SHA)
3. Setup Docker Buildx
4. Login to ghcr.io через `GITHUB_TOKEN`
5. Build and push с кэшированием layers
6. Публикация образов в ghcr.io

**Важные детали:**
- Использовать `docker/build-push-action@v5`
- Включить cache-from/cache-to для ускорения
- Теги: `latest` и `sha-{SHORT_SHA}`
- Образы: `ghcr.io/${{ github.repository_owner }}/homeguru-{service}:tag`

---

## 3. Создание docker-compose.prod.yml

### docker-compose.prod.yml

Версия для использования образов из registry:

**Изменения относительно docker-compose.yml:**
- Вместо `build:` использовать `image: ghcr.io/...`
- Остальная конфигурация идентична (networks, volumes, env, healthchecks)
- Использовать тег `latest` для всех образов

**Переменные окружения:**
- Те же самые env_file и environment секции
- Добавить комментарий о том, что нужен `.env` файл

---

## 4. Обновление документации

### README.md

**Добавить badge статуса сборки:**
```markdown
[![Build Docker Images](https://github.com/{owner}/{repo}/actions/workflows/build.yml/badge.svg)](https://github.com/{owner}/{repo}/actions/workflows/build.yml)
```

**Создать секцию "🐳 Docker образы":**
- Список опубликованных образов в ghcr.io
- Инструкция по pull образов: `docker pull ghcr.io/...`
- Команды для запуска через docker-compose.prod.yml
- Объяснение различий между local build и registry images

**Обновить секцию "Запуск через Docker":**
- Добавить два варианта: Local Build и Production Images
- Команда для local: `docker compose up --build`
- Команда для prod: `docker compose -f docker-compose.prod.yml up`

### devops/doc/reports/d1-testing-report.md

Шаблон для отчета о тестировании:
- Checklist проверок
- Результаты локальной проверки pull образов
- Проверка запуска через docker-compose.prod.yml
- Статус CI workflow

---

## 5. Тестирование и проверка

### Локальное тестирование после сборки в CI:

**5.1 Pull образов из registry:**
```bash
docker pull ghcr.io/{owner}/homeguru-bot:latest
docker pull ghcr.io/{owner}/homeguru-api:latest
docker pull ghcr.io/{owner}/homeguru-frontend:latest
```

**5.2 Запуск через docker-compose.prod.yml:**
```bash
docker compose -f docker-compose.prod.yml up
```

**5.3 Проверка работы сервисов:**
- PostgreSQL: логи должны показывать "ready"
- API: http://localhost:8000/docs доступен
- Frontend: http://localhost:3000 открывается
- Bot: логи показывают "polling started"

**5.4 Проверка CI:**
- Push в main должен запускать workflow
- Pull Request должен запускать сборку без публикации
- Образы появляются в Packages репозитория

---

## 6. Настройка публичного доступа к образам

После первой успешной публикации в GitHub:

1. Перейти в Packages репозитория
2. Для каждого образа (bot, api, frontend):
   - Settings → Danger Zone
   - Change visibility → Public
   - Confirm

Это позволит скачивать образы без авторизации.

---

## 7. Обновление devops-roadmap.md

Обновить таблицу спринтов:
- D-Sprint-1 статус: ✅ Completed
- Добавить ссылку на план: `[📋 D-Sprint-1 Plan](plans/d1-build-publish.md)`
- Обновить историю изменений с датой и версией

---

## Checklist выполнения

- [ ] Создать документацию по GitHub Actions и GHCR (2 файла в devops/doc/guides/)
- [ ] Создать .github/workflows/build.yml с matrix strategy для 3 образов
- [ ] Создать docker-compose.prod.yml для использования образов из registry
- [ ] Обновить README.md: добавить badge, секцию Docker образов, инструкции
- [ ] Создать шаблон отчета d1-testing-report.md в devops/doc/reports/
- [ ] Протестировать workflow: push в ветку, проверить сборку и публикацию
- [ ] Сделать образы публичными в GitHub Packages
- [ ] Локально проверить pull и запуск через docker-compose.prod.yml
- [ ] Обновить devops-roadmap.md: статус спринта, история изменений

---

## Ожидаемый результат

После завершения спринта:

1. **GitHub Actions автоматически:**
   - Собирает 3 Docker образа при push в main
   - Публикует образы в ghcr.io с тегами latest и sha-{commit}
   - Проверяет сборку в Pull Requests

2. **Docker образы доступны публично:**
   - `ghcr.io/{owner}/homeguru-bot:latest`
   - `ghcr.io/{owner}/homeguru-api:latest`
   - `ghcr.io/{owner}/homeguru-frontend:latest`

3. **Два способа запуска:**
   - Локальная сборка: `docker compose up --build`
   - Production образы: `docker compose -f docker-compose.prod.yml up`

4. **Готовность к D-Sprint-2:**
   - Образы готовы для развертывания на production сервере
   - Документация по использованию образов
   - CI/CD pipeline настроен и работает

---

## Технологический стек

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **CI/CD** | GitHub Actions | Автоматизация сборки образов |
| **Registry** | GitHub Container Registry (ghcr.io) | Хранение и публикация образов |
| **Build Cache** | Docker Buildx | Ускорение повторных сборок |
| **Tagging** | Docker meta action | Автоматическая генерация тегов |

---

## MVP подход - что НЕ входит в спринт

В соответствии с принципом MVP, следующие элементы будут добавлены позже:

- ❌ Lint checks в workflow
- ❌ Запуск тестов в CI
- ❌ Security scanning (Trivy, Snyk)
- ❌ Multi-platform builds (amd64, arm64)
- ❌ Версионирование через git tags
- ❌ Автоматический rollback при ошибках
- ❌ Уведомления в Slack/Telegram

Фокус спринта: **простота, скорость, работающая автоматическая сборка**.

