<!-- c6bb1035-06f0-430b-8789-63c59d222a9f 59efa11c-5f4a-4140-9334-1f3386b9cf68 -->
# План F-Sprint-4: Реализация ИИ-чата

## Цель

Разработать веб-интерфейс ИИ-чата с floating button в дашборде, поддержкой двух режимов работы (обычный и администратор) и интеграцией с LLM через backend API.

## Backend: Chat API

### 1. Модели и типы (`src/api/chat_models.py`)

Создать Pydantic модели для chat API:

- `ChatMessage`: модель сообщения чата (role, content, sql_query?, timestamp)
- `ChatRequest`: запрос на отправку сообщения (message, mode, session_id?)
- `ChatResponse`: ответ от чата (message, sql_query?, timestamp)
- `AuthRequest`: запрос аутентификации для админ режима (password)
- `AuthResponse`: ответ аутентификации (token, expires_at)

### 2. Text2SQL Prompt (`src/api/text2sql_prompt.txt`)

Создать system prompt для преобразования вопросов в SQL запросы:

- Инструкции по генерации SQL для БД (tables: users, messages)
- Примеры запросов и соответствующих SQL
- Правила безопасности (только SELECT, никаких DROP/DELETE)
- Формат ответа: только чистый SQL без markdown

### 3. Chat Service (`src/api/chat_service.py`)

Реализовать сервис обработки чат-запросов:

- `ChatService` класс с методами:
        - `process_message(message, mode, user_id)` - основной метод обработки
        - `_process_normal_mode(message, user_id)` - обработка обычного режима
        - `_process_admin_mode(message, user_id)` - обработка админ режима с text2sql
        - `_execute_sql_query(sql)` - выполнение SQL и получение результатов
        - `_format_sql_results(results, sql)` - форматирование результатов для LLM
- Интеграция с `LLMClient` (повторно использовать из `src/bot/llm_client.py`)
- Интеграция с `DialogueManager` для сохранения истории
- Валидация SQL запросов (только SELECT)

### 4. Аутентификация (`src/api/auth.py`)

Простая аутентификация для админ режима:

- Проверка пароля из env variable `ADMIN_PASSWORD`
- Генерация JWT токена с TTL (1 час)
- Middleware для проверки токена

### 5. Chat Endpoints (`src/api/main.py`)

Добавить новые endpoints:

```python
POST /api/chat/message
  - body: {message: str, mode: "normal"|"admin", session_id: str}
  - requires: auth token для mode=admin
  - returns: {message: str, sql_query?: str, timestamp: str}

GET /api/chat/history
  - params: session_id
  - returns: [{role: str, content: str, timestamp: str}]

POST /api/chat/clear
  - params: session_id
  - returns: {status: "ok"}

POST /api/chat/auth
  - body: {password: str}
  - returns: {token: str, expires_at: str}
```

### 6. Виртуальный пользователь для веб-чата

- При старте API создавать виртуального пользователя с `telegram_id = -1` (Web Chat User)
- Использовать `session_id` из frontend как identifier для разных сессий
- Мэппинг: `session_id` → `user_id` (хранить в памяти или Redis в будущем)

## Frontend: Chat UI

### 7. Зависимости и hooks

Добавить из референса 21st-ai-chat.md:

- Установить: `lucide-react`, `@radix-ui/react-slot`, `class-variance-authority`
- Скопировать компоненты: `button.tsx`, `textarea.tsx` (если отличаются от текущих)
- Создать hook: `src/hooks/use-textarea-resize.ts`

### 8. UI компоненты (`src/components/ui/`)

Создать базовые UI компоненты из референса:

- `chat-input.tsx` - композитный компонент ввода сообщения
        - `ChatInput` - контейнер с context
        - `ChatInputTextArea` - textarea с auto-resize
        - `ChatInputSubmit` - кнопка отправки с loading state

### 9. Chat компоненты (`src/components/chat/`)

Реализовать компоненты чата:

**ChatButton.tsx** - floating button

- Круглая кнопка с иконкой чата в правом нижнем углу
- Индикатор непрочитанных сообщений (badge)
- onClick открывает ChatWindow
- z-index для отображения поверх контента

**ChatWindow.tsx** - раскрывающееся окно чата

- Размер: ~400x600px
- Позиция: правый нижний угол над ChatButton
- Анимация появления/скрытия
- Header с заголовком, ModeToggle, кнопкой закрытия
- Body с MessageList
- Footer с ChatInput
- Responsive: на mobile занимает весь экран

**MessageList.tsx** - список сообщений

- Автоскролл к последнему сообщению
- Infinite scroll для истории (опционально)
- Loading state при загрузке истории
- Empty state ("Начните диалог...")

**Message.tsx** - отдельное сообщение

- Вид зависит от role: user (справа), assistant (слева)
- Форматирование markdown (опционально)
- SQL блок (expandable) для admin mode
- Timestamp

**ModeToggle.tsx** - переключатель режимов

- Switch: Normal ↔ Admin
- При переключении на Admin - показать modal аутентификации
- Индикатор текущего режима (иконка, цвет)
- Показывать только если аутентифицирован в admin mode

**AuthModal.tsx** - модальное окно аутентификации

- Input для пароля
- Submit button
- Error state при неверном пароле
- Закрывается при успешной аутентификации

### 10. API Integration (`src/lib/api.ts`, `src/hooks/`)

Расширить API клиент:

```typescript
// src/lib/api.ts
export async function sendChatMessage(
  message: string, 
  mode: "normal" | "admin", 
  sessionId: string
): Promise<ChatResponse>

export async function getChatHistory(
  sessionId: string
): Promise<ChatMessage[]>

export async function clearChatHistory(
  sessionId: string
): Promise<void>

export async function authenticateAdmin(
  password: string
): Promise<AuthResponse>
```

Создать hooks:

```typescript
// src/hooks/useChat.ts
export function useChat(sessionId: string)
  - Управление состоянием чата (messages, loading, error)
  - Отправка сообщений через React Query mutation
  - Загрузка истории через React Query query
  - Автогенерация session_id (uuid)

// src/hooks/useChatAuth.ts
export function useChatAuth()
  - Управление аутентификацией админ режима
  - Хранение токена в localStorage
  - Проверка валидности токена
  - Auto logout при истечении
```

### 11. Типы (`src/types/chat.ts`)

Создать TypeScript типы:

```typescript
export type ChatMode = "normal" | "admin";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sql_query?: string;
  timestamp: string;
}

export interface ChatResponse {
  message: string;
  sql_query?: string;
  timestamp: string;
}
```

### 12. Интеграция в Dashboard (`src/app/page.tsx`)

- Добавить ChatButton в layout
- Position: fixed bottom-4 right-4
- ChatWindow управляется состоянием (open/closed)
- z-index для корректного наложения

## Тестирование

### 13. Backend тесты (`tests/api/`)

- `test_chat_service.py`:
        - Тестирование обычного режима
        - Тестирование админ режима с text2sql
        - Тестирование валидации SQL (только SELECT)
        - Тестирование обработки ошибок
- `test_chat_endpoints.py`:
        - Тестирование всех chat endpoints
        - Тестирование аутентификации
        - Тестирование прав доступа
- `test_auth.py`:
        - Тестирование JWT токенов
        - Тестирование проверки паролей

### 14. Frontend тесты (`frontend/app/src/`)

- `components/chat/*.test.tsx`:
        - Unit тесты всех компонентов чата
        - Интеграционные тесты ChatWindow
        - Тестирование переключения режимов
        - Тестирование аутентификации
- `hooks/*.test.ts`:
        - Тестирование useChat hook
        - Тестирование useChatAuth hook

## Документация

### 15. Документация и примеры

- Обновить `README.md` с описанием chat API
- Создать `frontend/doc/plans/s4-ai-chat-plan.md` с детальным отчетом
- Добавить примеры использования в `src/api/examples.http`
- Обновить `frontend/doc/frontend-roadmap.md` (статус F-Sprint-4: ✅ Completed)

## Makefile команды

### 16. Команды для разработки

```makefile
# Backend
api-chat-test: запуск тестов chat API

# Frontend  
frontend-chat-test: запуск тестов chat компонентов

# E2E
chat-e2e: запуск E2E тестов чата
```

## Ключевые файлы

**Backend:**

- `src/api/chat_models.py` - Pydantic модели
- `src/api/chat_service.py` - сервис обработки
- `src/api/text2sql_prompt.txt` - промпт для text2sql
- `src/api/auth.py` - аутентификация
- `src/api/main.py` - endpoints (изменения)

**Frontend:**

- `src/components/ui/chat-input.tsx` - базовый компонент ввода
- `src/components/chat/ChatButton.tsx` - floating button
- `src/components/chat/ChatWindow.tsx` - окно чата
- `src/components/chat/MessageList.tsx` - список сообщений
- `src/components/chat/Message.tsx` - отдельное сообщение
- `src/components/chat/ModeToggle.tsx` - переключатель режимов
- `src/components/chat/AuthModal.tsx` - аутентификация
- `src/hooks/useChat.ts` - hook для чата
- `src/hooks/useChatAuth.ts` - hook для аутентификации
- `src/lib/api.ts` - API клиент (расширение)
- `src/types/chat.ts` - типы
- `src/app/page.tsx` - интеграция в dashboard (изменения)

**Тесты:**

- `tests/api/test_chat_service.py`
- `tests/api/test_chat_endpoints.py`
- `tests/api/test_auth.py`
- `frontend/app/src/components/chat/*.test.tsx`
- `frontend/app/src/hooks/useChat.test.ts`

## Критерии успеха

- ✅ Floating button в правом нижнем углу дашборда
- ✅ Раскрывающийся чат с адаптивным дизайном
- ✅ Обычный режим: общение с LLM работает
- ✅ Режим администратора: text2sql → SQL → результат → ответ
- ✅ Аутентификация для админ режима работает
- ✅ История диалога сохраняется и отображается
- ✅ SQL запросы отображаются в expandable блоке
- ✅ Backend тесты: coverage ≥ 80%
- ✅ Frontend тесты: coverage ≥ 80%
- ✅ TypeScript: 0 errors
- ✅ ESLint: 0 errors

### To-dos

- [ ] Создать Pydantic модели для chat API (chat_models.py)
- [ ] Создать system prompt для text2sql (text2sql_prompt.txt)
- [ ] Реализовать ChatService с обработкой обычного и админ режимов
- [ ] Реализовать аутентификацию для админ режима (auth.py)
- [ ] Добавить chat endpoints в FastAPI (main.py)
- [ ] Написать тесты для chat service, endpoints и auth
- [ ] Установить зависимости и создать базовые hooks
- [ ] Создать ChatInput компоненты из референса
- [ ] Реализовать основные chat компоненты (ChatButton, ChatWindow, MessageList, Message)
- [ ] Реализовать ModeToggle и AuthModal компоненты
- [ ] Расширить API клиент и создать useChat, useChatAuth hooks
- [ ] Интегрировать чат в dashboard через floating button
- [ ] Написать unit и integration тесты для chat компонентов
- [ ] Обновить документацию и создать sprint report