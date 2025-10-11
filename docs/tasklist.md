# Tasklist: Пошаговый план разработки

## 📊 Прогресс разработки

| Итерация | Задача | Статус | Дата |
|----------|--------|--------|------|
| 1 | Настройка + Эхо-бот | ✅ Done | 2025-10-10 |
| 2 | LLM интеграция | ✅ Done | 2025-10-10 |
| 3 | Менеджер диалогов | ✅ Done | 2025-10-10 |
| 4 | Команды бота | ✅ Done | 2025-10-10 |
| 5 | Логирование | ✅ Done | 2025-10-10 |
| 6 | Системный промпт HomeGuru | ✅ Done | 2025-10-11 |
| 7 | Обработка фотографий | ⏳ Pending | - |
| 8 | Обработка аудио | ⏳ Pending | - |
| 9 | Мониторинг LangSmith | ⏳ Pending | - |

**Легенда статусов:**
- ⏳ Pending - не начато
- 🚧 In Progress - в работе
- ✅ Done - завершено
- ❌ Blocked - заблокировано

---

## 📋 Детальный план

### Итерация 1: Настройка окружения + Эхо-бот
**Цель:** Рабочий эхо-бот в Telegram

**Настройка окружения:**
- [x] Создать структуру директорий (`src/bot/`, `tests/`)
- [x] Инициализировать проект с `uv` (создать `pyproject.toml`)
- [x] Добавить зависимости: `aiogram`, `openai`, `python-dotenv`, `pytest`
- [x] Создать `.env.example` с шаблоном переменных
- [x] Создать `.gitignore` (`.env`, `bot.log`, `__pycache__`, `.venv`)
- [x] Создать `Makefile` с базовыми командами

**Конфигурация:**
- [x] Создать `src/bot/config.py` с классом `Config`
- [x] Загрузка всех параметров из `.env` через `python-dotenv`
- [x] Создать свой `.env` файл с реальными токенами

**Эхо-бот:**
- [x] Создать `src/bot/bot.py` с классом `TelegramBot`
- [x] Настроить aiogram для работы с Telegram Bot API (polling)
- [x] Обработка команды `/start` - приветствие
- [x] Обработка текстовых сообщений - эхо
- [x] Создать `src/bot/main.py` - точка входа для запуска бота

**Тест:** Запустить бота, отправить `/start` и текстовое сообщение - получить эхо

---

### Итерация 2: LLM интеграция
**Цель:** Отправка запросов в OpenRouter

- [x] Создать `src/bot/llm_client.py` с классом `LLMClient`
- [x] Настроить `openai` client с `base_url` на OpenRouter
- [x] Метод `get_response(messages)` для отправки запросов
- [x] Добавление system prompt в начало сообщений
- [x] Интегрировать в бота: вместо эхо - ответ от LLM

**Тест:** Отправить сообщение боту - получить ответ от LLM (без истории)

---

### Итерация 3: Менеджер диалогов
**Цель:** Хранение истории и контекст диалога

- [x] Создать `src/bot/dialogue_manager.py` с классом `DialogueManager`
- [x] In-memory хранилище: `dict` с `user_id → [messages]`
- [x] Метод добавления сообщения в историю
- [x] Метод получения истории для пользователя
- [x] Ограничение истории (MAX_HISTORY_MESSAGES из .env)
- [x] Интегрировать в бота: передавать историю в LLM

**Тест:** Вести диалог с ботом - он помнит контекст предыдущих сообщений

---

### Итерация 4: Команды бота
**Цель:** Полный набор команд для управления

- [x] Команда `/reset` - очистка истории диалога
- [x] Команда `/help` - справка о доступных командах
- [x] Улучшить приветствие `/start` с описанием возможностей

**Тест:** Протестировать все команды: `/start`, `/reset`, `/help`

---

### Итерация 5: Логирование
**Цель:** Отладочная информация в логах

- [x] Настроить `logging` в `main.py`
- [x] Логи в файл `bot.log` + консоль
- [x] Добавить логи в `TelegramBot`: получение/отправка сообщений
- [x] Добавить логи в `LLMClient`: запросы/ответы
- [x] Добавить логи в `DialogueManager`: добавление/очистка истории
- [x] Логирование ошибок (ERROR level)

**Тест:** Запустить бота, взаимодействовать - проверить `bot.log`

---

### Итерация 6: Системный промпт HomeGuru ✅
**Цель:** Роль ИИ-дизайнера интерьеров через файл с промптом (TDD)

**TDD Планирование:**
- [x] Согласовать архитектуру: Config загружает промпт из файла, CommandHandler получает дополнительную команду `/role`
- [x] План тестов:
  - `test_config_loads_prompt_from_file()` - загрузка промпта из файла
  - `test_config_prompt_file_not_found()` - обработка отсутствия файла
  - `test_command_handler_get_role_message()` - команда `/role`
  - `test_start_message_with_homeguru_context()` - обновленное приветствие

**TDD Реализация (RED-GREEN-REFACTOR):**

**Создание файла системного промпта:**
- [x] 🔴 RED: Написать тест `test_config_loads_prompt_from_file()`
- [x] 🟢 GREEN: Создать файл `src/bot/system_prompt.txt` с описанием роли HomeGuru
- [x] 🔵 REFACTOR: Обновить `src/bot/config.py`: добавить метод `_load_system_prompt_from_file()` для загрузки из файла
- [x] Описать специализацию: дизайн интерьеров, консультации по стилям, анализ помещений
- [x] Указать ключевые компетенции: цветовые решения, мебель, декор
- [x] Определить стиль общения: профессиональный, дружелюбный, экспертный

**Обработка ошибок загрузки:**
- [x] 🔴 RED: Написать тест `test_config_prompt_file_not_found()`
- [x] 🟢 GREEN: Добавить обработку `FileNotFoundError` в Config
- [x] 🔵 REFACTOR: Fallback на дефолтный промпт при отсутствии файла
- [x] SYSTEM_PROMPT больше не используется из `.env` (загружается из файла)

**Команда /role:**
- [x] 🔴 RED: Написать тест `test_command_handler_get_role_message()`
- [x] 🟢 GREEN: Добавить метод `get_role_message()` в `CommandHandler`
- [x] 🔵 REFACTOR: Добавить обработчик команды `/role` в `TelegramBot.cmd_role()`
- [x] Отображение информации о роли HomeGuru
- [x] Перечисление ключевых возможностей и специализаций
- [x] Обновить метод `get_help_message()` в `CommandHandler` с информацией о `/role`

**Обновление приветствия:**
- [x] 🔴 RED: Написать тест `test_start_message_with_homeguru_context()`
- [x] 🟢 GREEN: Обновить `get_start_message()` в `CommandHandler` - приветствие от HomeGuru
- [x] 🔵 REFACTOR: Добавить описание специализации на дизайне интерьеров

**Проверка качества:**
- [x] `make quality` - все проверки проходят
- [x] Coverage: **98%** (превышает требование 80%)

**Результаты итерации 6:**
- ✅ Format: OK (ruff format, 0 изменений)
- ✅ Lint: All checks passed (ruff check, 0 errors)
- ✅ Typecheck: Success (mypy strict, 0 errors)
- ✅ Tests: **34/34 passed** (7 новых тестов)
- ✅ Coverage: **98%**
- ✅ Создан файл `src/bot/system_prompt.txt` с описанием роли HomeGuru
- ✅ Config загружает промпт из файла с fallback на дефолтный
- ✅ Добавлена команда `/role` для отображения специализации
- ✅ Обновлены сообщения `/start` и `/help` с контекстом HomeGuru

**Тест:** Отправить `/role` - получить информацию о роли ИИ-дизайнера. Ответы бота должны соответствовать роли HomeGuru.

---

### Итерация 7: Обработка фотографий
**Цель:** Анализ изображений интерьеров через Vision API (TDD + Protocol)

**TDD Планирование:**
- [ ] Согласовать архитектуру:
  - Создать `MediaProvider` Protocol для обработки медиа (DIP)
  - Создать `MediaProcessor` реализующий Protocol
  - Расширить `LLMProvider` Protocol для поддержки мультимодальных сообщений
  - Обновить `MessageHandler` для работы с медиа через Protocol
- [ ] План тестов:
  - `test_media_processor_download_photo()` - скачивание фото
  - `test_media_processor_photo_to_base64()` - конвертация в base64
  - `test_llm_client_multimodal_request()` - мультимодальный запрос
  - `test_message_handler_process_photo()` - обработка фото в MessageHandler
  - `test_dialogue_manager_multimodal_history()` - история с изображениями

**TDD Реализация (RED-GREEN-REFACTOR):**

**Protocol для медиа:**
- [ ] 🔴 RED: Написать тест `test_media_provider_protocol_compliance()`
- [ ] 🟢 GREEN: Добавить `MediaProvider` Protocol в `interfaces.py`:
  ```python
  class MediaProvider(Protocol):
      async def download_photo(self, file_id: str, bot: Bot) -> bytes: ...
      def photo_to_base64(self, photo_bytes: bytes) -> str: ...
  ```
- [ ] 🔵 REFACTOR: Документировать Protocol

**Создание MediaProcessor:**
- [ ] 🔴 RED: Написать тест `test_media_processor_download_photo()`
- [ ] 🟢 GREEN: Создать `src/bot/media_processor.py` с классом `MediaProcessor`
- [ ] 🔴 RED: Написать тест `test_media_processor_photo_to_base64()`
- [ ] 🟢 GREEN: Реализовать метод конвертации изображения в base64
- [ ] 🔵 REFACTOR: Добавить метод формирования мультимодального сообщения

**Расширение LLMProvider Protocol:**
- [ ] 🔴 RED: Написать тест `test_llm_provider_multimodal_messages()`
- [ ] 🟢 GREEN: Обновить `LLMProvider` Protocol - поддержка мультимодальных сообщений
- [ ] 🔵 REFACTOR: Обновить `LLMClient` для обработки Vision API через OpenRouter
- [ ] Проверить использование модели с Vision API через OpenRouter
- [ ] Обработка сообщений с изображениями в формате OpenAI API

**Обновление MessageHandler:**
- [ ] 🔴 RED: Написать тест `test_message_handler_with_media_provider()`
- [ ] 🟢 GREEN: Добавить зависимость `media_provider: MediaProvider` в конструктор `MessageHandler`
- [ ] 🔴 RED: Написать тест `test_message_handler_process_photo_message()`
- [ ] 🟢 GREEN: Добавить метод `handle_photo_message(user_id, username, photo_file_id, caption)`
- [ ] 🔵 REFACTOR: Интеграция с MediaProvider и передача в DialogueManager

**Обработчик фотографий в TelegramBot:**
- [ ] 🔴 RED: Написать тест `test_bot_handle_photo()`
- [ ] 🟢 GREEN: Добавить обработчик фото в `bot.py` - `async def handle_photo()`
- [ ] 🔵 REFACTOR: Делегировать обработку в `MessageHandler.handle_photo_message()`

**Обновление DialogueManager:**
- [ ] 🔴 RED: Написать тест `test_dialogue_manager_multimodal_history()`
- [ ] 🟢 GREEN: Обновить `DialogueStorage` Protocol - поддержка мультимодальных сообщений
- [ ] 🔴 RED: Написать тест `test_dialogue_manager_image_limit()`
- [ ] 🟢 GREEN: Добавить ограничение на количество изображений в истории
- [ ] 🔵 REFACTOR: Корректное формирование контекста с изображениями

**Логирование:**
- [ ] Логирование получения фото от пользователя
- [ ] Логирование обработки изображений
- [ ] Логирование мультимодальных запросов к LLM

**Проверка качества:**
- [ ] `make quality` - все проверки проходят
- [ ] Coverage ≥ 80%

**Тест:** Отправить боту фото интерьера - получить анализ и рекомендации от HomeGuru по дизайну.

---

### Итерация 8: Обработка аудио
**Цель:** Распознавание голосовых сообщений (TDD + Protocol)

**TDD Планирование:**
- [ ] Согласовать архитектуру:
  - Расширить `MediaProvider` Protocol для транскрибации аудио
  - Обновить `MediaProcessor` для работы с Whisper API
  - Добавить метод в `MessageHandler` для обработки голосовых сообщений
- [ ] План тестов:
  - `test_media_processor_download_audio()` - скачивание аудио
  - `test_media_processor_transcribe_audio()` - транскрибация
  - `test_message_handler_process_voice()` - обработка голосового сообщения
  - `test_transcription_error_handling()` - обработка ошибок

**TDD Реализация (RED-GREEN-REFACTOR):**

**Расширение MediaProvider Protocol:**
- [ ] 🔴 RED: Написать тест `test_media_provider_audio_support()`
- [ ] 🟢 GREEN: Добавить методы в `MediaProvider` Protocol:
  ```python
  async def download_audio(self, file_id: str, bot: Bot) -> bytes: ...
  async def transcribe_audio(self, audio_bytes: bytes) -> str: ...
  ```
- [ ] 🔵 REFACTOR: Документировать новые методы

**Speech-to-Text интеграция:**
- [ ] 🔴 RED: Написать тест `test_media_processor_transcribe_audio()`
- [ ] 🟢 GREEN: Добавить метод транскрибации в `MediaProcessor`
- [ ] 🔵 REFACTOR: Интеграция с OpenAI Whisper API (через OpenRouter или напрямую)
- [ ] Добавить параметры Whisper API в `.env` и `Config`
- [ ] Конвертация голосовых сообщений Telegram в формат для Whisper

**Обработчик голосовых сообщений в MessageHandler:**
- [ ] 🔴 RED: Написать тест `test_message_handler_handle_voice_message()`
- [ ] 🟢 GREEN: Добавить метод `handle_voice_message(user_id, username, voice_file_id)` в `MessageHandler`
- [ ] 🔵 REFACTOR: Транскрибация через MediaProvider → обработка как текста

**Обработчик в TelegramBot:**
- [ ] 🔴 RED: Написать тест `test_bot_handle_voice()`
- [ ] 🟢 GREEN: Добавить обработчик voice сообщений в `bot.py` - `async def handle_voice()`
- [ ] 🔵 REFACTOR: Делегировать обработку в `MessageHandler`

**Обработка ошибок:**
- [ ] 🔴 RED: Написать тест `test_transcription_error_handling()`
- [ ] 🟢 GREEN: Обработка ошибок при скачивании/транскрибации
- [ ] 🔵 REFACTOR: Информирование пользователя о проблемах с распознаванием

**Обновление документации:**
- [ ] 🔴 RED: Написать тест `test_help_message_includes_voice_support()`
- [ ] 🟢 GREEN: Обновить `/help` в `CommandHandler` с информацией о голосовых сообщениях

**Логирование:**
- [ ] Логирование получения голосовых сообщений
- [ ] Логирование процесса транскрибации
- [ ] Логирование результата распознавания

**Проверка качества:**
- [ ] `make quality` - все проверки проходят
- [ ] Coverage ≥ 80%

**Тест:** Отправить боту голосовое сообщение с вопросом о дизайне - получить текстовый ответ.

---

### Итерация 9: Мониторинг LangSmith
**Цель:** Трейсинг и анализ качества ответов LLM (TDD)

**TDD Планирование:**
- [ ] Согласовать архитектуру:
  - LangSmith интегрируется через декораторы/обертки без изменения Protocol
  - Трейсинг добавляется в `LLMClient` и `MessageHandler`
  - Не нарушаем SOLID принципы
- [ ] План тестов:
  - `test_config_langsmith_parameters()` - загрузка параметров LangSmith
  - `test_llm_client_with_tracing()` - трейсинг LLM запросов
  - `test_message_handler_with_tracing()` - трейсинг обработки сообщений
  - `test_tracing_metadata()` - метаданные в трейсах

**TDD Реализация (RED-GREEN-REFACTOR):**

**ADR и документация:**
- [ ] Создать ADR-02: Выбор LangSmith для мониторинга LLM
- [ ] Обосновать выбор LangSmith (трейсинг, аналитика, debugging)
- [ ] Создать инструкцию по настройке LangSmith аккаунта
- [ ] Документировать процесс получения API ключа

**Конфигурация LangSmith:**
- [ ] 🔴 RED: Написать тест `test_config_langsmith_parameters()`
- [ ] 🟢 GREEN: Добавить зависимость `langsmith` в `pyproject.toml`
- [ ] 🟢 GREEN: Добавить параметры в `.env`: `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`
- [ ] 🟢 GREEN: Обновить `Config` - загрузка параметров LangSmith
- [ ] 🔵 REFACTOR: Обновить `.env.example`

**Настройка трейсинга LLMClient:**
- [ ] 🔴 RED: Написать тест `test_llm_client_traceable()`
- [ ] 🟢 GREEN: Добавить декоратор `@traceable` в `LLMClient.get_response()`
- [ ] 🔵 REFACTOR: Настроить теги для разных типов запросов (текст, фото, аудио)
- [ ] Настроить метаданные: model, температуру

**Трейсинг MessageHandler (опционально):**
- [ ] 🔴 RED: Написать тест `test_message_handler_traceable()`
- [ ] 🟢 GREEN: Добавить трейсинг для `MessageHandler.handle_user_message()`
- [ ] 🔵 REFACTOR: Настроить метаданные: user_id, тип сообщения

**Инициализация в main.py:**
- [ ] 🔴 RED: Написать тест `test_langsmith_initialization()`
- [ ] 🟢 GREEN: Инициализация LangSmith в `main.py` через переменные окружения
- [ ] 🔵 REFACTOR: Настроить имя проекта: "homeguru"

**Логирование:**
- [ ] Логирование успешной инициализации LangSmith
- [ ] Логирование ошибок подключения к LangSmith

**Тестирование мониторинга:**
- [ ] Отправить несколько сообщений разного типа (текст, фото, аудио)
- [ ] Проверить отображение трейсов в LangSmith dashboard
- [ ] Проверить корректность логирования запросов и ответов
- [ ] Проверить метрики: latency, token usage

**Проверка качества:**
- [ ] `make quality` - все проверки проходят
- [ ] Coverage ≥ 80%

**Тест:** Взаимодействовать с ботом (текст, фото, аудио) - проверить трейсы в LangSmith dashboard.

---

## 🎯 Критерии готовности MVP

**Базовая функциональность (Итерации 1-5):**
- ✅ Бот работает в Telegram через polling
- ✅ Интеграция с OpenRouter через API
- ✅ Хранение истории диалогов (in-memory)
- ✅ Команды: `/start`, `/reset`, `/help`
- ✅ Логирование работы бота
- ✅ Тесты написаны для каждого компонента

**HomeGuru - ИИ-дизайнер интерьеров (Итерации 6-9):**
- [x] Роль HomeGuru через системный промпт в отдельном файле
- [x] Команда `/role` для отображения специализации
- [ ] Обработка и анализ фотографий интерьеров (Vision API)
- [ ] Распознавание голосовых сообщений (Speech-to-Text)
- [ ] Мониторинг всех запросов через LangSmith
- [ ] Мультимодальные возможности: текст + фото + аудио
- [ ] ADR-02 с обоснованием выбора LangSmith

---

## 📝 Заметки

**Общие правила:**
- После каждой итерации обновляй таблицу прогресса
- **TDD обязателен: тесты ПЕРЕД кодом** (RED-GREEN-REFACTOR)
- Каждая итерация начинается с согласования архитектуры и плана тестов
- Коммить изменения только после прохождения `make quality`
- Если итерация заблокирована - отметь статус ❌ и причину
- Вся разработка следует принципам из [conventions.md](conventions.md) и [workflow_tdd.mdc](.cursor/rules/workflow_tdd.mdc)

**Для итераций 6-9 (HomeGuru):**
- Итерации 6-9 выполняются последовательно, так как есть зависимости
- Итерация 6 (системный промпт) - базовая, выполняется первой
- Итерации 7-8 (фото/аудио) можно выполнить параллельно после итерации 6
- Итерация 9 (LangSmith) выполняется последней, когда все компоненты готовы
- При интеграции Vision/Speech-to-Text учитывай стоимость API запросов
- Тестируй мультимодальность на реальных фото интерьеров
- Проверяй качество транскрибации на русском и английском языках

**Архитектурные изменения в итерациях 6-9:**
- Итерация 6: Обновление `Config` и `CommandHandler`
- Итерация 7: Добавление `MediaProvider` Protocol и `MediaProcessor` класса
- Итерация 7: Расширение `LLMProvider` для мультимодальности
- Итерация 7: Обновление `DialogueStorage` для мультимодальной истории
- Итерация 8: Расширение `MediaProvider` для транскрибации
- Итерация 9: Трейсинг через декораторы без изменения Protocol

**TDD чеклист для каждой итерации:**
- ✅ Архитектура и план тестов согласованы?
- ✅ Тесты написаны ПЕРЕД кодом?
- ✅ RED-GREEN-REFACTOR циклы соблюдены?
- ✅ `make quality` проходит?
- ✅ Coverage ≥ 80%?
- ✅ Protocol интерфейсы применены где нужно?

