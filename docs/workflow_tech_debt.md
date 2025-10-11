# Workflow: Tech Debt - Правила работы с качеством кода

> Расширенная инструкция для code-ассистента по улучшению качества кода согласно [tasklist_tech_debt.md](tasklist_tech_debt.md)

## Основные принципы

1. **Качество без фанатизма** - улучшаем код, но сохраняем простоту
2. **Автоматизация проверок** - используем инструменты, а не ручной контроль
3. **Тестируемость** - код должен легко покрываться тестами
4. **Типобезопасность** - type hints для понимания и предотвращения ошибок
5. **Следуй SOLID** - разумно, без оверинжиниринга

---

## Процесс выполнения Tech Debt итерации

### 1️⃣ Планирование

**Перед началом итерации:**
- [ ] Прочитай описание итерации из [tasklist_tech_debt.md](tasklist_tech_debt.md)
- [ ] Оцени влияние изменений на существующий код
- [ ] Предложи решение с примерами кода
- [ ] Покажи как это улучшит качество/поддерживаемость
- [ ] **Дождись согласования** от разработчика

❗ **Не начинай рефакторинг без четкого плана!**

---

### 2️⃣ Реализация

**После согласования:**
- [ ] Реализуй изменения согласно плану
- [ ] Обнови/создай файлы конфигурации (pyproject.toml, Makefile)
- [ ] Примени изменения к существующему коду
- [ ] Убедись, что не нарушена работоспособность

**Критерии качества:**
- ✅ Код проходит `make format`
- ✅ Код проходит `make lint` без критических ошибок
- ✅ Код проходит `make typecheck` (mypy strict)
- ✅ Все тесты проходят `make test`
- ✅ Покрытие не снизилось

---

### 3️⃣ Проверка качества кода

**Обязательные проверки перед завершением:**

**Форматирование:**
```bash
make format
# Автоматически форматирует код через Ruff
```

**Линтинг:**
```bash
make lint
# Проверяет код на ошибки и стилистику
# Автоматически исправляет простые проблемы
```

**Статическая типизация:**
```bash
make typecheck
# Проверяет type hints через mypy --strict
# Должно проходить без ошибок
```

**Тестирование:**
```bash
make test
# Запускает все тесты с покрытием
# Цель: coverage ≥ 80%
```

**Полная проверка:**
```bash
make quality
# Запускает все проверки последовательно
# format → lint → typecheck → test
```

---

### 4️⃣ Обновление документации

**После реализации:**
- [ ] Отметь выполненные чекбоксы в [tasklist_tech_debt.md](tasklist_tech_debt.md)
- [ ] Обнови статус итерации (⏳ → 🚧 → ✅)
- [ ] Проставь дату завершения
- [ ] Зафиксируй результаты проверок (coverage %, mypy результаты)
- [ ] **Дождись подтверждения** от разработчика

❗ **Не переходи к следующей итерации без подтверждения!**

---

### 5️⃣ Коммит

**Формат коммитов для Tech Debt:**
```bash
# Формат: refactor(scope): описание
refactor(quality): add ruff and mypy configuration
refactor(types): add type hints to all modules
refactor(tests): increase test coverage to 85%
refactor(arch): introduce Protocol for DIP
refactor(structure): split TelegramBot by SRP
```

**Требования к коммиту:**
- [ ] Все проверки `make quality` проходят
- [ ] Coverage не снизился
- [ ] Нет breaking changes (если есть - документируй)
- [ ] **Дождись одобрения** перед выполнением

---

## Стандарты качества кода

### Форматирование (Ruff format)

**Автоматическое форматирование:**
- Длина строки: 100 символов
- Автоматическая сортировка импортов
- Единый стиль кавычек, отступов
- PEP 8 compliant

**Как использовать:**
```bash
# Форматировать весь код
make format

# Проверить без изменений
ruff format --check src tests
```

**Не требует ручной настройки** - Ruff всё делает сам.

---

### Линтинг (Ruff check)

**Проверяемые правила:**
- **E** - Ошибки PEP 8
- **F** - Pyflakes (неиспользуемые импорты, переменные)
- **I** - isort (сортировка импортов)
- **N** - pep8-naming (именование)
- **UP** - pyupgrade (современный Python синтаксис)
- **B** - bugbear (потенциальные баги)
- **C4** - comprehensions (упрощение списковых выражений)
- **SIM** - simplify (упрощение кода)

**Как использовать:**
```bash
# Проверка с автоисправлением
make lint

# Только проверка без исправлений
ruff check src tests

# Проверка конкретного файла
ruff check src/bot/bot.py
```

**Уровни ошибок:**
- 🔴 **Error** - обязательно исправить
- 🟡 **Warning** - желательно исправить
- 🔵 **Info** - для информации

---

### Статическая типизация (Mypy)

**Требования к type hints:**

**✅ Обязательно типизировать:**
- Все параметры функций/методов
- Все возвращаемые значения
- Атрибуты класса
- Переменные с неочевидным типом

**Примеры правильной типизации:**

```python
from typing import Protocol

class Config:
    telegram_token: str
    max_history: int
    
    def __init__(self) -> None:
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

class DialogueManager:
    dialogues: dict[int, list[dict[str, str]]]
    
    def __init__(self, max_history: int) -> None:
        self.dialogues = {}
        self.max_history = max_history
    
    def get_history(self, user_id: int) -> list[dict[str, str]]:
        return self.dialogues.get(user_id, [])

# Protocol для зависимостей
class LLMProvider(Protocol):
    def get_response(self, messages: list[dict[str, str]]) -> str: ...
```

**Как использовать:**
```bash
# Проверка типов
make typecheck

# Проверка конкретного файла
mypy src/bot/config.py --strict
```

**Режим strict включает:**
- `disallow_untyped_defs` - все функции типизированы
- `disallow_any_unimported` - запрет Any без явного указания
- `warn_return_any` - предупреждение при возврате Any
- `warn_unused_ignores` - предупреждение о лишних type: ignore

---

### Тестирование (Pytest)

**Стандарты тестирования:**

**Структура тестов:**
```
tests/
├── conftest.py              # Общие фикстуры
├── test_config.py           # Тесты для config.py
├── test_dialogue_manager.py # Тесты для dialogue_manager.py
├── test_llm_client.py       # Тесты для llm_client.py
├── test_bot.py              # Тесты для bot.py
├── test_message_handler.py  # Тесты для message_handler.py
└── test_command_handler.py  # Тесты для command_handler.py
```

**Правила именования:**
- Файл: `test_<module>.py`
- Тест: `def test_<что_тестируется>():`
- Фикстура: описательное имя без префикса test_

**Пример хороших тестов:**

```python
# conftest.py
import pytest
from src.bot.dialogue_manager import DialogueManager

@pytest.fixture
def dialogue_manager() -> DialogueManager:
    """Создает DialogueManager для тестов"""
    return DialogueManager(max_history=20)

# test_dialogue_manager.py
def test_add_message(dialogue_manager):
    """Тест добавления сообщения в историю"""
    dialogue_manager.add_message(123, "user", "Hello")
    
    history = dialogue_manager.get_history(123)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"

def test_max_history_limit(dialogue_manager):
    """Тест ограничения количества сообщений"""
    dm = DialogueManager(max_history=3)
    
    for i in range(5):
        dm.add_message(123, "user", f"Message {i}")
    
    history = dm.get_history(123)
    assert len(history) == 3
    assert history[0]["content"] == "Message 2"

@pytest.mark.asyncio
async def test_cmd_start(mock_bot, mock_message):
    """Тест команды /start"""
    await mock_bot.cmd_start(mock_message)
    mock_message.answer.assert_called_once()
```

**Что тестировать:**
- ✅ Базовая функциональность каждого метода
- ✅ Граничные случаи (пустые списки, None, максимальные значения)
- ✅ Обработка ошибок
- ✅ Взаимодействие компонентов (через моки)

**Что НЕ тестировать в unit-тестах:**
- ❌ Интеграции с внешними API (Telegram, OpenRouter)
- ❌ Реальные запросы к LLM
- ❌ Файловая система (использовать моки)

**Покрытие:**
```bash
# Запуск с отчетом о покрытии
make test

# Детальный HTML отчет
pytest --cov=src --cov-report=html
# Открыть: htmlcov/index.html

# Цель: ≥ 80% coverage
```

---

## Лучшие практики Python

### 1. Type Hints

**✅ Хорошо:**
```python
def get_history(self, user_id: int) -> list[dict[str, str]]:
    return self.dialogues.get(user_id, [])

class DialogueManager:
    dialogues: dict[int, list[dict[str, str]]]
```

**❌ Плохо:**
```python
def get_history(self, user_id):  # Без типов
    return self.dialogues.get(user_id, [])
```

---

### 2. Protocol для зависимостей (DIP)

**✅ Хорошо:**
```python
from typing import Protocol

class LLMProvider(Protocol):
    def get_response(self, messages: list[dict[str, str]]) -> str: ...

class TelegramBot:
    def __init__(self, llm: LLMProvider):  # Зависит от абстракции
        self.llm = llm
```

**❌ Плохо:**
```python
from llm_client import LLMClient

class TelegramBot:
    def __init__(self, llm: LLMClient):  # Зависит от конкретного класса
        self.llm = llm
```

---

### 3. Single Responsibility Principle

**✅ Хорошо:**
```python
# bot.py - только инфраструктура
class TelegramBot:
    def __init__(self, message_handler: MessageHandler):
        self.handler = message_handler
    
    async def handle_message(self, message: Message):
        response = await self.handler.process(message.text)
        await message.answer(response)

# message_handler.py - бизнес-логика
class MessageHandler:
    def process(self, text: str) -> str:
        # Обработка сообщения
        return response
```

**❌ Плохо:**
```python
class TelegramBot:
    # Всё в одном классе: инфраструктура + логика + команды
    async def handle_message(self, message: Message):
        # 100+ строк логики здесь
```

---

### 4. Валидация в конструкторах

**✅ Хорошо:**
```python
class Config:
    def __init__(self) -> None:
        load_dotenv()
        
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        self.max_history = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
```

**❌ Плохо:**
```python
class Config:
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Может быть None
```

---

### 5. Использование моков в тестах

**✅ Хорошо:**
```python
def test_llm_client_adds_system_prompt(mocker):
    mock_client = mocker.Mock()
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock(message=mocker.Mock(content="Test"))]
    mock_client.chat.completions.create.return_value = mock_response
    
    with mocker.patch('src.bot.llm_client.OpenAI', return_value=mock_client):
        client = LLMClient("key", "model", "System prompt")
        response = client.get_response([{"role": "user", "content": "Hi"}])
        
        assert response == "Test"
```

**❌ Плохо:**
```python
def test_llm_client():
    client = LLMClient(real_api_key, model, prompt)
    response = client.get_response([{"role": "user", "content": "Hi"}])
    # Реальный запрос к API - медленно, дорого, ненадежно
```

---

### 6. Async/await для IO операций

**✅ Хорошо:**
```python
class TelegramBot:
    async def handle_message(self, message: Message) -> None:
        response = await self.handler.process(message.text)
        await message.answer(response)
```

**❌ Плохо:**
```python
class TelegramBot:
    def handle_message(self, message: Message):  # Блокирующий вызов
        response = self.handler.process(message.text)
        message.answer(response)
```

---

### 7. Логирование с контекстом

**✅ Хорошо:**
```python
logger.info(f"Received message from user {user_id} (@{username}): {text[:50]}...")
logger.error(f"Error handling message from user {user_id}: {e}", exc_info=True)
```

**❌ Плохо:**
```python
logger.info("Message received")
logger.error("Error")  # Без контекста
```

---

## Чек-лист перед коммитом Tech Debt

### Автоматические проверки
- [ ] ✅ `make format` - код отформатирован
- [ ] ✅ `make lint` - линтер пройден
- [ ] ✅ `make typecheck` - типы корректны
- [ ] ✅ `make test` - все тесты проходят
- [ ] ✅ Coverage ≥ 80%

### Ручная проверка
- [ ] ✅ Код остался простым и понятным (KISS)
- [ ] ✅ Не добавлено избыточных абстракций
- [ ] ✅ Следует принципу "1 класс = 1 файл"
- [ ] ✅ Все методы типизированы
- [ ] ✅ Новый код покрыт тестами
- [ ] ✅ Логирование добавлено где нужно

### Документация
- [ ] ✅ Обновлен tasklist_tech_debt.md (прогресс, статус)
- [ ] ✅ Обновлены conventions.mdc (если нужно)
- [ ] ✅ Обновлен vision.md (если изменилась архитектура)

---

## Шаблон работы для Tech Debt итерации

```
1. Планирование
   "Предлагаю решение для итерации TD-N:
    - Настроить Ruff: [конфигурация]
    - Применить к модулям: [список]
    - Ожидаемый результат: [метрики]
    Согласовываем?"

2. Реализация
   [обновление pyproject.toml, Makefile]
   [применение к коду]
   "Реализация завершена. Готово к проверке."

3. Проверка качества
   $ make quality
   ✅ Format: OK
   ✅ Lint: 0 errors
   ✅ Typecheck: Success
   ✅ Tests: 45 passed, Coverage: 85%

4. Обновление документации
   [обновление tasklist_tech_debt.md]
   "Прогресс обновлен. Итерация TD-N завершена."

5. Коммит
   "Предлагаю закоммитить:
    git commit -m 'refactor(quality): add ruff and mypy configuration'"

6. Переход
   "Переходим к итерации TD-N+1?"
```

---

## Что НЕ делать

❌ Не рефакторь без согласования  
❌ Не коммить код, не прошедший `make quality`  
❌ Не снижай coverage при рефакторинге  
❌ Не добавляй сложности ради "красоты" кода  
❌ Не используй сложные паттерны там, где можно проще  
❌ Не нарушай существующие conventions ради новых стандартов  
❌ Не делай несколько Tech Debt итераций за раз  

---

## Интеграция с основным workflow

**При работе над новыми фичами:**
1. Разработка функционала (как в workflow.mdc)
2. Применение стандартов качества (этот workflow)
3. Проверка через `make quality`
4. Тестирование и коммит

**При работе над Tech Debt:**
1. Выполнение итерации по tasklist_tech_debt.md
2. Следование этому workflow
3. Обязательная проверка качества
4. Документирование изменений

---

## Метрики качества

### Цели для проекта

| Метрика | Цель | Текущее |
|---------|------|---------|
| Test Coverage | ≥ 80% | - |
| Mypy Strict | 0 errors | - |
| Ruff Errors | 0 critical | - |
| Code Complexity | Low | - |

### Как измерять

```bash
# Coverage
pytest --cov=src --cov-report=term-missing

# Mypy
mypy src tests --strict

# Ruff
ruff check src tests --statistics

# Все метрики
make quality
```

---

**Помни**: Качество кода важно, но простота и работоспособность важнее. Все улучшения должны делать код лучше, а не сложнее.

---

**Последнее обновление:** 2025-10-11

