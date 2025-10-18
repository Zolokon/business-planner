# GitHub Actions CI/CD Pipeline - Business Planner

> **Automated testing and deployment**  
> **Created**: 2025-10-17  
> **Platform**: GitHub Actions  
> **Target**: Digital Ocean Droplet

---

## 🎯 CI/CD Strategy

### Goals
- **Automate testing** - Run on every PR
- **Automate deployment** - Deploy on main push
- **Quality gates** - Only deploy if tests pass
- **Fast feedback** - Results in < 5 minutes

### Workflows

1. **CI** (Continuous Integration) - Test on PR
2. **CD** (Continuous Deployment) - Deploy on main push

---

## 📁 GitHub Actions Structure

```
.github/
└── workflows/
    ├── ci.yml          # Testing pipeline
    ├── deploy.yml      # Deployment pipeline
    └── weekly.yml      # Scheduled tasks (optional)
```

---

## ✅ CI Workflow (ci.yml)

### Purpose
Run tests, linting, type checking on every Pull Request

```yaml
name: CI - Tests and Linting

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [develop]

jobs:
  # --------------------------------------------------------------------------
  # Linting and Formatting
  # --------------------------------------------------------------------------
  lint:
    name: Lint and Format Check
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install black isort ruff mypy
          pip install -r requirements.txt
      
      - name: Black (formatting check)
        run: black --check --line-length 100 src/ tests/
      
      - name: isort (import sorting check)
        run: isort --check-only --profile black src/ tests/
      
      - name: Ruff (linting)
        run: ruff check src/ tests/
      
      - name: mypy (type checking)
        run: mypy src/ --strict
  
  # --------------------------------------------------------------------------
  # Unit Tests
  # --------------------------------------------------------------------------
  test:
    name: Unit and Integration Tests
    runs-on: ubuntu-latest
    
    services:
      # PostgreSQL for integration tests
      postgres:
        image: ankane/pgvector:latest
        env:
          POSTGRES_DB: planner_test
          POSTGRES_USER: planner
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      # Redis for integration tests
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql+asyncpg://planner:test@localhost:5432/planner_test
          REDIS_URL: redis://localhost:6379/0
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY_TEST }}
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term \
            --cov-fail-under=80
      
      - name: Upload coverage to Codecov (optional)
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
  
  # --------------------------------------------------------------------------
  # Security Scan
  # --------------------------------------------------------------------------
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Bandit (security linter)
        run: |
          pip install bandit
          bandit -r src/ -ll
      
      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
```

---

## 🚀 CD Workflow (deploy.yml)

### Purpose
Deploy to production on successful merge to main

```yaml
name: CD - Deploy to Production

on:
  push:
    branches: [main]

jobs:
  # --------------------------------------------------------------------------
  # Deploy
  # --------------------------------------------------------------------------
  deploy:
    name: Deploy to Digital Ocean
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Droplet
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DROPLET_IP }}
          username: planner
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/business-planner
            
            # Pull latest code
            git pull origin main
            
            # Update environment
            # (secrets managed separately on server)
            
            # Pull latest images
            docker-compose -f infrastructure/docker/docker-compose.prod.yml pull
            
            # Build and restart
            docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d --build
            
            # Run migrations
            docker-compose -f infrastructure/docker/docker-compose.prod.yml exec -T backend alembic upgrade head
            
            # Health check
            sleep 10
            curl -f http://localhost/health || exit 1
      
      - name: Notify on Telegram (success)
        if: success()
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_CHAT_ID }}
          token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          message: |
            ✅ Deployment successful!
            
            Branch: main
            Commit: ${{ github.event.head_commit.message }}
            Author: ${{ github.event.head_commit.author.name }}
      
      - name: Notify on Telegram (failure)
        if: failure()
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_CHAT_ID }}
          token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          message: |
            ❌ Deployment failed!
            
            Check: https://github.com/${{ github.repository }}/actions
```

---

## 🔐 GitHub Secrets

### Required Secrets

```
Settings → Secrets and variables → Actions

Secrets:
- DROPLET_IP              # Droplet IP address
- SSH_PRIVATE_KEY         # SSH key for deployment
- OPENAI_API_KEY_TEST     # Test API key (limited)
- TELEGRAM_CHAT_ID        # For notifications
- TELEGRAM_BOT_TOKEN      # For notifications (can be same as prod)
```

### How to Add SSH Key

```bash
# On your machine
ssh-keygen -t ed25519 -C "github-actions"

# Copy private key
cat ~/.ssh/id_ed25519
# Add to GitHub Secrets as SSH_PRIVATE_KEY

# Copy public key to Droplet
ssh-copy-id -i ~/.ssh/id_ed25519.pub planner@droplet-ip
```

---

## 📊 Workflow Triggers

### CI Workflow Triggers

```yaml
on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [develop]
```

**When runs**:
- New PR to main/develop
- Push to develop branch
- **NOT** on push to main (that triggers deploy)

### CD Workflow Triggers

```yaml
on:
  push:
    branches: [main]
```

**When runs**:
- Push to main branch
- **Only if CI passed** (protected branch rule)

---

## 🎯 Branch Protection

### Main Branch Rules

```
Settings → Branches → Branch protection rules

Rules for 'main':
✅ Require pull request before merging
✅ Require status checks to pass:
   - lint
   - test
   - security
✅ Require branches to be up to date
✅ Include administrators (even CEO must follow rules!)
□ Require approvals (optional, for team)
```

**Benefit**: Can't break production accidentally

---

## 🔄 Deployment Flow

### Complete Flow

```
1. Developer creates feature branch
   ↓
2. Makes changes, commits
   ↓
3. Pushes to GitHub
   ↓
4. Opens Pull Request to main
   ↓
5. CI runs automatically:
   - Linting (Black, isort, Ruff)
   - Type checking (mypy)
   - Tests (pytest)
   - Security scan
   ↓
6. If CI passes ✅ → Can merge
   If CI fails ❌ → Fix issues
   ↓
7. Merge PR to main
   ↓
8. CD deploys automatically:
   - SSH to Droplet
   - Pull code
   - Build Docker images
   - Restart services
   - Run migrations
   - Health check
   ↓
9. Telegram notification sent
   ✅ Success or ❌ Failure
```

**Total time**: ~5-7 minutes from merge to deployment

---

## 🧪 Testing the Pipeline

### Test CI Locally

```bash
# Install act (run GitHub Actions locally)
# https://github.com/nektos/act

# Run CI workflow
act pull_request

# Run specific job
act pull_request -j test
```

### Test CD (Staging)

```yaml
# Create staging environment
# staging.yml (copy of deploy.yml)

on:
  push:
    branches: [develop]

# Deploy to staging server instead
host: ${{ secrets.STAGING_DROPLET_IP }}
```

---

## 📊 CI/CD Metrics

### Target Times

| Workflow | Target | Typical |
|----------|--------|---------|
| **Linting** | < 1 min | ~30s |
| **Tests** | < 3 min | ~2 min |
| **Security scan** | < 2 min | ~1 min |
| **Deployment** | < 5 min | ~3 min |
| **Total** | < 10 min | ~6 min |

### Success Rate Target

- CI success rate: > 90%
- CD success rate: > 95%
- Rollback frequency: < 5% of deploys

---

## 🔙 Rollback Strategy

### Automatic Rollback

```yaml
# In deploy.yml, add health check
- name: Health check after deploy
  run: |
    for i in {1..5}; do
      if curl -f https://planner.yourdomain.com/health; then
        echo "Deployment successful"
        exit 0
      fi
      echo "Retry $i/5..."
      sleep 10
    done
    
    echo "Deployment failed health check"
    exit 1

# If fails, rollback
- name: Rollback on failure
  if: failure()
  run: |
    ssh planner@$DROPLET_IP "cd /opt/business-planner && git reset --hard HEAD~1 && docker-compose up -d --build"
```

### Manual Rollback

```bash
# SSH to Droplet
ssh planner@droplet-ip

# Check git log
git log --oneline -5

# Rollback to previous version
git reset --hard abc123  # Previous commit

# Rebuild
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d --build
```

---

## 📖 References

- GitHub Actions Docs: https://docs.github.com/en/actions
- Docker: `docs/08-infrastructure/docker/docker-spec.md`
- Terraform: `docs/08-infrastructure/terraform/terraform-spec.md`

---

**Status**: ✅ CI/CD Pipeline Specified  
**Workflows**: 2 (CI, CD)  
**Automation**: Full (test → deploy)  
**Time**: ~6 minutes end-to-end  
**Next**: Monitoring & Security

