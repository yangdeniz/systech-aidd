<!-- 5c955ed7-cc4e-4167-a98c-2d7256d88700 5382de07-1f76-42c2-9f6a-849b1381ca49 -->
# Sprint 3 - Реализация Dashboard статистики диалогов

## Обзор

Реализация полнофункционального дашборда статистики для HomeGuru с интеграцией Mock API. Дашборд включает 4 метрики, временной график активности, список последних диалогов, топ пользователей и переключатель темы (светлая/темная).

**Референс:** dashboard-01 от shadcn/ui

**Статус:** F-Sprint-2 завершен (Next.js + TypeScript + React Query + shadcn/ui config)

## Архитектура компонентов

```
src/app/page.tsx (главная страница)
  ├── Header (с ThemeToggle в правом верхнем углу)
  ├── MetricCards (секция с 4 карточками)
  │   └── MetricCard × 4
  ├── ActivityChart (график с переключателем периода)
  └── Grid Layout
      ├── RecentDialogues (список диалогов)
      └── TopUsers (список топ-пользователей)
```

## Этапы реализации

### 1. Установка shadcn/ui компонентов и темизации

**Команды для установки:**

```bash
cd frontend/app
pnpm install next-themes
pnpm dlx shadcn@latest add card
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add tabs
pnpm dlx shadcn@latest add table
pnpm dlx shadcn@latest add badge
pnpm dlx shadcn@latest add dropdown-menu
```

**Компоненты:**

- `next-themes` - библиотека для управления темами
- `Card` - для MetricCard, секций диалогов/пользователей
- `Button` - для переключателя периодов
- `Tabs` - для периодов (Day/Week/Month)
- `Table` - для списков диалогов и пользователей
- `Badge` - для трендов и статусов
- `DropdownMenu` - для переключателя темы

### 2. Настройка темизации

#### 2.1 ThemeProvider

**Файл:** `src/components/providers/ThemeProvider.tsx`

**Функционал:**

- Обертка над `next-themes`
- Поддержка системной темы
- Переключение между light/dark/system
```typescript
"use client";
import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}
```


#### 2.2 Обновление layout.tsx

**Файл:** `src/app/layout.tsx`

**Изменения:**

- Добавить `ThemeProvider` внутри `QueryProvider`
- Добавить `suppressHydrationWarning` в `<html>`

#### 2.3 ThemeToggle Component

**Файл:** `src/components/layout/ThemeToggle.tsx`

**Функционал:**

- Dropdown menu с опциями: Light, Dark, System
- Иконки: Sun, Moon, Monitor (lucide-react)
- Позиция: правый верхний угол страницы

**Используемые компоненты:**

- `Button`, `DropdownMenu`, `DropdownMenuItem`
- Иконки: `Sun`, `Moon`, `Monitor`

### 3. Создание UI компонентов дашборда

#### 3.1 MetricCard Component

**Файл:** `src/components/dashboard/MetricCard.tsx`

**Функционал:**

- Отображение заголовка метрики
- Большое числовое значение
- Процент изменения с иконкой тренда (↑/↓)
- Текстовое описание тренда
- Адаптивная верстка
- Поддержка темной темы

**Пропсы:**

```typescript
interface MetricCardProps {
  title: string;
  value: string | number;
  changePercent: number;
  description: string;
}
```

**Используемые компоненты:** `Card`, `CardHeader`, `CardTitle`, `CardContent`

**Иконки:** `TrendingUp`, `TrendingDown` из lucide-react

#### 3.2 ActivityChart Component

**Файл:** `src/components/dashboard/ActivityChart.tsx`

**Функционал:**

- Area chart с плавной кривой (Recharts)
- Заливка области под графиком
- Tooltip при наведении
- Переключатель периодов (Day/Week/Month)
- Адаптивность к ширине контейнера
- Поддержка темной темы (цвета графика)
- Формат дат на оси X: `yyyy-MM-dd`

**Пропсы:**

```typescript
interface ActivityChartProps {
  data: TimeSeriesPoint[];
  period: Period;
  onPeriodChange: (period: Period) => void;
}
```

**Используемые компоненты:**

- Recharts: `AreaChart`, `Area`, `XAxis`, `YAxis`, `Tooltip`, `ResponsiveContainer`
- shadcn/ui: `Tabs`, `TabsList`, `TabsTrigger`, `Card`
- date-fns: `format(date, 'yyyy-MM-dd')` для форматирования дат

**Темизация Recharts:**

- Использовать CSS переменные для цветов
- Адаптировать цвета осей и текста под тему

#### 3.3 RecentDialogues Component

**Файл:** `src/components/dashboard/RecentDialogues.tsx`

**Функционал:**

- Список последних 10 диалогов
- Колонки: User ID, Username, Message Count, Last Message
- Форматирование времени ("2 hours ago")
- Empty state если нет данных

**Пропсы:**

```typescript
interface RecentDialoguesProps {
  dialogues: DialogueInfo[];
}
```

**Используемые компоненты:**

- shadcn/ui: `Card`, `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell`
- date-fns: `formatDistanceToNow()` для относительного времени

#### 3.4 TopUsers Component

**Файл:** `src/components/dashboard/TopUsers.tsx`

**Функционал:**

- Список топ-5 пользователей
- Колонки: Rank, User ID, Username, Total Messages, Dialogues
- Сортировка по убыванию сообщений
- Empty state если нет данных

**Пропсы:**

```typescript
interface TopUsersProps {
  users: TopUser[];
}
```

**Используемые компоненты:**

- shadcn/ui: `Card`, `Table`, `Badge` (для ранга)

### 4. Обновление главной страницы

**Файл:** `src/app/page.tsx`

**Изменения:**

1. Добавить Header с заголовком и ThemeToggle
2. Разместить 4 MetricCard в grid layout (2×2 или 4×1)
3. Добавить ActivityChart с управлением периодом
4. Разместить RecentDialogues и TopUsers в grid (1×2)
5. Обеспечить responsive layout (grid breakpoints)

**Layout структура:**

```tsx
<main className="min-h-screen bg-background">
  <div className="container mx-auto p-4 md:p-8 space-y-8">
    {/* Header with Title and Theme Toggle */}
    <header className="flex items-center justify-between">
      <h1 className="text-4xl font-bold">HomeGuru Dashboard</h1>
      <ThemeToggle />
    </header>
    
    {/* Metrics Grid */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {data.metrics.map((metric, idx) => (
        <MetricCard key={idx} {...metric} />
      ))}
    </div>
    
    {/* Activity Chart */}
    <ActivityChart 
      data={data.time_series}
      period={period}
      onPeriodChange={setPeriod}
    />
    
    {/* Bottom Grid */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <RecentDialogues dialogues={data.recent_dialogues} />
      <TopUsers users={data.top_users} />
    </div>
  </div>
</main>
```

### 5. Улучшение состояний и обработки ошибок

**Изменения в `page.tsx`:**

1. Loading state с skeleton компонентами (опционально)
2. Error state с дружелюбным сообщением и retry кнопкой
3. Empty state если данных нет
4. Плавные анимации переходов (Tailwind transitions)

### 6. Responsive Design

**Breakpoints:**

- Mobile (< 768px): 1 колонка
- Tablet (768px - 1024px): 2 колонки для метрик, стек для остального
- Desktop (> 1024px): 4 колонки для метрик, 2 колонки для низа

**Подход:**

- Использовать Tailwind responsive classes: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- Проверить отображение на разных размерах экрана
- Проверить работу темной темы на всех breakpoints

### 7. Тестирование компонентов

**Unit Tests:**

**`src/components/layout/ThemeToggle.test.tsx`:**

- Отображение кнопки переключения темы
- Работа dropdown menu
- Переключение между light/dark/system

**`src/components/dashboard/MetricCard.test.tsx`:**

- Отображение title, value, description
- Правильная иконка тренда (↑ для положительных, ↓ для отрицательных)
- Цвет изменения (зеленый/красный)

**`src/components/dashboard/ActivityChart.test.tsx`:**

- Рендеринг графика с данными
- Переключение периодов
- Обработка пустых данных

**`src/components/dashboard/RecentDialogues.test.tsx`:**

- Отображение списка диалогов
- Форматирование username (Anonymous если null)
- Форматирование времени

**`src/components/dashboard/TopUsers.test.tsx`:**

- Отображение топ-5 пользователей
- Правильная сортировка (проверяется визуально)
- Empty state

**Integration Test для `page.tsx`:**

- Загрузка данных из Mock API
- Отображение всех секций
- Переключение периода обновляет данные

### 8. Quality Checks

**Проверки перед завершением:**

- ✅ TypeScript: `pnpm run typecheck` - 0 errors
- ✅ ESLint: `pnpm run lint` - 0 errors
- ✅ Tests: `pnpm run test:ci` - все тесты проходят
- ✅ Coverage: >= 80%
- ✅ Prettier: `pnpm run format:check` - все отформатировано
- ✅ Visual: проверка на desktop/tablet/mobile размерах
- ✅ Темизация: проверка light/dark/system тем
- ✅ Accessibility: базовые проверки (semantic HTML, alt texts)

## Файлы для создания/изменения

**Новые файлы:**

```
src/components/ui/           # shadcn/ui компоненты (автоматически)
  ├── card.tsx
  ├── button.tsx
  ├── tabs.tsx
  ├── table.tsx
  ├── badge.tsx
  └── dropdown-menu.tsx

src/components/providers/
  └── ThemeProvider.tsx      # Provider для next-themes

src/components/layout/       # Layout компоненты
  ├── ThemeToggle.tsx
  └── ThemeToggle.test.tsx

src/components/dashboard/    # Компоненты дашборда
  ├── MetricCard.tsx
  ├── MetricCard.test.tsx
  ├── ActivityChart.tsx
  ├── ActivityChart.test.tsx
  ├── RecentDialogues.tsx
  ├── RecentDialogues.test.tsx
  ├── TopUsers.tsx
  └── TopUsers.test.tsx
```

**Изменяемые файлы:**

```
src/app/layout.tsx            # Добавление ThemeProvider
src/app/page.tsx              # Основная страница дашборда
src/app/page.test.tsx         # Интеграционный тест страницы
src/app/globals.css           # Возможные дополнения для темной темы
```

## Примерные тайминги

- Установка зависимостей и shadcn/ui компонентов: 5 мин
- Настройка темизации (ThemeProvider + ThemeToggle): 30 мин
- MetricCard + тесты: 30 мин
- ActivityChart + тесты: 45 мин
- RecentDialogues + тесты: 30 мин
- TopUsers + тесты: 30 мин
- Обновление page.tsx и layout.tsx: 30 мин
- Responsive design и полировка: 30 мин
- Тестирование темизации: 15 мин
- Quality checks и исправления: 30 мин

**Итого:** ~4.5 часа

## Технические заметки

1. **next-themes**: Использовать `attribute="class"` для Tailwind dark mode
2. **Recharts responsiveness**: Оборачивать в `ResponsiveContainer` с `width="100%" height={350}`
3. **Recharts темизация**: Использовать CSS переменные `hsl(var(--primary))` для адаптации под тему
4. **Date formatting**: Использовать `date-fns` вместо нативного `Date`
5. **TypeScript**: Все компоненты строго типизированы
6. **CSS Variables**: Использовать shadcn/ui CSS переменные для цветов
7. **Accessibility**: Использовать семантичные теги (`<main>`, `<header>`, `<section>`)
8. **Empty states**: Предусмотреть fallback для пустых данных
9. **Hydration**: Добавить `suppressHydrationWarning` в layout для избежания ошибок темизации

## Критерии завершения

- [ ] Настроена темизация с next-themes
- [ ] ThemeToggle работает в правом верхнем углу
- [ ] Все 4 компонента дашборда реализованы и покрыты тестами
- [ ] Главная страница отображает полный дашборд
- [ ] Responsive design работает на всех breakpoints
- [ ] Темная и светлая темы корректно отображаются
- [ ] Переключение периода корректно обновляет данные
- [ ] Все quality checks проходят (lint, types, tests, format)
- [ ] Coverage >= 80%
- [ ] Dashboard соответствует референсу и требованиям

### To-dos

- [ ] Установить shadcn/ui компоненты (card, button, tabs, table, badge)
- [ ] Создать компонент MetricCard с тестами
- [ ] Создать компонент ActivityChart с Recharts и тестами
- [ ] Создать компонент RecentDialogues с таблицей и тестами
- [ ] Создать компонент TopUsers с таблицей и тестами
- [ ] Обновить page.tsx с layout дашборда и всеми компонентами
- [ ] Реализовать responsive design для mobile/tablet/desktop
- [ ] Выполнить все quality checks (lint, types, tests, format, coverage)