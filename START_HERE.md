# 🚀 START HERE - Business Planner

> **For New AI Sessions**: Read this FIRST to understand the project context
> **Last Updated**: 2025-10-22
> **Current Phase**: Production + Optimization 🟢

---

## ⚡ Quick Context (30 seconds)

**What**: Voice-first task manager for CEO managing 4 businesses via Telegram bot
**User**: Константин (Almaty, Kazakhstan) - manages Inventum, Inventum Lab, R&D, Import & Trade
**Tech Stack**: FastAPI + LangGraph + PostgreSQL + GPT-5 Nano + Digital Ocean
**Cost**: $9-12/month (AI + infrastructure)
**Status**: ✅ In production at https://inventum.com.kz
**Bot**: @PM_laboratory_bot (fully operational)

---

## 📍 Production Status

### Infrastructure
- **Server**: Digital Ocean Droplet (164.92.225.137)
- **Domain**: https://inventum.com.kz (SSL via Let's Encrypt)
- **Database**: PostgreSQL 15 + pgvector extension
- **Cache**: Redis 7
- **Process**: systemd service (auto-restart)
- **Web Server**: Nginx reverse proxy
- **Telegram**: Webhook configured and working

### Application Status
- ✅ Voice message processing (Whisper → GPT-5 Nano → Task)
- ✅ Task management (/start, /today, /week, /task, /complete)
- ✅ Inline callbacks (Edit, Delete, Complete)
- ✅ Daily summary (8 AM Almaty time)
- ✅ Evening summary (7 PM Almaty time) - NEW! 🎉
- ✅ Weekly analytics (Friday 5 PM)
- ✅ Smart priority detection
- ✅ Business context isolation (4 businesses)

### Monitoring
- **Logs**: `/root/business-planner/app.log`
- **Systemd**: `journalctl -u business-planner -f`
- **Health**: `curl https://inventum.com.kz/health`

---

## 🏗️ Architecture Overview

### Tech Stack
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Voice** | OpenAI Whisper | Russian speech-to-text |
| **AI Parsing** | GPT-5 Nano | Fast task extraction (~0.85s) |
| **AI Analytics** | GPT-5 | Weekly insights & analysis |
| **Backend** | FastAPI | Async REST API |
| **Orchestration** | LangGraph | AI workflow management |
| **Database** | PostgreSQL 15 + pgvector | Vector search for RAG |
| **Cache** | Redis 7 | Session management |
| **Deployment** | Docker + systemd | Container orchestration |
| **Interface** | Telegram Bot API | User interaction |

### Cost Breakdown (Monthly)
- Voice transcription (Whisper): $1-2
- Task parsing (GPT-5 Nano): $0.30-0.50
- Weekly analytics (GPT-5): $1-2
- Embeddings: $0.50
- **AI Total**: $3-5/month
- **Droplet**: $6/month
- **TOTAL**: **$9-12/month** ✨

---

## 👥 Business Context

### The 4 Businesses

**1. INVENTUM (id: 1)** - Dental equipment repair
- Team: Максим (Director), Дима (Master), Максут (Field Service)
- Keywords: фрезер, ремонт, диагностика, сервис
- Location: мастерская

**2. INVENTUM LAB (id: 2)** - Dental laboratory (CAD/CAM)
- Team: Юрий Владимирович (Director), Мария (CAD/CAM Operator)
- Keywords: коронка, моделирование, CAD, CAM, протез
- Location: лаборатория

**3. R&D (id: 3)** - Prototype development
- Team: Максим, Дима (cross-functional from Inventum)
- Keywords: разработка (explicit mention required)
- Location: workshop

**4. IMPORT & TRADE (id: 4)** - Equipment import from China
- Team: Слава (Legal/Accounting)
- Keywords: поставщик, Китай, контракт, таможня, импорт

**Cross-Business Team**:
- Константин (CEO) - manages all 4 businesses
- Лиза (Marketing/SMM) - works across all businesses

**Total Team**: 8 people

---

## 🔄 Core User Flow

```
1. User sends voice message (Russian)
       ↓
2. Whisper API transcribes
       ↓
3. GPT-5 Nano parses task structure
   - title, business_id, deadline, priority, executor
       ↓
4. RAG finds similar tasks (embeddings)
       ↓
5. Task saved to PostgreSQL with vector
       ↓
6. Telegram sends confirmation
   - Shows transcript ("ВЫ СКАЗАЛИ:")
   - Shows task details with action buttons
```

---

## 🎯 Key Features

### Task Creation
- **Voice-first**: Natural Russian speech input
- **Smart parsing**: GPT-5 Nano extracts structure
- **Business detection**: Location keywords + context
- **Priority detection**: Keyword-based (важно, срочно, не важная)
- **Deadline parsing**: Natural language (завтра, в пятницу в 14:00)
- **Executor assignment**: Explicit mention or defaults to CEO

### Task Management
- **Commands**: /today, /week, /task, /complete, /help
- **Inline buttons**: Edit, Delete, Complete, Cancel
- **Filtering**: By business, date, status
- **Status tracking**: open, in_progress, completed

### Automation
- **Daily Summary** (8 AM Almaty time):
  - Grouped by business
  - Color-coded priorities (🔴🟡🟢)
  - Sorted by deadline time, then priority
  - Shows executor and time
  - Hides empty businesses

- **Evening Summary** (7 PM Almaty time) - NEW! 🎉:
  - Shows incomplete tasks (deadline today or overdue)
  - Grouped by business
  - Interactive buttons: "↪️ На завтра" and "✅ Готово"
  - Celebration message if all tasks done
  - Quick actions for each task

- **Weekly Analytics** (Friday 5 PM):
  - Completion metrics
  - Time tracking analysis
  - Insights and recommendations

### Intelligence
- **RAG System**: Learns from past tasks for better time estimates
- **Vector Search**: pgvector for semantic similarity
- **Business Isolation**: Each business has separate context
- **Smart Defaults**: Priority (Средний), deadline (+7 days)

---

## 📊 Development Phases

```
Phase 0: Specifications  [████████████████████████████] 100% ✅
Phase 1: Core Development[████████████████████████████] 100% ✅
Phase 2: Git Setup       [████████████████████████████] 100% ✅
Phase 3: Deployment      [████████████████████████████] 100% ✅
Phase 4: Bug Fixes       [████████████████████████████] 100% ✅
Phase 5: Testing         [█████████████████░░░░░░░░░░░] 70% 🔄
Phase 6: Analytics       [░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0%
```

### Current Status: Phase 5 - Testing (70%)

**Completed:**
- ✅ pytest configuration
- ✅ Database fixtures (SQLite in-memory)
- ✅ 44 unit tests passing
  - Message formatting: 13 tests
  - Task parsing: 11 tests
  - Priority detection: 11 tests
  - Task Repository: 9 tests

**In Progress:**
- ⏳ Command handler tests
- ⏳ Callback handler tests
- ⏳ Integration tests

**Next Steps:**
- Integration tests (end-to-end workflows)
- Coverage reporting setup
- CI/CD pipeline configuration

---

## 📝 Recent Session Summary (2025-10-22)

### Session 3: Bug Fixes & Evening Summary (MAJOR FEATURE)

**1. CRITICAL BUG FIX: Completed tasks in daily summary** 🐛
- **Issue**: Tasks marked as done still appeared in morning summary
- **Root cause**: Status mismatch - `repository` set `status="done"`, but `daily_summary` filtered `status!="completed"`
- **Fix**: Use consistent `"done"` status everywhere (per DB schema)
- **Commit**: [bd0b700](https://github.com/Zolokon/business-planner/commit/bd0b700)

**2. BUG FIX: Artificial 23:59 time for date-only deadlines** 🐛
- **Issue**: System automatically set 23:59 for tasks without explicit time
- **Problem**: Created false impression of precise timing
- **Fix**: Use 00:00 (midnight) for date-only deadlines
  - "завтра" → `2025-10-23 00:00:00` → displays as "23.10.2025"
  - "завтра в 15:00" → `2025-10-23 15:00:00` → displays as "23.10.2025 в 15:00"
- **Files**: [voice_task_creation.py](src/ai/graphs/voice_task_creation.py), [callback_handler.py](src/telegram/handlers/callback_handler.py)
- **Commit**: [4c9236a](https://github.com/Zolokon/business-planner/commit/4c9236a)

**3. Evening Task Summary (7 PM Automation)** 📊
- **User request**: "в конце дня хочу увидеть задачи которые не выполнились"
- **Implementation**:
  - APScheduler cron job at 19:00 (7 PM) Almaty time
  - Shows incomplete tasks with deadline today or overdue
  - Grouped by business, sorted by overdue → priority
  - Interactive buttons for each task:
    - **↪️ На завтра** - Reschedules to tomorrow (keeps time if set)
    - **✅ Готово** - Marks as completed
  - Celebration message if all tasks done: "🎉 ОТЛИЧНАЯ РАБОТА!"
- **Message format**:
  ```
  📊 ИТОГИ ДНЯ (22.10.2025)
  Незавершённые задачи: 3

  МАСТЕРСКАЯ INVENTUM

  🔴 Починить фрезер
  Дедлайн: сегодня, 15:00
  [↪️ На завтра] [✅ Готово]

  🟡 Диагностика станка
  Дедлайн: просрочено (21.10)
  [↪️ На завтра] [✅ Готово]
  ```
- **Testing**:
  - Manual trigger: `POST /trigger-evening-summary`
  - Production test: 4 incomplete tasks shown
  - User tested: 3 tasks completed via buttons ✅
- **Files**:
  - [evening_summary.py](src/services/evening_summary.py) - Core logic
  - [callback_handler.py](src/telegram/handlers/callback_handler.py) - Button handlers
  - [scheduler.py](src/services/scheduler.py) - Job scheduling
  - [system.py](src/api/routes/system.py) - Test endpoint
- **Commit**: [99816f1](https://github.com/Zolokon/business-planner/commit/99816f1)

### Deployment Results
- ✅ All changes deployed to production
- ✅ Scheduler running (3 jobs: daily 8 AM, evening 7 PM, weekly Friday 5 PM)
- ✅ Evening summary tested: 4 tasks sent, 3 completed via buttons
- ✅ Bug fixes verified in production
- ✅ No regressions introduced

---

## 📝 Previous Session Summary (2025-10-20)

### Session 1: Optimizations & Critical Bug Fix

**1. GPT-5 Nano Prompt Optimization** ✨
- 57% token reduction (564 → 245 tokens)
- 10-15% faster response time
- Maintained all critical business logic
- [Documentation](docs/PROMPT_OPTIMIZATION.md)

**2. Transcript Display Feature** 🎯
- Users now see what Whisper recognized
- Two separate messages: transcript + task details
- Builds transparency and trust

**3. CRITICAL BUG FIX: TypedDict Deadline** 🐛
- Issue: Deadline parsed correctly but lost in state flow
- Root cause: TypedDict key mismatch (`parsed_deadline_text` vs `parsed_deadline`)
- Fixed: Renamed TypedDict key to match code usage
- [Post-mortem](docs/BUGS/DEADLINE_TYPEDDICT_BUG.md)

### Session 2: Priority System & Daily Summaries (MAJOR FEATURES)

**4. Smart Priority System** 🎯
- **User feedback**: "Приоритет только большими буквами" + "назначается случайно"
- **Changes**:
  - Title Case formatting: "ВЫСОКИЙ" → "Высокий"
  - Smart keyword detection:
    - HIGH (1): "важно", "важная", "срочно", "ASAP"
    - MEDIUM (2): Default for most tasks
    - LOW (3): "не важно", "не такая важная", "не срочно"
    - BACKLOG (4): "отложить", "потом", "в бэклог"
- **Testing**: 11 test cases covering all priority levels
- **Files**: [voice_task_creation.py:343-347](src/ai/graphs/voice_task_creation.py#L343-L347), [openai_client.py:316-321](src/infrastructure/external/openai_client.py#L316-L321)

**5. Daily Task Summary (8 AM Automation)** 📋
- **User request**: "в 8 утра список задач"
- **Implementation**:
  - APScheduler cron job at 8:00 AM Almaty time (UTC+5)
  - Grouped by business
  - Color-coded priorities: 🔴 Высокий, 🟡 Средний, 🟢 Низкий
  - Sorted by deadline time, then priority
  - Shows executor and time if specified
  - Filters: today/tomorrow only, excludes backlog
- **Message format**:
  ```
  📋 ЗАДАЧИ НА СЕГОДНЯ (21 октября)

  МАСТЕРСКАЯ INVENTUM
  🔴 Починить фрезер (Максим, 10:00)
  🟡 Диагностика оборудования

  Всего: 2 задачи (1 срочная, 1 средняя)
  ```
- **Testing**: Manual trigger via `/trigger-daily-summary`
- **Production**: Tested successfully with 20 tasks
- **Files**: [daily_summary.py](src/services/daily_summary.py), [scheduler.py](src/services/scheduler.py)

**6. Bug Fixes** 🔧
- Wrong telegram_id (found via production logs)
- Task status filter ("open" vs "active")
- Endpoint routing conflict (`/tasks/clear-all` → `/clear-all-tasks`)
- Priority keyword expansion ("не такая важная")

**7. Database Cleanup Endpoint** 🗑️
- `DELETE /clear-all-tasks` for testing/development
- Permanently deletes all user tasks
- [system.py:117-155](src/api/routes/system.py#L117-L155)

### Previous Deployment Results (2025-10-20)
- ✅ All changes deployed to production
- ✅ Scheduler running (2 jobs: daily 8 AM, weekly Friday 5 PM)
- ✅ Daily summary tested: 20 tasks sent successfully
- ✅ 44/44 unit tests passing
- ✅ No regressions introduced

### Business Rules Updated
- **Deadline formatting**: Shows time if specified (e.g., "21.10.2025 в 14:30")
- **Business detection**: Location keywords override team membership
  - "мастерская" → always Inventum (id:1)
  - "лаборатория" → always Inventum Lab (id:2)
  - "разработка" explicitly mentioned → R&D (id:3)
  - Максим/Дима default to Inventum unless "разработка" present
- **Priority assignment**: Smart keyword-based with default to Средний

---

## 🔑 Key Files

### Configuration
- [.env.example](.env.example) - Environment variables template
- [requirements.txt](requirements.txt) - Python dependencies
- [pyproject.toml](pyproject.toml) - Project metadata

### Source Code
- [src/main.py](src/main.py) - FastAPI application entry point
- [src/api/routes/](src/api/routes/) - REST API endpoints
- [src/bot/handlers/](src/bot/handlers/) - Telegram bot handlers
- [src/ai/graphs/](src/ai/graphs/) - LangGraph workflows
- [src/services/](src/services/) - Business logic & scheduler
- [src/infrastructure/](src/infrastructure/) - External services (OpenAI, DB)

### Testing
- [tests/conftest.py](tests/conftest.py) - Shared fixtures
- [tests/unit/](tests/unit/) - Unit tests
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing documentation

### Documentation
- [DEPLOY.md](DEPLOY.md) - Deployment guide
- [docs/TEAM.md](docs/TEAM.md) - Team structure & roles
- [docs/BUSINESS_DETECTION_RULES.md](docs/BUSINESS_DETECTION_RULES.md) - Business detection logic
- [docs/BUGS/](docs/BUGS/) - Bug post-mortems

### Infrastructure
- [docker-compose.prod.yml](docker-compose.prod.yml) - Production Docker setup
- [Dockerfile](Dockerfile) - Application container
- [infrastructure/terraform/](infrastructure/terraform/) - IaC configuration

---

## 🚀 Quick Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/unit/ -v -m unit

# Run application locally
python -m src.main
```

### Production Deployment
```bash
# SSH to server
ssh root@164.92.225.137

# Pull latest code
cd /root/business-planner && git pull origin main

# Restart service
sudo systemctl restart business-planner

# Check status
sudo systemctl status business-planner

# View logs
tail -f /root/business-planner/app.log
journalctl -u business-planner -f
```

### Testing Endpoints
```bash
# Health check
curl https://inventum.com.kz/health

# Trigger daily summary (8 AM)
curl -X POST https://inventum.com.kz/trigger-daily-summary

# Trigger evening summary (7 PM) - NEW!
curl -X POST https://inventum.com.kz/trigger-evening-summary

# Clear all tasks (CAUTION!)
curl -X DELETE https://inventum.com.kz/clear-all-tasks
```

---

## 🎯 Next Steps

### Immediate Priorities
1. **Complete Phase 5 Testing** (30% remaining)
   - Add command handler tests
   - Add callback handler tests
   - Set up integration tests
   - Configure coverage reporting

2. **Begin Phase 6: Analytics** (0% complete)
   - Weekly analytics implementation
   - Time tracking improvements
   - Performance metrics dashboard

### Future Enhancements
- Mobile app (React Native)
- Multi-user support (team collaboration)
- Advanced RAG (better time estimates)
- Voice output (text-to-speech responses)
- Analytics dashboard (web interface)

---

## 📞 Contact & Support

**Production Bot**: @PM_laboratory_bot
**GitHub**: https://github.com/Zolokon/business-planner
**Server**: 164.92.225.137 (Digital Ocean)
**Domain**: https://inventum.com.kz

**User**: Константин (CEO)
**Location**: Almaty, Kazakhstan (UTC+5)
**Team**: 8 people across 4 businesses

---

**Last Updated**: 2025-10-23
**Status**: 🟢 Production & Operational
**Next Review**: After Phase 5 completion

---

## 🎉 Latest Features

### Session 4 (2025-10-23)
1. **Bug Fix**: Archived (deleted) tasks no longer appear in daily summary
2. **Feature Change**: Task deletion now permanently removes tasks (was: archived)
   - User requirement: "когда я удаляю задачу я хочу ее удалить чтобы ее вообще не было"

### Session 3 (2025-10-22)
1. **Evening Summary at 7 PM** - Shows incomplete tasks with quick action buttons
2. **Bug Fix**: Completed tasks no longer appear in daily summary
3. **Bug Fix**: Date-only deadlines now use 00:00 instead of 23:59
4. **Scheduler**: Now running 3 automated jobs (morning, evening, weekly)
