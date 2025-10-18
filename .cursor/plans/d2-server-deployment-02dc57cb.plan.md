<!-- 02dc57cb-f717-4ebf-93f7-b83c60444a94 4678ab82-b040-4cf7-a2fa-593178b981c6 -->
# План D-Sprint-2: Развертывание на сервер

## Обзор

Создать детальную пошаговую инструкцию для ручного развертывания приложения на production сервере 92.255.78.249 и выполнить развертывание.

## Подготовительный этап

### 1. Создать .env.production шаблон

**Файл:** `env.production` (в корне проекта)

Включить все необходимые переменные с описанием:

- `DATABASE_URL` - для PostgreSQL (homeguru/homeguru_dev)
- `COLLECTOR_MODE=real` - режим работы
- `ADMIN_USERNAME`, `ADMIN_PASSWORD` - для создания администратора при миграции
- `JWT_SECRET_KEY` - секретный ключ (минимум 32 символа, случайная строка)
- `JWT_ACCESS_TOKEN_EXPIRE_DAYS=30`
- `OPENROUTER_API_KEY` - для LLM
- `LLM_MODEL=anthropic/claude-3.5-sonnet`
- `TELEGRAM_BOT_TOKEN` - для бота
- `NEXT_PUBLIC_API_URL=http://92.255.78.249:8003` - для frontend

Каждая переменная должна иметь комментарий с описанием.

### 2. Адаптировать docker-compose.prod.yml

**Файл:** `docker-compose.prod.yml`

Изменения:

- API порт: `8003:8000` (вместо `8000:8000`)
- Frontend порт: `3003:3000` (вместо `3000:3000`)
- Frontend environment: `NEXT_PUBLIC_API_URL=http://92.255.78.249:8003`
- Образы используются из GHCR (уже настроено): `ghcr.io/yangdeniz/homeguru-*:latest`
- PostgreSQL: оставить credentials как есть (homeguru/homeguru_dev)

## Документация

### 3. Создать инструкцию manual-deploy.md

**Файл:** `devops/doc/guides/manual-deploy.md`

Структура инструкции:

**Раздел 1: Требования**

- Список необходимого: SSH ключ, доступ к серверу, файлы для копирования
- Проверка предустановленного ПО на сервере (Docker, Docker Compose)

**Раздел 2: Подготовка локально**

- Создание `.env` файла на основе `env.production`
- Заполнение всех секретов (OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, JWT_SECRET_KEY)
- Список файлов для копирования: `docker-compose.prod.yml`, `.env`

**Раздел 3: Подключение к серверу**

- SSH команда с использованием ключа: `ssh -i path/to/key systech@92.255.78.249`
- Создание рабочей директории: `mkdir -p /opt/systech/sunko && cd /opt/systech/sunko`

**Раздел 4: Копирование файлов**

- Команда `scp` для `docker-compose.prod.yml`: `scp -i path/to/key docker-compose.prod.yml systech@92.255.78.249:/opt/systech/sunko/`
- Команда `scp` для `.env`: `scp -i path/to/key .env systech@92.255.78.249:/opt/systech/sunko/.env`

**Раздел 5: Загрузка образов**

- `docker compose -f docker-compose.prod.yml pull` - загрузка всех образов из GHCR (публичные, логин не нужен)

**Раздел 6: Запуск сервисов**

- `docker compose -f docker-compose.prod.yml up -d` - запуск в фоновом режиме
- Проверка статуса: `docker compose -f docker-compose.prod.yml ps`

**Раздел 7: Миграции базы данных**

- Миграции запускаются автоматически при старте API через `docker-entrypoint-api.sh`
- Проверка логов: `docker compose -f docker-compose.prod.yml logs api`

**Раздел 8: Проверка работоспособности**

- Проверка статуса контейнеров: `docker compose ps`
- Просмотр логов каждого сервиса: `docker compose logs [service]`
- Проверка healthcheck API: `curl http://localhost:8003/`
- Проверка доступности извне: `curl http://92.255.78.249:8003/`
- Проверка frontend: открыть в браузере `http://92.255.78.249:3003`

**Раздел 9: Troubleshooting**

- Типичные проблемы и решения
- Команды для перезапуска: `docker compose restart [service]`
- Остановка всех сервисов: `docker compose down`
- Очистка и пересоздание: `docker compose down -v && docker compose up -d`

## Выполнение развертывания

### 4. Развернуть проект на сервере

Пройти по всем шагам инструкции `manual-deploy.md`:

1. Подготовить `.env` файл локально с реальными значениями
2. Подключиться к серверу по SSH
3. Скопировать необходимые файлы
4. Загрузить образы Docker
5. Запустить все сервисы
6. Проверить работоспособность

### 5. Финальная проверка

Убедиться что:

- ✅ PostgreSQL запущен и доступен
- ✅ Bot запущен и работает
- ✅ API доступен по http://92.255.78.249:8003
- ✅ Frontend доступен по http://92.255.78.249:3003
- ✅ Миграции БД выполнены успешно
- ✅ Healthcheck API возвращает успешный ответ
- ✅ Все контейнеры в статусе "running"

## Обновление документации

### 6. Обновить devops-roadmap.md

Отметить D-Sprint-2 как завершенный, добавить ссылку на инструкцию и отчет.

### 7. Создать отчет d2-deployment-report.md

**Файл:** `devops/doc/reports/d2-deployment-report.md`

Содержание:

- Дата и время развертывания
- Использованные версии образов
- Проблемы и их решения
- Финальный статус всех сервисов
- Скриншоты/вывод команд проверки
- Рекомендации для автоматизации в D3

## Ключевые файлы

- `env.production` - шаблон переменных окружения для production
- `docker-compose.prod.yml` - конфигурация с портами 3003, 8003
- `devops/doc/guides/manual-deploy.md` - пошаговая инструкция развертывания
- `devops/doc/reports/d2-deployment-report.md` - отчет о выполненном развертывании
- `devops/doc/devops-roadmap.md` - обновленный roadmap

### To-dos

- [ ] Создать env.production с описанием всех переменных окружения для production
- [ ] Адаптировать docker-compose.prod.yml под порты 3003, 8003 и NEXT_PUBLIC_API_URL
- [ ] Создать детальную инструкцию devops/doc/guides/manual-deploy.md с командами готовыми к копированию
- [ ] Выполнить развертывание на сервере 92.255.78.249 по инструкции manual-deploy.md
- [ ] Проверить работоспособность всех сервисов (API, Frontend, Bot, DB)
- [ ] Создать отчет devops/doc/reports/d2-deployment-report.md о выполненном развертывании
- [ ] Обновить devops/doc/devops-roadmap.md - отметить D-Sprint-2 как завершенный