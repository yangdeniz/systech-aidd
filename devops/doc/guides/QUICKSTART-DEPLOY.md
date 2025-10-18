# 🚀 Быстрый старт: Развертывание на сервере

**Время:** ~20-30 минут  
**Сервер:** 92.255.78.249  
**Порты:** API - 8003, Frontend - 3003

---

## ✅ Что нужно иметь

- SSH ключ для доступа к серверу
- Заполненный `.env` файл с секретами

---

## 📋 Пошаговая инструкция

### 1. Подготовка .env файла (локально)

```powershell
cd c:\DEV\systech-aidd\systech-aidd

# Создайте .env из шаблона
Copy-Item env.production .env

# Отредактируйте .env, заполните:
# - ADMIN_PASSWORD (сильный пароль)
# - JWT_SECRET_KEY (сгенерируйте: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - OPENROUTER_API_KEY (ваш API ключ)
# - TELEGRAM_BOT_TOKEN (токен бота)
```

**Важно:** Все остальные переменные уже настроены правильно!

---

### 2. Копирование файлов на сервер

```powershell
# Замените на ваш путь к SSH ключу
$key = "путь\к\вашему\ключу.pem"

# Скопируйте конфигурационные файлы
scp -i $key docker-compose.prod.yml systech@92.255.78.249:/opt/systech/sunko/
scp -i $key .env systech@92.255.78.249:/opt/systech/sunko/

# Скопируйте исходники для сборки frontend
scp -i $key -r frontend systech@92.255.78.249:/opt/systech/sunko/
```

⏱️ **Время:** 2-3 минуты

---

### 3. Развертывание на сервере

```bash
# Подключитесь к серверу
ssh -i <путь_к_ключу> systech@92.255.78.249

cd /opt/systech/sunko

# Загрузите образы bot и api из GHCR
docker compose -f docker-compose.prod.yml pull bot api postgres

# Соберите frontend (API URL уже захардкожен в Dockerfile.frontend)
docker compose -f docker-compose.prod.yml build frontend

# Запустите все сервисы
docker compose -f docker-compose.prod.yml up -d

# Проверьте статус
docker compose -f docker-compose.prod.yml ps
```

⏱️ **Время:** 10-15 минут (загрузка образов + сборка frontend)

---

### 4. Проверка работоспособности

```bash
# Проверьте статус контейнеров (все должны быть Up)
docker compose -f docker-compose.prod.yml ps

# Проверьте логи
docker compose -f docker-compose.prod.yml logs api | tail -20
docker compose -f docker-compose.prod.yml logs frontend | tail -20
docker compose -f docker-compose.prod.yml logs bot | tail -20

# Проверьте API
curl http://localhost:8003/
```

**Ожидаемый ответ:**
```json
{"message":"HomeGuru API is running","version":"1.0.0"}
```

**В браузере:**
- Frontend: http://92.255.78.249:3003
- API Docs: http://92.255.78.249:8003/docs

**Откройте DevTools (F12) → Network** и проверьте, что запросы идут на `92.255.78.249:8003`

---

## 🔧 Если что-то пошло не так

### Проблема: Контейнер перезапускается

```bash
docker compose -f docker-compose.prod.yml logs <service_name>
```

Проверьте:
- Все переменные в `.env` заполнены?
- `OPENROUTER_MODEL` и `LLM_MODEL` присутствуют?

### Проблема: Frontend обращается к localhost:8000

```bash
# Пересоберите frontend
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

API URL захардкожен в `Dockerfile.frontend` (строка 18).

### Проблема: API недоступен снаружи

```bash
# Проверьте, что API слушает на правильном порту
docker port homeguru-api
# Должно быть: 0.0.0.0:8003->8000/tcp
```

---

## 📊 Полезные команды

```bash
# Посмотреть логи в реальном времени
docker compose -f docker-compose.prod.yml logs -f

# Перезапустить сервис
docker compose -f docker-compose.prod.yml restart <service_name>

# Остановить все
docker compose -f docker-compose.prod.yml down

# Запустить заново
docker compose -f docker-compose.prod.yml up -d

# Статистика использования ресурсов
docker stats
```

---

## ✅ Чек-лист успешного развертывания

- [ ] Все 4 контейнера в статусе `Up`
- [ ] API доступен: `curl http://localhost:8003/` возвращает JSON
- [ ] API доступен снаружи: http://92.255.78.249:8003
- [ ] Frontend открывается: http://92.255.78.249:3003
- [ ] В DevTools запросы идут на `92.255.78.249:8003` (не на localhost)
- [ ] Нет ошибок в логах: `docker compose logs`
- [ ] Bot подключился к Telegram (если используется)

---

## 📚 Дополнительная информация

Детальная инструкция: `devops/doc/guides/manual-deploy.md`  
Troubleshooting: см. раздел в `manual-deploy.md`

---

**После успешного развертывания заполните отчет:**  
`devops/doc/reports/d2-deployment-report.md`

---

**Следующий шаг:** D-Sprint-3 - Auto Deploy через GitHub Actions

