# ⚡ Quick Start - Business Planner

> **От установки до первого голосового сообщения за 5 минут!**

---

## 📋 Что нужно:

1. ✅ Python 3.11+
2. ✅ Docker (для PostgreSQL)
3. ⚠️ Telegram Bot Token - [Получить от @BotFather](https://t.me/BotFather)
4. ⚠️ OpenAI API Key - [Получить здесь](https://platform.openai.com/api-keys)

---

## 🚀 Запуск за 5 минут:

### Шаг 1: Клонировать репозиторий (если ещё не сделано)

```bash
cd planer_4
```

### Шаг 2: Автоматическая настройка

```bash
make setup
```

Эта команда:
- ✅ Создаст файл `.env`
- ✅ Установит все зависимости
- ✅ Предложит ввести API ключи

**ИЛИ** создайте `.env` вручную:

```bash
# Windows PowerShell
Copy-Item docs/examples/.env.example .env

# Linux/Mac
cp docs/examples/.env.example .env
```

### Шаг 3: Получить API ключи

#### 🤖 Telegram Bot Token:

1. Открыть Telegram, найти [@BotFather](https://t.me/BotFather)
2. Отправить: `/newbot`
3. Ввести имя: `Business Planner Bot`
4. Ввести username: `business_planner_bot`
5. Скопировать токен: `1234567890:ABCdef...`

#### 🧠 OpenAI API Key:

1. Открыть: https://platform.openai.com/api-keys
2. Нажать **Create new secret key**
3. Скопировать ключ: `sk-proj-...`
4. ⚠️ **Важно**: Привязать карту в **Billing**!

**Подробнее**: См. [SETUP_API_KEYS.md](SETUP_API_KEYS.md)

### Шаг 4: Вставить ключи в .env

Открыть файл `.env` и заполнить:

```env
# Telegram (ОБЯЗАТЕЛЬНО!)
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather

# OpenAI (ОБЯЗАТЕЛЬНО!)
OPENAI_API_KEY=sk-proj-ваш_ключ

# Database (оставить как есть для локального запуска)
DATABASE_URL=postgresql+asyncpg://planner:planner123@localhost:5432/planner
```

### Шаг 5: Запустить PostgreSQL

```bash
make docker-up
```

Или вручную:
```bash
cd infrastructure/docker
docker-compose up -d
```

### Шаг 6: Применить миграции (TODO: Setup Alembic)

```bash
# TODO: Будет доступно после настройки Alembic
# make db-migrate
```

**Пока что**: База создастся автоматически при первом запуске

### Шаг 7: Запустить приложение!

```bash
make run-debug
```

Вы увидите:
```
🚀 Business Planner starting...
✅ Database connected
✅ Telegram bot initialized
📱 Bot running in polling mode
💬 Send voice messages to start!
```

### Шаг 8: Тестировать в Telegram!

1. Открыть Telegram
2. Найти: `@ваш_username_бота`
3. Нажать **Start**
4. Отправить: `/start`
5. **Отправить голосовое сообщение**:
   
   🎤 *"Нужно починить фрезер для Иванова до завтра"*

6. Получить ответ:
   ```
   ✅ Создал задачу:
   
   Починить фрезер для Иванова
   
   🔧 Бизнес: Inventum
   📅 18 окт, 18:00
   ⏱️ ~1 ч 30 мин (на основе 3 похожих задач)
   
   [✅ Завершить] [✏️ Изменить]
   ```

---

## 🎉 Готово!

Теперь вы можете:

- ✅ Отправлять голосовые сообщения → автоматическое создание задач
- ✅ Использовать команды: `/today`, `/week`, `/task`, `/complete`
- ✅ Нажимать на inline кнопки под задачами
- ✅ Просматривать задачи через REST API: http://localhost:8000/docs

---

## 🐛 Проблемы?

### ❌ "Invalid token"
- Проверьте что скопировали **весь** токен от @BotFather
- Токен должен быть формата: `1234567890:ABCdef...`

### ❌ "Incorrect API key provided"
- Ключ должен начинаться с `sk-proj-` или `sk-`
- Проверьте что **привязана карта** в OpenAI Billing
- Создайте новый ключ если старый не работает

### ❌ "Database connection failed"
- Проверьте что PostgreSQL запущен: `make docker-up`
- Проверьте `DATABASE_URL` в `.env`
- Попробуйте: `docker ps` (должен быть контейнер postgres)

### ❌ "Module not found"
- Установите зависимости: `pip install -r requirements.txt`
- Или: `make install`

### ❌ Бот не отвечает
- Проверьте что приложение запущено (`make run-debug`)
- Проверьте логи в консоли
- Попробуйте: `/start` в боте

---

## 📚 Дополнительные команды:

```bash
# Посмотреть все команды
make help

# Запустить тесты (TODO)
make test

# Форматировать код
make format

# Проверить код
make lint

# Очистить кеш
make clean

# Остановить PostgreSQL
make docker-down

# Посмотреть логи PostgreSQL
make docker-logs
```

---

## 🔗 Полезные ссылки:

- **Подробная настройка**: [SETUP_API_KEYS.md](SETUP_API_KEYS.md)
- **Telegram Bot**: [TELEGRAM_BOT_READY.md](TELEGRAM_BOT_READY.md)
- **Phase 1 Complete**: [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md)
- **Документация**: [docs/](docs/)
- **API Docs**: http://localhost:8000/docs (после запуска)

---

## 🎯 Следующие шаги:

1. ✅ **Тестировать**: Отправляйте разные голосовые сообщения
2. ✅ **Команды**: Попробуйте `/today`, `/week`
3. ✅ **API**: Откройте http://localhost:8000/docs
4. ⏳ **Deployment**: См. Phase 4 когда готовы к продакшену

---

## 💡 Советы:

### Голосовые сообщения:

Говорите естественно, бот понимает русский язык:

- ✅ "Нужно починить фрезер для Иванова до завтра"
- ✅ "Максиму сделать прототип крышки к понедельнику"
- ✅ "Позвонить поставщику в Китае сегодня вечером"
- ✅ "Лизе подготовить пост для инстаграма"

Бот автоматически определит:
- **Бизнес** (Inventum, Lab, R&D, Trade)
- **Исполнителя** (8 членов команды)
- **Дедлайн** (с учетом рабочих дней)
- **Приоритет** (1-4)
- **Время** (на основе истории похожих задач)

### Команды:

- `/today` - Видеть что срочно
- `/week` - Планировать неделю
- `/task` - Быстро создать задачу текстом
- `/complete` - Отметить выполнение (учится на этом!)

---

## 🎉 Вы готовы!

**Отправьте первое голосовое сообщение и дайте AI сделать магию!** ✨

---

**Business Planner v1.0**  
**Created with ❤️ using AI-First Development**

