# Telegram Bot Commands - Business Planner

> **Complete Telegram bot interaction specification**  
> **Created**: 2025-10-17  
> **Reference**: ADR-007 (Telegram Architecture)

---

## 🤖 Bot Commands

### Standard Commands (BotFather)

```
/start - Начало работы с ботом
/today - Задачи на сегодня
/tomorrow - Задачи на завтра
/week - Задачи на неделю
/projects - Список проектов
/weekly - Недельная аналитика
/help - Помощь и инструкции
```

---

## 📋 Command Specifications

### /start

**Purpose**: Welcome message and onboarding

**Trigger**: First interaction with bot or explicit /start command

**Response**:
```
👋 Привет, Константин!

Я помогу управлять задачами для ваших 4 бизнесов:
🔧 Inventum - Ремонт оборудования
🦷 Inventum Lab - Лаборатория
🔬 R&D - Разработка
💼 Import & Trade - Импорт из Китая

📝 Просто отправьте голосовое сообщение с задачей!

Например:
🎤 "Завтра утром Дима должен починить фрезер для Иванова"

Или используйте команды:
/today - Что на сегодня?
/weekly - Недельная аналитика
/help - Помощь
```

**Implementation**:
```python
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    
    # Create or update user in database
    await user_service.get_or_create(
        telegram_id=user.id,
        name=user.first_name or user.username
    )
    
    # Send welcome message
    await update.message.reply_text(WELCOME_MESSAGE)
```

---

### /today

**Purpose**: Show today's tasks grouped by business and priority

**Trigger**: User wants to see daily agenda

**Response Format**:
```
📅 Задачи на сегодня (Четверг, 17 октября)

🔴 Срочные (сделать до обеда):

🔧 Inventum:
  • Ремонт главного вала ⏱️ 2ч [Дима]
  
💼 Import & Trade:
  • Проверить таможенные документы ⏱️ 1ч [Слава]

🟡 Запланированные:

🦷 Inventum Lab:
  • Моделировать 5 коронок ⏱️ 3ч [Мария]

──────────────
Всего: 3 задачи, ~6 часов
```

**Parameters**:
```
/today - All businesses
/today inventum - Only Inventum tasks
/today lab - Only Lab tasks
```

**Implementation**:
```python
async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /today command."""
    
    # Parse optional business filter
    business_filter = None
    if context.args:
        business_name = context.args[0].lower()
        business_filter = BUSINESS_NAME_TO_ID.get(business_name)
    
    # Get today's tasks
    tasks = await task_service.get_today_tasks(
        user_id=update.effective_user.id,
        business_id=business_filter
    )
    
    # Format and send
    message = format_today_tasks(tasks)
    await update.message.reply_text(message, parse_mode='HTML')
```

---

### /tomorrow

**Purpose**: Show tomorrow's tasks (planning ahead)

**Response Format**: Similar to /today but for tomorrow

---

### /week

**Purpose**: Show week overview (Mon-Fri)

**Response Format**:
```
📅 Неделя 21-25 октября

Понедельник (5 задач, 8ч):
  🔧 Inventum: 3 задачи
  🦷 Lab: 2 задачи

Вторник (3 задачи, 5ч):
  🔬 R&D: 2 задачи
  💼 Trade: 1 задача

Среда (4 задачи, 6ч):
  ...

Четверг (2 задачи, 3ч):
  ...

Пятница (1 задача, 2ч):
  ...

──────────────
Итого: 15 задач, 24 часа
```

---

### /projects

**Purpose**: List all active projects

**Response Format**:
```
📁 Активные проекты

🔧 Inventum:
  • Ремонт фрезера Иванова (3 задачи, до 31.10)
  • Сервисное обслуживание Петрова (2 задачи, до 24.10)

🦷 Inventum Lab:
  • Заказ на 10 коронок (5 задач, до 22.10)

🔬 R&D:
  • Прототип нового наконечника (4 задачи, до 15.11)

💼 Import & Trade:
  • Декабрьская поставка (6 задач, до 01.12)

──────────────
Всего: 5 проектов, 20 задач
```

**Parameters**:
```
/projects - All businesses
/projects inventum - Only Inventum projects
```

---

### /weekly

**Purpose**: Weekly analytics with AI insights (GPT-5)

**Trigger**: User requests weekly review (or automatic every Monday)

**Response Format**:
```
📊 Недельная аналитика (14-20 октября)

✅ Выполнено: 23 задачи
⏱️ Время: 42 часа

По бизнесам:
🔧 Inventum: 10 задач (18ч)
🦷 Lab: 8 задач (15ч)
🔬 R&D: 3 задачи (12ч)
💼 Trade: 2 задачи (3ч)

🎯 Точность оценок: 78% (+5% за неделю!)

💡 Инсайты от AI:
• Вторник - самый продуктивный день
• R&D задачи стабильно занимают на 15% больше времени
• Inventum: отличная точность оценок (85%)

🎯 Рекомендации:
• Планировать сложные R&D задачи на вторник
• Для Inventum выездов закладывать +30 минут на дорогу
• Делегировать больше задач Максуту

──────────────
Отличная неделя! 🎉
```

**Note**: Uses **GPT-5** (not Nano) for deep analysis

---

### /help

**Purpose**: Show help and available commands

**Response**:
```
📖 Помощь - Business Planner

🎤 Создание задач:
Отправьте голосовое сообщение:
"Завтра утром Дима должен починить фрезер"

Или текстом:
"Позвонить поставщику до конца недели"

📋 Команды:
/today - Задачи на сегодня
/tomorrow - Задачи на завтра
/week - Обзор недели
/projects - Список проектов
/weekly - Недельная аналитика
/help - Эта справка

✏️ Действия с задачами:
• Отметить выполненной: нажмите ✅
• Изменить: нажмите ✏️
• Удалить: нажмите 🗑️

💡 Бизнесы:
🔧 Inventum - Ремонт оборудования
🦷 Inventum Lab - Лаборатория
🔬 R&D - Разработка
💼 Import & Trade - Импорт

Вопросы? Напишите @support
```

---

## 🎤 Voice Message Handling

### Flow

```
User sends voice message
    ↓
Bot receives via webhook
    ↓
"🎧 Обрабатываю..." (typing action)
    ↓
Whisper API transcription (~2 sec)
    ↓
GPT-5 Nano parsing (~1 sec)
    ↓
RAG time estimation (~1 sec)
    ↓
Create task in DB (~0.5 sec)
    ↓
Send confirmation (~0.5 sec)
    ↓
Total: ~5 seconds ✅
```

### Response Format

**Success**:
```
✅ Создал задачу:

📞 Позвонить поставщику фрез

💼 Бизнес: Import & Trade
📁 Проект: Декабрьская поставка
👤 Кому: Слава
📅 Завтра, пятница 09:00
⏱️ ~45 минут (на основе 3 похожих звонков)

[Inline Buttons]
[✅ Выполнено] [✏️ Изменить] [🗑️ Удалить]
```

**Parsing Error**:
```
❌ Не удалось распознать задачу

Пожалуйста, уточните:
• Что нужно сделать?
• Для какого бизнеса?

Или отправьте текстом:
"Позвонить поставщику для Trade до завтра"
```

---

## ✏️ Text Message Handling

### Flow
Same as voice, but skip Whisper transcription

### Examples

**Simple task**:
```
User: "Починить фрезер"

Bot:
✅ Создал задачу:
🔧 Inventum: Починить фрезер
📅 24.10 (через 7 дней)
⏱️ ~2 часа
```

**Detailed task**:
```
User: "Максим, сделай диагностику платы для Иванова завтра к обеду, проект Ремонт фрезера Иванова"

Bot:
✅ Создал задачу:
🔧 Inventum: Диагностика платы для Иванова
👤 Максим
📁 Ремонт фрезера Иванова
📅 Завтра 13:00
⏱️ ~1.5 часа
```

---

## 🔘 Inline Buttons (Callback Queries)

### Task Actions

Every task message includes action buttons:

```
[✅ Выполнено] [✏️ Изменить] [🗑️ Удалить]
```

### Callback Data Format
```
complete_{task_id}
edit_{task_id}
delete_{task_id}
```

### Handlers

#### Complete Button
```
User clicks: ✅ Выполнено

Bot asks:
"⏱️ Сколько времени заняло?

Отправьте число минут или:
• 30 мин
• 1.5 часа
• 2ч 15м"

User responds: "2 часа"

Bot:
"✅ Отлично! Задача выполнена за 2 часа.
📊 Точность оценки: 93% (оценка была 2ч 10м)"
```

#### Edit Button
```
User clicks: ✏️ Изменить

Bot:
"Что изменить?
1️⃣ Название
2️⃣ Дедлайн
3️⃣ Кому назначено
4️⃣ Приоритет"

User chooses, bot guides through edit
```

#### Delete Button
```
User clicks: 🗑️ Удалить

Bot:
"Удалить задачу 'Починить фрезер'?

[Да, удалить] [Отмена]"

User confirms → Task archived
```

---

## 🔔 Notifications (Future Phase)

### Daily Reminder (Morning)
```
🌅 Доброе утро, Константин!

Сегодня 5 задач:
🔴 2 срочных
🟡 3 запланированных

Общее время: ~7 часов

/today - посмотреть все задачи
```

### Deadline Reminder
```
⏰ Напоминание

Через 1 час дедлайн:
🔧 "Ремонт главного вала"

Успеете? 😊
```

### Weekly Report (Monday Morning)
```
📊 Недельный отчет готов!

/weekly - посмотреть аналитику
```

---

## 🎯 Error Messages

### Voice Recognition Failed
```
🎤 Не удалось распознать голосовое сообщение

Возможные причины:
• Слишком тихо
• Фоновый шум
• Слишком быстро

Попробуйте еще раз или напишите текстом
```

### Business Detection Failed
```
❓ Не могу определить бизнес

Для какого бизнеса эта задача?

[🔧 Inventum] [🦷 Lab]
[🔬 R&D] [💼 Trade]
```

### Rate Limit
```
⚠️ Слишком много сообщений

Подождите минуту и попробуйте снова
```

### API Error
```
❌ Произошла ошибка

Попробуйте позже или напишите @support
```

---

## 📱 Message Types Handled

### 1. Voice Messages ⭐
- **Primary input method**
- Max 2 minutes (120 seconds)
- Russian language
- Processed via Whisper → GPT-5 Nano

### 2. Text Messages
- **Alternative input**
- Parsed same as voice transcript
- Supports commands (/today, etc.)

### 3. Commands
- **10 commands** (see above)
- Help and navigation

### 4. Callback Queries
- **Inline button presses**
- Task actions (complete, edit, delete)
- Navigation buttons

### 5. Replies
- **Conversational context**
- Edit flows
- Confirmations

---

## 🎨 Message Formatting

### Markdown/HTML Support
```python
# Telegram supports HTML
await bot.send_message(
    chat_id=chat_id,
    text="<b>Создал задачу:</b>\n<i>Починить фрезер</i>",
    parse_mode='HTML'
)

# Or Markdown
await bot.send_message(
    text="*Создал задачу:*\n_Починить фрезер_",
    parse_mode='MarkdownV2'
)
```

### Emojis
Used extensively for visual clarity:
- 🔧 Inventum
- 🦷 Inventum Lab
- 🔬 R&D
- 💼 Import & Trade
- 🔴 Urgent (Priority 1)
- 🟡 Scheduled (Priority 2)
- ✅ Done
- ⏱️ Time
- 📅 Date
- 👤 Person

---

## 🔄 Conversation Flows

### Create Task Flow

```
User: [voice] "Дима должен починить фрезер завтра"
    ↓
Bot: "🎧 Обрабатываю..." (typing action)
    ↓ (3-5 seconds)
Bot: 
"✅ Создал задачу:
🔧 Inventum: Починить фрезер
👤 Дима
📅 Завтра 09:00
⏱️ ~2 часа

[✅ Выполнено] [✏️ Изменить] [🗑️ Удалить]"
```

### Complete Task Flow

```
User: Clicks [✅ Выполнено]
    ↓
Bot: "⏱️ Сколько времени заняло?"
    ↓
User: "2ч 30м"
    ↓
Bot: 
"✅ Отлично! Задача выполнена.
⏱️ Время: 2ч 30м
📊 Оценка была: 2ч (точность 83%)

Система учла это для будущих оценок! 🎯"
```

### Edit Task Flow

```
User: Clicks [✏️ Изменить]
    ↓
Bot: "Что изменить?"
     [Название] [Дедлайн] [Кому] [Приоритет]
    ↓
User: Clicks [Дедлайн]
    ↓
Bot: "Когда нужно сделать?"
    ↓
User: "Послезавтра вечером"
    ↓
Bot: "✅ Дедлайн обновлен: 19.10 в 18:00"
```

---

## ⚡ Quick Actions (Without Commands)

### Natural Language Understanding

```
User: "Что на сегодня?"
Bot: (same as /today)

User: "Покажи проекты"
Bot: (same as /projects)

User: "Аналитика за неделю"
Bot: (same as /weekly)

User: "Выполнил задачу ремонт фрезера за 2 часа"
Bot: Finds task, marks complete
```

**Implementation**: NLU layer using GPT-5 Nano

---

## 🎯 Response Time Goals

| Action | Target | Actual |
|--------|--------|--------|
| Command response | < 2 sec | ~1 sec ✅ |
| Voice → Task | < 10 sec | ~5 sec ✅ |
| Text → Task | < 5 sec | ~3 sec ✅ |
| Button press | < 1 sec | ~0.5 sec ✅ |
| /weekly (GPT-5) | < 15 sec | ~10 sec ✅ |

---

## 🔒 Security

### User Verification
```python
async def verify_user(telegram_id: int) -> User:
    """Verify user is authorized."""
    
    user = await user_repo.get_by_telegram_id(telegram_id)
    
    if not user:
        raise UnauthorizedError(
            "Unauthorized. Contact @admin to get access."
        )
    
    return user
```

**Current**: Only Константин has access  
**Future**: Can add team members (8 people)

### Webhook Signature Validation
See ADR-007 for details

---

## 📊 Usage Analytics

### Log All Interactions
```python
logger.info(
    "telegram_interaction",
    user_id=user.id,
    interaction_type="voice_message",
    business_detected=business_id,
    processing_time_ms=processing_time,
    success=True
)
```

### Metrics to Track
- Messages per day
- Voice vs text ratio
- Command usage frequency
- Error rate
- Processing time

---

## 🧪 Testing Telegram Commands

### Unit Tests
```python
async def test_start_command():
    """Test /start command response."""
    update = create_mock_update(text="/start")
    
    await start_command(update, context)
    
    # Verify welcome message sent
    assert "Привет" in sent_message
    assert "4 бизнеса" in sent_message


async def test_today_command_filters_business():
    """Test /today with business filter."""
    # Create tasks in different businesses
    await create_test_tasks()
    
    # Request Inventum only
    update = create_mock_update(text="/today inventum")
    
    await today_command(update, context)
    
    # Verify only Inventum tasks shown
    assert "🔧 Inventum" in sent_message
    assert "🦷 Lab" not in sent_message
```

---

## 📖 References

- ADR-007: Telegram Architecture
- Telegram Bot API: https://core.telegram.org/bots/api
- python-telegram-bot: https://python-telegram-bot.org/

---

**Status**: ✅ Telegram Commands Specification Complete  
**Total Commands**: 7 main commands  
**Message Types**: 5 (voice, text, commands, callbacks, replies)  
**Response Time**: < 10 seconds (voice-to-task)  
**Next**: Pydantic Models (Data Contracts)

