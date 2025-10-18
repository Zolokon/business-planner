# 🎯 Business Planner - AI Voice Task Manager

> Voice-first task management system for entrepreneurs managing multiple businesses via Telegram bot

[![Status](https://img.shields.io/badge/status-specifications-yellow)]()
[![Phase](https://img.shields.io/badge/phase-0-blue)]()
[![AI](https://img.shields.io/badge/AI-GPT--5%20Nano-green)]()
[![Deployment](https://img.shields.io/badge/deploy-Digital%20Ocean-blue)]()

---

## 🚀 **NEW AI SESSION? → Read [START_HERE.md](START_HERE.md) FIRST!**

> **Quick context handoff for AI assistants**: Everything you need to continue work is in [START_HERE.md](START_HERE.md)

---

## 📖 Project Overview

**Business Planner** transforms voice messages into structured tasks using AI, eliminating manual data entry while maintaining full control over task organization. The system learns from historical data to improve time estimates and task categorization.

### 🎯 Key Features

- 🎤 **Voice-First**: Speak naturally, AI handles the rest
- 🤖 **AI-Powered**: GPT-5 Nano for parsing, GPT-5 for analytics
- 🧠 **Self-Learning**: RAG-based time estimation that improves over time
- 🏢 **Multi-Business**: Manage 4 distinct businesses with context isolation
- 📊 **Smart Analytics**: Weekly insights and productivity recommendations
- ⚡ **Fast**: < 10 seconds from voice to task creation

---

## 🏗️ Architecture

### AI Models Strategy

| Tier | Model | Use Case | Cost |
|------|-------|----------|------|
| **Tier 1** | GPT-5 Nano | Task parsing, business detection | $0.05/1M tokens |
| **Tier 2** | GPT-5 Nano | Time estimation, prioritization | $0.05/1M tokens |
| **Tier 3** | GPT-5 | Weekly analytics, insights | Standard pricing |
| **Voice** | Whisper | Speech-to-text transcription | $0.006/min |
| **Embeddings** | text-embedding-3-small | RAG vector search | $0.02/1M tokens |

### Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **AI Orchestration**: LangGraph
- **Database**: PostgreSQL 15 + pgvector
- **Cache**: Redis 7
- **Bot**: python-telegram-bot
- **Deployment**: Digital Ocean Droplet ($6/month)
- **Containerization**: Docker + Docker Compose
- **IaC**: Terraform
- **CI/CD**: GitHub Actions

---

## 📁 Project Structure

```
planer_4/
├── README.md                      # Project overview (you are here)
├── .cursorrules                   # AI coding rules (to be created)
├── .gitignore                     # Git ignore rules
│
├── planning/                      # 📋 Project planning & tracking
│   ├── PROJECT_PLAN.md            # Master plan with timeline
│   ├── SPEC_CHECKLIST.md          # Detailed specification checklist
│   ├── STATUS.md                  # Current status & progress
│   └── GETTING_STARTED.md         # Quick start guide
│
├── docs/                          # 📚 Technical documentation
│   ├── 00-project-brief.md        # Original project brief
│   ├── 01-architecture/           # Architecture & ADRs
│   ├── 02-database/               # Database schemas
│   ├── 03-api/                    # API specifications
│   ├── 04-domain/                 # Domain model (DDD)
│   ├── 05-ai-specifications/      # AI prompts & strategies
│   ├── 06-implementation/         # Implementation guides
│   ├── 07-testing/                # Test scenarios
│   └── 08-infrastructure/         # Digital Ocean & DevOps
│
├── src/                           # 💻 Source code (to be created)
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration
│   ├── api/                       # API endpoints
│   ├── domain/                    # Business logic
│   ├── infrastructure/            # Database, external services
│   ├── ai/                        # LangGraph & AI
│   └── telegram/                  # Telegram bot handlers
│
├── tests/                         # ✅ Tests (to be created)
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
│
├── infrastructure/                # 🌊 Infrastructure as Code
│   ├── terraform/                 # Terraform configs
│   ├── docker/                    # Dockerfiles & compose
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml     # Development
│   │   └── docker-compose.prod.yml
│   └── github/                    # GitHub Actions workflows
│
└── scripts/                       # 🛠️ Helper scripts
    ├── setup.sh                   # Initial setup
    ├── deploy.sh                  # Deployment script
    └── backup.sh                  # Backup script
```

---

## 🚀 Current Status

### Phase 0: Specifications (In Progress)

We're following an **AI-First Development** approach - creating comprehensive specifications before writing code. This enables AI to generate high-quality code with minimal errors.

#### ✅ Completed
- [x] Project requirements analysis
- [x] AI models selection (GPT-5 Nano, GPT-5)
- [x] Digital Ocean Droplet architecture ($6/month)
- [x] Project structure organized
- [x] Planning documents created (planning/ folder)
- [x] Documentation structure ready (docs/ folder)

#### 🟡 In Progress
- [ ] `.cursorrules` - AI coding rules
- [ ] Architecture Decision Records (ADRs)
- [ ] Database schema design

#### ⚪ Next Steps
- [ ] Complete all specifications (3 weeks)
- [ ] Begin core development
- [ ] Deploy to Digital Ocean

**Progress**: ~5% | See [PROJECT_PLAN.md](planning/PROJECT_PLAN.md) for detailed roadmap

---

## 📋 Key Documents

### Planning & Progress
1. **[PROJECT_PLAN.md](planning/PROJECT_PLAN.md)** - Master plan with phases, timeline, and progress tracking
2. **[SPEC_CHECKLIST.md](planning/SPEC_CHECKLIST.md)** - Detailed checklist of all specifications
3. **[STATUS.md](planning/STATUS.md)** - Current status and recent updates
4. **[GETTING_STARTED.md](planning/GETTING_STARTED.md)** - Quick start guide

### Technical Documentation
5. **[docs/00-project-brief.md](docs/00-project-brief.md)** - Complete project brief
6. **[Discription.pdf](Discription.pdf)** - Original project brief (PDF)

---

## 💡 Development Philosophy

### AI-First Development

1. **Specifications First**: Complete specs before coding
2. **Clear Contracts**: Unambiguous interfaces and data models
3. **AI-Friendly**: Documentation that AI can understand and implement
4. **Iterative**: Continuous refinement based on feedback

### Design Principles

- **Voice First**: Optimize for speech, not typing
- **Context Isolation**: Each business is a separate context
- **Learn from Usage**: Self-improving time estimates
- **User Control**: AI assists, user decides
- **Fast & Reliable**: < 10s response, 99.5% uptime

---

## 🎯 Success Metrics

### Technical Metrics
- ⚡ Task creation: **< 10 seconds** (voice → confirmation)
- 🎯 Parsing accuracy: **> 90%** (business, deadline)
- ⏱️ Time estimate accuracy: **50% → 80%** (over 1 month)
- 🚀 API response: **< 2 seconds** (95th percentile)
- 💪 Uptime: **> 99.5%**

### Business Metrics
- 📝 User creates **10+ tasks/day** via voice
- ✅ **80% of tasks** created without manual editing
- 📅 Daily active usage of `/today` command
- 📊 Weekly analytics reviewed
- 📈 Continuous improvement in estimate accuracy

---

## 💰 Cost Estimate

### AI Costs (Monthly, ~300 tasks)
- Voice transcription: ~$1-2
- GPT-5 Nano (parsing): ~$0.30-0.50
- Embeddings: ~$0.50
- GPT-5 (analytics): ~$1-2
- **Total AI**: ~$3-5/month

### Infrastructure (Digital Ocean)
- **Droplet (Basic)**: $6/month
  - 1 GB RAM / 1 vCPU / 25 GB SSD
  - Includes: PostgreSQL + Redis + Backend
  - All-in-one Docker Compose setup
- Backups (optional): +$1.20/month
- **Total Infra**: ~$6-7/month

### **Grand Total**: ~$9-12/month

**Note**: Ultra affordable for managing 4 businesses! Can upgrade Droplet as needed ($12, $18, $24/month options available).

---

## 🛠️ Quick Start (Coming Soon)

Once development is complete:

```bash
# Clone repository
git clone https://github.com/yourusername/planer_4.git
cd planer_4

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run with Docker Compose (Development)
cd infrastructure/docker
docker-compose up

# Deploy to Digital Ocean Droplet
cd infrastructure/terraform
terraform init
terraform apply
```

---

## 📚 Documentation

All documentation is in the `docs/` directory:

- **Architecture**: System design, diagrams, ADRs
- **Database**: Schema, migrations, indexes
- **API**: OpenAPI spec, Telegram commands
- **Domain**: Business rules, entities, events
- **AI**: Prompts, RAG strategy, LangGraph flows
- **Infrastructure**: Digital Ocean, Terraform, CI/CD
- **Testing**: Test scenarios, fixtures, quality metrics

---

## 🤝 Contributing

This is currently a private project. Once specifications are complete and core functionality is implemented, contribution guidelines will be added.

---

## 📄 License

TBD

---

## 📞 Contact

**Project Owner**: Константин (CEO, 4 businesses, team of 8 people)  
**Location**: Almaty, Kazakhstan  
**AI Assistant**: Claude (Anthropic) via Cursor  
**Deployment**: Digital Ocean

---

## 🗺️ Roadmap

### Phase 0: Specifications (Current - Week 1-3)
- Complete all technical specifications
- Create AI-ready documentation
- Design database and API

### Phase 1: Core Development (Week 4-6)
- Voice → Task creation flow
- Telegram bot integration
- Basic commands (/start, /today)

### Phase 2: AI Intelligence (Week 7-9)
- RAG implementation
- Time estimation learning
- Smart features (projects, prioritization)

### Phase 3: Analytics & Polish (Week 10-11)
- Weekly analytics (GPT-5)
- UX improvements
- Performance optimization

### Phase 4: Production Deployment (Week 12)
- Digital Ocean deployment
- Monitoring setup
- Production launch

---

## 🎉 Why This Project?

Traditional task managers require too much manual input. This system understands natural speech, learns from behavior, and respects the complexity of managing multiple businesses. It's not another todo app - it's an AI assistant that grows smarter with every task.

---

**Status**: 🟡 Phase 0 - Creating Specifications  
**Last Updated**: 2025-10-17  
**Next Milestone**: Complete `.cursorrules` and begin ADRs

