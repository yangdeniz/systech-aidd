<!-- b4751b1f-7b41-4ed9-89f0-994470abc04f f384208b-a3b6-44bd-ac3a-ba1a01c50f4f -->
# F-Sprint-6: Аутентификация и RBAC (Одна таблица users)

## Обзор

Создать production-ready систему аутентификации с RBAC для разделения функционала между обычными пользователями (user) и администраторами (administrator). Используется единая таблица `users` для Telegram и веб-пользователей с разделением по полю `user_type`.

## Backend: Расширение таблицы users

### 1. Расширение модели User

**Файл:** `src/bot/models.py`

Добавить новые поля:

- `user_type` (enum: "telegram", "web", NOT NULL, default="telegram")
- `password_hash` (String(255), nullable) - только для web users
- `role` (enum: "user", "administrator", nullable) - только для web users
- `last_login` (DateTime, nullable) - для web users

Изменить существующие:

- `telegram_id` → nullable (NULL для web users)
- `username` остается nullable (есть у обоих типов)

### 2. Database Migration

**Команда:** `make db-revision MSG='extend users for web auth'`

Миграция:

- Добавить enum `UserType` и `UserRole`
- Добавить поля: `user_type`, `password_hash`, `role`, `last_login`
- Изменить `telegram_id` constraint на nullable
- Обновить существующие записи: SET `user_type = 'telegram'`
- Добавить CHECK constraint для валидации типов пользователей
- Создать unique partial index на `(username)` WHERE `user_type='web'`
- Seed: создать администратора (username/password из env, `user_type='web'`, `role='administrator'`)

**Environment:** `ADMIN_USERNAME`, `ADMIN_PASSWORD`

### 3. Auth Service

**Новый файл:** `src/api/auth_service.py`

Функции:

- `hash_password(password: str) -> str` - bcrypt с rounds=12
- `verify_password(password: str, hash: str) -> bool`
- `authenticate_web_user(username: str, password: str, session) -> User | None`
- `create_session_token(user: User) -> tuple[str, datetime]` - JWT (30 дней)
- `verify_session_token(token: str) -> dict[str, Any]`

### 4. API Endpoints

**Файл:** `src/api/main.py`

**POST /api/auth/register**

- Body: `{username, password, first_name?}`
- Validate: username уникален, password минимум 8 символов
- Create: новый web user с `role='user'`, `user_type='web'`
- Response: `{token, expires_at, role, username, user_id}` (автоматический login)
- HTTP 400: username уже занят или слабый пароль

**POST /api/auth/login**

- Body: `{username, password}`
- Validate: web user с правильным паролем
- Update: `last_login = now()`
- Response: `{token, expires_at, role, username, user_id}`
- JWT payload: `{user_id, username, role, user_type, exp}`

**GET /api/auth/verify**

- Header: Authorization Bearer
- Validate JWT token
- Response: `{valid: true, user_id, username, role}`

**POST /api/auth/logout**

- Response: `{status: "ok"}` (клиент удаляет token)

### 5. Middleware для RBAC

**Новый файл:** `src/api/middleware.py`

Dependencies:

- `get_current_web_user(token: HTTPBearer, session) -> User` - извлекает web user
- `require_admin(user: User = Depends(get_current_web_user))` - проверяет role='administrator'

Применение:

```python
@app.get("/stats", dependencies=[Depends(require_admin)])
```

### 6. Обновление существующих endpoints

**Файл:** `src/api/main.py`

- `/stats` - добавить `Depends(require_admin)`
- `/api/chat/message` - для admin mode требовать admin role
- Удалить старую логику с `ADMIN_PASSWORD` из `src/api/auth.py`
- Обновить chat service для работы с web users по `user.id`

### 7. Обновление ChatService

**Файл:** `src/api/main.py` (chat logic)

- При login сохранять `session_id → user.id` маппинг
- Убрать логику с `get_or_create_web_user_id`
- ChatService использует `user.id` напрямую из authenticated user
- Сообщения сохраняются с `messages.user_id = user.id`

### 8. Backend Testing

**Новые файлы:**

- `tests/api/test_auth_service.py` - hash, verify, authenticate (8 тестов)
- `tests/api/test_web_auth_endpoints.py` - login, verify, logout (10 тестов)
- `tests/api/test_rbac_middleware.py` - dependencies, admin access (7 тестов)

Минимум 25 backend тестов.

## Frontend: Login и Protected Routes

### 9. Auth Context

**Новый файл:** `frontend/app/src/contexts/AuthContext.tsx`

State:

- `user: {user_id, username, role, token} | null`
- `isLoading: boolean`

Methods:

- `login(username, password): Promise<void>`
- `logout(): void`
- `verifyAndRestoreSession(): Promise<void>`

Storage: localStorage keys `auth_token`, `auth_user`

**Hook:** `frontend/app/src/hooks/useAuth.ts`

### 10. Login Page

**Новый файл:** `frontend/app/src/app/login/page.tsx`

UI:

- Center card с формой
- Username + Password inputs
- Submit button (loading state)
- Error display
- Ссылка "Нет аккаунта? Зарегистрироваться" → `/register`
- ThemeToggle в header

Logic:

- Submit → API login → save token → redirect by role
- Admin → `/admin/dashboard`
- User → `/user/chat`

### 11. Register Page

**Новый файл:** `frontend/app/src/app/register/page.tsx`

UI:

- Center card с формой регистрации
- Username input (с валидацией уникальности)
- Password input (минимум 8 символов)
- Confirm Password input (должен совпадать)
- First Name input (опционально)
- Submit button (loading state)
- Error/Success display
- Ссылка "Уже есть аккаунт? Войти" → `/login`
- ThemeToggle в header

Validation:

- Username: 3-50 символов, только буквы, цифры, underscore
- Password: минимум 8 символов
- Password confirmation: должен совпадать с password

Logic:

- Submit → API register → автоматический login → save token → redirect `/user/chat`
- Все новые пользователи получают role='user'
- HTTP 400: показать ошибку (username занят, слабый пароль)

### 12. Protected Routes

**Новый компонент:** `frontend/app/src/components/auth/ProtectedRoute.tsx`

Props: `allowedRoles?: string[]`

Logic:

- Проверяет auth token
- Если нет → redirect `/login`
- Если роль не подходит → redirect `/unauthorized`

### 13. Layout для User

**Route group:** `frontend/app/src/app/(user)/`

**Layout:** `(user)/layout.tsx`

- Compact header: title, ThemeToggle, username, Logout
- No sidebar
- Full height content

**Page:** `(user)/chat/page.tsx`

- ChatWindow открыт всегда (full screen)
- Только Normal mode
- No ModeToggle

### 13. Layout для Administrator

**Route group:** `frontend/app/src/app/(admin)/`

**Layout:** `(admin)/layout.tsx`

- Sidebar navigation:
  - "Аналитика" → `/admin/dashboard`
  - "Чат" → `/admin/chat`
- Header: ThemeToggle, username, Logout
- Mobile: hamburger menu

**Pages:**

- `(admin)/dashboard/page.tsx` - переместить текущий dashboard
- `(admin)/chat/page.tsx` - чат full screen, admin mode

### 14. Рефакторинг главной страницы

**Файл:** `frontend/app/src/app/page.tsx`

Redirect logic:

- No auth → `/login`
- role='user' → `/user/chat`
- role='administrator' → `/admin/dashboard`

**Удалить:**

- `<ChatButton>` компонент (теперь не нужен)
- `<ChatWindow>` из page.tsx (перенесен в routes)

### 15. Theme Persistence

**Файл:** `frontend/app/src/components/providers/ThemeProvider.tsx`

Добавить:

- Save theme в `localStorage.theme_preference`
- Restore on mount
- Sync между компонентами

### 16. API Client с Auth

**Файл:** `frontend/app/src/lib/api.ts`

Axios interceptors:

- Request: добавлять `Authorization: Bearer <token>` из localStorage
- Response 401: logout + redirect `/login`

Новые функции:

- `loginUser(username, password)` → POST /api/auth/login
- `verifyAuthToken()` → GET /api/auth/verify
- `logoutUser()` → POST /api/auth/logout

### 17. Frontend Tests

**Файлы:**

- `frontend/app/src/app/login/page.test.tsx` (5 тестов)
- `frontend/app/src/contexts/AuthContext.test.tsx` (8 тестов)
- `frontend/app/src/components/auth/ProtectedRoute.test.tsx` (5 тестов)

Минимум 18 frontend тестов.

## Infrastructure

### 18. Environment Variables

**Файл:** `.env.example` (создать)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/homeguru

# Admin seed
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_in_production

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_DAYS=30

# API
COLLECTOR_MODE=real
OPENROUTER_API_KEY=your-key
```

### 19. Makefile Commands

**Новые команды:**

- `make db-create-web-user USERNAME=... PASSWORD=... ROLE=...` - создать web user
- `make db-list-web-users` - список web users

### 20. Documentation

**Файл:** `docs/plans/f-sprint-6-auth-rbac.md`

Sections:

- Архитектура одной таблицы
- Обоснование решения
- Примеры использования
- Security considerations
- Testing coverage

**Update:** `frontend/doc/frontend-roadmap.md` - статус ✅

## Архитектурные решения

### Database Design

**Одна таблица users:**

- `user_type` различает Telegram vs Web
- Telegram: `telegram_id` NOT NULL, `password_hash` NULL
- Web: `telegram_id` NULL, `password_hash` NOT NULL
- CHECK constraint обеспечивает консистентность
- Partial unique index на `username` для web users

**Преимущества:**

- Простая связь с messages через `user_id = users.id`
- Единая статистика по всем пользователям
- Меньше кода, один репозиторий

**Компромиссы:**

- Nullable поля требуют валидации
- CHECK constraints для безопасности
- Условная логика в коде по `user_type`

### Security

- bcrypt rounds=12
- JWT 30 дней
- Partial index на username (только web)
- Password hash изолирован проверками

### Frontend Architecture

- Next.js App Router с route groups
- React Context для auth state
- localStorage для persistence
- Protected routes с role checking

## Критерии завершения

- ✅ Таблица users расширена (user_type, password_hash, role)
- ✅ Миграция с CHECK constraints и seed админа
- ✅ Auth service с bcrypt и JWT
- ✅ Login/verify/logout endpoints
- ✅ RBAC middleware на /stats
- ✅ ChatService интегрирован с web users
- ✅ Login page реализована
- ✅ AuthContext работает
- ✅ Protected routes по ролям
- ✅ User layout: chat only
- ✅ Admin layout: sidebar + dashboard + chat
- ✅ Theme persistence
- ✅ 43+ тестов (25 backend + 18 frontend)
- ✅ Документация завершена

### To-dos

- [ ] Создать модель WebUser и миграцию с seed данными администратора
- [ ] Реализовать auth_service.py с bcrypt и JWT функциями
- [ ] Добавить API endpoints для login/verify/logout
- [ ] Создать RBAC middleware и защитить существующие endpoints
- [ ] Написать тесты для auth service, endpoints и middleware (20+ тестов)
- [ ] Создать AuthContext и useAuth hook
- [ ] Реализовать страницу логина с формой
- [ ] Создать ProtectedRoute компонент для защиты маршрутов
- [ ] Создать layout и страницу с чатом для role=user
- [ ] Создать layout с sidebar и страницы для role=administrator
- [ ] Рефакторинг главной страницы и удаление floating chat для админа
- [ ] Обновить API client с auth interceptors и новыми функциями
- [ ] Добавить сохранение темы в localStorage
- [ ] Написать тесты для auth flow и компонентов (15+ тестов)
- [ ] Создать sprint report и обновить roadmap