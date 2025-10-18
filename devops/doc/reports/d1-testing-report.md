# Отчет о тестировании D-Sprint-1: Build & Publish

**Дата:** 2025-10-18  
**Спринт:** D-Sprint-1 - Build & Publish  
**Статус:** 🚧 In Progress

---

## Цель спринта

Автоматическая сборка и публикация Docker образов в GitHub Container Registry через GitHub Actions с поддержкой локального и production режимов.

---

## Checklist проверок

### 1. Создание файлов и документации

- [ ] ✅ Создан `.github/workflows/build.yml`
- [ ] ✅ Создан `docker-compose.prod.yml`
- [ ] ✅ Создан `devops/doc/guides/github-actions-intro.md`
- [ ] ✅ Создан `devops/doc/guides/ghcr-setup.md`
- [ ] ✅ Создан `devops/doc/plans/d1-build-publish.md`
- [ ] ✅ Создан этот отчет `devops/doc/reports/d1-testing-report.md`

### 2. GitHub Actions Workflow

- [ ] Workflow файл корректно настроен
- [ ] Matrix strategy работает для 3 сервисов (bot, api, frontend)
- [ ] Triggers настроены: push на main и pull_request
- [ ] Permissions установлены: packages: write
- [ ] Docker Buildx настроен
- [ ] Кэширование layers включено (type=gha)
- [ ] Теги генерируются правильно (latest + sha-xxx)

### 3. Проверка CI/CD

#### 3.1 Push в main ветку

- [ ] Workflow запускается автоматически при push в main
- [ ] Все 3 образа собираются параллельно
- [ ] Сборка завершается успешно (зеленый статус ✅)
- [ ] Образы публикуются в GHCR
- [ ] Образы появляются в GitHub Packages

**Результат:**
```
Status: [ ]
Время сборки: ___ минут
Ссылка на workflow run: ___
```

#### 3.2 Pull Request

- [ ] Workflow запускается при создании PR
- [ ] Образы собираются, но НЕ публикуются
- [ ] Статус сборки отображается в PR

**Результат:**
```
Status: [ ]
PR #: ___
Ссылка: ___
```

### 4. GitHub Container Registry

#### 4.1 Проверка опубликованных образов

После первой успешной сборки проверить наличие образов:

- [ ] `ghcr.io/{owner}/homeguru-bot` существует
- [ ] `ghcr.io/{owner}/homeguru-api` существует
- [ ] `ghcr.io/{owner}/homeguru-frontend` существует
- [ ] Образы связаны с репозиторием (Repository link)
- [ ] У образов есть тег `latest`
- [ ] У образов есть тег `sha-{commit}`

**Список образов:**
```
1. ghcr.io/___/homeguru-bot:latest
2. ghcr.io/___/homeguru-api:latest
3. ghcr.io/___/homeguru-frontend:latest
```

#### 4.2 Настройка публичного доступа

- [ ] Bot образ сделан публичным (Public)
- [ ] API образ сделан публичным (Public)
- [ ] Frontend образ сделан публичным (Public)

**Шаги для каждого образа:**
1. GitHub → Packages → выбрать пакет
2. Package settings → Danger Zone
3. Change visibility → Public
4. Подтвердить

### 5. Локальное тестирование

#### 5.1 Pull образов из registry

Проверить возможность скачивания образов БЕЗ авторизации (для публичных образов):

```bash
docker pull ghcr.io/{owner}/homeguru-bot:latest
docker pull ghcr.io/{owner}/homeguru-api:latest
docker pull ghcr.io/{owner}/homeguru-frontend:latest
```

**Результат:**
- [ ] Bot образ скачан успешно
- [ ] API образ скачан успешно
- [ ] Frontend образ скачан успешно
- [ ] Авторизация НЕ требовалась

**Размеры образов:**
```
bot:      ___ MB
api:      ___ MB
frontend: ___ MB
```

#### 5.2 Запуск через docker-compose.prod.yml

```bash
# Обновить docker-compose.prod.yml с правильным owner
# Запустить контейнеры
docker compose -f docker-compose.prod.yml up
```

**Результат:**
- [ ] PostgreSQL запустился успешно
- [ ] Bot запустился успешно
- [ ] API запустился успешно
- [ ] Frontend запустился успешно
- [ ] Все сервисы работают корректно

#### 5.3 Проверка работоспособности сервисов

**PostgreSQL:**
```bash
docker compose -f docker-compose.prod.yml logs postgres | grep "ready"
```
- [ ] Логи показывают "database system is ready to accept connections"

**API:**
- [ ] http://localhost:8000 открывается
- [ ] http://localhost:8000/docs показывает Swagger UI
- [ ] Health check endpoint работает

**Frontend:**
- [ ] http://localhost:3000 открывается
- [ ] Страница отображается корректно
- [ ] Подключение к API работает

**Bot:**
```bash
docker compose -f docker-compose.prod.yml logs bot
```
- [ ] Логи показывают успешный запуск
- [ ] Нет критических ошибок

### 6. Документация

- [ ] README.md обновлен с badge статуса сборки
- [ ] README.md содержит секцию "Docker образы"
- [ ] README.md содержит инструкции по использованию
- [ ] devops-roadmap.md обновлен (статус спринта, история)

---

## Результаты тестирования

### Успешные проверки ✅

*Список успешно пройденных проверок:*

1. 
2. 
3. 

### Обнаруженные проблемы ❌

*Список проблем и их решений:*

| # | Проблема | Решение | Статус |
|---|----------|---------|--------|
| 1 |          |         |        |
| 2 |          |         |        |

### Метрики

**Время сборки образов в CI:**
- Bot: ___ сек
- API: ___ сек
- Frontend: ___ сек
- **Общее (параллельно):** ___ мин

**Размеры образов:**
- Bot: ___ MB
- API: ___ MB
- Frontend: ___ MB
- **Всего:** ___ MB

**Кэширование:**
- Первая сборка: ___ мин
- Повторная сборка (с кэшем): ___ мин
- Ускорение: ___x

---

## Performance

### Сравнение локальной сборки vs Registry образы

**Локальная сборка (`docker compose up --build`):**
- Время первой сборки: ___ мин
- Время повторной сборки: ___ мин

**Registry образы (`docker compose -f docker-compose.prod.yml up`):**
- Время pull образов: ___ мин
- Время запуска: ___ сек

**Вывод:**  
Использование образов из registry ускоряет развертывание в ___x раз.

---

## Troubleshooting

### Проблемы и решения

#### Проблема 1: Workflow не запускается

**Симптомы:**
- Нет запуска workflow после push

**Причина:**
- Workflow файл не в `.github/workflows/`
- Синтаксическая ошибка в YAML

**Решение:**
```bash
# Проверить синтаксис
yamllint .github/workflows/build.yml
```

#### Проблема 2: Ошибка "permission_denied" при публикации

**Симптомы:**
- Workflow падает на этапе push образа

**Причина:**
- Отсутствует `permissions: packages: write`

**Решение:**
Добавить в workflow:
```yaml
permissions:
  contents: read
  packages: write
```

#### Проблема 3: Не могу pull образ локально

**Симптомы:**
- `docker pull` требует авторизацию

**Причина:**
- Образ всё ещё private

**Решение:**
Сделать образ публичным в GitHub Packages → Package settings → Change visibility → Public

#### Проблема 4: Frontend не может подключиться к API

**Симптомы:**
- Frontend запущен, но не работает

**Причина:**
- Неверный `NEXT_PUBLIC_API_URL`

**Решение:**
Проверить переменную окружения в `docker-compose.prod.yml`:
```yaml
environment:
  NEXT_PUBLIC_API_URL: http://localhost:8000
```

---

## Следующие шаги

После успешного завершения D-Sprint-1:

1. [ ] Завершить все проверки из checklist
2. [ ] Обновить статус спринта в devops-roadmap.md на ✅ Completed
3. [ ] Добавить скриншоты успешных workflow runs в документацию
4. [ ] Переходить к D-Sprint-2: Развертывание на сервер

---

## Заключение

**Общий статус:** [ ] ✅ Успешно / [ ] ⚠️ С замечаниями / [ ] ❌ Требует доработки

**Комментарии:**

*Общие выводы по спринту, достигнутые результаты, рекомендации.*

---

**Подготовил:** ___  
**Дата завершения тестирования:** ___  
**Версия документа:** 1.0

