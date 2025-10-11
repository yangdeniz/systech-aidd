# Technical Debt: План улучшений по Code Quality

## 📊 Прогресс итераций

| Итерация | Задача | Статус | Дата |
|----------|--------|--------|------|
| TD-1 | Автоматизация контроля качества | ✅ Done | 2025-10-11 |
| TD-2 | Type hints и статическая типизация | ✅ Done | 2025-10-11 |
| TD-3 | Расширение покрытия тестами | ✅ Done | 2025-10-11 |
| TD-4 | Рефакторинг: Protocol/ABC для DIP | ✅ Done | 2025-10-11 |
| TD-5 | Рефакторинг: TelegramBot SRP | ⏳ Pending | - |

**Легенда статусов:**
- ⏳ Pending - не начато
- 🚧 In Progress - в работе
- ✅ Done - завершено
- ❌ Blocked - заблокировано

---

## 📋 Детальный план итераций

### Итерация TD-1: Автоматизация контроля качества
**Цель:** Внедрить автоматические инструменты проверки кода

**Обновить pyproject.toml:**
- [x] Добавить `ruff>=0.3.0` в dev зависимости (форматтер + линтер)
- [x] Добавить `mypy>=1.9.0` в dev зависимости (type checker)
- [x] Добавить `pytest-cov>=4.1.0` для покрытия тестами
- [x] Добавить `pytest-asyncio>=0.23.0` для async тестов
- [x] Обновить версию pytest до `>=8.0.0`

**Настроить Ruff:**
- [x] Добавить секцию `[tool.ruff]` в `pyproject.toml`
- [x] Настроить `target-version = "py311"`
- [x] Настроить `line-length = 100`
- [x] Добавить правила: `["E", "F", "I", "N", "UP", "B", "C4", "SIM"]`

**Настроить Mypy:**
- [x] Добавить секцию `[tool.mypy]` в `pyproject.toml`
- [x] Настроить `python_version = "3.11"`
- [x] Включить `strict = true`
- [x] Настроить `warn_return_any = true`
- [x] Настроить `warn_unused_configs = true`

**Настроить Pytest:**
- [x] Добавить секцию `[tool.pytest.ini_options]`
- [x] Настроить `asyncio_mode = "auto"`
- [x] Настроить `testpaths = ["tests"]`

**Обновить Makefile:**
- [x] Добавить команду `format: ruff format src tests`
- [x] Добавить команду `lint: ruff check src tests --fix`
- [x] Добавить команду `typecheck: mypy src/bot`
- [x] Обновить команду `test` с покрытием: `pytest tests/ -v --cov=src --cov-report=term-missing`
- [x] Добавить команду `quality` для запуска всех проверок: `make format lint typecheck test`

**Проверка соответствия:**
- [x] ✅ Соответствует принципам KISS из `conventions.md` (стандартные инструменты)
- [x] ✅ Соответствует принципу "минимум зависимостей" из `vision.md`
- [x] ✅ Исключены pre-commit hooks (только ручной запуск через Make)
- [x] ✅ Интеграция не нарушает существующую архитектуру

**Результаты проверок TD-1:**
- ✅ Format: OK (10 files reformatted)
- ✅ Lint: OK (All checks passed!)
- ⚠️ Typecheck: 30 ошибок типов (исправим в TD-2)
- ✅ Tests: 10 passed
- 📊 Coverage: 36% (улучшим в TD-3)

**Тест:** ✅ `make quality` запущено - инфраструктура работает

---

### Итерация TD-2: Type hints и статическая типизация
**Цель:** Добавить полные type hints во все модули

**config.py:**
- [x] Добавить type hints для атрибутов класса (`str`, `int`)
- [x] Добавить тип возврата `-> None` для `__init__`
- [x] Добавить валидацию обязательных параметров с `ValueError`
- [x] Добавить дефолтное значение для system_prompt

**dialogue_manager.py:**
- [x] Заменить `list` на `list[dict[str, str]]` для истории
- [x] Заменить `dict` на `dict[int, list[dict[str, str]]]` для dialogues
- [x] Добавить тип возврата для всех методов
- [x] Уточнить типы параметров: `user_id: int`, `role: str`, `content: str`

**llm_client.py:**
- [x] Добавить type hints для всех параметров конструктора
- [x] Заменить `list` на `list[dict[str, str]]` для messages
- [x] Добавить тип возврата `-> str` для `get_response`
- [x] Добавить тип для `self.client: OpenAI`
- [x] Добавить проверку `None` для response_text

**bot.py:**
- [x] Добавить type hints для конструктора
- [x] Добавить типы для всех async методов: `async def ... -> None`
- [x] Добавить проверки `message.from_user is None`
- [x] Убедиться, что все атрибуты класса типизированы

**main.py:**
- [x] Добавить `-> None` для `setup_logging()`
- [x] Добавить `-> None` для `main()`

**Проверка статической типизации:**
- [x] Запустить `make typecheck` - прошло без ошибок
- [x] Исправлены все найденные проблемы с типами (30 → 0)
- [x] Strict mode mypy не выдает ошибок

**Проверка соответствия:**
- [x] ✅ Код остается простым и понятным (`conventions.md`)
- [x] ✅ Типы помогают понять API без документации (`conventions.md`)
- [x] ✅ Не добавляем избыточных абстракций (`conventions.md`)
- [x] ✅ Следуем принципу "1 класс = 1 файл" (`vision.md`)

**Результаты проверок TD-2:**
- ✅ Format: OK (2 files reformatted)
- ✅ Lint: All checks passed!
- ✅ Typecheck: **SUCCESS - 0 errors!** (было 30 ошибок)
- ✅ Tests: 10 passed
- 📊 Coverage: 39% (увеличилось с 36%)

**Тест:** ✅ `mypy src/bot --strict` - Success: no issues found in 6 source files

---

### Итерация TD-3: Расширение покрытия тестами
**Цель:** Увеличить покрытие до ≥80%, добавить недостающие тесты

**Создать conftest.py с фикстурами:**
- [x] Создать `tests/conftest.py`
- [x] Добавить фикстуру `dialogue_manager` (DialogueManager instance)
- [x] Добавить фикстуру `mock_llm_client` (мокированный LLMClient)
- [x] Добавить фикстуру `mock_message` (мокированное Telegram Message)
- [x] Добавить фикстуру `mock_bot_token` (тестовый токен)

**Создать test_bot.py:**
- [x] Создать `tests/test_bot.py`
- [x] Тест `test_bot_initialization` - проверка создания экземпляра
- [x] Тест `test_cmd_start` - проверка команды /start
- [x] Тест `test_cmd_help` - проверка команды /help
- [x] Тест `test_cmd_reset` - проверка команды /reset
- [x] Тест `test_handle_message_success` - успешная обработка сообщения
- [x] Тест `test_handle_message_error` - обработка ошибок
- [x] Тест `test_cmd_start_no_user` - проверка None для user
- [x] Тест `test_handle_message_no_text` - проверка None для text
- [x] Использовать `pytest-asyncio` для async тестов

**Улучшить test_config.py:**
- [x] Добавить тест `test_config_missing_telegram_token` - отсутствие токена
- [x] Добавить тест `test_config_missing_api_key` - отсутствие API ключа
- [x] Добавить тест `test_config_missing_model` - отсутствие модели
- [x] Добавить тест `test_config_default_system_prompt` - дефолтный промпт
- [x] Исправить моки для изоляции от реального .env

**Улучшить test_llm_client.py:**
- [x] Добавить тест `test_llm_client_error_handling` - обработка ошибок API
- [x] Добавить тест `test_llm_client_empty_response` - пустой ответ от LLM
- [x] Добавить тест `test_llm_client_with_empty_messages` - пустой список сообщений

**Создать test_main.py:**
- [x] Создать `tests/test_main.py`
- [x] Тест `test_setup_logging` - проверка настройки логирования
- [x] Тест `test_main_initialization` - проверка инициализации компонентов

**Исправление импортов:**
- [x] Исправить относительные импорты в `bot.py` (`.dialogue_manager`, `.llm_client`)
- [x] Исправить относительные импорты в `main.py` (`.config`, `.bot`, и т.д.)

**Проверка покрытия:**
- [x] Запустить `pytest --cov=src --cov-report=term-missing`
- [x] Проверить coverage report - **98%** (цель ≥80%)
- [x] Добавлено **17 новых тестов** (было 10, стало 27)

**Проверка соответствия:**
- [x] ✅ Тесты простые и понятные (`conventions.md`)
- [x] ✅ Тесты проверяют базовую функциональность (`vision.md`)
- [x] ✅ Не тестируем интеграции с внешними API в unit-тестах (`vision.md`)
- [x] ✅ Используем моки для внешних зависимостей (`vision.md`)

**Результаты проверок TD-3:**
- ✅ Format: OK (4 files reformatted)
- ✅ Lint: All checks passed! (10 fixed, 0 remaining)
- ✅ Typecheck: **SUCCESS - 0 errors!**
- ✅ Tests: **27 passed** (было 10)
- 📊 Coverage: **98%** 🎉 (цель была 80%)

**Детали покрытия по модулям:**
- `config.py`: 100% ✅
- `dialogue_manager.py`: 100% ✅
- `llm_client.py`: 100% ✅
- `bot.py`: 95% ✅
- `main.py`: 97% ✅

**Тест:** ✅ `make quality` - все проверки пройдены успешно!

---

### Итерация TD-4: Рефакторинг: Protocol/ABC для Dependency Inversion
**Цель:** Внедрить абстракции для ключевых зависимостей (SOLID DIP)

**Создать src/bot/interfaces.py:**
- [x] Создать файл `src/bot/interfaces.py`
- [x] Определить `Protocol` класс `LLMProvider` с методом `get_response`
- [x] Определить `Protocol` класс `DialogueStorage` с методами для работы с историей
- [x] Добавить docstrings с описанием контрактов
- [x] Добавить полные type hints

**LLMProvider Protocol:**
```python
from typing import Protocol

class LLMProvider(Protocol):
    """Контракт для провайдеров LLM"""
    
    def get_response(self, messages: list[dict[str, str]]) -> str:
        """Получить ответ от LLM на основе истории сообщений"""
        ...
```

**DialogueStorage Protocol:**
```python
class DialogueStorage(Protocol):
    """Контракт для хранилищ диалогов"""
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в историю"""
        ...
    
    def get_history(self, user_id: int) -> list[dict[str, str]]:
        """Получить историю диалога пользователя"""
        ...
    
    def clear_history(self, user_id: int) -> None:
        """Очистить историю диалога"""
        ...
```

**Обновить bot.py:**
- [x] Изменить тип параметров конструктора на Protocol типы
- [x] `llm_client: LLMProvider` вместо `LLMClient`
- [x] `dialogue_manager: DialogueStorage` вместо `DialogueManager`
- [x] Обновить импорты (`from .interfaces import DialogueStorage, LLMProvider`)

**Обновить main.py:**
- [x] Убедиться, что передаваемые объекты соответствуют Protocol
- [x] Код работает без изменений (duck typing) ✅

**Обновить тесты:**
- [x] В `conftest.py` обновить типы фикстур на Protocol
- [x] `dialogue_manager() -> DialogueStorage`
- [x] `mock_llm_client() -> LLMProvider`
- [x] Убедиться, что тесты проходят после рефакторинга

**Проверка соответствия:**
- [x] ✅ Минимум новых абстракций - только для ключевых зависимостей (`conventions.md`)
- [x] ✅ Protocol проще, чем ABC - выбираем Protocol (`conventions.md`)
- [x] ✅ Не создаем избыточных уровней абстракции (`conventions.md`)
- [x] ✅ Код остается простым и понятным (`vision.md`)
- [x] ✅ Легко добавить новые имплементации в будущем (SOLID DIP)

**Результаты проверок TD-4:**
- ✅ Format: OK (3 files reformatted)
- ✅ Lint: All checks passed!
- ✅ Typecheck: **SUCCESS - 0 errors!** (7 source files)
- ✅ Tests: **27 passed**
- 📊 Coverage: **98%** (interfaces.py: 100%)

**Преимущества:**
- 🔓 **Слабая связанность** - TelegramBot зависит от абстракций, а не реализаций
- 🧪 **Легко тестировать** - моки автоматически соответствуют Protocol
- 🔄 **Легко расширять** - можно добавить новые LLM провайдеры или хранилища
- 📝 **Чистый код** - Protocol проще чем ABC, соблюдает Duck Typing

**Тест:** ✅ `make quality` - все проверки пройдены успешно!

---

### Итерация TD-5: Рефакторинг: TelegramBot - Single Responsibility
**Цель:** Разделить TelegramBot на более мелкие компоненты (SOLID SRP)

**Анализ текущих обязанностей:**
- [ ] TelegramBot содержит: инфраструктуру aiogram + обработку команд + бизнес-логику
- [ ] Необходимо разделить на: TelegramBot (инфраструктура) + MessageHandler (логика)

**Создать src/bot/message_handler.py:**
- [ ] Создать класс `MessageHandler` - бизнес-логика обработки сообщений
- [ ] Перенести метод `handle_message` из `TelegramBot`
- [ ] Конструктор принимает `LLMProvider` и `DialogueStorage`
- [ ] Метод `async def handle_user_message(user_id: int, username: str, text: str) -> str`
- [ ] Возвращает текст ответа вместо прямой отправки
- [ ] Добавить полные type hints

**Создать src/bot/command_handler.py:**
- [ ] Создать класс `CommandHandler` - обработка команд бота
- [ ] Перенести команды `/start`, `/help`, `/reset` из `TelegramBot`
- [ ] Конструктор принимает `DialogueStorage`
- [ ] Методы возвращают текст ответа: `get_start_message() -> str`
- [ ] Метод `reset_dialogue(user_id: int) -> str`
- [ ] Добавить полные type hints

**Обновить src/bot/bot.py:**
- [ ] Упростить `TelegramBot` - только инфраструктура aiogram
- [ ] Конструктор принимает `MessageHandler` и `CommandHandler`
- [ ] Команды делегируют работу в `CommandHandler` и отправляют ответ
- [ ] `handle_message` делегирует в `MessageHandler` и отправляет ответ
- [ ] Убрать всю бизнес-логику из класса

**Обновить src/bot/main.py:**
- [ ] Создать экземпляры `MessageHandler` и `CommandHandler`
- [ ] Передать их в конструктор `TelegramBot`
- [ ] Убедиться, что всё работает корректно

**Создать тесты:**
- [ ] `tests/test_message_handler.py` - тесты для MessageHandler
- [ ] `tests/test_command_handler.py` - тесты для CommandHandler
- [ ] Обновить `tests/test_bot.py` - теперь тестируем только инфраструктуру

**Проверка соответствия:**
- [ ] ✅ Каждый класс имеет одну ответственность (SOLID SRP)
- [ ] ✅ Код проще для понимания и тестирования
- [ ] ✅ Следуем принципу "1 класс = 1 файл" (`conventions.md`)
- [ ] ✅ Не создали избыточных абстракций - только логическое разделение
- [ ] ✅ Модульная структура соответствует `vision.md`

**Финальная проверка:**
- [ ] Запустить `make quality` - все проверки проходят
- [ ] Покрытие тестами не снизилось (≥80%)
- [ ] Код легче читать и тестировать
- [ ] Легко добавить новые команды или типы сообщений

**Тест:** Запустить бота вручную, протестировать все команды и текстовые сообщения

---

## 🎯 Критерии завершения Tech Debt итераций

**После TD-1 (Автоматизация):**
- ✅ Все инструменты настроены в `pyproject.toml`
- ✅ Makefile содержит команды `format`, `lint`, `typecheck`, `test`, `quality`
- ✅ `make quality` выполняется без критических ошибок

**После TD-2 (Type hints):**
- ✅ Все модули имеют полные type hints
- ✅ `mypy --strict` проходит без ошибок
- ✅ Код понятен благодаря типам

**После TD-3 (Тесты):**
- ✅ Покрытие тестами ≥80%
- ✅ Все основные компоненты покрыты тестами
- ✅ `tests/conftest.py` содержит переиспользуемые фикстуры

**После TD-4 (Protocol/DIP):**
- ✅ Создан `interfaces.py` с Protocol классами
- ✅ TelegramBot зависит от абстракций, а не конкретных классов
- ✅ Легко добавить альтернативные имплементации

**После TD-5 (SRP):**
- ✅ TelegramBot - только инфраструктура
- ✅ MessageHandler - бизнес-логика сообщений
- ✅ CommandHandler - обработка команд
- ✅ Каждый класс имеет одну четкую ответственность

---

## 📝 Правила работы с Tech Debt

**Общие правила:**
- После каждой итерации обновляй таблицу прогресса
- Запускай `make quality` после каждого изменения
- Все изменения должны быть покрыты тестами
- Следуй всем соглашениям из `conventions.md`
- Не отклоняйся от простоты и принципа KISS
- Коммить после успешного прохождения всех проверок

**Проверка соответствия документам на каждой итерации:**
- [ ] ✅ Соответствует `conventions.md` (KISS, без оверинжиниринга)
- [ ] ✅ Соответствует `workflow.md` и `workflow_tech_debt.md` (согласование → реализация → проверка)
- [ ] ✅ Соответствует `vision.md` (MVP подход, простота, ООП с 1 класс = 1 файл)
- [ ] ✅ Следует принципам SOLID (SRP, DIP) без избыточности

**Последовательность выполнения:**
- TD-1 → TD-2 → TD-3 можно выполнять последовательно или параллельно
- TD-4 → TD-5 выполняются только после завершения TD-1,2,3
- Не переходи к следующей итерации без завершения предыдущей

**Приоритет:**
1. **Критично**: TD-1 (инструменты), TD-2 (типы)
2. **Важно**: TD-3 (тесты)
3. **Желательно**: TD-4 (DIP), TD-5 (SRP)

---

## 🔄 Интеграция с основным tasklist.md

**Связь с основной разработкой:**
- Tech Debt итерации выполняются параллельно с функциональными итерациями
- Рекомендуется выполнить TD-1 и TD-2 перед итерацией 6 (HomeGuru)
- TD-3 можно выполнять инкрементально вместе с новыми фичами
- TD-4 и TD-5 - опционально, после завершения основного MVP

**Момент для выполнения:**
- **Сейчас**: TD-1, TD-2 (после итерации 5 - Логирование)
- **Перед итерацией 6**: TD-3 (расширение тестов)
- **После MVP**: TD-4, TD-5 (рефакторинг архитектуры)

---

## 💡 Заметки

**Важно помнить:**
- Качество кода важно, но не важнее работающего MVP
- Все улучшения должны сохранять простоту проекта
- Type hints помогают, но не должны усложнять код
- Тесты нужны для уверенности, а не для метрик
- Рефакторинг делаем только когда есть реальная боль
- SOLID применяем разумно, без фанатизма

**Когда делать Tech Debt:**
- ✅ После завершения базовой функциональности (итерации 1-5)
- ✅ Перед добавлением сложных фич (итерации 6-9)
- ✅ Когда код становится сложно поддерживать
- ❌ Не делаем "на будущее" без реальной необходимости

**Best Practices для проекта:**
- Используем Ruff вместо Black + Flake8 (проще и быстрее)
- Используем Protocol вместо ABC (проще и pythonic)
- Coverage ≥80% - разумный баланс между качеством и временем
- Strict mypy - помогает найти баги на ранней стадии
- Make для автоматизации - просто и эффективно

---

**Последнее обновление:** 2025-10-11

