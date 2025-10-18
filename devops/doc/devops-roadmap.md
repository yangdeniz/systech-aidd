# DevOps Roadmap проекта HomeGuru

## О DevOps

**Цель:** Автоматизация процессов сборки, развертывания и доставки приложения на production сервер с использованием Docker, Docker Compose и GitHub Actions.

**Подход:** MVP DevOps - максимально быстрый путь от локального запуска до автоматического развертывания на удаленном сервере. Фокус на простоте и скорости без преждевременной оптимизации.

**Ключевые документы:**
- [🎯 vision.md](../../docs/vision.md) - Техническое видение всего проекта
- [🗺️ roadmap.md](../../docs/roadmap.md) - Основной roadmap проекта
- [🚀 frontend-roadmap.md](../../frontend/doc/frontend-roadmap.md) - Frontend roadmap

---

## Легенда статусов

| Иконка | Статус | Описание |
|--------|--------|----------|
| ⏳ | Pending | Спринт запланирован, работа не начата |
| 🚧 | In Progress | Спринт в активной разработке |
| ✅ | Completed | Спринт успешно завершен |
| 🔄 | On Hold | Спринт приостановлен |
| ❌ | Cancelled | Спринт отменен |

---

## Спринты DevOps разработки

| Код | Название | Статус | План спринта | Отчет |
|-----|----------|--------|--------------|-------|
| **D-Sprint-0** | Basic Docker Setup | ✅ Completed | [📋 Plan](plans/d0-basic-docker-setup.md) | [📊 Report](reports/d0-testing-report.md) |
| **D-Sprint-1** | Build & Publish | ✅ Completed | [📋 Plan](plans/d1-build-publish.md) | [📊 Summary](reports/d1-summary.md) |
| **D-Sprint-2** | Развертывание на сервер | 🚧 In Progress | [📋 Guide](guides/manual-deploy.md) | [📊 Report](reports/d2-deployment-report.md) |
| **D-Sprint-3** | Auto Deploy | ⏳ Pending | *TBD* | - |

---

## D-Sprint-0: Basic Docker Setup

### Цель
Запустить все сервисы проекта локально через docker-compose одной командой.

### Состав работ
**Docker контейнеризация:**
- Создание `Dockerfile.bot` для Telegram бота (Python + UV)
- Создание `Dockerfile.api` для FastAPI сервиса (Python + UV)
- Создание `Dockerfile.frontend` для веб-интерфейса (Next.js + pnpm)
- Создание `.dockerignore` файлов для каждого сервиса

**Docker Compose оркестрация:**
- Обновление `docker-compose.yml` для 4 сервисов: PostgreSQL, Bot, API, Frontend
- Настройка сетевых связей между сервисами
- Конфигурация переменных окружения
- Настройка volume mounts для персистентности данных

**Инфраструктура:**
- Проверка работоспособности: `docker-compose up` - всё работает локально
- Обновление `README.md` с инструкциями по запуску через Docker
- Документация по переменным окружения

**Контекст проекта:**
- В проекте уже существует `docker-compose.yml` для PostgreSQL
- Есть файл `.env` с конфигурацией базы данных
- Необходимо расширить существующую конфигурацию

**Ожидаемый результат:**
Команда `docker-compose up` запускает все 4 сервиса, они корректно взаимодействуют между собой, приложение полностью функционально.

---

## D-Sprint-1: Build & Publish

### Цель
Автоматическая сборка и публикация Docker образов в GitHub Container Registry при каждом push в main ветку.

### Состав работ
**GitHub Actions workflow:**
- Создание `.github/workflows/build.yml`
- Trigger: push в main ветку
- Jobs: сборка образов для bot, api, frontend
- Публикация образов в `ghcr.io` с тегом `latest`
- Оптимизация: использование кэша слоев Docker

**Настройка GitHub Container Registry:**
- Создание инструкции по настройке permissions для GHCR
- Документация по управлению токенами доступа
- Best practices для работы с приватными образами

**Качество и мониторинг:**
- Добавление badges статуса сборки в README
- Уведомления о статусе сборки (success/failure)
- Версионирование образов (latest + SHA commit)

**Документация:**
- Руководство `doc/guides/github-registry-setup.md`
- Обновление `README.md` с badges и ссылками на образы

**Ожидаемый результат:**
После push в main автоматически собираются и публикуются 3 Docker образа в GHCR, доступные для pull на любом сервере.

---

## D-Sprint-2: Развертывание на сервер

### Цель
Создать пошаговую инструкцию для ручного развертывания приложения на удаленном production сервере и выполнить развертывание.

### Информация о сервере
- **IP адрес:** 92.255.78.249
- **Пользователь:** systech
- **Рабочая директория:** /opt/systech/sunko
- **Порты:** API - 8003, Frontend - 3003
- **Предустановлено:** Docker, Docker Compose

### Состав работ

**Подготовка production окружения:**
- ✅ Создание `env.production` шаблона с описанием всех переменных
- ✅ Адаптация `docker-compose.prod.yml` под порты 3003, 8003
- ✅ Настройка `NEXT_PUBLIC_API_URL=http://92.255.78.249:8003`

**Документация:**
- ✅ Детальное руководство `devops/doc/guides/manual-deploy.md`
  - Требования и подготовка
  - SSH подключение с использованием ключа
  - Копирование `docker-compose.prod.yml` и `.env` на сервер
  - Загрузка образов из GHCR (публичные, без `docker login`)
  - Запуск сервисов в фоновом режиме
  - Автоматическое выполнение миграций БД при старте API
  - Проверка работоспособности всех сервисов
  - Чек-лист развертывания
  - Troubleshooting и типичные проблемы

**Пошаговая инструкция включает:**
1. Подготовка `.env` файла с секретами
2. SSH подключение: `ssh -i key systech@92.255.78.249`
3. Создание директории: `/opt/systech/sunko`
4. Копирование файлов через `scp`
5. Загрузка образов: `docker compose -f docker-compose.prod.yml pull`
6. Запуск: `docker compose -f docker-compose.prod.yml up -d`
7. Проверка: логи, healthcheck, доступность API/Frontend

**Выполнение развертывания:**
- 🚧 Развертывание выполняется вручную по инструкции
- 🚧 Заполнение отчета `devops/doc/reports/d2-deployment-report.md`

**Созданные файлы:**
- `env.production` - шаблон переменных окружения для production
- `docker-compose.prod.yml` - обновлен (порты 3003, 8003)
- `devops/doc/guides/manual-deploy.md` - 700+ строк детальной инструкции
- `devops/doc/reports/d2-deployment-report.md` - шаблон отчета

**Ожидаемый результат:**
Следуя инструкции, любой разработчик может вручную развернуть приложение на production сервере за 15-20 минут. Все сервисы доступны через интернет по адресам:
- API: http://92.255.78.249:8003
- Frontend: http://92.255.78.249:3003

---

## D-Sprint-3: Auto Deploy

### Цель
Автоматическое развертывание приложения на production сервер через GitHub Actions по нажатию кнопки (manual trigger).

### Состав работ
**GitHub Actions workflow:**
- Создание `.github/workflows/deploy.yml`
- Trigger: `workflow_dispatch` (ручной запуск через UI GitHub)
- SSH подключение к серверу через GitHub Secrets
- Pull новых версий образов с GHCR
- Restart сервисов через `docker-compose restart`
- Запуск миграций базы данных (если нужно)

**Настройка GitHub Secrets:**
- `SSH_KEY` - приватный SSH ключ для подключения
- `SSH_HOST` - адрес production сервера
- `SSH_USER` - пользователь для SSH
- Инструкция по добавлению secrets в репозиторий

**Уведомления и мониторинг:**
- Уведомления о статусе деплоя (success/failure)
- Slack/Telegram уведомления (опционально)
- Rollback стратегия при ошибках
- Логирование процесса деплоя

**Документация:**
- Руководство `doc/guides/auto-deploy-setup.md`
- Настройка GitHub secrets пошагово
- Обновление `README.md` с кнопкой "Deploy to Production"

**Безопасность:**
- Best practices для SSH ключей
- Ротация credentials
- Audit log для деплоев

**Ожидаемый результат:**
Нажатие кнопки "Run workflow" в GitHub Actions автоматически развертывает последнюю версию приложения на production сервере за 3-5 минут.

---

## Архитектура MVP DevOps Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  Developer Push to Main                                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  D-Sprint-1: GitHub Actions - Build & Publish                  │
│  • Build Docker images (bot, api, frontend)                    │
│  • Push to ghcr.io with tag latest                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  GitHub Container Registry (ghcr.io)                            │
│  • ghcr.io/username/homeguru-bot:latest                         │
│  • ghcr.io/username/homeguru-api:latest                         │
│  • ghcr.io/username/homeguru-frontend:latest                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼ (Manual Trigger)
┌─────────────────────────────────────────────────────────────────┐
│  D-Sprint-3: GitHub Actions - Auto Deploy                      │
│  • SSH to production server                                     │
│  • docker-compose pull                                          │
│  • docker-compose restart                                       │
│  • Run migrations                                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Production Server                                               │
│  • PostgreSQL (port 5432)                                       │
│  • Bot (connects to DB + Telegram API)                         │
│  • API (FastAPI on port 8000)                                  │
│  • Frontend (Next.js on port 3000)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Технологический стек

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **Контейнеризация** | Docker | Изоляция и упаковка приложений |
| **Оркестрация** | Docker Compose | Управление multi-container приложением |
| **CI/CD** | GitHub Actions | Автоматизация сборки и деплоя |
| **Registry** | GitHub Container Registry (ghcr.io) | Хранение Docker образов |
| **Deployment** | SSH + docker-compose | Развертывание на production сервере |
| **Database** | PostgreSQL 16 | Персистентность данных |

---

## История изменений

| Дата | Версия | Изменения |
|------|--------|-----------|
| 2025-10-18 | 1.4 | D-Sprint-2 начат. Создан env.production, обновлен docker-compose.prod.yml, создано руководство manual-deploy.md (704 строки), шаблон отчета d2-deployment-report.md |
| 2025-10-18 | 1.3 | D-Sprint-1 завершен. GitHub Actions CI/CD, автоматическая публикация образов в GHCR, docker-compose.prod.yml |
| 2025-10-18 | 1.2 | D-Sprint-1 начат. GitHub Actions workflow, docker-compose.prod.yml, документация по GHCR, обновление README |
| 2025-10-18 | 1.1 | D-Sprint-0 завершен. Контейнеризация всех сервисов, docker-compose с 4 сервисами, обновление README.md |
| 2025-10-18 | 1.0 | Создание DevOps roadmap. Планирование спринтов D-Sprint-0 до D-Sprint-3 |


