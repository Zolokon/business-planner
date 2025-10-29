# Business Planner - Web Interface

Современный веб-интерфейс для управления задачами 4 бизнесов.

## 🎨 Технологии

- **React 18** + **TypeScript**
- **Vite** (быстрая сборка)
- **Material UI (MUI)** (Material Design)
- **React Router** (навигация)
- **Axios** (API клиент)

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd frontend
npm install
```

### 2. Настройка окружения

Создайте файл `.env`:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Запуск dev сервера

```bash
npm run dev
```

Откроется на **http://localhost:5173**

### 4. Убедитесь что Backend запущен

```bash
# В корневой директории проекта
cd ..
python -m uvicorn src.main:app --reload
```

Backend должен работать на **http://localhost:8000**

## 📦 Сборка для продакшн

```bash
npm run build
```

Результат будет в папке `dist/`

## 🎯 Основные функции

### Dashboard (Главная страница)
- Карточки 4 бизнесов с цветовым кодированием
- Статистика: всего задач, срочные, в работе, просроченные
- Быстрый переход к задачам бизнеса

### Список задач бизнеса
- Таблица всех задач с:
  - Название и описание
  - Приоритет (цветной чип)
  - Статус (открыта, в работе, завершена)
  - Дедлайн (с подсветкой просроченных)
  - Исполнитель
- **Фильтры**:
  - По статусу
  - По приоритету
- **Действия**:
  - ✅ Завершить задачу
  - 🗑️ Удалить задачу

### Дополнительно
- 🌓 Тёмная / светлая тема
- 📱 Адаптивный дизайн
- ⚡ Мгновенная загрузка (Vite HMR)

## 🏗️ Структура проекта

```
frontend/
├── src/
│   ├── api/              # API клиент
│   │   ├── client.ts     # Axios instance
│   │   └── tasks.ts      # Tasks API methods
│   ├── pages/            # Страницы
│   │   ├── Dashboard.tsx # Главная страница
│   │   └── BusinessTasks.tsx # Задачи бизнеса
│   ├── types/            # TypeScript типы
│   │   └── index.ts      # Task, Business, константы
│   ├── App.tsx           # Главный компонент
│   └── main.tsx          # Entry point
├── .env                  # Переменные окружения
└── package.json
```

## 🎨 Цветовая схема бизнесов

| Бизнес | Цвет | Описание |
|--------|------|----------|
| **INVENTUM** | 🔴 Красный | Ремонт стоматологического оборудования |
| **INVENTUM LAB** | 🔵 Синий | Зуботехническая лаборатория (CAD/CAM) |
| **R&D** | 🟢 Зелёный | Разработка прототипов |
| **TRADE** | 🟠 Оранжевый | Импорт из Китая |

## 📝 Приоритеты задач

| Приоритет | Цвет | Название |
|-----------|------|----------|
| 1 | 🔴 | Высокий |
| 2 | 🟠 | Средний |
| 3 | 🟢 | Низкий |
| 4 | ⚪ | Отложено |

## 🔧 Доступные команды

```bash
npm run dev        # Запустить dev сервер
npm run build      # Собрать для продакшн
npm run preview    # Просмотр production build
npm run lint       # Запустить линтер
```

## 🚀 Деплой

### Production сборка

```bash
npm run build
```

### Деплой на сервер

Скопируйте содержимое `dist/` на веб-сервер (nginx/apache):

```bash
# Пример для nginx
scp -r dist/* root@164.92.225.137:/var/www/planner/
```

### Конфигурация nginx

```nginx
server {
    listen 80;
    server_name planner.inventum.com.kz;

    root /var/www/planner;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy к FastAPI backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📚 API Endpoints

Приложение использует следующие эндпоинты:

- `GET /tasks/` - Получить список задач
- `GET /tasks/:id` - Получить задачу по ID
- `POST /tasks/` - Создать задачу
- `PATCH /tasks/:id` - Обновить задачу
- `DELETE /tasks/:id` - Удалить задачу
- `POST /tasks/:id/complete` - Завершить задачу

## 🐛 Troubleshooting

### Ошибка CORS

Убедитесь что в [backend/src/main.py](../src/main.py) настроен CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Backend не отвечает

Проверьте что FastAPI запущен:

```bash
curl http://localhost:8000/health
```

## 🔧 Рабочий Процесс (Workflow)

### 📚 Документация для Разработки

Создана **полная система** для структурированной разработки:

1. **[WORKFLOW_INDEX.md](WORKFLOW_INDEX.md)** - 🗂️ Навигация
   - Центральный индекс всех workflow документов
   - Схема процесса разработки
   - Чек-листы для каждого этапа
   - **НАЧНИТЕ ОТСЮДА!**

2. **[DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)** - 📖 Полное руководство
   - Общие принципы разработки
   - Процесс разработки (4 этапа: Планирование → Реализация → Проверка → Коммит)
   - Правила компонентов и коммитов
   - Взаимодействие AI ↔ Пользователь
   - Примеры workflow

3. **[WORKFLOW_QUICK.md](WORKFLOW_QUICK.md)** - ⚡ Быстрая справка
   - Процесс в 4 шага (1 страница)
   - Обязательные правила адаптивности
   - Структура компонента
   - Чек-лист перед коммитом
   - **Держите открытым при работе!**

4. **[TASK_TEMPLATE.md](TASK_TEMPLATE.md)** - 📋 Шаблон задачи
   - Шаблон для каждой новой функции
   - Требования, план, технические детали
   - Критерии завершения
   - **Используйте при каждой новой задаче!**

### 🎯 Быстрый Старт Workflow

```bash
# Перед началом работы:
1. Прочитайте WORKFLOW_INDEX.md (5 минут)
2. Держите WORKFLOW_QUICK.md открытым
3. При новой задаче → скопируйте TASK_TEMPLATE.md

# При работе:
- AI следует DEVELOPMENT_WORKFLOW.md
- Пользователь проверяет по WORKFLOW_QUICK.md
```

---

## 📐 Адаптивный Дизайн

### 📚 Документация по Responsive Design

Созданы **5 подробных руководств** по адаптивному дизайну:

1. **[RESPONSIVE_DESIGN_GUIDE.md](RESPONSIVE_DESIGN_GUIDE.md)** - 📖 Полное руководство
   - Breakpoints и сетка
   - Практические примеры
   - Готовые паттерны
   - Best practices

2. **[RESPONSIVE_CHEATSHEET.md](RESPONSIVE_CHEATSHEET.md)** - 📱 Шпаргалка
   - Быстрые команды
   - Spacing scale
   - Готовые утилиты
   - Тестовые размеры

3. **[EXAMPLES.md](EXAMPLES.md)** - 🎨 Примеры кода
   - Dashboard адаптивный
   - Таблица → Карточки
   - AppBar с меню
   - Business Card
   - Custom hooks

4. **[QUICK_START_RESPONSIVE.md](QUICK_START_RESPONSIVE.md)** - ⚡ Быстрый старт
   - 15-минутное внедрение
   - Пошаговые инструкции
   - Тестирование
   - Частые проблемы

5. **[RESPONSIVE_CHECKLIST.md](RESPONSIVE_CHECKLIST.md)** - ✅ Контрольный список
   - Проверка всех компонентов
   - Тестирование на устройствах
   - Performance
   - Lighthouse scores

### 🛠️ Готовые Утилиты

Созданы файлы для быстрого применения:

```
frontend/src/
├── theme/
│   ├── breakpoints.ts    # 📐 Конфигурация breakpoints
│   └── index.ts          # 🎨 Централизованная тема
└── utils/
    └── responsive.ts     # 🛠️ Утилиты для адаптива
```

### 🎯 Breakpoints (Material UI)

```typescript
xs: 0px      // 📱 Mobile phones
sm: 600px    // 📱 Tablets (portrait)
md: 900px    // 📱 Tablets (landscape)
lg: 1200px   // 💻 Laptops
xl: 1536px   // 🖥️ Large monitors
```

### ⚡ Быстрое Применение

```typescript
import { responsivePadding } from './utils/responsive';
import { createAppTheme } from './theme';

// Адаптивные отступы
<Box sx={responsivePadding(2, 3, 4, 6)}>

// Адаптивная Grid
<Grid container spacing={{ xs: 2, sm: 3, md: 4 }}>
  <Grid item xs={12} sm={6} lg={3}>
    <Card />
  </Grid>
</Grid>

// useMediaQuery для условной логики
const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
{isMobile ? <MobileView /> : <DesktopView />}
```

### 📱 Адаптивная Сетка

```
Mobile (xs):   [████████████] 1 column  (12/12)
Tablet (sm):   [██████][████] 2 columns (6/12 each)
Desktop (lg):  [███][██][███] 4 columns (3/12 each)
```

### 🧪 Тестирование

**Chrome DevTools** (F12 → Responsive Mode):

1. iPhone SE (375px) - мобильная версия
2. iPad Mini (768px) - планшет
3. MacBook Air (1440px) - десктоп

---

**Автор**: Claude + Константин
**Дата**: 2025-10-27 (обновлено: адаптивный дизайн)
**Версия**: 1.1.0
