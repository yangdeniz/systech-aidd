<!-- fafce97a-57ef-4e94-bb66-b419107381bc d5ff97ee-5649-4549-99d0-796b6954c093 -->
# F-Sprint-2: Инициализация Frontend проекта

## Цель

Создать фундамент frontend проекта с Next.js, TypeScript, shadcn/ui, Tailwind CSS и настроить инструменты разработки для последующей реализации дашборда.

## Технологический стек

**Framework & Language:**

- Next.js 15 (App Router)
- React 19
- TypeScript 5.x

**UI & Styling:**

- shadcn/ui (компонентная библиотека)
- Tailwind CSS (утилитарные стили)
- Radix UI (примитивы для shadcn/ui)

**State & Data:**

- React Context API (глобальное состояние)
- TanStack Query (React Query) для серверного состояния и кеширования

**Testing & Quality:**

- Jest + React Testing Library
- ESLint (Next.js config + TypeScript)
- Prettier (форматтер)

**Charts:**

- Recharts (рекомендуется shadcn/ui)

**Package Manager:**

- pnpm

## Структура задач

### 1. Инициализация Next.js проекта

**Расположение:** `frontend/app/` (Next.js App Router структура)

**Действия:**

```bash
cd frontend
pnpm create next-app@latest app --typescript --tailwind --app --src-dir --import-alias "@/*" --no-git
```

**Параметры:**

- `--typescript` - TypeScript
- `--tailwind` - Tailwind CSS
- `--app` - App Router (не Pages Router)
- `--src-dir` - использовать src/ директорию
- `--import-alias "@/*"` - алиасы для импортов
- `--no-git` - не инициализировать git (уже есть в корне)

**Результат:**

```
frontend/app/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   └── lib/
├── public/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── postcss.config.mjs
└── .eslintrc.json
```

### 2. Установка shadcn/ui

**Инициализация:**

```bash
cd frontend/app
pnpm dlx shadcn@latest init
```

**Конфигурация при инициализации:**

- Style: New York (более современный)
- Base color: Slate
- CSS variables: Yes (для темизации)

**Установка необходимых компонентов для дашборда:**

```bash
pnpm dlx shadcn@latest add card
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add tabs
pnpm dlx shadcn@latest add table
pnpm dlx shadcn@latest add skeleton
```

**Результат:**

- `src/components/ui/` - компоненты shadcn/ui
- `src/lib/utils.ts` - утилиты (cn() для className)
- Обновленный `tailwind.config.ts` с темами

### 3. Настройка зависимостей

**Установка дополнительных библиотек:**

```bash
cd frontend/app

# State Management & Data Fetching
pnpm add @tanstack/react-query axios

# Charts
pnpm add recharts

# Date utilities
pnpm add date-fns

# Development
pnpm add -D @types/node @types/react @types/react-dom
```

### 4. Конфигурация TypeScript

**Обновление `tsconfig.json`:**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowJs": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "incremental": true,
    "forceConsistentCasingInFileNames": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "plugins": [
      {
        "name": "next"
      }
    ]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 5. Настройка инструментов качества

**Prettier конфигурация (`frontend/app/.prettierrc.json`):**

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

**Prettier ignore (`frontend/app/.prettierignore`):**

```
node_modules
.next
out
dist
coverage
.pnpm-store
```

**ESLint конфигурация (обновить `.eslintrc.json`):**

```json
{
  "extends": [
    "next/core-web-vitals",
    "next/typescript",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

**Установка Prettier плагина:**

```bash
cd frontend/app
pnpm add -D prettier eslint-config-prettier
```

### 6. Настройка Jest + React Testing Library

**Установка зависимостей:**

```bash
cd frontend/app
pnpm add -D jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom @types/jest
```

**Jest конфигурация (`frontend/app/jest.config.js`):**

```js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/app/layout.tsx',
  ],
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
```

**Jest setup (`frontend/app/jest.setup.js`):**

```js
import '@testing-library/jest-dom'
```

### 7. Структура проекта

**Создать следующую структуру:**

```
frontend/app/src/
├── app/
│   ├── layout.tsx              # Root layout с providers
│   ├── page.tsx                # Главная страница (дашборд)
│   ├── globals.css             # Глобальные стили
│   └── api/                    # (опционально) API routes
├── components/
│   ├── ui/                     # shadcn/ui компоненты (auto-generated)
│   ├── dashboard/              # Компоненты дашборда
│   │   ├── MetricCard.tsx
│   │   ├── ActivityChart.tsx
│   │   ├── RecentDialogues.tsx
│   │   └── TopUsers.tsx
│   ├── layout/                 # Layout компоненты
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   └── providers/              # Context providers
│       └── QueryProvider.tsx
├── lib/
│   ├── utils.ts                # Утилиты (cn() и др.)
│   ├── api.ts                  # API клиент (axios)
│   └── constants.ts            # Константы приложения
├── types/
│   ├── api.ts                  # Типы для API (из backend models)
│   └── dashboard.ts            # Типы для дашборда
└── hooks/
    ├── useStats.ts             # Хук для получения статистики
    └── usePeriod.ts            # Хук для управления периодом
```

### 8. API клиент и типы

**`src/types/api.ts`** - Типы из backend (src/api/models.py):

```typescript
export interface MetricCard {
  title: string;
  value: string | number;
  change_percent: number;
  description: string;
}

export interface TimeSeriesPoint {
  date: string; // ISO format
  value: number;
}

export interface DialogueInfo {
  user_id: number;
  username: string | null;
  message_count: number;
  last_message_at: string; // ISO datetime
}

export interface TopUser {
  user_id: number;
  username: string | null;
  total_messages: number;
  dialogue_count: number;
}

export interface StatsResponse {
  metrics: MetricCard[];
  time_series: TimeSeriesPoint[];
  recent_dialogues: DialogueInfo[];
  top_users: TopUser[];
}

export type Period = "day" | "week" | "month";
```

**`src/lib/api.ts`** - API клиент:

```typescript
import axios from "axios";
import type { StatsResponse, Period } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function getStats(period: Period): Promise<StatsResponse> {
  const response = await apiClient.get<StatsResponse>("/stats", {
    params: { period },
  });
  return response.data;
}

export default apiClient;
```

**`.env.local`** - Environment variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 9. React Query Provider

**`src/components/providers/QueryProvider.tsx`:**

```typescript
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 минута
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

**Обновить `src/app/layout.tsx`:**

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "HomeGuru Dashboard",
  description: "Admin dashboard for HomeGuru bot statistics",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
```

### 10. Базовые хуки

**`src/hooks/useStats.ts`:**

```typescript
import { useQuery } from "@tanstack/react-query";
import { getStats } from "@/lib/api";
import type { Period } from "@/types/api";

export function useStats(period: Period) {
  return useQuery({
    queryKey: ["stats", period],
    queryFn: () => getStats(period),
  });
}
```

### 11. Простая главная страница

**`src/app/page.tsx`:**

```typescript
"use client";

import { useState } from "react";
import { useStats } from "@/hooks/useStats";
import type { Period } from "@/types/api";

export default function HomePage() {
  const [period, setPeriod] = useState<Period>("week");
  const { data, isLoading, error } = useStats(period);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading stats</div>;

  return (
    <main className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">HomeGuru Dashboard</h1>
      <div className="space-y-4">
        <div>
          <label>Period: </label>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value as Period)}
            className="ml-2 p-2 border rounded"
          >
            <option value="day">Day</option>
            <option value="week">Week</option>
            <option value="month">Month</option>
          </select>
        </div>
        <pre className="bg-gray-100 p-4 rounded overflow-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </main>
  );
}
```

### 12. Команды в package.json

**Обновить `frontend/app/package.json`:**

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
    "test": "jest --watch",
    "test:ci": "jest --ci --coverage",
    "test:coverage": "jest --coverage",
    "typecheck": "tsc --noEmit",
    "quality": "pnpm run format:check && pnpm run lint && pnpm run typecheck && pnpm run test:ci"
  }
}
```

### 13. Команды в Makefile (корневой)

**Добавить в `Makefile` (корень проекта):**

```makefile
# Frontend commands
.PHONY: frontend-install frontend-dev frontend-build frontend-test frontend-lint frontend-format frontend-quality

frontend-install:
	@echo "Installing frontend dependencies..."
	cd frontend/app && pnpm install

frontend-dev:
	@echo "Starting frontend development server..."
	cd frontend/app && pnpm run dev

frontend-build:
	@echo "Building frontend for production..."
	cd frontend/app && pnpm run build

frontend-test:
	@echo "Running frontend tests..."
	cd frontend/app && pnpm run test:ci

frontend-lint:
	@echo "Linting frontend code..."
	cd frontend/app && pnpm run lint

frontend-format:
	@echo "Formatting frontend code..."
	cd frontend/app && pnpm run format

frontend-quality:
	@echo "Running frontend quality checks..."
	cd frontend/app && pnpm run quality

# Combined quality check (backend + frontend)
quality-all: quality frontend-quality
	@echo "All quality checks passed!"
```

### 14. Документация

**`frontend/doc/frontend-vision.md`** - Видение frontend проекта (аналог vision.md для backend):

```markdown
# Техническое видение Frontend проекта HomeGuru

## 1. Технологии
- Next.js 15 (App Router)
- React 19
- TypeScript 5.x
- shadcn/ui + Tailwind CSS
- TanStack Query (React Query)
- Jest + React Testing Library
- Recharts

## 2. Принципы разработки
- KISS (Keep It Simple, Stupid)
- Component-based architecture
- Type Safety (strict TypeScript)
- Testing (Jest + RTL, coverage ≥ 80%)
- Responsive design (mobile-first)

## 3. Структура проекта
[Описание структуры]

## 4. Архитектура
[Диаграммы и описание]

## 5. API Integration
[Описание интеграции с Mock API]

## 6. State Management
- React Context API для глобального состояния
- TanStack Query для серверных данных

## 7. Styling Strategy
- Tailwind CSS для утилитарных классов
- shadcn/ui компоненты
- CSS variables для темизации

## 8. Testing Strategy
[Описание стратегии тестирования]

## 9. Quality Standards
- TypeScript strict mode
- ESLint + Prettier
- Test coverage ≥ 80%
- No console.log в production
```

**`docs/addrs/ADR-03.md`** - Архитектурное решение о выборе frontend стека:

```markdown
# ADR-03: Выбор технологического стека для Frontend

## Статус
Принято - 2025-10-17

## Контекст
Необходимо выбрать технологический стек для разработки административной панели дашборда HomeGuru.

## Решение

**Framework:** Next.js 15
- App Router для современной архитектуры
- Server Components для оптимизации
- Excellent TypeScript support
- Built-in optimization

**UI Library:** shadcn/ui
- Компоненты на базе Radix UI
- Копируемые компоненты (не npm-пакет)
- Полная кастомизация
- Отличная документация

**State Management:** React Context API + TanStack Query
- Context API для простого глобального состояния
- React Query для серверных данных и кеширования
- No Redux overhead для MVP

**Testing:** Jest + React Testing Library
- Industry standard
- Отличная интеграция с Next.js
- Поддержка TypeScript

**Charts:** Recharts
- Рекомендуется shadcn/ui
- Declarative API
- Responsive

## Последствия

**Положительные:**
- Быстрая разработка с shadcn/ui
- Type safety с TypeScript
- Отличный DX с Next.js
- SEO-friendly (если понадобится)

**Отрицательные:**
- Кривая обучения Next.js App Router
- shadcn/ui требует копирования компонентов

## Альтернативы
- Vite + React (легковесность, но нет SSR)
- Material-UI (больше компонентов, но тяжелее)
- Redux (overkill для MVP)
```

### 15. Тестирование установки

**Создать простой тест (`frontend/app/src/app/page.test.tsx`):**

```typescript
import { render, screen } from "@testing-library/react";
import HomePage from "./page";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

describe("HomePage", () => {
  it("renders dashboard title", () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <HomePage />
      </QueryClientProvider>
    );
    expect(screen.getByText(/HomeGuru Dashboard/i)).toBeInTheDocument();
  });
});
```

### 16. Обновление frontend roadmap

**Обновить `frontend/doc/frontend-roadmap.md`:**

- Изменить статус F-Sprint-2 с "⏳ Pending" на "✅ Completed"
- Добавить ссылку на план: `[📋 F-Sprint-2 Plan](plans/s2-init-plan.md)`
- Обновить секцию "История изменений"

### 17. Создание отчета о спринте

**Создать `frontend/doc/plans/s2-init-plan.md`** - копию этого плана

**Создать `docs/plans/f-sprint-2-init.md`** - отчет о выполнении спринта с результатами

## Итоговая структура файлов

```
frontend/
├── doc/
│   ├── dashboard-requirements.md
│   ├── frontend-vision.md            # ✨ NEW
│   ├── frontend-roadmap.md           # UPDATED
│   ├── frontend-reference.PNG
│   └── plans/
│       ├── s1-mock-api-plan.md
│       └── s2-init-plan.md           # ✨ NEW
└── app/                               # ✨ NEW Next.js project
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx
    │   │   └── globals.css
    │   ├── components/
    │   │   ├── ui/                   # shadcn/ui
    │   │   ├── dashboard/            # Dashboard components
    │   │   ├── layout/               # Layout components
    │   │   └── providers/            # Providers
    │   ├── lib/
    │   │   ├── utils.ts
    │   │   ├── api.ts
    │   │   └── constants.ts
    │   ├── types/
    │   │   ├── api.ts
    │   │   └── dashboard.ts
    │   └── hooks/
    │       ├── useStats.ts
    │       └── usePeriod.ts
    ├── public/
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── next.config.ts
    ├── .eslintrc.json
    ├── .prettierrc.json
    ├── jest.config.js
    ├── jest.setup.js
    └── .env.local

docs/
├── addrs/
│   ├── ADR-01.md
│   ├── ADR-02.md
│   └── ADR-03.md                     # ✨ NEW
└── plans/
    ├── f-sprint-1-mock-api.md
    └── f-sprint-2-init.md            # ✨ NEW

Makefile                               # UPDATED with frontend commands
```

## Критерии завершения

- [ ] Next.js проект инициализирован в `frontend/app/`
- [ ] shadcn/ui установлен и сконфигурирован
- [ ] TypeScript настроен (strict mode)
- [ ] ESLint + Prettier настроены
- [ ] Jest + RTL настроены и работают
- [ ] Базовая структура проекта создана
- [ ] API клиент реализован с типами
- [ ] React Query provider настроен
- [ ] Простая главная страница работает и подключается к Mock API
- [ ] Базовый тест написан и проходит
- [ ] Команды в Makefile добавлены и работают
- [ ] Документация создана (frontend-vision.md, ADR-03.md)
- [ ] Roadmap обновлен
- [ ] Отчет о спринте создан

## Проверка работоспособности

```bash
# 1. Установка зависимостей
make frontend-install

# 2. Запуск Mock API (в отдельном терминале)
make api-run

# 3. Запуск frontend dev server
make frontend-dev

# 4. Открыть http://localhost:3000
# Должна отобразиться главная страница с данными от Mock API

# 5. Запуск тестов
make frontend-test

# 6. Проверка качества
make frontend-quality
```

## Следующие шаги

После завершения F-Sprint-2:

- **F-Sprint-3**: Реализация dashboard компонентов (MetricCard, ActivityChart, etc.)
- **F-Sprint-4**: Реализация ИИ-чата
- **F-Sprint-5**: Переход с Mock API на Real API

### To-dos

- [ ] Инициализация Next.js проекта с TypeScript и Tailwind CSS
- [ ] Установка и конфигурация shadcn/ui с базовыми компонентами
- [ ] Установка дополнительных зависимостей (React Query, Recharts, axios)
- [ ] Настройка Prettier, ESLint, Jest + React Testing Library
- [ ] Создание структуры проекта (components, lib, types, hooks)
- [ ] Реализация API клиента и TypeScript типов для backend models
- [ ] Настройка React Query provider и базовых хуков
- [ ] Создание простой главной страницы с интеграцией Mock API
- [ ] Написание базовых тестов для проверки установки
- [ ] Добавление frontend команд в корневой Makefile
- [ ] Создание frontend-vision.md и ADR-03.md
- [ ] Обновление frontend-roadmap.md и создание отчета о спринте