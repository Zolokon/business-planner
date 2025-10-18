# ADR-007: Telegram Bot Architecture with Webhooks

**Status**: ✅ Accepted  
**Date**: 2025-10-17  
**Deciders**: Константин (CEO), Development Team  
**Tags**: telegram, bot, webhooks, integration

---

## Context

Business Planner's primary interface is a **Telegram bot**. User (Константин) interacts entirely through Telegram:

### User Interactions
- **Voice messages** - Main input method (90% of tasks)
- **Text messages** - Alternative input
- **Commands** - `/today`, `/weekly`, `/projects`, etc.
- **Inline buttons** - ✅ Complete task, ✏️ Edit, 🗑️ Delete
- **Notifications** - Reminders, weekly reports

### Requirements
- **Always available** - 24/7 uptime
- **Fast response** - < 5 seconds from message to reply
- **Reliable** - No missed messages
- **Secure** - Validate Telegram signature
- **Scalable** - Handle multiple messages if user sends burst

### Scale
- **Users**: 1 (Константин)
- **Messages**: ~20-30 per day
- **Peak**: ~5 messages in quick succession
- **Voice messages**: ~500/month (~1-2 per day)

---

## Decision

We will use **Telegram Bot API with Webhooks** (not long polling).

Bot receives messages via HTTPS webhook → FastAPI endpoint → LangGraph workflows.

---

## Alternatives Considered

### 1. Long Polling
**Description**: Bot actively requests updates from Telegram servers

```python
# Long polling approach
async def main():
    application = Application.builder().token(TOKEN).build()
    
    # Bot polls Telegram every few seconds
    await application.run_polling()
```

**Pros**:
- ✅ Simpler to setup (no HTTPS needed)
- ✅ Works behind firewall/NAT
- ✅ No domain/SSL certificate needed
- ✅ Good for development

**Cons**:
- ❌ **Constant connections**: Bot must stay connected
- ❌ **Resource waste**: Polling even with no messages
- ❌ **Higher latency**: Check every N seconds (1-5 sec delay)
- ❌ **Not production-recommended**: Telegram recommends webhooks
- ❌ **Harder to scale**: One polling process per bot

**Latency**:
```
User sends message → Telegram stores → Bot polls (up to 5 sec) → Process
Total: 0-5 second unnecessary delay
```

**Verdict**: ❌ **Rejected** - Not recommended for production, wasteful

---

### 2. Webhooks (Direct to Application) ⭐
**Description**: Telegram POSTs updates directly to our endpoint

```python
# Webhook approach
@app.post("/webhook/telegram")
async def telegram_webhook(update: dict):
    # Telegram instantly sends message here
    await process_update(update)
    return {"ok": True}
```

**Pros**:
- ✅ **Instant delivery**: Zero polling delay
- ✅ **Efficient**: Only receive messages when sent
- ✅ **Scalable**: Can handle multiple instances
- ✅ **Production-recommended**: Telegram's preferred method
- ✅ **Stateless**: No persistent connection needed

**Cons**:
- ⚠️ **Requires HTTPS**: Need SSL certificate
- ⚠️ **Public endpoint**: Need public IP/domain
- ⚠️ **Validation needed**: Must verify Telegram signature

**Latency**:
```
User sends message → Telegram POSTs instantly → Process
Total: ~100ms (just network)
```

**Verdict**: ✅ **Accepted** - Best for production

---

### 3. Webhooks via Queue (Redis/RabbitMQ)
**Description**: Webhook → Queue → Worker processes

```python
# Webhook pushes to queue
@app.post("/webhook/telegram")
async def telegram_webhook(update: dict):
    await redis.lpush("telegram_updates", json.dumps(update))
    return {"ok": True}

# Separate worker processes queue
async def worker():
    while True:
        update = await redis.brpop("telegram_updates")
        await process_update(update)
```

**Pros**:
- ✅ Decoupled (webhook and processing separate)
- ✅ Can scale workers independently
- ✅ Built-in retry (queue persistence)

**Cons**:
- ❌ **Overkill**: For 1 user, 20 messages/day
- ❌ **Added complexity**: Extra moving part
- ❌ **Slightly higher latency**: Queue adds ~10-50ms
- ❌ **More infrastructure**: Need to manage queue

**Verdict**: ❌ **Rejected** - Over-engineering for our scale

---

### 4. Webhooks with Telegram Bot API Server
**Description**: Self-hosted Telegram Bot API server

**Pros**:
- ✅ Can handle larger files
- ✅ No Telegram cloud dependency
- ✅ More control

**Cons**:
- ❌ **Complexity**: Need to run additional server
- ❌ **Resources**: Requires ~500MB RAM
- ❌ **Maintenance**: Another service to manage
- ❌ **Unnecessary**: Official API is sufficient

**Verdict**: ❌ **Rejected** - Unnecessary complexity

---

## Detailed Rationale

### 1. Why Webhooks Win 🎯

#### Instant Delivery
```
Long Polling:
User → Telegram → Wait → Bot polls → Process
Latency: 0-5 seconds random delay

Webhooks:
User → Telegram → Instant POST → Process
Latency: ~100ms network only
```

**For voice-to-task flow**:
- Voice message → Whisper (2s) → GPT-5 Nano (1s) → Create task (0.5s)
- Total: ~3.5 seconds

With long polling: 3.5s + up to 5s = **8.5 seconds**
With webhooks: **3.5 seconds** ✅

**Goal**: < 10 seconds total → Webhooks essential

---

#### Resource Efficiency

**Long Polling** (constant connection):
```python
# Bot polls every 2 seconds, 24/7
Requests per day: 43,200 polling requests
Actual messages: ~30
Waste: 99.93% of requests are empty
```

**Webhooks** (on-demand):
```python
# Only when user sends message
Requests per day: ~30 webhook calls
Actual messages: ~30
Efficiency: 100%
```

**Winner**: Webhooks - 1000x more efficient

---

### 2. Implementation with python-telegram-bot

#### Setup Webhook
```python
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from fastapi import FastAPI, Request, Response

# FastAPI app
app = FastAPI()

# Telegram application
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Register handlers
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("today", today_command))
telegram_app.add_handler(MessageHandler(filters.VOICE, voice_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT, text_handler))

# Webhook endpoint
@app.post("/webhook/telegram")
async def telegram_webhook(request: Request) -> Response:
    """Receive updates from Telegram."""
    
    # Get update from request
    update_data = await request.json()
    
    # Validate signature (security)
    if not validate_telegram_signature(request):
        return Response(status_code=403)
    
    # Process update
    update = Update.de_json(update_data, telegram_app.bot)
    await telegram_app.process_update(update)
    
    return Response(status_code=200)


# Set webhook on startup
@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{BASE_URL}/webhook/telegram"
    await telegram_app.bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True  # Ignore old messages on restart
    )
    logger.info(f"Webhook set to {webhook_url}")


# Remove webhook on shutdown
@app.on_event("shutdown")
async def remove_webhook():
    await telegram_app.bot.delete_webhook()
```

---

### 3. Message Flow

#### Voice Message Processing
```
1. User sends voice message
   ↓
2. Telegram POSTs to /webhook/telegram
   {
     "message": {
       "voice": {
         "file_id": "AwACAgIAAxkBAAIC...",
         "duration": 15
       }
     }
   }
   ↓
3. FastAPI validates signature
   ↓
4. voice_handler triggered
   ↓
5. Download voice file from Telegram
   file_bytes = await context.bot.get_file(file_id).download_as_bytearray()
   ↓
6. Trigger LangGraph workflow (ADR-001)
   result = await voice_task_graph.invoke({
     "audio": file_bytes,
     "user_id": user_id
   })
   ↓
7. Send response back to user
   await context.bot.send_message(
     chat_id=chat_id,
     text=f"✅ Создал задачу:\n{result['task'].title}\n..."
   )
```

**Total time**: ~4-5 seconds (within goal) ✅

---

### 4. Security

#### Validate Telegram Requests
```python
import hmac
import hashlib

def validate_telegram_signature(request: Request) -> bool:
    """Verify request is from Telegram."""
    
    # Get secret token
    secret_token = os.getenv("TELEGRAM_SECRET_TOKEN")
    
    # Check X-Telegram-Bot-Api-Secret-Token header
    received_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    
    if not received_token:
        logger.warning("Missing Telegram secret token")
        return False
    
    # Constant-time comparison (prevent timing attacks)
    return hmac.compare_digest(received_token, secret_token)


# Set secret token when creating webhook
await bot.set_webhook(
    url=webhook_url,
    secret_token=TELEGRAM_SECRET_TOKEN  # Random string
)
```

**Security measures**:
- ✅ Secret token validation
- ✅ HTTPS only (SSL certificate)
- ✅ IP whitelist (optional, Telegram IPs: 149.154.160.0/20, 91.108.4.0/22)
- ✅ Rate limiting (per user_id)

---

### 5. Error Handling

#### Retry Strategy
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
async def send_message_with_retry(
    bot: Bot,
    chat_id: int,
    text: str
) -> Message:
    """Send message with automatic retry."""
    try:
        return await bot.send_message(chat_id=chat_id, text=text)
    except TelegramError as e:
        logger.error(f"Failed to send message: {e}")
        raise
```

#### Handle Telegram API Errors
```python
from telegram.error import TelegramError, NetworkError, TimedOut

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Process voice message
        result = await process_voice_message(update.message.voice)
        
        # Send response
        await update.message.reply_text(format_task_response(result))
        
    except NetworkError:
        # Telegram API network issue
        await update.message.reply_text(
            "❌ Ошибка связи. Попробуйте позже."
        )
    except TimedOut:
        # Request timeout
        await update.message.reply_text(
            "⏱️ Превышено время ожидания. Попробуйте еще раз."
        )
    except WhisperAPIError:
        # Voice recognition failed
        await update.message.reply_text(
            "🎤 Не удалось распознать голос. Попробуйте еще раз."
        )
    except Exception as e:
        # Unknown error
        logger.exception("Unexpected error in voice_handler")
        await update.message.reply_text(
            "❌ Произошла ошибка. Попробуйте позже."
        )
```

---

### 6. Rate Limiting

#### Prevent Abuse
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/webhook/telegram")
@limiter.limit("30/minute")  # Max 30 messages per minute
async def telegram_webhook(request: Request):
    ...
```

#### Per-User Rate Limiting
```python
from collections import defaultdict
from datetime import datetime, timedelta

# Simple in-memory rate limiter
user_message_times = defaultdict(list)

async def check_rate_limit(user_id: int, limit: int = 10, window: int = 60) -> bool:
    """Check if user is within rate limit."""
    
    now = datetime.now()
    cutoff = now - timedelta(seconds=window)
    
    # Remove old timestamps
    user_message_times[user_id] = [
        t for t in user_message_times[user_id] if t > cutoff
    ]
    
    # Check limit
    if len(user_message_times[user_id]) >= limit:
        return False
    
    # Add current timestamp
    user_message_times[user_id].append(now)
    return True


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit: 10 messages per minute
    if not await check_rate_limit(user_id, limit=10, window=60):
        await update.message.reply_text(
            "⚠️ Слишком много сообщений. Подождите минуту."
        )
        return
    
    # Process message
    ...
```

---

### 7. Inline Keyboards (Task Actions)

#### Interactive Buttons
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def send_task_with_actions(
    bot: Bot,
    chat_id: int,
    task: Task
):
    """Send task with action buttons."""
    
    text = format_task(task)
    
    # Create inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("✅ Выполнено", callback_data=f"complete_{task.id}"),
            InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_{task.id}"),
        ],
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{task.id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup
    )


# Handle button callbacks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses."""
    
    query = update.callback_query
    await query.answer()  # Acknowledge
    
    # Parse callback_data
    action, task_id = query.data.split("_")
    
    if action == "complete":
        # Mark task complete
        await complete_task(int(task_id))
        await query.edit_message_text("✅ Задача выполнена!")
        
    elif action == "edit":
        # Start edit flow
        await query.edit_message_text("Отправьте новый заголовок задачи:")
        # Set conversation state...
        
    elif action == "delete":
        # Delete task
        await delete_task(int(task_id))
        await query.edit_message_text("🗑️ Задача удалена")
```

---

### 8. Testing Webhooks Locally

#### Development Setup
```python
# For local development, use ngrok to expose localhost

# 1. Start ngrok
# ngrok http 8000

# 2. Get public URL
# https://abc123.ngrok.io

# 3. Set webhook to ngrok URL
await bot.set_webhook("https://abc123.ngrok.io/webhook/telegram")

# 4. Test with real Telegram messages
```

**Alternative**: Use long polling in development
```python
if os.getenv("ENVIRONMENT") == "development":
    # Development: Long polling
    await application.run_polling()
else:
    # Production: Webhooks
    await setup_webhook()
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│           Telegram Servers                  │
│  (User sends message via Telegram app)      │
└─────────────────┬───────────────────────────┘
                  │
                  │ HTTPS POST (instant)
                  ▼
┌─────────────────────────────────────────────┐
│         Digital Ocean Droplet               │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Nginx (SSL Termination)             │  │
│  │  - Validates HTTPS                   │  │
│  │  - Forwards to backend               │  │
│  └────────────┬─────────────────────────┘  │
│               │                             │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │  FastAPI Backend                     │  │
│  │  /webhook/telegram endpoint          │  │
│  │  - Validates Telegram signature      │  │
│  │  - Rate limiting                     │  │
│  └────────────┬─────────────────────────┘  │
│               │                             │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │  python-telegram-bot                 │  │
│  │  - Parses Update object              │  │
│  │  - Triggers handlers                 │  │
│  └────────────┬─────────────────────────┘  │
│               │                             │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │  Message Handlers                    │  │
│  │  - voice_handler → LangGraph         │  │
│  │  - text_handler → LangGraph          │  │
│  │  - command_handlers                  │  │
│  └──────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables
```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_SECRET_TOKEN=random-secret-string-for-webhook-validation

# Webhook
WEBHOOK_URL=https://planner.yourdomain.com/webhook/telegram

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=30
MAX_VOICE_MESSAGES_PER_HOUR=100
```

### Bot Settings (BotFather)
```
/setcommands
start - Начало работы
today - Задачи на сегодня
tomorrow - Задачи на завтра  
week - Задачи на неделю
weekly - Недельная аналитика
projects - Список проектов
help - Помощь

/setdescription
Business Planner - голосовой планировщик задач для управления 4 бизнесами

/setabouttext
Создавайте задачи голосом, получайте умные оценки времени, анализируйте продуктивность.
```

---

## Monitoring

### Key Metrics
```python
# Log all webhook calls
logger.info(
    "telegram_webhook_received",
    user_id=user_id,
    message_type=message_type,
    processing_time_ms=processing_time
)

# Track errors
logger.error(
    "telegram_error",
    error_type=type(e).__name__,
    user_id=user_id,
    message_id=message_id
)
```

### Alerts
- Webhook endpoint returns 5xx
- Processing time > 5 seconds
- Error rate > 5%
- Webhook stopped receiving messages (> 1 day silence)

---

## Consequences

### Positive
- ✅ **Instant delivery**: Zero polling delay
- ✅ **Efficient**: Only process actual messages
- ✅ **Production-ready**: Telegram's recommended approach
- ✅ **Scalable**: Stateless, can handle multiple instances
- ✅ **Fast**: Meets < 10 second goal easily
- ✅ **Reliable**: Telegram guarantees delivery
- ✅ **Secure**: HTTPS + secret token validation

### Negative
- ⚠️ **Requires HTTPS**: Need SSL certificate (solved with Let's Encrypt)
- ⚠️ **Public endpoint**: Need to secure properly
- ⚠️ **Testing harder**: Need ngrok or similar for local dev

### Mitigation
- **HTTPS**: Free Let's Encrypt certificate (automatic renewal)
- **Security**: Secret token + rate limiting + validation
- **Testing**: Long polling for local dev, webhooks for production

---

## Success Criteria

Will be considered successful if:
- [ ] Message-to-response time < 5 seconds (95th percentile)
- [ ] Zero missed messages
- [ ] Webhook uptime > 99%
- [ ] Can handle 100 messages/day burst
- [ ] User never notices latency

---

## References

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [Telegram Webhooks Guide](https://core.telegram.org/bots/webhooks)
- ADR-001: LangGraph (workflows triggered by messages)
- ADR-006: Digital Ocean Droplet (hosting)

---

## Review History

- **2025-10-17**: Initial version - Webhooks approach accepted
- **Status**: ✅ Accepted and ready for implementation

---

**Decision**: Use Telegram Bot API with Webhooks  
**Confidence**: Very High (10/10)  
**Risk**: Very Low (standard approach)  
**Impact**: High (primary user interface)  
**Performance**: < 5 second response time achievable  
**Recommendation**: Webhooks in production, long polling in development

