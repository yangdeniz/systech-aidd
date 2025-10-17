# ADR-04: Выбор технологического стека для Frontend

## Статус
✅ Принято - 17 октября 2025

## Контекст

Необходимо выбрать технологический стек для разработки административной панели дашборда HomeGuru. Дашборд должен отображать статистику диалогов Telegram-бота, предоставлять визуализацию данных и в будущем интегрировать ИИ-чат для администратора.

**Требования:**
- Современный стек с хорошей экосистемой
- TypeScript для type safety
- Быстрая разработка UI компонентов
- Хорошая интеграция с REST API
- Поддержка графиков и визуализации
- Простота тестирования
- Оптимизация performance

## Решение

Выбран следующий технологический стек:

### Framework: Next.js 15

**Обоснование:**
- App Router для современной архитектуры с Server/Client Components
- Excellent TypeScript support из коробки
- Built-in optimization (images, fonts, code splitting)
- SEO-friendly (может пригодиться в будущем)
- Отличная документация и большое community
- File-based routing для простоты навигации
- API routes для будущих функций (если потребуется)

**Альтернативы:**
- **Vite + React**: Более легковесно, но нет SSR и встроенных оптимизаций
- **Create React App**: Устарел, не рекомендуется React team
- **Remix**: Хороший выбор, но меньше adoption и экосистема

### UI Library: shadcn/ui

**Обоснование:**
- Компоненты на базе Radix UI (accessibility из коробки)
- Копируемые компоненты (не npm-пакет) - полный контроль
- Полная кастомизация через Tailwind CSS
- Отличная документация с примерами
- Современный дизайн (New York style)
- Интеграция с TypeScript и React Query
- Рекомендуется Next.js community

**Альтернативы:**
- **Material-UI (MUI)**: Больше компонентов, но тяжелее и сложнее кастомизация
- **Chakra UI**: Хороший выбор, но меньше примеров для дашбордов
- **Ant Design**: Отличная библиотека, но специфичный дизайн

### Styling: Tailwind CSS 4

**Обоснование:**
- Utility-first подход для быстрой разработки
- Tree-shaking для минимального bundle size
- CSS variables для темизации
- Отличная интеграция с Next.js
- Консистентный дизайн через design tokens
- Responsive design из коробки

### State Management: React Context API + TanStack Query

**Обоснование:**
- **Context API** для простого глобального состояния (settings, theme)
- **TanStack Query (React Query)** для серверного состояния:
  - Автоматическое кеширование
  - Loading и error states из коробки
  - Оптимистичные обновления
  - Фоновое обновление данных
  - Отличная TypeScript поддержка
  - Меньше boilerplate чем Redux

**Альтернативы:**
- **Redux Toolkit**: Overkill для MVP, больше boilerplate
- **Zustand**: Хороший выбор, но React Query лучше для API данных
- **Jotai/Recoil**: Интересные, но меньше adoption

### HTTP Client: axios

**Обоснование:**
- Удобный API для HTTP запросов
- Автоматическая JSON трансформация
- Interceptors для обработки ошибок
- TypeScript support
- Проверенная временем библиотека

**Альтернативы:**
- **fetch**: Нативный, но меньше features
- **ky**: Современный, но меньше community

### Charts: Recharts

**Обоснование:**
- Рекомендуется shadcn/ui
- Declarative API (React-way)
- Responsive charts из коробки
- TypeScript support
- Достаточно примеров для area/line charts
- Легковесная библиотека

**Альтернативы:**
- **Chart.js**: Популярный, но императивный API
- **Victory**: Декларативный, но тяжелее
- **Visx (D3)**: Мощный, но сложнее для простых графиков

### Testing: Jest + React Testing Library

**Обоснование:**
- Industry standard для React testing
- Отличная интеграция с Next.js
- TypeScript support
- Хорошая документация
- Testing best practices (user-centric tests)

**Альтернативы:**
- **Vitest**: Быстрее, но меньше adoption для Next.js
- **Cypress/Playwright**: Хороши для E2E, но не для unit tests

### Package Manager: pnpm

**Обоснование:**
- Быстрее npm и yarn
- Эффективное использование дискового пространства
- Строгое разрешение зависимостей
- Отличная поддержка monorepos (на будущее)
- Рекомендуется Next.js community

## Последствия

### Положительные
- ✅ Быстрая разработка с shadcn/ui компонентами
- ✅ Type safety с TypeScript strict mode
- ✅ Отличный DX с Next.js + Tailwind
- ✅ Performance optimization из коробки
- ✅ SEO-friendly (если понадобится public dashboard)
- ✅ Простота тестирования с RTL
- ✅ Хорошая экосистема и community support
- ✅ Легкая интеграция с Backend API
- ✅ Minimal bundle size благодаря tree-shaking

### Отрицательные
- ⚠️ Кривая обучения Next.js App Router (новая концепция)
- ⚠️ shadcn/ui требует копирования компонентов (но это и плюс)
- ⚠️ Tailwind CSS может показаться многословным (но это субъективно)
- ⚠️ React Query добавляет абстракцию для простых запросов

### Риски и митigation
- **Риск**: Сложность Server/Client Components в Next.js
  - **Митigation**: Использовать Client Components для интерактивности, документация хорошая
- **Риск**: Обновления shadcn/ui требуют ручного копирования
  - **Митigation**: Обновлять компоненты только при необходимости
- **Риск**: Bundle size может вырасти с большим количеством компонентов
  - **Митigation**: Dynamic imports, code splitting, мониторинг bundle size

## Альтернативы (подробнее)

### 1. Vite + React + Material-UI
**За:**
- Быстрый dev server
- Больше готовых компонентов в MUI
- Проще для начинающих

**Против:**
- Нет SSR/SSG
- MUI тяжелее и сложнее кастомизация
- Меньше оптимизаций из коробки

### 2. Next.js + Chakra UI + Redux
**За:**
- Chakra UI хорошая библиотека
- Redux для сложного состояния

**Против:**
- Chakra UI тяжелее shadcn/ui
- Redux overkill для MVP
- Больше boilerplate

### 3. Remix + shadcn/ui + Zustand
**За:**
- Remix современный framework
- Zustand легковесный state manager

**Против:**
- Remix меньше adoption
- Меньше примеров и документации
- Сложнее найти разработчиков

## Метрики успеха

Решение считается успешным если:
- ✅ Development velocity высокая (компоненты быстро создаются)
- ✅ TypeScript errors = 0
- ✅ Test coverage ≥ 80%
- ✅ Bundle size оптимальный (< 300KB gzipped для initial load)
- ✅ Performance (Lighthouse score ≥ 90)
- ✅ Developer Experience положительный

## Пересмотр решения

Решение может быть пересмотрено если:
- Next.js App Router покажет критические проблемы
- shadcn/ui перестанет развиваться
- Появятся значительно лучшие альтернативы
- Performance станет проблемой

**Следующий пересмотр:** После F-Sprint-3 (реализация дашборда)

## Ссылки

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Recharts Documentation](https://recharts.org/)

## История изменений

| Дата | Версия | Изменения |
|------|--------|-----------|
| 2025-10-17 | 1.0 | Первоначальное решение для F-Sprint-2 |

---

**Автор:** AI Agent  
**Reviewers:** Development Team  
**Status:** ✅ Approved and Implemented

