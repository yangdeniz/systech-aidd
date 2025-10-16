# Developer Quickstart: Первый день разработчика

Что нужно знать, чтобы начать разработку HomeGuru.

---

## О проекте в 30 секунд

**HomeGuru** - Telegram-бот с ИИ-дизайнером интерьеров.

- **Архитектура:** MVP-монолит с мультимодальностью
- **Стек:** Python 3.11+, aiogram, OpenRouter, Faster-Whisper
- **Принципы:** KISS, TDD, SOLID (SRP + DIP)
- **Качество:** 98% coverage, strict mypy, 0 errors

---

## Структура проекта

```
systech-aidd/
├── src/bot/           # Исходный код
│   ├── main.py              # Точка входа
│   ├── bot.py               # Telegram инфраструктура
│   ├── message_handler.py   # Бизнес-логика сообщений
│   ├── command_handler.py   # Обработка команд
│   ├── llm_client.py        # Интеграция с OpenRouter
│   ├── dialogue_manager.py  # История диалогов (in-memory)
│   ├── media_processor.py   # Обработка фото/аудио
│   ├── config.py            # Конфигурация из .env
│   ├── interfaces.py        # Protocol интерфейсы
│   └── system_prompt.txt    # Роль HomeGuru
│
├── tests/             # Тесты (66 тестов, 98% coverage)
│   ├── conftest.py          # Общие фикстуры
│   └── test_*.py            # Тесты для каждого модуля
│
├── docs/              # Документация
│   ├── vision.md            # Техническое видение
│   ├── roadmap.md           # Roadmap по спринтам
│   ├── tasklists/           # Тасклисты спринтов
│   ├── conventions.md       # Соглашения разработки
│   ├── workflow.md          # Процесс работы
│   └── guides/              # Гайды
│
├── .env               # Конфигурация (не в git)
├── pyproject.toml     # Зависимости + настройки инструментов
├── Makefile           # Команды разработки
└── README.md          # Обзор проекта
```

---

## Ключевые команды

### Установка и запуск

```bash
make install    # Установка зависимостей (uv sync)
make run        # Запуск бота
```

### Проверка качества

```bash
make format     # Форматирование (Ruff)
make lint       # Линтинг + автофикс (Ruff)
make typecheck  # Проверка типов (Mypy strict)
make test       # Тесты + coverage
make quality    # Все проверки (обязательно перед коммитом!)
```

---

## Первое изменение (TDD)

### 1. Создай ветку

```bash
git checkout -b feature/my-feature
```

### 2. Напиши тест (RED)

**Файл:** `tests/test_my_feature.py`

```python
def test_my_new_feature():
    # Arrange
    manager = DialogueManager(max_history=20)
    
    # Act
    result = manager.some_new_method()
    
    # Assert
    assert result == expected_value
```

Запусти тест - он должен упасть:
```bash
pytest tests/test_my_feature.py -v
```

### 3. Реализуй код (GREEN)

**Файл:** `src/bot/dialogue_manager.py`

```python
def some_new_method(self) -> ReturnType:
    # Минимальная реализация для прохождения теста
    return result
```

Запусти тест - он должен пройти:
```bash
pytest tests/test_my_feature.py -v
```

### 4. Улучши код (REFACTOR)

Оптимизируй реализацию, тесты остаются зелеными.

### 5. Проверь качество

```bash
make quality
```

**Ожидаемый результат:**
- ✅ Format: OK
- ✅ Lint: All checks passed
- ✅ Typecheck: Success
- ✅ Tests: All passed
- ✅ Coverage: ≥80%

### 6. Коммит

```bash
git add .
git commit -m "feat: add new feature"
```

---

## Где искать что

### Нужно понять архитектуру?
→ `docs/vision.md` (техническое видение)  
→ `docs/guides/03-architecture-overview.md` (обзор)

### Нужно добавить функциональность?
→ `docs/tasklist.md` (текущий план)  
→ `docs/workflow.md` (процесс работы)

### Нужно написать тест?
→ `docs/.cursor/rules/qa_conventions.mdc` (правила тестирования)  
→ `tests/conftest.py` (фикстуры)

### Нужно понять соглашения?
→ `docs/conventions.md` (coding conventions)

### Проблемы с конфигурацией?
→ `docs/guides/07-configuration.md` (детальная настройка)

### Нужно понять модуль?
→ `docs/guides/04-codebase-tour.md` (тур по коду)

---

## Основные принципы

### KISS (Keep It Simple)
- Простота важнее "правильной" архитектуры
- Если можно проще - делай проще
- Код должен быть понятен без комментариев

### TDD (Test-Driven Development)
- **Тесты пишутся ПЕРЕД кодом**
- RED → GREEN → REFACTOR
- Coverage ≥ 80%

### Type Safety
- Type hints обязательны везде
- Mypy strict mode (0 errors)
- Используй современный синтаксис: `list[str]`, `dict[int, str]`

### SOLID (разумно)
- **SRP:** каждый класс = одна ответственность
- **DIP:** зависимость от Protocol, не от реализаций
- Не применяем остальные принципы без необходимости

### Правило "1 класс = 1 файл"
- `TelegramBot` → `bot.py`
- `MessageHandler` → `message_handler.py`
- `Config` → `config.py`

---

## Структура тестов

### Naming
```python
def test_add_message():              # Основной сценарий
def test_add_message_exceeds_limit():  # Edge case
def test_get_history_empty():        # Граничный случай
```

### AAA Pattern
```python
def test_clear_history():
    # Arrange - подготовка
    dm = DialogueManager(max_history=20)
    dm.add_message(123, "user", "Hello")
    
    # Act - действие
    dm.clear_history(123)
    
    # Assert - проверка
    assert dm.get_history(123) == []
```

### Фикстуры
```python
# tests/conftest.py
@pytest.fixture
def dialogue_manager() -> DialogueStorage:
    return DialogueManager(max_history=20)

# tests/test_module.py
def test_something(dialogue_manager):
    # используй фикстуру
    dialogue_manager.add_message(123, "user", "Hi")
```

---

## Типичные задачи

### Добавить новую команду

1. **Тест:** `tests/test_command_handler.py`
2. **Логика:** `src/bot/command_handler.py` (метод)
3. **Handler:** `src/bot/bot.py` (регистрация)
4. **Проверка:** `make quality`

### Изменить роль бота

1. Отредактируй `src/bot/system_prompt.txt`
2. Перезапусти бота (`make run`)

### Добавить новый параметр конфигурации

1. Добавь в `.env.example`
2. Добавь в `src/bot/config.py` (атрибут + загрузка)
3. Добавь тест в `tests/test_config.py`
4. Обнови `docs/guides/07-configuration.md`

### Изменить модель LLM

Измени в `.env`:
```env
OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

---

## Чеклист перед коммитом

- [ ] Тесты написаны ПЕРЕД кодом (TDD)
- [ ] `make quality` проходит без ошибок
- [ ] Coverage ≥ 80%
- [ ] Type hints добавлены (все параметры, возвраты)
- [ ] Код простой и понятный (KISS)
- [ ] Соблюдено "1 класс = 1 файл"
- [ ] Логирование добавлено (где нужно)
- [ ] Документация обновлена (если нужно)

---

## Быстрые ссылки

| Что нужно | Где искать |
|-----------|-----------|
| 🏗 Архитектура | `docs/vision.md`, `docs/guides/03-architecture-overview.md` |
| 📋 Текущие задачи | `docs/tasklist.md` |
| 📏 Соглашения | `docs/conventions.md` |
| 🔄 Процесс работы | `docs/workflow.md` |
| 🧪 Тестирование | `docs/.cursor/rules/qa_conventions.mdc` |
| ⚙️ Конфигурация | `docs/guides/07-configuration.md` |
| 🗺 Тур по коду | `docs/guides/04-codebase-tour.md` |

---

## Следующие шаги

После освоения базовых команд:

1. **Изучи архитектуру:** [`03-architecture-overview.md`](03-architecture-overview.md)
2. **Прочитай vision:** `docs/vision.md`
3. **Изучи workflow:** `docs/workflow.md`
4. **Посмотри conventions:** `docs/conventions.md`

---

## Помощь

**Вопросы по коду?** → Читай `docs/guides/04-codebase-tour.md`

**Проблемы с запуском?** → Читай `docs/guides/01-getting-started.md`

**Не проходят тесты?** → Читай `docs/.cursor/rules/qa_conventions.mdc`

**Вопросы по процессу?** → Читай `docs/workflow.md`

---

**Готов к разработке?** 🚀 Начни с простой задачи из `docs/tasklist.md`!

