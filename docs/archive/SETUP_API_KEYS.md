# 🔑 Настройка API ключей - Business Planner

> **Быстрый гайд по получению Telegram Bot Token и OpenAI API Key**

---

## 1️⃣ Telegram Bot Token

### Шаг 1: Создать бота через @BotFather

1. **Открыть Telegram**, найти **@BotFather**
2. Отправить команду: `/newbot`
3. Ввести имя бота (например: `Business Planner Bot`)
4. Ввести username бота (должен заканчиваться на `bot`, например: `business_planner_bot`)

### Шаг 2: Получить токен

После создания @BotFather пришлёт сообщение:
```
Done! Congratulations on your new bot...

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

Keep your token secure and store it safely...
```

**Это и есть ваш `TELEGRAM_BOT_TOKEN`** ✅

### Шаг 3: Настроить бота (опционально)

```
/setdescription - Установить описание
/setabouttext - Установить "О боте"
/setuserpic - Установить аватар
```

Рекомендуемое описание:
```
🤖 AI-ассистент для управления задачами
Отправьте голосовое сообщение — я создам задачу автоматически!
```

---

## 2️⃣ OpenAI API Key

### Шаг 1: Зарегистрироваться на OpenAI

1. Перейти на: https://platform.openai.com/
2. Нажать **Sign Up** (или **Log In** если есть аккаунт)
3. Подтвердить email

### Шаг 2: Добавить способ оплаты

1. Перейти в **Settings** → **Billing**
2. Нажать **Add payment method**
3. Ввести данные карты

⚠️ **Важно**: Без карты API не будет работать (даже в бесплатном tier)

### Шаг 3: Создать API Key

1. Перейти в **API Keys**: https://platform.openai.com/api-keys
2. Нажать **Create new secret key**
3. Дать имя (например: `Business Planner`)
4. **СРАЗУ СКОПИРОВАТЬ КЛЮЧ** (больше не покажется!)

Формат ключа:
```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Это ваш `OPENAI_API_KEY`** ✅

### Шаг 4: Проверить лимиты

1. Перейти в **Usage**: https://platform.openai.com/usage
2. Установить **Usage limits** (например, $10/месяц)
3. Настроить email уведомления

---

## 3️⃣ Создать .env файл

### Вариант A: Автоматически (рекомендуется)

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

### Вариант B: Вручную

Создать файл `.env` в корне проекта:

```env
# ============================================================================
# Business Planner - Environment Variables
# ============================================================================

# ============================================================================
# Application Settings
# ============================================================================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

API_HOST=0.0.0.0
API_PORT=8000

# ============================================================================
# OpenAI Configuration
# ============================================================================
OPENAI_API_KEY=sk-proj-ваш_ключ_сюда

# Model Selection
MODEL_PARSER=gpt-4o-mini
MODEL_REASONING=gpt-4o-mini
MODEL_ANALYTICS=gpt-4o
MODEL_VOICE=whisper-1
MODEL_EMBEDDINGS=text-embedding-3-small

# ============================================================================
# Telegram Bot
# ============================================================================
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_SECRET_TOKEN=random_secret_string_123456
TELEGRAM_WEBHOOK_URL=
TELEGRAM_USE_WEBHOOK=false

# ============================================================================
# Database - PostgreSQL
# ============================================================================
DATABASE_URL=postgresql+asyncpg://planner:planner123@localhost:5432/planner

# ============================================================================
# Redis - Cache
# ============================================================================
REDIS_URL=redis://localhost:6379/0

# ============================================================================
# RAG Configuration
# ============================================================================
EMBEDDING_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
RAG_TOP_K=5

# ============================================================================
# Business Rules
# ============================================================================
DEFAULT_DEADLINE_DAYS=7
WORKDAY_START_HOUR=9
WORKDAY_END_HOUR=18
TIMEZONE=Asia/Almaty

TIME_MORNING=09:00
TIME_AFTERNOON=13:00
TIME_EVENING=18:00

# ============================================================================
# Rate Limiting
# ============================================================================
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500
```

---

## 4️⃣ Заполнить обязательные поля

### Минимально необходимые:

```env
# ✅ ОБЯЗАТЕЛЬНО - Telegram
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather

# ✅ ОБЯЗАТЕЛЬНО - OpenAI  
OPENAI_API_KEY=sk-proj-ваш_ключ

# ✅ ОБЯЗАТЕЛЬНО - Database (если запускаете локально)
DATABASE_URL=postgresql+asyncpg://planner:planner123@localhost:5432/planner
```

### Опционально (для продакшена):

```env
TELEGRAM_SECRET_TOKEN=сгенерировать_случайную_строку
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook/telegram
TELEGRAM_USE_WEBHOOK=true
```

---

## 5️⃣ Сгенерировать SECRET_TOKEN

Для webhook в production нужен случайный токен:

### PowerShell:
```powershell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Linux:
```bash
openssl rand -hex 32
```

Результат вставить в `.env`:
```env
TELEGRAM_SECRET_TOKEN=полученная_случайная_строка
```

---

## 6️⃣ Безопасность ⚠️

### ✅ ОБЯЗАТЕЛЬНО:

1. **Добавить .env в .gitignore**
   ```
   .env
   .env.local
   .env.production
   ```

2. **НИКОГДА не коммитить .env в git!**
   ```bash
   git status  # Проверить что .env не в списке
   ```

3. **Не делиться токенами**
   - Не отправлять в чаты
   - Не публиковать в issues
   - Не показывать в скриншотах

### 🔄 Если токен утёк:

**Telegram:**
1. @BotFather → `/token`
2. Выбрать бота
3. `/revoke` - отозвать старый токен
4. Получить новый

**OpenAI:**
1. https://platform.openai.com/api-keys
2. Найти утекший ключ
3. Нажать **Revoke**
4. Создать новый

---

## 7️⃣ Проверка настройки

### Проверить .env:

```bash
# Windows
type .env

# Linux/Mac
cat .env
```

### Проверить что токены работают:

```python
# test_keys.py
import os
from dotenv import load_dotenv

load_dotenv()

# Check Telegram
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
print(f"✅ Telegram: {'OK' if telegram_token else '❌ NOT SET'}")

# Check OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
print(f"✅ OpenAI: {'OK' if openai_key and openai_key.startswith('sk-') else '❌ NOT SET'}")

# Check Database
db_url = os.getenv("DATABASE_URL")
print(f"✅ Database: {'OK' if db_url else '❌ NOT SET'}")
```

Запустить:
```bash
python test_keys.py
```

Ожидаемый результат:
```
✅ Telegram: OK
✅ OpenAI: OK
✅ Database: OK
```

---

## 8️⃣ Проверить что бот работает

### Запустить приложение:

```bash
make run-debug
```

### Найти бота в Telegram:

1. Открыть Telegram
2. Найти: `@ваш_username_бота`
3. Нажать **Start**
4. Отправить `/start`

Должен ответить приветствием! ✅

---

## 9️⃣ Частые ошибки

### ❌ "Invalid token"
- Проверить что скопировали весь токен
- Проверить что нет лишних пробелов
- Формат: `1234567890:ABCdef...`

### ❌ "Incorrect API key provided"
- Ключ должен начинаться с `sk-`
- Проверить что ключ не истёк
- Проверить что карта привязана

### ❌ "Database connection failed"
- Проверить что PostgreSQL запущен
- Проверить DATABASE_URL
- Проверить что база создана

---

## 🎯 Готово!

После настройки всех ключей:

```bash
# 1. Проверить .env
cat .env

# 2. Установить зависимости (если ещё не установлены)
pip install -r requirements.txt

# 3. Запустить PostgreSQL
docker-compose up -d postgres

# 4. Запустить приложение
make run-debug

# 5. Тестировать в Telegram!
```

---

## 📞 Полезные ссылки:

- **Telegram Bot API**: https://core.telegram.org/bots
- **@BotFather**: https://t.me/BotFather
- **OpenAI Platform**: https://platform.openai.com/
- **OpenAI API Keys**: https://platform.openai.com/api-keys
- **OpenAI Usage**: https://platform.openai.com/usage
- **OpenAI Pricing**: https://openai.com/api/pricing/

---

**Готово! Теперь у вас есть все ключи для запуска!** 🚀

