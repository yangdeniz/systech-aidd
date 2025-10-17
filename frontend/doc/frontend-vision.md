# Техническое видение Frontend проекта HomeGuru

## 1. Технологии

### Основные технологии
- **Next.js 15** - современный React framework с App Router
- **React 19** - библиотека для построения UI
- **TypeScript 5.x** - статическая типизация для безопасности кода
- **pnpm** - быстрый и эффективный менеджер пакетов

### UI и стилизация
- **shadcn/ui** - современная компонентная библиотека на базе Radix UI
- **Tailwind CSS 4** - utility-first CSS framework
- **Radix UI** - unstyled UI primitives для доступности
- **Lucide React** - иконки

### State Management и Data Fetching
- **React Context API** - для простого глобального состояния
- **TanStack Query (React Query)** - для серверного состояния и кеширования
- **axios** - HTTP клиент для API запросов

### Визуализация данных
- **Recharts** - декларативная библиотека для графиков
- **date-fns** - работа с датами

### Quality Tools
- **Jest** - фреймворк для тестирования
- **React Testing Library** - тестирование React компонентов
- **ESLint** - линтинг кода с правилами Next.js и TypeScript
- **Prettier** - форматирование кода

## 2. Принципы разработки

### Главные принципы
- **KISS (Keep It Simple, Stupid)** - максимальная простота
- **Component-based architecture** - модульная архитектура
- **Type Safety** - строгая типизация TypeScript
- **Testing** - покрытие тестами ≥ 80%
- **Responsive Design** - адаптивный дизайн для всех устройств

### Практическое применение
- Один компонент = одна ответственность
- Переиспользуемые UI компоненты через shadcn/ui
- Типизация всех функций и компонентов
- Server Components где возможно для оптимизации
- Client Components только где необходимо (интерактивность)

## 3. Структура проекта

```
frontend/app/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout с providers
│   │   ├── page.tsx            # Главная страница (дашборд)
│   │   └── globals.css         # Глобальные стили
│   ├── components/
│   │   ├── ui/                 # shadcn/ui компоненты
│   │   ├── dashboard/          # Компоненты дашборда
│   │   ├── layout/             # Layout компоненты
│   │   └── providers/          # Context providers
│   ├── lib/
│   │   ├── utils.ts            # Утилиты (cn() и др.)
│   │   ├── api.ts              # API клиент
│   │   └── constants.ts        # Константы приложения
│   ├── types/
│   │   ├── api.ts              # Типы для API
│   │   └── dashboard.ts        # Типы для дашборда
│   └── hooks/
│       ├── useStats.ts         # Хук для статистики
│       └── usePeriod.ts        # Хук для периодов
├── public/                     # Статические файлы
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── .eslintrc.json
├── .prettierrc.json
├── jest.config.js
└── jest.setup.js
```

## 4. Архитектура

### Слои приложения

```
User Interface Layer (React Components)
    ↓
State Management Layer (React Query + Context)
    ↓
API Client Layer (axios)
    ↓
Backend Mock API (src/api/main.py)
```

### Основные компоненты

**Page Components (src/app/):**
- Страницы приложения на базе Next.js App Router
- Server Components по умолчанию
- Client Components для интерактивности

**UI Components (src/components/ui/):**
- shadcn/ui компоненты
- Переиспользуемые, типизированные
- Стилизация через Tailwind CSS

**Business Components (src/components/dashboard/, src/components/layout/):**
- Компоненты дашборда (MetricCard, ActivityChart, etc.)
- Layout компоненты (Header, Sidebar, Footer)
- Интеграция с API через hooks

**Providers (src/components/providers/):**
- QueryProvider для React Query
- Будущие providers для темизации, авторизации

**Custom Hooks (src/hooks/):**
- Переиспользуемая логика
- Интеграция с React Query
- Type-safe hooks

**API Layer (src/lib/api.ts):**
- Централизованный API клиент
- Типизированные запросы
- Обработка ошибок

**Type Definitions (src/types/):**
- Типы для API responses
- Типы для компонентов
- Shared types

## 5. API Integration

### Mock API (F-Sprint-1)
- Backend: FastAPI на порту 8000
- Endpoint: `GET /stats?period={day|week|month}`
- Response: JSON со всеми данными для дашборда

### API Client
```typescript
// src/lib/api.ts
const apiClient = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

export async function getStats(period: Period): Promise<StatsResponse> {
  const response = await apiClient.get("/stats", { params: { period } });
  return response.data;
}
```

### React Query Integration
```typescript
// src/hooks/useStats.ts
export function useStats(period: Period) {
  return useQuery({
    queryKey: ["stats", period],
    queryFn: () => getStats(period),
  });
}
```

## 6. State Management

### Server State (React Query)
- Кеширование API responses
- Автоматическое обновление данных
- Loading и error states
- Optimistic updates (для будущих функций)

### Client State (React Context API)
- Глобальное состояние приложения
- Настройки UI (тема, язык)
- User preferences

## 7. Styling Strategy

### Tailwind CSS
- Utility-first подход
- Быстрая разработка
- Консистентный дизайн
- Tree-shaking для минимального bundle size

### CSS Variables
- Темизация через CSS переменные
- Поддержка dark/light mode
- Кастомизация shadcn/ui компонентов

### Component Styling
```tsx
// Использование cn() для условных стилей
<div className={cn(
  "base-styles",
  isActive && "active-styles",
  variant === "primary" && "primary-styles"
)}>
```

## 8. Testing Strategy

### Unit Tests (Jest + RTL)
- Тестирование компонентов в изоляции
- Тестирование hooks
- Тестирование утилит
- Coverage ≥ 80%

### Integration Tests
- Тестирование взаимодействия компонентов
- Тестирование API integration
- Мокирование React Query

### Example Test
```typescript
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

## 9. Quality Standards

### TypeScript Strict Mode
- Все файлы типизированы
- Нет `any` без явной необходимости
- Interface/Type для всех props
- Type inference где возможно

### ESLint Rules
- Next.js recommended rules
- TypeScript recommended rules
- React hooks rules
- Custom project rules

### Prettier Configuration
- Консистентное форматирование
- Автоматическое при сохранении
- Integration с ESLint

### Code Review Checklist
- [ ] TypeScript errors: 0
- [ ] ESLint errors: 0
- [ ] Tests passing: 100%
- [ ] Coverage ≥ 80%
- [ ] No console.log в production
- [ ] Responsive на всех breakpoints
- [ ] Доступность (accessibility)

## 10. Development Workflow

### Setup
```bash
# Установка зависимостей
make frontend-install

# Запуск dev server
make frontend-dev
```

### Development
```bash
# Форматирование
make frontend-format

# Линтинг
make frontend-lint

# Тесты
make frontend-test
```

### Quality Checks
```bash
# Все проверки вместе
make frontend-quality

# Backend + Frontend качество
make quality-all
```

## 11. Performance Optimization

### Next.js Optimizations
- Server Components для статического контента
- Client Components только для интерактивности
- Image optimization через next/image
- Font optimization через next/font
- Code splitting автоматически

### React Query Optimizations
- Кеширование responses (staleTime: 60s)
- Предотвращение дублирования запросов
- Фоновое обновление данных
- Pagination для больших данных (будущее)

### Bundle Size
- Tree-shaking через ES modules
- Dynamic imports для больших компонентов
- Анализ bundle size через next/bundle-analyzer (опционально)

## 12. Roadmap

### F-Sprint-2: Инициализация (Current)
- ✅ Настройка Next.js + TypeScript
- ✅ Установка shadcn/ui
- ✅ Конфигурация quality tools
- ✅ API client + types
- ✅ Базовая страница с интеграцией Mock API

### F-Sprint-3: Dashboard Implementation
- [ ] Компоненты MetricCard
- [ ] Компонент ActivityChart (Recharts)
- [ ] Компонент RecentDialogues
- [ ] Компонент TopUsers
- [ ] Layout с Header/Sidebar
- [ ] Responsive design

### F-Sprint-4: AI Chat
- [ ] Chat UI компонент
- [ ] Интеграция с chat API
- [ ] Визуализация SQL результатов
- [ ] Streaming responses (если потребуется)

### F-Sprint-5: Real API Integration
- [ ] Переключение с Mock на Real API
- [ ] Обработка ошибок
- [ ] Loading states
- [ ] Production deployment

## 13. Заключение

Frontend проект HomeGuru построен на современном стеке технологий с акцентом на простоту, типобезопасность и качество кода. Next.js + TypeScript + shadcn/ui обеспечивают отличный DX и высокую производительность. React Query упрощает работу с серверным состоянием. Строгие стандарты качества (ESLint, Prettier, Jest) гарантируют maintainability кода.

**Ключевые принципы:**
- ✅ KISS - простота превыше всего
- ✅ Type Safety - строгая типизация
- ✅ Testing - высокое покрытие
- ✅ Quality - автоматизированные проверки
- ✅ Performance - оптимизация из коробки

**Метрики качества:**
- TypeScript strict mode: 0 errors
- ESLint: 0 errors
- Test coverage: ≥ 80%
- Prettier: все файлы отформатированы

---

**Дата создания:** 17 октября 2025  
**Версия:** 1.0  
**Статус:** Active Development

