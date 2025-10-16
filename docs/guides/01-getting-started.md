# Getting Started: HomeGuru за 15 минут

Быстрый старт с Telegram-ботом HomeGuru - ИИ-дизайнером интерьеров.

---

## Предварительные требования

- **Python 3.11+** ([скачать](https://www.python.org/downloads/))
- **uv** - менеджер зависимостей ([установка](https://github.com/astral-sh/uv))
- **Git**

---

## Шаг 1: Клонирование проекта

```bash
git clone <repository-url>
cd systech-aidd
```

---

## Шаг 2: Установка зависимостей

```bash
make install
```

Команда установит все необходимые зависимости через `uv sync --all-extras`.

**Что установится:**
- Основные: `aiogram`, `openai`, `python-dotenv`, `faster-whisper`
- Dev-инструменты: `pytest`, `ruff`, `mypy`

---

## Шаг 3: Получение API ключей

### 3.1 Telegram Bot Token

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь команду `/newbot`
3. Следуй инструкциям (имя бота, username)
4. Скопируй полученный токен (формат: `123456:ABC-DEF...`)

### 3.2 OpenRouter API Key

1. Зарегистрируйся на [openrouter.ai](https://openrouter.ai)
2. Перейди в [Keys](https://openrouter.ai/keys)
3. Создай новый API ключ
4. Скопируй ключ (формат: `sk-or-...`)

---

## Шаг 4: Настройка .env

Создай файл `.env` из шаблона:

```bash
cp .env.example .env
```

Заполни обязательные параметры в `.env`:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# OpenRouter (мультимодальная модель)
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=google/gemini-pro-1.5

# Dialogue Settings
MAX_HISTORY_MESSAGES=20

# Faster-Whisper (Speech-to-Text)
WHISPER_MODEL=base
WHISPER_DEVICE=cpu
```

**Обязательные параметры:**
- `TELEGRAM_BOT_TOKEN` - токен бота
- `OPENROUTER_API_KEY` - ключ OpenRouter
- `OPENROUTER_MODEL` - модель LLM (рекомендуется `google/gemini-pro-1.5`)

**Опциональные параметры** (можно оставить по умолчанию):
- `MAX_HISTORY_MESSAGES` - количество сообщений в истории (по умолчанию 20)
- `WHISPER_MODEL` - модель Whisper для аудио (tiny/base/small, по умолчанию base)
- `WHISPER_DEVICE` - устройство для Whisper (cpu/cuda, по умолчанию cpu)

---

## Шаг 5: Первый запуск

```bash
make run
```

**Ожидаемый вывод:**

```
2025-10-12 10:00:00 - root - INFO - Logging configured successfully
2025-10-12 10:00:00 - root - INFO - Starting bot initialization...
2025-10-12 10:00:00 - root - INFO - LLM client initialized
2025-10-12 10:00:00 - root - INFO - Dialogue manager initialized with max_history=20
2025-10-12 10:00:00 - root - INFO - MediaProcessor initialized with Whisper model=base, device=cpu
2025-10-12 10:00:00 - root - INFO - MessageHandler initialized with MediaProcessor
2025-10-12 10:00:00 - root - INFO - CommandHandler initialized
2025-10-12 10:00:00 - root - INFO - Telegram bot initialized
2025-10-12 10:00:00 - root - INFO - Bot is starting polling...
```

Бот запущен! 🎉

---

## Шаг 6: Тестирование бота

Открой Telegram и найди своего бота по username.

### Тест 1: Команда /start

Отправь: `/start`

**Ожидаемый ответ:**
```
Привет! 👋 Я HomeGuru - ваш личный ИИ-дизайнер интерьеров!

Я помогу вам с:
🎨 Подбором стилей интерьера
🌈 Цветовыми решениями
🛋 Выбором мебели и декора
📐 Планировкой пространства
💡 Советами по освещению

Просто опишите ваш запрос или отправьте фото вашего интерьера!

Доступные команды:
/role - узнать о моей специализации
/reset - начать новый диалог
/help - справка
```

### Тест 2: Текстовое сообщение

Отправь: `Какой стиль выбрать для маленькой гостиной?`

**Ожидаемый результат:** Бот ответит рекомендациями по дизайну от HomeGuru.

### Тест 3: Команда /role

Отправь: `/role`

**Ожидаемый результат:** Информация о специализации HomeGuru.

### Тест 4: Команда /reset

Отправь: `/reset`

**Ожидаемый результат:** `История диалога очищена. Начнём сначала! 🔄`

### Тест 5: Фотография (опционально)

Отправь фото интерьера (с подписью или без).

**Ожидаемый результат:** Бот проанализирует фото и даст рекомендации по дизайну.

### Тест 6: Голосовое сообщение (опционально)

Отправь голосовое сообщение с вопросом о дизайне.

**Ожидаемый результат:** Бот распознает речь и ответит текстом.

---

## Остановка бота

Нажми `Ctrl+C` в терминале.

---

## Troubleshooting

### Бот не запускается

**Проблема:** `ValueError: TELEGRAM_BOT_TOKEN is required`

**Решение:** Проверь `.env` файл - все обязательные параметры заполнены?

---

**Проблема:** `ModuleNotFoundError: No module named 'aiogram'`

**Решение:** Запусти `make install`

---

**Проблема:** `openai.AuthenticationError`

**Решение:** Проверь `OPENROUTER_API_KEY` в `.env`

---

### Бот не отвечает

**Проблема:** Бот не реагирует на команды в Telegram

**Решение:** 
- Проверь логи в `bot.log`
- Убедись, что токен бота правильный
- Проверь, что бот не заблокирован в Telegram

---

**Проблема:** Ошибка при запросе к LLM

**Решение:**
- Проверь баланс на OpenRouter
- Проверь правильность модели в `OPENROUTER_MODEL`
- Смотри детали в `bot.log`

---

## Логи

Все логи сохраняются в файл `bot.log` в корне проекта.

Просмотр последних логов:
```bash
tail -f bot.log
```

---

## Следующие шаги

✅ Бот работает - переходи к изучению:
- [`02-developer-quickstart.md`](02-developer-quickstart.md) - первый день разработчика
- [`03-architecture-overview.md`](03-architecture-overview.md) - архитектура проекта
- [`07-configuration.md`](07-configuration.md) - детальная настройка

---

## Краткий чеклист

- [ ] Python 3.11+ установлен
- [ ] uv установлен
- [ ] Проект склонирован
- [ ] `make install` выполнен успешно
- [ ] Получен Telegram Bot Token
- [ ] Получен OpenRouter API Key
- [ ] `.env` файл создан и заполнен
- [ ] `make run` запускает бота без ошибок
- [ ] `/start` работает в Telegram
- [ ] Бот отвечает на текстовые сообщения

**Всё работает?** 🎉 Поздравляем! Переходи к следующим гайдам.

