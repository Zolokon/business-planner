# 🚀 START HERE - Business Planner

> **For New AI Sessions**: Read this FIRST to understand the project context
> **Last Updated**: 2025-10-29
> **Current Phase**: Production + Web UI 🟢

---

## ⚡ Quick Context (30 seconds)

**What**: Voice-first task manager for CEO managing 4 businesses via Telegram bot + Web UI
**User**: Константин (Almaty, Kazakhstan) - manages Inventum, Inventum Lab, R&D, Import & Trade
**Tech Stack**: FastAPI + React + PostgreSQL + GPT-5 Nano + Digital Ocean
**Cost**: $9-12/month (AI + infrastructure)
**Status**: ✅ In production at https://inventum.com.kz
**Interfaces**:
- 🤖 Telegram Bot: @PM_laboratory_bot (fully operational)
- 🌐 Web UI: https://inventum.com.kz (NEW!)

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

**Telegram Bot:**
- ✅ Voice message processing (Whisper → GPT-5 Nano → Task)
- ✅ Task management (/start, /today, /week, /task, /complete)
- ✅ Inline callbacks (Edit, Delete, Complete)
- ✅ Daily summary (8 AM Almaty time)
- ✅ Evening summary (7 PM Almaty time)
- ✅ Weekly analytics (Friday 5 PM)
- ✅ Smart priority detection
- ✅ Business context isolation (4 businesses)

**Web UI (NEW!):**
- ✅ Dashboard with 4 business cards
- ✅ Task list view with filtering by business
- ✅ Real-time task status (open/done)
- ✅ Task completion tracking
- ✅ Responsive Material UI design
- ✅ Direct integration with production database

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

1. **Frontend Development** (Using New Workflow System!)
   - Follow [WORKFLOW_INDEX.md](frontend/WORKFLOW_INDEX.md) for all new features
   - Create components using [TASK_TEMPLATE.md](frontend/TASK_TEMPLATE.md)
   - Apply responsive design with utilities from [src/utils/responsive.ts](frontend/src/utils/responsive.ts)
   - Next features to implement:
     - Task creation form (modal)
     - Task editing functionality
     - Filters and search
     - Charts/analytics dashboard

2. **Complete Phase 5 Testing** (30% remaining)
   - Add command handler tests
   - Add callback handler tests
   - Set up integration tests
   - Configure coverage reporting

3. **Begin Phase 6: Analytics** (0% complete)
   - Weekly analytics implementation
   - Time tracking improvements
   - Performance metrics dashboard

### Future Enhancements
- **Web Interface:**
  - Deploy frontend to production (nginx)
  - Add authentication
  - Kanban board view
  - Real-time updates (WebSocket)
- **Mobile:**
  - React Native app
  - Push notifications
- **Collaboration:**
  - Multi-user support
  - Team dashboards
- **AI:**
  - Advanced RAG (better time estimates)
  - Voice output (text-to-speech responses)

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

**Last Updated**: 2025-10-28
**Status**: 🟢 Production & Operational + 🎨 Web Interface + 🔌 Backend Connected
**Next Review**: After Phase 5 completion

---

## 🎉 Latest Features

### Session 7 (2025-10-28) - LAYOUT FIX & BACKEND CONNECTION! 🔌

**CRITICAL FIX: Layout Architecture Issue** 🐛
- **Problem**: Pages didn't fit screen at 100% zoom
  - Main page needed 125% zoom to reach edges
  - Business tasks page had "strange size"
- **Root Cause**: Vite's default CSS had conflicting centering
  - `body { display: flex; place-items: center; }` in [index.css:25-31](frontend/src/index.css#L25-L31)
  - This centered ALL content, preventing full-width layout
- **Solution**: Removed centering from body element
  ```css
  /* Before */
  body {
    margin: 0;
    display: flex;        ← REMOVED
    place-items: center;  ← REMOVED
    min-width: 320px;
    min-height: 100vh;
  }

  /* After */
  body {
    margin: 0;
    min-width: 320px;
    min-height: 100vh;
  }
  ```
- **Key Insight**: "Мне нужен надежный, фундаментальный инструмент" - Fixed at architecture level, not with workarounds
- **Result**: ✅ Both pages now properly extend to screen edges at 100% zoom

**Backend Integration Complete** 🚀
- **FastAPI Backend**: Running on http://localhost:8000
  - Server: Python 3.11.9, FastAPI 0.104.1, Uvicorn 0.24.0
  - Entry point: [src/main.py](src/main.py)
  - API routes: `/tasks/`, `/health`, `/businesses`, `/members`
- **Frontend Connection**: Configured via [frontend/src/api/client.ts](frontend/src/api/client.ts)
  - Base URL: `http://localhost:8000` (from `VITE_API_URL`)
  - Axios client with interceptors ready
- **CORS**: Enabled in [main.py:100-106](src/main.py#L100-L106)
  - Development: allows all origins (`*`)
  - Production: restricted to specific domain
- **Testing**:
  - ✅ Root endpoint: Returns app info
  - ✅ Tasks endpoint: Returns `[]` (empty, DB not initialized yet)
  - ✅ Frontend can connect to backend
- **Status**: Ready for data integration once DB is initialized

**Development Environment**
- Frontend: Vite dev server on http://localhost:5173
- Backend: FastAPI with hot reload on http://localhost:8000
- Both services running simultaneously in background

**Next Steps**:
- Initialize PostgreSQL database for real data
- Or create mock data for demo
- Test full CRUD operations from frontend

**Files Changed**:
- [frontend/src/index.css](frontend/src/index.css) - Removed body centering

**Architecture Decision**:
- Chose fundamental CSS fix over responsive/adaptive workarounds
- Aligns with Material UI's layout system
- Simple, maintainable solution

---

### Session 6 (2025-10-27) - FRONTEND DEVELOPMENT SYSTEM! 🔧

**MAJOR SYSTEM: Complete Workflow & Responsive Design Framework**

Created comprehensive development infrastructure for structured frontend development:

**🔧 Workflow System (4 documents):**

1. **[WORKFLOW_INDEX.md](frontend/WORKFLOW_INDEX.md)** - Central navigation
   - Process overview (4 stages: Planning → Implementation → Testing → Commit)
   - AI ↔ User interaction patterns
   - Checklists for each stage
   - **START HERE for any new session!**

2. **[DEVELOPMENT_WORKFLOW.md](frontend/DEVELOPMENT_WORKFLOW.md)** - Complete guide (20 min)
   - General development principles
   - Component structure rules
   - Commit message standards
   - Real workflow examples

3. **[WORKFLOW_QUICK.md](frontend/WORKFLOW_QUICK.md)** - Quick reference (1 page)
   - 4-step process
   - Mandatory responsive props
   - Pre-commit checklist
   - **Keep open while working!**

4. **[TASK_TEMPLATE.md](frontend/TASK_TEMPLATE.md)** - Task template
   - Requirements, plan, technical details
   - Completion criteria
   - **Use for each new feature!**

**📐 Responsive Design System (7 documents):**

1. **[RESPONSIVE_INDEX.md](frontend/RESPONSIVE_INDEX.md)** - Navigation
2. **[RESPONSIVE_DESIGN_GUIDE.md](frontend/RESPONSIVE_DESIGN_GUIDE.md)** - Complete guide
3. **[RESPONSIVE_CHEATSHEET.md](frontend/RESPONSIVE_CHEATSHEET.md)** - Quick reference
4. **[EXAMPLES.md](frontend/EXAMPLES.md)** - Code examples
5. **[QUICK_START_RESPONSIVE.md](frontend/QUICK_START_RESPONSIVE.md)** - 15-min implementation
6. **[RESPONSIVE_CHECKLIST.md](frontend/RESPONSIVE_CHECKLIST.md)** - QA checklist
7. **[BREAKPOINTS_VISUAL.md](frontend/BREAKPOINTS_VISUAL.md)** - Visual diagrams

**🛠️ Ready-to-Use Utilities (3 TypeScript files):**

1. **[src/theme/breakpoints.ts](frontend/src/theme/breakpoints.ts)**
   - Breakpoint configuration (xs: 0, sm: 600, md: 900, lg: 1200, xl: 1536)
   - Device widths constants
   - Spacing scale (8px grid)
   - Touch target sizes (44×44px)

2. **[src/theme/index.ts](frontend/src/theme/index.ts)**
   - Centralized theme with light/dark mode
   - Responsive typography (auto-scales by breakpoint)
   - Touch-friendly components (buttons ≥ 44px)
   - Factory function: `createAppTheme(mode)`

3. **[src/utils/responsive.ts](frontend/src/utils/responsive.ts)**
   - 15+ utility functions:
     - `responsivePadding(xs, sm, md, lg)`
     - `responsiveMargin(xs, sm, md, lg)`
     - `responsiveFontSize(base, scale)`
     - `hideOnMobile`, `showOnMobileOnly`
     - `touchFriendlyButton`
     - and more...

**📊 Key Statistics:**
- **Documents created:** 13 files (~150 KB)
- **Code utilities:** 3 TypeScript files
- **Coverage:** Complete workflow + responsive design
- **Time to learn:** 5 min (quick) to 1 hour (deep)

**🎯 How to Use:**

**For AI (next session start):**
```
1. Read WORKFLOW_INDEX.md (refresh process)
2. Ask user: "What are we working on today?"
3. If new feature → create plan from TASK_TEMPLATE.md
4. Follow DEVELOPMENT_WORKFLOW.md step-by-step
5. Apply responsive design automatically (use utils)
```

**For User (Константин):**
```
1. Keep WORKFLOW_QUICK.md open as reference
2. New task → copy TASK_TEMPLATE.md
3. AI follows structured process automatically
4. Check responsiveness: F12 → 375px, 768px, 1440px
```

**🔑 Key Principles:**

1. **Mobile First** - Start with xs, expand to lg
2. **Step-by-Step** - One subtask at a time, verify each
3. **Quality > Speed** - Better slow and correct than fast and broken
4. **Centralized Theme** - Always use `src/theme/index.ts`
5. **Utilities First** - Don't duplicate, use `responsive.ts`
6. **Touch Targets** - All buttons ≥ 44×44px
7. **Documentation** - Code must be understandable in 6 months

**📐 Responsive Breakpoints (Material UI):**
```
xs: 0px      📱 Mobile phones (portrait)
sm: 600px    📱 Tablets (portrait)
md: 900px    📱 Tablets (landscape)
lg: 1200px   💻 Laptops
xl: 1536px   🖥️ Large monitors
```

**🔄 Typical Workflow:**
```
User: "Let's create [feature name]"
AI:   Creates plan (TASK_TEMPLATE.md)
      Breaks into subtasks
      Asks confirmation

User: "Yes"
AI:   Step 1/N: Creates code
      Asks to verify

User: "Works" / "Needs fix"
AI:   Continues / Fixes

...

AI:   All done! Commit message ready:
      feat: [feature]
      - Created X
      - Added Y
      - Tested on xs, md, lg

User: "Commit"
AI:   ✅ Done! What's next?
```

**📝 Updated Files:**
- [frontend/README.md](frontend/README.md) - Added Workflow & Responsive sections

**🎓 Learning Path:**
1. **First time:** Read WORKFLOW_INDEX.md (5 min)
2. **Daily use:** Keep WORKFLOW_QUICK.md open
3. **Deep dive:** Study DEVELOPMENT_WORKFLOW.md (20 min)
4. **Reference:** Use RESPONSIVE_CHEATSHEET.md as needed

**✨ Benefits:**
- ✅ Structured development process
- ✅ Automatic responsive design
- ✅ Quality control at each step
- ✅ Consistent code style
- ✅ Fast development with utilities
- ✅ Clear AI ↔ User communication

---

### Session 5 (2025-10-27) - WEB INTERFACE! 🚀

**MAJOR FEATURE: React + Material UI Web Dashboard**

Created professional web interface for task management:

**Tech Stack:**
- ⚛️ React 18 + TypeScript
- ⚡ Vite (fast build tool)
- 🎨 Material UI (Material Design)
- 🚦 React Router (SPA navigation)
- 📡 Axios (API client)

**Features Implemented:**

1. **Dashboard Page** ([frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx))
   - 4 business cards in 2x2 grid layout
   - Color-coded by business (Inventum: red, Lab: blue, R&D: green, Trade: orange)
   - Real-time statistics: total tasks, high priority, in progress, overdue
   - Hover animations and responsive design
   - Click card → navigate to business tasks

2. **Business Tasks Page** ([frontend/src/pages/BusinessTasks.tsx](frontend/src/pages/BusinessTasks.tsx))
   - Table view of all tasks for selected business
   - Filters: by status (open/in_progress/done), by priority (1-4)
   - Actions: ✅ Complete task, 🗑️ Delete task
   - Deadline highlighting (overdue tasks in red)
   - Shows: title, description, priority chip, status, deadline, executor

3. **Theme System**
   - 🌓 Dark/Light mode toggle (AppBar button)
   - Material Design 3 components
   - Responsive breakpoints (mobile/tablet/desktop)

**Architecture:**
```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          # Axios configuration
│   │   └── tasks.ts           # Tasks API methods
│   ├── pages/
│   │   ├── Dashboard.tsx      # Main dashboard
│   │   └── BusinessTasks.tsx  # Task list by business
│   ├── types/
│   │   └── index.ts           # TypeScript types
│   └── App.tsx                # Main app + routing
├── index.html                  # Added Roboto font + Material Icons
├── .env                        # API URL configuration
└── README.md                   # Full documentation
```

**Development:**
- Local dev server: `npm run dev` → http://localhost:5175
- Backend: FastAPI already has REST API endpoints ready
- CORS configured for `localhost:5173`

**Fixes Applied:**
1. Fixed TypeScript `verbatimModuleSyntax` error in tsconfig
2. Improved responsive layout with adaptive margins/padding
3. Added Google Fonts (Roboto) for Material UI
4. Fixed card heights to be uniform (minHeight: 280px)
5. Added proper spacing between AppBar and content
6. Made grid responsive: 1 column (mobile) → 2 columns (desktop)

**Documentation:**
- Complete README: [frontend/README.md](frontend/README.md)
- Installation guide
- Development setup
- API endpoints reference
- Deployment instructions (nginx configuration)

---

### Session 8 (2025-10-29) - **Production Deployment**

**Completed:**
1. ✅ **Database Integration**: Connected frontend to production PostgreSQL database
   - Created SSH tunnel: `localhost:5433 → production:5432`
   - Updated `.env` with tunneled connection
   - Added `TaskRepository.find_all()` method for fetching all user tasks
   - Fixed `/tasks/` API endpoint to return all tasks when no business filter

2. ✅ **Frontend Deployed to Production**:
   - Built production bundle: `npm run build`
   - Uploaded to server: `/var/www/planner`
   - Configured Nginx to serve frontend + proxy API requests
   - URL: https://inventum.com.kz

3. ✅ **Nginx Configuration**:
   ```nginx
   location / {
       try_files $uri $uri/ /index.html;  # Frontend
   }
   location ~ ^/(tasks|businesses|api) {
       proxy_pass http://127.0.0.1:8000;  # Backend API
   }
   ```

4. ✅ **Git Workflow**:
   - Committed all frontend code + API changes
   - Pushed to GitHub main branch
   - Pulled on production server
   - Restarted backend service

5. ✅ **HTTP Basic Auth Protection** (Security):
   - Added password protection for Web UI
   - Configured Nginx with `auth_basic`
   - Created `.htpasswd` file on server
   - Excluded `/health` and `/telegram/` from auth (for bot)
   - Credentials stored in `WEB_UI_CREDENTIALS.txt` (local only, not in git)
   - Username: `admin` / Password: generated 20-char secure string

**Current Status:**
- 🌐 **Web UI Live**: https://inventum.com.kz
  - 🔐 **Protected**: HTTP Basic Auth (username/password required)
  - 📋 **Credentials**: See `WEB_UI_CREDENTIALS.txt` (not in git)
- 🤖 **Telegram Bot**: Still working (@PM_laboratory_bot)
- 📊 **Real Data**: Frontend shows 15 production tasks (2 open, 13 done)
- 🔒 **SSL**: Let's Encrypt certificates active

**Next Steps for Web:**
- [x] Add authentication - ✅ **DONE** (HTTP Basic Auth)
- [ ] Create task form (add new tasks from web)
- [ ] Add charts/analytics dashboard
- [ ] Implement Kanban board view
- [ ] Add real-time updates (WebSocket)

---

### Session 7 (2025-10-28) - **Web UI Created**
1. **Bug Fix**: Deleted tasks permanently removed from database (hard delete)
   - Changed from soft delete (archived) to permanent deletion
   - User requirement: "когда я удаляю задачу я хочу ее удалить чтобы ее вообще не было"
2. **Database Cleanup**: Manually deleted 1 orphaned archived task from Lab business

### Session 3 (2025-10-22)
1. **Evening Summary at 7 PM** - Shows incomplete tasks with quick action buttons
2. **Bug Fix**: Completed tasks no longer appear in daily summary
3. **Bug Fix**: Date-only deadlines now use 00:00 instead of 23:59
4. **Scheduler**: Now running 3 automated jobs (morning, evening, weekly)
