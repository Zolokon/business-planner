# 📋 Business Planner - Master Project Plan

> **Project Status**: 🟡 Phase 0 - Specifications  
> **Start Date**: 17 октября 2025  
> **Target Launch**: TBD  
> **Deployment**: Digital Ocean Droplet ($6/month)

---

## 🎯 Project Overview

**What**: Voice-first task management system for 4 business directions via Telegram bot  
**Core Value**: AI-powered voice → structured tasks with self-learning time estimation  
**Key Innovation**: RAG-based learning isolated by business context  

---

## 📊 Project Status Dashboard

| Phase | Status | Progress | Start Date | End Date |
|-------|--------|----------|------------|----------|
| **Phase 0: Specifications** | 🟡 In Progress | 5% | 17.10.2025 | TBD |
| **Phase 1: Core Development** | ⚪ Not Started | 0% | TBD | TBD |
| **Phase 2: AI Intelligence** | ⚪ Not Started | 0% | TBD | TBD |
| **Phase 3: Deployment** | ⚪ Not Started | 0% | TBD | TBD |
| **Phase 4: Production** | ⚪ Not Started | 0% | TBD | TBD |

**Legend**: ✅ Done | 🟢 In Review | 🟡 In Progress | 🔴 Blocked | ⚪ Not Started

---

## 🗂️ Phase 0: Specifications & Design

**Goal**: Create complete AI-ready specifications before writing code  
**Duration**: ~3 weeks  
**Status**: 🟡 In Progress (5%)

### Week 1: Core Architecture & Foundation

#### 1.1 Project Setup
- [ ] ✅ Project requirements analysis
- [ ] ✅ AI models selection (GPT-5 Nano, GPT-5)
- [ ] ✅ Digital Ocean architecture decision
- [ ] 🟡 Create PROJECT_PLAN.md (this file)
- [ ] ⚪ Create SPEC_CHECKLIST.md
- [ ] ⚪ Create folder structure

#### 1.2 AI Rules & Context (`.cursorrules`)
- [ ] ⚪ Code style rules (Black, isort, type hints)
- [ ] ⚪ Architecture patterns (LangGraph, DDD)
- [ ] ⚪ Naming conventions
- [ ] ⚪ Testing requirements
- [ ] ⚪ Documentation standards
- [ ] ⚪ AI prompting guidelines

#### 1.3 Architecture Decision Records (ADR)
- [ ] ⚪ ADR-001: Why LangGraph over simple chains
- [ ] ⚪ ADR-002: Why GPT-5 Nano for parsing
- [ ] ⚪ ADR-003: Business context isolation strategy
- [ ] ⚪ ADR-004: RAG implementation approach
- [ ] ⚪ ADR-005: Why PostgreSQL + pgvector
- [ ] ⚪ ADR-006: Digital Ocean Droplet deployment ($6/month)
- [ ] ⚪ ADR-007: Telegram Bot architecture

#### 1.4 Database Design
- [ ] ⚪ Entity-Relationship diagram (Mermaid)
- [ ] ⚪ Complete SQL schema with comments
- [ ] ⚪ pgvector configuration
- [ ] ⚪ Indexes strategy
- [ ] ⚪ Migration plan
- [ ] ⚪ Seed data for testing

#### 1.5 Domain Model (DDD)
- [ ] ⚪ Bounded contexts definition (4 businesses)
- [ ] ⚪ Entities specification
- [ ] ⚪ Value Objects
- [ ] ⚪ Aggregates
- [ ] ⚪ Domain Events
- [ ] ⚪ Business Rules documentation

---

### Week 2: API Contracts & AI Specifications

#### 2.1 API Specification
- [ ] ⚪ OpenAPI 3.0 specification (Swagger)
- [ ] ⚪ Telegram Bot commands spec
- [ ] ⚪ Webhook endpoints
- [ ] ⚪ Error codes & handling
- [ ] ⚪ Rate limiting strategy
- [ ] ⚪ Authentication & security

#### 2.2 Data Models (Pydantic)
- [ ] ⚪ Task model with validation
- [ ] ⚪ Project model
- [ ] ⚪ Business model
- [ ] ⚪ User model
- [ ] ⚪ Member model
- [ ] ⚪ Analytics models
- [ ] ⚪ API Request/Response schemas

#### 2.3 LangGraph State Machines
- [ ] ⚪ Voice Task Creation Flow diagram
- [ ] ⚪ Daily Planning Flow diagram
- [ ] ⚪ Task Completion Flow diagram
- [ ] ⚪ Weekly Analytics Flow diagram
- [ ] ⚪ Project Management Flow diagram
- [ ] ⚪ State definitions
- [ ] ⚪ Node specifications

#### 2.4 AI Prompts Library
- [ ] ⚪ Task parser prompt (GPT-5 Nano)
- [ ] ⚪ Business detector prompt
- [ ] ⚪ Deadline parser prompt
- [ ] ⚪ Time estimator prompt (RAG-enhanced)
- [ ] ⚪ Priority calculator prompt
- [ ] ⚪ Daily optimizer prompt
- [ ] ⚪ Weekly analytics prompt (GPT-5)
- [ ] ⚪ Pattern analysis prompt
- [ ] ⚪ Recommendations prompt

#### 2.5 RAG Strategy
- [ ] ⚪ Embedding generation strategy
- [ ] ⚪ Vector search configuration
- [ ] ⚪ Business context filtering
- [ ] ⚪ Similarity threshold tuning
- [ ] ⚪ Historical data structure
- [ ] ⚪ Learning feedback loop

---

### Week 3: Infrastructure & Testing

#### 3.1 Digital Ocean Architecture
- [ ] ⚪ Infrastructure diagram (Mermaid)
- [ ] ⚪ Component specifications
- [ ] ⚪ Networking & security
- [ ] ⚪ Scaling strategy
- [ ] ⚪ Cost estimation

#### 3.2 Infrastructure as Code (Terraform)
- [ ] ⚪ Main configuration
- [ ] ⚪ Droplet setup ($6/month plan)
- [ ] ⚪ Docker + Docker Compose config
- [ ] ⚪ PostgreSQL container
- [ ] ⚪ Redis container
- [ ] ⚪ Networking & firewall
- [ ] ⚪ Monitoring & logging
- [ ] ⚪ Variables & secrets

#### 3.3 Docker Configuration
- [ ] ⚪ Multi-stage Dockerfile
- [ ] ⚪ docker-compose.yml (development)
- [ ] ⚪ docker-compose.prod.yml (production)
- [ ] ⚪ .dockerignore
- [ ] ⚪ Health checks
- [ ] ⚪ Volume management

#### 3.4 CI/CD Pipeline
- [ ] ⚪ GitHub Actions workflow
- [ ] ⚪ Automated testing
- [ ] ⚪ Linting & formatting
- [ ] ⚪ Docker image build
- [ ] ⚪ Auto-deployment to DO
- [ ] ⚪ Rollback strategy

#### 3.5 Monitoring & Security
- [ ] ⚪ Logging strategy (structured JSON)
- [ ] ⚪ Metrics collection
- [ ] ⚪ Alerting rules
- [ ] ⚪ Secrets management
- [ ] ⚪ Environment variables spec
- [ ] ⚪ Backup & restore plan

#### 3.6 Testing Specifications
- [ ] ⚪ BDD test scenarios (Gherkin)
- [ ] ⚪ Unit test strategy
- [ ] ⚪ Integration test plan
- [ ] ⚪ E2E test scenarios
- [ ] ⚪ Test data fixtures
- [ ] ⚪ Quality metrics & coverage

---

## 🚀 Phase 1: Core Development (MVP)

**Goal**: Implement basic voice → task creation loop  
**Duration**: ~2-3 weeks  
**Status**: ⚪ Not Started

### 1.1 Project Bootstrap
- [ ] ⚪ Initialize FastAPI project
- [ ] ⚪ Setup project structure
- [ ] ⚪ Configure dependencies (requirements.txt)
- [ ] ⚪ Setup database connection
- [ ] ⚪ Setup Redis connection
- [ ] ⚪ Configure environment variables

### 1.2 Database Implementation
- [ ] ⚪ Run SQL schema migrations
- [ ] ⚪ Setup pgvector extension
- [ ] ⚪ Create SQLAlchemy models
- [ ] ⚪ Implement repository pattern
- [ ] ⚪ Seed initial data

### 1.3 Telegram Bot Core
- [ ] ⚪ Setup Telegram Bot API
- [ ] ⚪ Implement webhook handler
- [ ] ⚪ Voice message receiver
- [ ] ⚪ Message formatter & sender
- [ ] ⚪ Error handling

### 1.4 Voice Processing Pipeline
- [ ] ⚪ OpenAI Whisper integration
- [ ] ⚪ Audio format handling
- [ ] ⚪ Transcription error handling
- [ ] ⚪ Language detection (Russian)

### 1.5 Task Parser (GPT-5 Nano)
- [ ] ⚪ Implement parser LangGraph node
- [ ] ⚪ Extract task title
- [ ] ⚪ Detect business context
- [ ] ⚪ Parse deadline (smart parsing)
- [ ] ⚪ Identify project
- [ ] ⚪ Structured output validation

### 1.6 Task Management
- [ ] ⚪ Create task endpoint
- [ ] ⚪ Update task endpoint
- [ ] ⚪ Complete task endpoint
- [ ] ⚪ List tasks endpoint
- [ ] ⚪ Task status management

### 1.7 Basic Commands
- [ ] ⚪ /start - Welcome message
- [ ] ⚪ /today - Daily task list
- [ ] ⚪ /help - Help information
- [ ] ⚪ Task completion flow

### 1.8 Testing & QA
- [ ] ⚪ Unit tests for parsers
- [ ] ⚪ Integration tests
- [ ] ⚪ Manual testing scenarios
- [ ] ⚪ Bug fixes

---

## 🧠 Phase 2: AI Intelligence & Learning

**Goal**: Implement RAG, time estimation, smart features  
**Duration**: ~2-3 weeks  
**Status**: ⚪ Not Started

### 2.1 Embeddings & Vector Search
- [ ] ⚪ Generate embeddings for tasks
- [ ] ⚪ Implement vector search
- [ ] ⚪ Business context filtering
- [ ] ⚪ Similarity scoring

### 2.2 Time Estimation (RAG-enhanced)
- [ ] ⚪ Implement RAG pipeline
- [ ] ⚪ Historical task retrieval
- [ ] ⚪ GPT-5 Nano time estimator
- [ ] ⚪ Learning feedback loop
- [ ] ⚪ Accuracy tracking

### 2.3 Smart Deadline Parsing
- [ ] ⚪ Natural language parsing ("завтра утром")
- [ ] ⚪ Workday logic (Mon-Fri)
- [ ] ⚪ Weekend adjustment
- [ ] ⚪ Timezone handling (UTC+5 Almaty)
- [ ] ⚪ Time defaults (утром→09:00, etc.)

### 2.4 Priority System
- [ ] ⚪ Eisenhower matrix implementation
- [ ] ⚪ Urgency detection
- [ ] ⚪ Importance scoring
- [ ] ⚪ Auto-prioritization

### 2.5 Project Management
- [ ] ⚪ Create project command
- [ ] ⚪ Assign tasks to projects
- [ ] ⚪ Project listing
- [ ] ⚪ Project status tracking

### 2.6 Team Member Assignment
- [ ] ⚪ Member database
- [ ] ⚪ Auto-assignment logic
- [ ] ⚪ Business-specific teams
- [ ] ⚪ Task delegation

### 2.7 Daily Plan Optimizer
- [ ] ⚪ /today enhanced view
- [ ] ⚪ Task grouping by business
- [ ] ⚪ Priority sorting
- [ ] ⚪ Time estimation display

---

## 📊 Phase 3: Analytics & Production Features

**Goal**: Weekly analytics, insights, polish  
**Duration**: ~1-2 weeks  
**Status**: ⚪ Not Started

### 3.1 Weekly Analytics (GPT-5)
- [ ] ⚪ /weekly command
- [ ] ⚪ Time tracking per business
- [ ] ⚪ Task completion stats
- [ ] ⚪ Productivity patterns
- [ ] ⚪ Strategic recommendations

### 3.2 Advanced Features
- [ ] ⚪ Task editing via bot
- [ ] ⚪ Task search
- [ ] ⚪ Recurring tasks
- [ ] ⚪ Reminders
- [ ] ⚪ Task notes

### 3.3 User Experience Polish
- [ ] ⚪ Better message formatting
- [ ] ⚪ Emojis & visual hierarchy
- [ ] ⚪ Inline keyboards
- [ ] ⚪ Confirmation dialogs
- [ ] ⚪ Error messages improvement

### 3.4 Performance Optimization
- [ ] ⚪ Caching strategy (Redis)
- [ ] ⚪ Database query optimization
- [ ] ⚪ Vector search tuning
- [ ] ⚪ API response time optimization

---

## 🌊 Phase 4: Digital Ocean Deployment

**Goal**: Deploy to production on Digital Ocean Droplet ($6/month)
**Duration**: ~1 week  
**Status**: ⚪ Not Started

### 4.1 Infrastructure Setup
- [ ] ⚪ Digital Ocean account setup
- [ ] ⚪ Create Droplet (Basic $6/month)
- [ ] ⚪ Run Terraform scripts
- [ ] ⚪ Configure firewall rules
- [ ] ⚪ Setup SSL certificates (Let's Encrypt)
- [ ] ⚪ Configure domain (if needed)

### 4.2 Docker Setup on Droplet
- [ ] ⚪ Install Docker & Docker Compose
- [ ] ⚪ Copy docker-compose.prod.yml
- [ ] ⚪ Setup volumes for data persistence
- [ ] ⚪ Configure environment variables

### 4.3 Database Migration
- [ ] ⚪ Backup local data
- [ ] ⚪ Start PostgreSQL container
- [ ] ⚪ Run migrations
- [ ] ⚪ Verify schema
- [ ] ⚪ Setup automated backups

### 4.4 Deployment
- [ ] ⚪ Build Docker images
- [ ] ⚪ Deploy all containers
- [ ] ⚪ Verify all services running
- [ ] ⚪ Configure secrets
- [ ] ⚪ Setup Nginx reverse proxy

### 4.4 CI/CD Activation
- [ ] ⚪ Connect GitHub repository
- [ ] ⚪ Configure GitHub Actions
- [ ] ⚪ Test automated deployment
- [ ] ⚪ Setup branch protection

### 4.5 Monitoring Setup
- [ ] ⚪ Configure logging
- [ ] ⚪ Setup metrics dashboard
- [ ] ⚪ Create alert rules
- [ ] ⚪ Test alerting

### 4.6 Production Testing
- [ ] ⚪ Smoke tests
- [ ] ⚪ End-to-end testing
- [ ] ⚪ Load testing
- [ ] ⚪ Security audit

### 4.7 Launch
- [ ] ⚪ Soft launch (limited users)
- [ ] ⚪ Monitor for issues
- [ ] ⚪ Bug fixes
- [ ] ⚪ Full production launch

---

## 📈 Success Metrics

### Technical Metrics
- [ ] Task creation speed: < 10 seconds (voice → confirmation)
- [ ] Parsing accuracy: > 90% (business, deadline)
- [ ] Time estimate accuracy: 50% → 80% (over 1 month)
- [ ] API response time: < 2 seconds (95th percentile)
- [ ] Uptime: > 99.5%

### Business Metrics
- [ ] User creates 10+ tasks/day via voice
- [ ] 80% tasks created without manual editing
- [ ] User actively uses /today daily
- [ ] User reviews weekly analytics
- [ ] Time estimate accuracy improves weekly

---

## 🛠️ Technical Stack Reference

### AI Models
- **Voice**: OpenAI Whisper ($0.006/min)
- **Tier 1**: GPT-5 Nano ($0.05/1M tokens) - Parsing, estimation
- **Tier 2**: GPT-5 Nano - Smart logic
- **Tier 3**: GPT-5 - Weekly analytics
- **Embeddings**: text-embedding-3-small ($0.02/1M)

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Orchestration**: LangGraph
- **Database**: PostgreSQL 15 + pgvector
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0

### Infrastructure
- **Platform**: Digital Ocean Droplet ($6/month)
- **Containerization**: Docker + Docker Compose
- **IaC**: Terraform
- **CI/CD**: GitHub Actions
- **Monitoring**: Structured logging + Prometheus (optional)

### Telegram
- **Bot API**: python-telegram-bot
- **Webhook**: FastAPI endpoint

---

## 📝 Notes & Decisions

### 2025-10-17: Project Initialization
- ✅ Reviewed project brief
- ✅ Selected GPT-5 Nano for Tier 1 & 2
- ✅ Selected GPT-5 for Tier 3 (weekly analytics)
- ✅ Decided on Digital Ocean Droplet ($6/month) for hosting
- ✅ Organized project structure (planning/, infrastructure/, docs/)
- ✅ Committed to AI-first development with full specifications
- ✅ Updated cost estimates: ~$9-12/month total

### Next Session
- [ ] Create .cursorrules
- [ ] Start ADR documentation
- [ ] Begin database schema design

---

## 🔗 Related Documents

- `Discription.pdf` - Original project brief
- `docs/00-project-brief.md` - Markdown version of brief
- `SPEC_CHECKLIST.md` - Detailed specification checklist
- `.cursorrules` - AI coding rules
- `docs/01-architecture/` - Architecture documentation
- `docs/08-infrastructure/` - Digital Ocean setup

---

**Last Updated**: 2025-10-17  
**Next Review**: TBD  
**Project Lead**: User + Claude (AI Assistant)

