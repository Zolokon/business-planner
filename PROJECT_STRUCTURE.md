# 📂 Project Structure - Business Planner

> **Clean, organized, AI-friendly structure**  
> **Updated**: 2025-10-17  
> **Philosophy**: Keep root clean, group by purpose

---

## 🎯 Structure Philosophy

### Why This Organization?

1. **Clean Root** - Only essential files (README, .gitignore, .cursorrules)
2. **Grouped by Purpose** - Related files in dedicated folders
3. **AI-Friendly** - Clear naming, logical hierarchy
4. **Scalable** - Easy to grow without mess
5. **Professional** - Industry best practices

---

## 📁 Complete Structure

```
planer_4/
│
├── 🚀 START_HERE.md                 # ← START HERE for new AI sessions!
├── 📄 README.md                     # Project overview & quick start
├── 🔒 .gitignore                    # Git ignore rules
├── 🤖 .cursorrules                  # AI coding rules (to be created)
├── 📋 Discription.pdf               # Original project brief
├── 📊 PROJECT_STRUCTURE.md          # Complete structure guide (this file)
├── 📝 UPDATES.md                    # Recent changes log
├── 📋 SUMMARY.md                    # Session summary
│
├── 📋 planning/                     # PROJECT PLANNING & TRACKING
│   ├── PROJECT_PLAN.md              # Master plan with timeline
│   ├── SPEC_CHECKLIST.md            # Detailed specification checklist
│   ├── STATUS.md                    # Current project status
│   └── GETTING_STARTED.md           # Quick start guide
│
├── 📚 docs/                         # TECHNICAL DOCUMENTATION
│   ├── 00-project-brief.md          # Project brief (markdown)
│   │
│   ├── 01-architecture/             # Architecture & Decisions
│   │   ├── adr/                     # Architecture Decision Records
│   │   │   ├── 001-langraph.md
│   │   │   ├── 002-gpt5-nano.md
│   │   │   ├── 003-business-isolation.md
│   │   │   ├── 004-rag-strategy.md
│   │   │   ├── 005-postgresql-pgvector.md
│   │   │   ├── 006-digital-ocean-droplet.md
│   │   │   └── 007-telegram-architecture.md
│   │   │
│   │   └── diagrams/                # Mermaid diagrams
│   │       ├── system-overview.md
│   │       ├── langgraph-flows.md
│   │       └── database-schema.md
│   │
│   ├── 02-database/                 # Database Design
│   │   ├── schema.sql               # Complete SQL schema
│   │   ├── seed-data.sql            # Initial data
│   │   └── migrations/              # Database migrations
│   │
│   ├── 03-api/                      # API Specifications
│   │   ├── openapi.yaml             # OpenAPI 3.0 spec
│   │   └── telegram-commands.md     # Bot commands spec
│   │
│   ├── 04-domain/                   # Domain Model (DDD)
│   │   ├── bounded-contexts.md      # Business contexts
│   │   ├── entities.md              # Domain entities
│   │   ├── business-rules.md        # Business logic rules
│   │   └── events.md                # Domain events
│   │
│   ├── 05-ai-specifications/        # AI Configuration
│   │   ├── models-config.md         # Model settings
│   │   ├── rag-strategy.md          # RAG implementation
│   │   ├── langgraph-flows.md       # Workflow specifications
│   │   └── prompts/                 # AI prompts library
│   │       ├── task-parser.md
│   │       ├── business-detector.md
│   │       ├── deadline-parser.md
│   │       ├── time-estimator.md
│   │       ├── priority-calculator.md
│   │       ├── daily-optimizer.md
│   │       └── weekly-analytics.md
│   │
│   ├── 06-implementation/           # Implementation Guides
│   │   ├── project-structure.md     # Code organization
│   │   ├── dependencies.md          # Package requirements
│   │   └── coding-standards.md      # Code style guide
│   │
│   ├── 07-testing/                  # Testing Strategy
│   │   ├── test-scenarios.md        # BDD scenarios
│   │   ├── test-data.md             # Fixtures & mocks
│   │   └── quality-metrics.md       # Success criteria
│   │
│   └── 08-infrastructure/           # Infrastructure Docs
│       ├── digital-ocean.md         # DO setup guide
│       ├── deployment.md            # Deployment process
│       ├── monitoring.md            # Observability
│       └── security.md              # Security practices
│
├── 💻 src/                          # SOURCE CODE (to be created)
│   ├── main.py                      # FastAPI application entry
│   ├── config.py                    # Configuration management
│   │
│   ├── api/                         # API Layer
│   │   ├── __init__.py
│   │   ├── routes/                  # API endpoints
│   │   │   ├── tasks.py
│   │   │   ├── projects.py
│   │   │   └── analytics.py
│   │   └── dependencies.py          # API dependencies
│   │
│   ├── domain/                      # Domain Layer (Business Logic)
│   │   ├── __init__.py
│   │   ├── models/                  # Pydantic models
│   │   │   ├── task.py
│   │   │   ├── project.py
│   │   │   ├── business.py
│   │   │   └── user.py
│   │   ├── services/                # Business services
│   │   │   ├── task_service.py
│   │   │   ├── project_service.py
│   │   │   └── analytics_service.py
│   │   └── rules/                   # Business rules
│   │       ├── deadline_rules.py
│   │       └── priority_rules.py
│   │
│   ├── infrastructure/              # Infrastructure Layer
│   │   ├── __init__.py
│   │   ├── database/                # Database access
│   │   │   ├── connection.py
│   │   │   ├── repositories/
│   │   │   └── models.py            # SQLAlchemy models
│   │   ├── cache/                   # Redis cache
│   │   │   └── redis_client.py
│   │   └── external/                # External services
│   │       └── openai_client.py
│   │
│   ├── ai/                          # AI Layer
│   │   ├── __init__.py
│   │   ├── graphs/                  # LangGraph workflows
│   │   │   ├── voice_task_creation.py
│   │   │   ├── daily_planning.py
│   │   │   └── weekly_analytics.py
│   │   ├── prompts/                 # Prompt templates
│   │   ├── parsers/                 # AI parsers
│   │   │   ├── task_parser.py
│   │   │   ├── business_detector.py
│   │   │   └── deadline_parser.py
│   │   └── rag/                     # RAG system
│   │       ├── embeddings.py
│   │       └── retriever.py
│   │
│   ├── telegram/                    # Telegram Bot Layer
│   │   ├── __init__.py
│   │   ├── bot.py                   # Bot instance
│   │   ├── handlers/                # Message handlers
│   │   │   ├── voice.py
│   │   │   ├── commands.py
│   │   │   └── callbacks.py
│   │   └── keyboards.py             # Inline keyboards
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── logger.py                # Logging setup
│       ├── datetime_utils.py        # Date/time helpers
│       └── validators.py            # Input validation
│
├── ✅ tests/                        # TESTS (to be created)
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   │
│   ├── unit/                        # Unit tests
│   │   ├── test_parsers.py
│   │   ├── test_services.py
│   │   └── test_rules.py
│   │
│   ├── integration/                 # Integration tests
│   │   ├── test_api.py
│   │   ├── test_database.py
│   │   └── test_telegram.py
│   │
│   ├── e2e/                         # End-to-end tests
│   │   └── test_voice_to_task.py
│   │
│   └── fixtures/                    # Test data
│       ├── tasks.py
│       └── projects.py
│
├── 🌊 infrastructure/               # INFRASTRUCTURE AS CODE
│   │
│   ├── terraform/                   # Terraform configs
│   │   ├── main.tf                  # Main configuration
│   │   ├── variables.tf             # Variables
│   │   ├── outputs.tf               # Outputs
│   │   ├── droplet.tf               # Droplet setup ($6/month)
│   │   ├── networking.tf            # Firewall & networking
│   │   └── monitoring.tf            # Monitoring setup
│   │
│   ├── docker/                      # Docker configs
│   │   ├── Dockerfile               # Production image
│   │   ├── Dockerfile.dev           # Development image
│   │   ├── docker-compose.yml       # Development compose
│   │   ├── docker-compose.prod.yml  # Production compose
│   │   ├── .dockerignore            # Docker ignore
│   │   └── nginx/                   # Nginx configs
│   │       └── nginx.conf
│   │
│   └── github/                      # GitHub Actions
│       ├── ci.yml                   # Continuous Integration
│       └── deploy.yml               # Deployment workflow
│
└── 🛠️ scripts/                     # HELPER SCRIPTS
    ├── setup.sh                     # Initial setup script
    ├── deploy.sh                    # Deployment script
    ├── backup.sh                    # Backup script
    ├── test.sh                      # Run tests
    └── db-migrate.sh                # Database migrations
```

---

## 📋 Folder Purposes

### Root Level
| File/Folder | Purpose |
|-------------|---------|
| `START_HERE.md` | **← START HERE!** Quick context for new AI sessions |
| `README.md` | Project overview, quick start |
| `PROJECT_STRUCTURE.md` | Complete structure guide |
| `UPDATES.md` | Recent changes and updates |
| `SUMMARY.md` | Session summary |
| `.gitignore` | Git ignore rules |
| `.cursorrules` | AI coding standards (to be created) |
| `Discription.pdf` | Original project brief |

### `planning/` - Project Management
| File | Purpose |
|------|---------|
| `PROJECT_PLAN.md` | Master plan with 4 phases, timeline |
| `SPEC_CHECKLIST.md` | 28 specification areas, ~200 items |
| `STATUS.md` | Current status, progress tracking |
| `GETTING_STARTED.md` | Quick start guide for new developers |

**Why separate?** Keep planning/tracking separate from technical docs

### `docs/` - Technical Documentation
| Section | Purpose |
|---------|---------|
| `01-architecture/` | System design, ADRs, diagrams |
| `02-database/` | Schema, migrations, seed data |
| `03-api/` | OpenAPI specs, endpoints |
| `04-domain/` | Business logic, DDD models |
| `05-ai-specifications/` | AI models, prompts, RAG |
| `06-implementation/` | Coding guides, standards |
| `07-testing/` | Test strategy, scenarios |
| `08-infrastructure/` | DevOps, deployment docs |

**Why organized?** Each phase has its own section

### `src/` - Source Code
**Clean Architecture** with clear layers:
- **API Layer** - HTTP endpoints
- **Domain Layer** - Business logic (core)
- **Infrastructure Layer** - Database, cache, external services
- **AI Layer** - LangGraph workflows, RAG
- **Telegram Layer** - Bot handlers

**Why layered?** Separation of concerns, testability

### `tests/` - Testing
**Three test levels:**
- **Unit** - Test individual functions
- **Integration** - Test components together
- **E2E** - Test complete workflows

### `infrastructure/` - IaC
**Everything to deploy:**
- **Terraform** - Create Droplet, configure
- **Docker** - Containerization (dev & prod)
- **GitHub** - CI/CD workflows

### `scripts/` - Automation
Helper scripts for common tasks

---

## 🎯 Navigation Guide

### "I'm a NEW AI SESSION"
→ **START WITH `START_HERE.md`** - everything you need!

### "I want to understand the project"
→ Read `README.md` in root

### "I want to see the plan"
→ Go to `planning/PROJECT_PLAN.md`

### "I want to see progress"
→ Check `planning/STATUS.md`

### "I want to understand architecture"
→ Read `docs/01-architecture/`

### "I want to see database design"
→ Look at `docs/02-database/schema.sql`

### "I want to understand AI"
→ Explore `docs/05-ai-specifications/`

### "I want to deploy"
→ Use `infrastructure/terraform/` and `infrastructure/docker/`

### "I want to code"
→ Work in `src/` following structure

### "I want to test"
→ Write tests in `tests/`

---

## 💡 Best Practices

### Do's ✅
- **Keep root clean** - Only essential files
- **Group by purpose** - Related files together
- **Use README in each folder** - Explain what's inside
- **Follow naming conventions** - Consistent names
- **Document as you go** - Update docs with code

### Don'ts ❌
- **Don't scatter files** - Use proper folders
- **Don't mix concerns** - Planning ≠ Code ≠ Infrastructure
- **Don't skip README** - Always document folders
- **Don't use vague names** - Be specific
- **Don't leave orphan files** - Everything has a place

---

## 🔄 Workflow

### Adding New Feature
1. **Plan** → Update `planning/PROJECT_PLAN.md`
2. **Spec** → Document in `docs/`
3. **Code** → Implement in `src/`
4. **Test** → Write tests in `tests/`
5. **Deploy** → Update `infrastructure/` if needed

### Finding Something
1. Check `README.md` for overview
2. Check `planning/STATUS.md` for current work
3. Navigate to appropriate `docs/` section
4. Look in `src/` for implementation

---

## 📊 File Counts

| Category | Folders | Files (planned) |
|----------|---------|-----------------|
| Planning | 1 | 4 |
| Documentation | 8 | ~30 |
| Source Code | ~15 | ~40 |
| Tests | 4 | ~20 |
| Infrastructure | 3 | ~15 |
| Scripts | 1 | ~5 |
| **Total** | **~32** | **~114** |

---

## 🎉 Benefits of This Structure

### For You (Developer)
✅ Always know where to find things  
✅ Easy to navigate  
✅ Clear what's what  
✅ Professional organization  

### For AI (Cursor/Claude)
✅ Clear context boundaries  
✅ Logical file locations  
✅ Easy to generate code  
✅ Consistent patterns  

### For Team
✅ Easy onboarding  
✅ Clear responsibilities  
✅ Scalable structure  
✅ Industry standard  

---

## 📝 Notes

- Structure is **flexible** - can evolve
- Focus on **clarity** over perfection
- **Document changes** when restructuring
- Keep **README.md** in each major folder
- Use **.gitkeep** for empty folders in Git

---

**Last Updated**: 2025-10-17  
**Status**: ✅ Structure Complete  
**Next**: Begin creating specifications

