# Frontend Roadmap проекта HomeGuru

## О Frontend

**Цель:** Разработка веб-интерфейса для административной панели HomeGuru с дашбордом статистики по диалогам и веб-чатом для администратора.

**Ключевые документы:**
- [🎯 vision.md](vision.md) - Техническое видение всего проекта
- [🗺️ roadmap.md](roadmap.md) - Основной roadmap проекта
- 💡 frontend/doc/frontend-vision.md - Видение frontend проекта *(планируется в F-Sprint-2)*

---

## Легенда статусов

| Иконка | Статус | Описание |
|--------|--------|----------|
| ⏳ | Pending | Спринт запланирован, работа не начата |
| 🚧 | In Progress | Спринт в активной разработке |
| ✅ | Completed | Спринт успешно завершен |
| 🔄 | On Hold | Спринт приостановлен |
| ❌ | Cancelled | Спринт отменен |

---

## Спринты Frontend разработки

| Код | Название | Статус | План спринта |
|-----|----------|--------|--------------|
| **F-Sprint-1** | Требования к дашборду и Mock API | ✅ Completed | [📋 F-Sprint-1 Plan](plans/s1-mock-api-plan.md) |
| **F-Sprint-2** | Инициализация Frontend проекта | ✅ Completed | [📋 F-Sprint-2 Plan](plans/s2-init-plan.md) |
| **F-Sprint-3** | Реализация dashboard | ✅ Completed | [📋 F-Sprint-3 Plan](plans/s3-dashboard-plan.md) |
| **F-Sprint-4** | Реализация ИИ-чата | ✅ Completed | [📋 F-Sprint-4 Plan](plans/s4-ai-chat-plan.md) |
| **F-Sprint-5** | Переход с MockAPI на реальный API | ✅ Completed | [📋 F-Sprint-5 Plan](plans/s5-real-api-plan.md) |
| **F-Sprint-6** | Аутентификация и RBAC | ⏳ Pending | [📋 F-Sprint-6 Plan](plans/s6-auth-rbac-plan.md) |

---

## F-Sprint-1: Требования к дашборду и Mock API

### Цель
Сформировать функциональные требования к дашборду статистики диалогов и создать Mock API для разработки frontend без зависимости от бэкенда.

### Состав работ
**Проектирование:**
- Формирование емких и лаконичных функциональных требований к дашборду для статистики по диалогам
- Проектирование контракта API для фронтенда (KISS подход - один метод для статистики)
- Проектирование интерфейса реализации сбора статистики (StatCollector) с 2 реализациями: Mock и Real

**Реализация Mock API:**
- Реализация Mock реализации StatCollector
- Создание entrypoint для запуска API
- Автоматическая генерация документации API

**Инфраструктура:**
- Создание команд запуска API
- Создание команд тестирования получения статистики по диалогам

---

## F-Sprint-2: Каркас frontend проекта

### Цель
Создать фундамент frontend проекта с выбором технологического стека, структурой проекта и настройкой инструментов разработки.

### Состав работ
**Концепция и vision:**
- Генерация концепции frontend проекта
- Определение требований к пользовательскому интерфейсу
- Создание документа frontend/doc/frontend-vision.md (аналог vision.md)

**Технологический стек:**
- Анализ современных frontend технологий
- Выбор оптимального набора технологий (framework, UI библиотека, state management, build tools)
- Документирование решений (ADR)

**Инфраструктура:**
- Создание структуры проекта
- Настройка инструментов разработки (линтеры, форматтеры, тесты)
- Создание команд запуска и проверки качества
- Настройка CI/CD pipeline для frontend

---

## F-Sprint-3: Реализация dashboard ✅

### Цель
Разработать дашборд статистики по диалогам с интеграцией Mock API для отображения данных.

### Состав работ
**UI компоненты:** ✅
- Реализация dashboard на основе референса и требований из F-Sprint-1
- Разработка компонентов визуализации статистики (графики, таблицы, метрики)
- Адаптивный дизайн для различных устройств
- Темизация Light/Dark с переключателем

**Интеграция:** ✅
- Интеграция с Mock API из F-Sprint-1
- Настройка API клиента для взаимодействия с backend
- Управление состоянием данных статистики через React Query

**Тестирование:** ✅
- Unit тесты компонентов (29 тестов)
- Интеграционное тестирование с Mock API
- Coverage: 78.77%
- Quality checks: TypeScript, ESLint, Prettier

### Результаты
- ✅ 4 компонента dashboard: MetricCard, ActivityChart, RecentDialogues, TopUsers
- ✅ ThemeToggle с Light/Dark темами
- ✅ Responsive design для mobile/tablet/desktop
- ✅ Динамическое форматирование дат (HH:mm для Day, yyyy-MM-dd для Week/Month)
- ✅ 29 unit/integration тестов, все проходят
- ✅ shadcn/ui компоненты с кастомизацией (cursor-pointer)

[Подробный отчет](plans/s3-dashboard-plan.md)

---

## F-Sprint-4: Реализация ИИ-чата ✅

### Цель
Разработать веб-интерфейс ИИ-чата для администратора с возможностью задавать вопросы по статистике диалогов через естественный язык и общаться с HomeGuru LLM.

### Состав работ
**Backend API для чата:** ✅
- Реализация Chat API endpoints (auth, message, history, clear)
- Интеграция text2sql подхода (вопрос → SQL → выполнение → LLM → ответ)
- Обработка двух режимов: Normal (HomeGuru) и Admin (статистика)
- JWT аутентификация для админ режима
- Валидация SQL (только SELECT)

**UI чата:** ✅
- Floating button в правом нижнем углу дашборда
- Раскрывающееся окно чата с адаптивным дизайном
- Компоненты: ChatButton, ChatWindow, MessageList, Message
- ModeToggle для переключения между режимами
- AuthModal для аутентификации админов
- Expandable SQL блоки для отладки

**API Integration:** ✅
- useChat hook для управления состоянием
- useChatAuth hook для аутентификации
- Расширен API клиент (sendChatMessage, getChatHistory, и др.)
- Session ID генерация и маппинг на backend

**Тестирование:** ✅
- 58+ backend тестов (ChatService, Auth, Endpoints)
- TypeScript: 0 errors
- ESLint: 0 errors
- Frontend build успешен

**Референсы:**
- [Референс компонента чата от 21st.dev](references/21st-ai-chat.md) - использован для UI чата

### Результаты
- ✅ Полнофункциональный веб-чат с LLM
- ✅ Два режима: Normal и Admin
- ✅ Text2SQL pipeline для админ режима
- ✅ JWT аутентификация
- ✅ История диалогов сохраняется
- ✅ SQL запросы отображаются для отладки
- ✅ 58+ backend тестов

[Подробный отчет](plans/s4-ai-chat-plan.md)

---

## F-Sprint-5: Переход с MockAPI на реальный API ✅

### Цель
Заменить Mock реализацию StatCollector на реальную с интеграцией базы данных и переключить frontend на использование production API.

### Состав работ
**Реальный StatCollector:** ✅
- Реализация Real реализации StatCollector с PostgreSQL
- Интеграция с базой данных через SQLAlchemy async ORM
- Оптимизация SQL-запросов для сбора статистики
- Кэширование данных статистики (in-memory, TTL 60 секунд)

**Интеграция:** ✅
- Factory pattern для переключения Mock/Real через env var
- Настройка конфигурации через `COLLECTOR_MODE` environment variable
- API клиент на frontend без изменений (обратная совместимость)

**Тестирование и деплой:** ✅
- 32 новых unit теста для Real collector, cache, config
- Performance тестирование (кэш дает 50-200x ускорение)
- Документация и sprint report

### Результаты
- ✅ RealStatCollector с оптимизированными SQL запросами
- ✅ In-memory cache с TTL (60 секунд)
- ✅ Factory pattern: легкое переключение Mock ↔ Real
- ✅ Новые Makefile команды: `api-run-real`, `api-info`, `api-clear-cache`
- ✅ 100% обратная совместимость API
- ✅ Production-ready deployment

[Подробный отчет](plans/s5-real-api-plan.md)

---

## F-Sprint-6: Аутентификация и RBAC ✅

### Цель
Внедрить систему аутентификации с ролевым доступом (Role-Based Access Control) для разделения функционала между обычными пользователями и администраторами.

### Состав работ
**Система аутентификации:** ✅
- Страницы login и register
- Регистрация новых пользователей
- Валидация пароля и получение роли пользователя
- Сохранение сессии в localStorage с JWT
- Автоматическая проверка и валидация токена
- Кнопка "Logout" с очисткой сессии

**Роли пользователей:** ✅
- Роль `user`: доступ к чату в обычном режиме
- Роль `administrator`: доступ к дашбордам
- Seed администратора через миграцию
- RBAC middleware для проверки прав доступа

**UI для роли User:** ✅
- Чат отображается full-screen при входе
- Только обычный режим чата (Normal mode)
- Кнопка смены темы и "Logout"
- Компактный header

**UI для роли Administrator:** ✅
- Dashboard отображается при входе (главная страница)
- Header с username, theme toggle и logout
- Защищенный доступ к статистике

**Backend интеграция:** ✅
- API endpoints: POST `/api/auth/register`, POST `/api/auth/login`, GET `/api/auth/verify`, POST `/api/auth/logout`
- JWT tokens с TTL 30 дней
- RBAC middleware защищает `/stats` endpoint
- bcrypt для hashing паролей
- Единая таблица users для Telegram и Web пользователей

**Рефакторинг:** ✅
- Реорганизация структуры страниц (route groups)
- Role-based routing в main page
- Отдельные layouts для user и administrator
- API client с auth interceptors
- AuthContext для управления состоянием

### Результаты
- ✅ Полноценная система аутентификации с регистрацией и login
- ✅ RBAC с ролями user/administrator
- ✅ JWT tokens с TTL 30 дней
- ✅ Персонализированный UI для каждой роли
- ✅ Protected endpoints (/stats требует admin)
- ✅ Auth interceptors в API client
- ✅ bcrypt для паролей (rounds=12)
- ✅ Единая таблица users (user_type: telegram/web)
- ✅ Seed администратора через миграцию

[Подробный отчет](../docs/plans/f-sprint-6-auth-rbac.md)

---

## История изменений

| Дата | Версия | Изменения |
|------|--------|-----------|
| 2025-10-17 | 1.7 | F-Sprint-6 завершен. Аутентификация с JWT, RBAC (user/administrator), login/register pages, protected routes |
| 2025-10-17 | 1.6 | Добавлен F-Sprint-6: Аутентификация и RBAC. Планирование системы с ролями user/administrator |
| 2025-10-17 | 1.5 | F-Sprint-4 завершен. Веб-чат с LLM (Normal и Admin режимы), JWT auth, text2sql, 58+ тестов |
| 2025-10-17 | 1.4 | F-Sprint-3 завершен. Dashboard с метриками, графиками, таблицами и темизацией (Light/Dark) |
| 2025-10-17 | 1.3 | F-Sprint-5 завершен. Real API с PostgreSQL, кэширование, factory pattern Mock/Real |
| 2025-10-17 | 1.2 | F-Sprint-2 завершен. Инициализирован Next.js проект с TypeScript, shadcn/ui, React Query |
| 2025-10-17 | 1.1 | F-Sprint-1 завершен. Создан Mock API с документацией, тестами и примерами |
| 2025-10-17 | 1.0 | Создание frontend roadmap. Планирование спринтов F-Sprint-1 до F-Sprint-5 |


