# Business Planner - AI Voice Task Manager

> Voice-first task management system for entrepreneurs managing multiple businesses via Telegram bot + Web UI

[![Status](https://img.shields.io/badge/status-production-brightgreen)]()
[![AI](https://img.shields.io/badge/AI-GPT--4o--mini-green)]()
[![Deployment](https://img.shields.io/badge/deploy-Digital%20Ocean-blue)]()

**Live**: https://inventum.com.kz | **Bot**: @PM_laboratory_bot

---

## New AI Session? Read [START_HERE.md](START_HERE.md) first!

---

## Overview

**Business Planner** transforms voice messages into structured tasks using AI, eliminating manual data entry while maintaining full control over task organization.

### Key Features

- **Voice-First**: Speak naturally in Russian, AI handles the rest
- **AI-Powered**: GPT-4o-mini for parsing (~0.85s), GPT-4o for analytics
- **Multi-Business**: Manage 4 distinct businesses with context isolation
- **Smart Analytics**: Daily summaries (8 AM), evening reports (7 PM), weekly analytics (Friday 5 PM)
- **Fast**: < 10 seconds from voice to task creation
- **Web UI**: Modern React dashboard with Material-UI

### The 4 Businesses

1. **INVENTUM** - Dental equipment repair
2. **INVENTUM LAB** - Dental laboratory (CAD/CAM)
3. **R&D** - Prototype development
4. **Import & Trade** - Commerce/logistics

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python 3.11+) |
| **Frontend** | React 19 + TypeScript + Material-UI |
| **AI Orchestration** | LangGraph |
| **Voice** | OpenAI Whisper |
| **LLM** | GPT-4o-mini (parsing), GPT-4o (analytics) |
| **Database** | PostgreSQL 15 + pgvector |
| **Cache** | Redis 7 |
| **Bot** | python-telegram-bot |
| **Deployment** | Digital Ocean Droplet + Nginx + systemd |

---

## Project Structure

```
planer_4/
├── src/                      # Backend (FastAPI)
│   ├── main.py               # Application entry point
│   ├── config.py             # Configuration
│   ├── api/routes/           # REST API endpoints
│   ├── domain/models/        # Business logic (DDD)
│   ├── infrastructure/       # Database, external services
│   ├── ai/                   # LangGraph workflows
│   └── telegram/             # Bot handlers
│
├── frontend/                 # Web UI (React + TypeScript)
│   └── src/
│       ├── pages/            # Dashboard, tasks
│       └── components/       # UI components
│
├── docs/                     # Documentation
│   ├── 01-architecture/      # ADRs
│   ├── 02-database/          # Schema
│   ├── 03-api/               # API specs
│   ├── deployment/           # Deploy guide
│   └── archive/              # Historical docs
│
├── tests/                    # Test suite
├── migrations/               # Alembic migrations
├── scripts/                  # Helper scripts
└── infrastructure/           # Docker, Terraform
```

---

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd planer_4
cp .env.example .env
# Edit .env with your API keys

# Run with Docker (development)
docker-compose up -d

# Run backend
python src/main.py

# Run frontend
cd frontend && npm install && npm run dev
```

---

## Cost

| Component | Monthly |
|-----------|---------|
| AI (Whisper + GPT) | $3-5 |
| Digital Ocean Droplet | $6 |
| **Total** | **$9-12** |

---

## Documentation

- [START_HERE.md](START_HERE.md) - Quick context for AI sessions
- [docs/deployment/DEPLOY.md](docs/deployment/DEPLOY.md) - Deployment guide
- [docs/](docs/) - Full technical documentation

---

## Contact

**Project Owner**: Константин (CEO, 4 businesses)
**Location**: Almaty, Kazakhstan

---

**Status**: Production
**Last Updated**: 2025-11-26
