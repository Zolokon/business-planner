# Source Code - Business Planner

> **Application source code**  
> **Architecture**: Domain-Driven Design (DDD)  
> **Created**: 2025-10-17

---

## 📁 Structure

```
src/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
│
├── api/                 # API Layer (FastAPI routes)
│   ├── routes/
│   │   ├── tasks.py
│   │   ├── projects.py
│   │   ├── analytics.py
│   │   └── telegram.py
│   └── dependencies.py  # FastAPI dependencies
│
├── domain/              # Domain Layer (Business Logic - DDD)
│   ├── models/          # Pydantic domain models
│   │   ├── task.py
│   │   ├── project.py
│   │   ├── member.py
│   │   └── user.py
│   ├── services/        # Business services
│   │   ├── task_service.py
│   │   └── project_service.py
│   └── rules/           # Business rules
│       ├── deadline_rules.py
│       └── priority_rules.py
│
├── infrastructure/      # Infrastructure Layer
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py    # SQLAlchemy ORM models
│   │   └── repositories/
│   │       ├── task_repository.py
│   │       └── project_repository.py
│   ├── cache/
│   │   └── redis_client.py
│   └── external/
│       └── openai_client.py
│
├── ai/                  # AI Layer (LangGraph, RAG)
│   ├── graphs/          # LangGraph workflows
│   │   ├── voice_task_creation.py
│   │   └── weekly_analytics.py
│   ├── prompts/         # AI prompt templates
│   ├── parsers/         # AI parsers
│   │   └── task_parser.py
│   └── rag/             # RAG system
│       ├── embeddings.py
│       └── retriever.py
│
├── telegram/            # Telegram Bot Layer
│   ├── bot.py           # Bot instance
│   ├── handlers/        # Message handlers
│   │   ├── voice.py
│   │   ├── commands.py
│   │   └── callbacks.py
│   └── keyboards.py     # Inline keyboards
│
└── utils/               # Utilities
    ├── logger.py        # Structured logging
    └── datetime_utils.py
```

---

## 🏗️ Architecture Layers

### Clean Architecture (DDD)

```
API Layer
  ↓ depends on
Domain Layer (Core - no framework dependencies)
  ↑ used by
Infrastructure Layer (Database, External APIs)
```

**Key Principle**: Domain layer is pure Python, no FastAPI/SQLAlchemy

---

## 📖 References

- **Architecture**: `docs/01-architecture/`
- **Domain Model**: `docs/04-domain/`
- **Coding Rules**: `.cursorrules`

---

## 🚀 Quick Start

```bash
# Install dependencies
make install

# Run application
make run

# Run with debug logging
make run-debug

# Run tests
make test
```

---

**Status**: ✅ Project structure initialized  
**Next**: Implement domain models and repositories

