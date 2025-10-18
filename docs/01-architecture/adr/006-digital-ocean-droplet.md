# ADR-006: Use Digital Ocean Basic Droplet ($6/month)

**Status**: ✅ Accepted  
**Date**: 2025-10-17  
**Deciders**: Константин (CEO), Development Team  
**Tags**: infrastructure, deployment, cost-optimization, docker

---

## Context

Business Planner needs production hosting for:

### Application Components
- **FastAPI backend** - Python application server
- **PostgreSQL 15** - Database with pgvector (ADR-005)
- **Redis 7** - Cache and session storage
- **LangGraph workflows** - AI orchestration
- **Telegram bot** - Always-on webhook receiver

### Requirements
- **Budget**: As low as possible (entrepreneur mindset)
- **Reliability**: 99%+ uptime
- **Performance**: Handle 500 tasks/month (~0.02 req/min)
- **Scalability**: Ability to grow if needed
- **Simplicity**: Easy to deploy and maintain
- **Security**: SSL, firewall, regular updates

### Scale
- **Users**: 1 (Константин)
- **Traffic**: Very low (~20-30 requests/day)
- **Storage**: < 1GB in first year
- **Memory**: ~500MB application + database
- **CPU**: Minimal (mostly I/O waiting on AI APIs)

---

## Decision

We will deploy on **Digital Ocean Basic Droplet** ($6/month) using Docker Compose.

All services (FastAPI, PostgreSQL, Redis) will run as Docker containers on a single server.

---

## Alternatives Considered

### 1. Digital Ocean App Platform (Managed)
**Description**: Fully managed platform-as-a-service

**Configuration**:
```
App Platform (Web Service): $5/month
Managed PostgreSQL (Basic): $15/month
Managed Redis (Basic): $15/month
Total: $35/month
```

**Pros**:
- ✅ Fully managed (auto-scaling, auto-healing)
- ✅ Zero-downtime deployments
- ✅ Automatic SSL certificates
- ✅ Built-in monitoring
- ✅ No server maintenance
- ✅ GitHub integration (auto-deploy on push)

**Cons**:
- ❌ **Cost**: $35/month (5.8x more expensive)
- ❌ **Overkill**: Designed for high traffic (we have ~20 req/day)
- ❌ **Less control**: Can't customize infrastructure
- ❌ **Network latency**: Services separated (managed DB is external)
- ❌ **Vendor lock-in**: Platform-specific configurations

**Annual Cost**: $420/year

**Verdict**: ❌ **Rejected** - Too expensive for our low-traffic use case

---

### 2. AWS / GCP / Azure
**Description**: Major cloud providers

**Estimated Cost**:
```
AWS:
- EC2 t3.micro: $8-10/month
- RDS (smallest): $15-20/month
- ElastiCache: $15/month
Total: $38-45/month

Similar for GCP and Azure
```

**Pros**:
- ✅ Enterprise-grade infrastructure
- ✅ Extensive services
- ✅ Global presence

**Cons**:
- ❌ **Cost**: $40+/month minimum
- ❌ **Complexity**: Steep learning curve
- ❌ **Overkill**: Designed for large-scale applications
- ❌ **Billing complexity**: Many hidden costs

**Verdict**: ❌ **Rejected** - Overpriced and over-complicated

---

### 3. Heroku
**Description**: Platform-as-a-service (like App Platform)

**Cost**:
```
Heroku:
- Dyno (Basic): $7/month
- Postgres (Basic): $9/month
- Redis (Mini): $15/month
Total: $31/month
```

**Pros**:
- ✅ Very simple to use
- ✅ Git-based deployment

**Cons**:
- ❌ **Cost**: $31/month (5.2x more expensive)
- ❌ **Dyno sleep**: Free tier sleeps after 30 min (need paid)
- ❌ **Less popular**: Fewer resources than DO
- ❌ **Salesforce ownership**: Uncertain future

**Verdict**: ❌ **Rejected** - Expensive, uncertain future

---

### 4. Shared Hosting (cPanel)
**Description**: Traditional web hosting

**Cost**: $5-10/month

**Pros**:
- ✅ Very cheap
- ✅ Simple control panel

**Cons**:
- ❌ **No Docker support**: Can't use our stack
- ❌ **No root access**: Can't install pgvector
- ❌ **No WebSocket**: Telegram webhooks problematic
- ❌ **Limited Python**: Old versions, limited packages
- ❌ **Shared resources**: Performance unpredictable

**Verdict**: ❌ **Rejected** - Technical limitations

---

### 5. VPS (Linode, Vultr, Hetzner)
**Description**: Competitors to Digital Ocean

**Cost**: $5-6/month (similar to DO)

**Pros**:
- ✅ Similar pricing
- ✅ Similar features
- ✅ Good performance

**Cons**:
- ⚠️ **Less documentation**: Fewer tutorials
- ⚠️ **Smaller community**: Less Stack Overflow content
- ⚠️ **Location**: Hetzner (Germany) - far from Kazakhstan

**Verdict**: ⚠️ **Considered but passed** - Digital Ocean has better docs/community

---

### 6. Digital Ocean Basic Droplet + Docker Compose ⭐
**Description**: Single VPS with all services containerized

**Cost**:
```
Basic Droplet: $6/month
- 1 GB RAM
- 1 vCPU (regular performance)
- 25 GB SSD
- 1 TB transfer

Optional: Backups +$1.20/month (20%)

Total: $6-7/month
```

**Pros**:
- ✅ **Extremely affordable**: $6/month (or $72/year)
- ✅ **Full control**: Root access, install anything
- ✅ **Simple**: All-in-one server, no network between services
- ✅ **Fast**: Local communication between containers
- ✅ **Docker native**: Official Docker support
- ✅ **Good documentation**: Extensive tutorials
- ✅ **Large community**: Easy to find help
- ✅ **Easy scaling**: Can upgrade in seconds
- ✅ **Terraform support**: Infrastructure-as-code ready

**Cons**:
- ⚠️ **Manual management**: Need to maintain server
- ⚠️ **Single point of failure**: If Droplet down, everything down
- ⚠️ **Self-managed**: Responsible for updates, security

**Mitigation**:
- **Management**: Docker Compose simplifies (one command deploys)
- **Single point**: Acceptable for MVP, can add replicas later
- **Self-managed**: Automated with scripts, minimal time investment

**Verdict**: ✅ **Accepted** - Best balance of cost, control, and simplicity

---

## Detailed Rationale

### 1. Cost Comparison 💰

#### Annual Infrastructure Costs

| Platform | Monthly | Annual | vs Droplet |
|----------|---------|--------|------------|
| **DO Droplet** | $6 | **$72** | - |
| DO App Platform | $35 | $420 | +$348 (5.8x) |
| AWS | $40 | $480 | +$408 (6.7x) |
| Heroku | $31 | $372 | +$300 (5.2x) |

**Savings**: $300-400/year by choosing Droplet!

**Total Project Cost**:
```
AI (GPT-5 Nano + GPT-5): $3-5/month
Infrastructure (Droplet): $6/month
Total: $9-12/month = $108-144/year ✨
```

**vs. App Platform alternative**:
```
AI: $3-5/month
Infrastructure (App Platform): $35/month
Total: $38-40/month = $456-480/year
```

**Annual Savings**: **$312-372** with Droplet choice! 🎉

---

### 2. Resource Requirements

#### What We Actually Need

**Current Load** (500 tasks/month):
- Requests: ~20-30 per day
- Peak: ~5 requests/hour
- Database: < 100MB
- Memory: ~500-700MB total

**Droplet Resources**:
- RAM: 1 GB (plenty for our needs)
- CPU: 1 vCPU (enough - mostly waiting on AI APIs)
- Storage: 25 GB (we use < 1 GB)
- Transfer: 1 TB (we use < 10 GB)

**Headroom**: 5-10x capacity for growth ✅

#### Resource Allocation Plan

```yaml
services:
  backend:
    mem_limit: 256m      # FastAPI + LangGraph
    cpus: 0.5
    
  postgres:
    mem_limit: 384m      # PostgreSQL + pgvector
    cpus: 0.3
    
  redis:
    mem_limit: 64m       # Redis cache
    cpus: 0.1
    
  nginx:
    mem_limit: 32m       # Reverse proxy
    cpus: 0.1

Total: ~736MB / 1024MB available (72% usage)
```

**Result**: Comfortably fits in $6 Droplet ✅

---

### 3. Deployment Simplicity

#### Docker Compose All-in-One

**Single Command Deployment**:
```bash
# Deploy entire application
docker-compose up -d

# Update application
git pull
docker-compose up -d --build

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend
```

**vs. App Platform**:
- Need to configure in UI
- Separate configs for each service
- Network configuration between services
- Multiple deployment steps

**Winner**: Droplet with Docker Compose (simpler)

---

### 4. Performance

#### Local vs Network

**Droplet (all-in-one)**:
```
FastAPI → PostgreSQL: < 1ms (localhost)
FastAPI → Redis: < 1ms (localhost)
Total internal latency: Negligible
```

**App Platform (managed services)**:
```
App → Managed PostgreSQL: 2-5ms (network)
App → Managed Redis: 2-5ms (network)
Total internal latency: 4-10ms added
```

**Impact**:
- For our use case: Minimal (AI calls are 1-2 seconds)
- But Droplet is still faster ✅

---

### 5. Scaling Strategy

#### Growth Path

**Year 1** (current):
- Droplet: $6/month ✅
- Resources: < 50% used
- Performance: Excellent

**Year 2** (2x growth):
- Same Droplet: $6/month ✅
- Resources: ~70% used
- Performance: Still good

**Year 3** (5x growth):
- Upgrade to $12 Droplet: $12/month
  - 2 GB RAM
  - 1 vCPU
  - 50 GB SSD
- Or add Redis on separate $4 Droplet
- Still cheaper than App Platform!

**Year 4+** (10x growth):
- Option A: Upgrade to $18 Droplet (4GB RAM)
- Option B: Split services across multiple Droplets
- Option C: Move to App Platform (if revenue justifies)

**Key**: Can scale incrementally as needed ✅

---

## Implementation Details

### 1. Server Setup

#### Initial Droplet Creation
```bash
# Using Terraform (Infrastructure as Code)
resource "digitalocean_droplet" "planner" {
  image  = "docker-20-04"  # Docker pre-installed
  name   = "business-planner"
  region = "fra1"          # Frankfurt (closest to Kazakhstan)
  size   = "s-1vcpu-1gb"   # $6/month
  
  ssh_keys = [var.ssh_key_fingerprint]
  
  tags = ["production", "planner"]
  
  # Enable backups (recommended, +$1.20/month)
  backups = true
}

# Firewall
resource "digitalocean_firewall" "planner" {
  name = "planner-firewall"
  
  droplet_ids = [digitalocean_droplet.planner.id]
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0"]  # SSH (consider restricting)
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]  # HTTP
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]  # HTTPS
  }
  
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
  }
}
```

---

### 2. Docker Compose Configuration

#### Production docker-compose.yml
```yaml
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - letsencrypt:/etc/letsencrypt
    depends_on:
      - backend
    restart: unless-stopped
    mem_limit: 32m
  
  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile
    environment:
      - DATABASE_URL=postgresql://planner:${DB_PASSWORD}@postgres:5432/planner
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ENVIRONMENT=production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    mem_limit: 256m
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  # PostgreSQL with pgvector
  postgres:
    image: ankane/pgvector:latest
    environment:
      - POSTGRES_DB=planner
      - POSTGRES_USER=planner
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    mem_limit: 384m
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U planner"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  # Redis Cache
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 50mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    restart: unless-stopped
    mem_limit: 64m
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  letsencrypt:

networks:
  default:
    name: planner_network
```

---

### 3. SSL/HTTPS Setup

#### Let's Encrypt with Certbot
```bash
# Install Certbot
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Obtain SSL certificate (auto-renewal enabled)
certbot --nginx -d planner.yourdomain.com --email your@email.com --agree-tos --non-interactive

# Certbot auto-renews via systemd timer
systemctl status certbot.timer
```

**Cost**: $0 (Let's Encrypt is free) ✅

---

### 4. Deployment Workflow

#### CI/CD with GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Droplet
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DROPLET_IP }}
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/business-planner
            git pull origin main
            docker-compose pull
            docker-compose up -d --build
            docker-compose exec -T backend alembic upgrade head
```

**Deployment time**: ~2-3 minutes
**Downtime**: < 10 seconds (rolling restart)

---

### 5. Backup Strategy

#### Automated Backups
```bash
#!/bin/bash
# /opt/scripts/backup.sh

# Database backup
docker-compose exec -T postgres pg_dump -U planner planner | gzip > "/backups/db_$(date +%Y%m%d_%H%M%S).sql.gz"

# Keep last 7 days
find /backups -name "db_*.sql.gz" -mtime +7 -delete

# Upload to DO Spaces (optional, S3-compatible)
s3cmd put "/backups/db_$(date +%Y%m%d_%H%M%S).sql.gz" s3://planner-backups/
```

**Schedule** (crontab):
```
0 2 * * * /opt/scripts/backup.sh  # Daily at 2 AM
```

**Storage**:
- Local: Last 7 days (~50MB)
- DO Spaces: 30 days (~200MB) - $1/month
- DO Snapshots (optional): Weekly full image - $0.20/week

---

### 6. Monitoring

#### Health Checks
```python
# src/api/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    checks = {
        "status": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
        "ai_api": await check_openai(),
    }
    
    if all(checks.values()):
        return {"status": "healthy", "checks": checks}
    else:
        raise HTTPException(status_code=503, detail=checks)
```

#### External Monitoring
- **UptimeRobot**: Free tier (5 min checks)
- **Better Uptime**: $10/month (1 min checks) - optional
- **DO Monitoring**: Built-in, free

**Alert on**:
- Droplet CPU > 80%
- Memory > 90%
- Disk > 80%
- HTTP 5xx errors

---

## Maintenance

### Regular Tasks

#### Weekly
- ✅ Check logs for errors
- ✅ Verify backups
- ✅ Monitor resource usage

#### Monthly  
- ✅ Update Docker images
- ✅ Review disk usage
- ✅ Check SSL certificate

#### Quarterly
- ✅ Security updates (apt upgrade)
- ✅ Review performance metrics
- ✅ Test backup restoration

**Time investment**: ~1 hour/month

---

## Security

### Hardening Checklist
- ✅ SSH key-only (disable password auth)
- ✅ Firewall (only 22, 80, 443 open)
- ✅ Fail2ban (auto-ban brute force attempts)
- ✅ Automatic security updates
- ✅ Non-root Docker containers
- ✅ Secrets in environment variables (not in code)
- ✅ HTTPS only (HTTP redirects to HTTPS)
- ✅ Regular backups

---

## Consequences

### Positive
- ✅ **Ultra-low cost**: $6/month = $72/year
- ✅ **Savings**: $300-400/year vs alternatives
- ✅ **Full control**: Can customize everything
- ✅ **Simple deployment**: Docker Compose single command
- ✅ **Fast**: No network latency between services
- ✅ **Scalable**: Easy to upgrade as needed
- ✅ **Portable**: Can migrate to any Docker host
- ✅ **Learning**: Good DevOps experience

### Negative
- ⚠️ **Manual management**: Responsible for updates
- ⚠️ **Single point of failure**: No automatic failover
- ⚠️ **Limited redundancy**: One server only
- ⚠️ **Time investment**: ~1 hour/month maintenance

### Mitigation
- **Management**: Automated with scripts, Docker simplifies
- **Single point**: Acceptable for MVP, daily backups
- **Redundancy**: Can add later if needed (load balancer + replica)
- **Time**: Minimal, worth the $300/year savings

---

## When to Migrate

### Stay on Droplet if:
- ✅ Traffic < 1000 requests/day
- ✅ Revenue < $1000/month
- ✅ Team size = 1-2 people
- ✅ Cost sensitivity high

### Consider App Platform if:
- ⚠️ Traffic > 10,000 requests/day
- ⚠️ Revenue > $5000/month
- ⚠️ Team size > 5 people
- ⚠️ Need 99.9% SLA
- ⚠️ Want zero DevOps time

**Our case**: Stay on Droplet for Year 1-2 minimum ✅

---

## Success Criteria

Will be considered successful if:
- [ ] Monthly cost stays at $6-7
- [ ] Uptime > 99% (< 7 hours downtime/month)
- [ ] Deployment takes < 5 minutes
- [ ] Maintenance < 2 hours/month
- [ ] Can handle 5x traffic growth without upgrade

---

## References

- [Digital Ocean Pricing](https://www.digitalocean.com/pricing)
- [Digital Ocean Droplets](https://docs.digitalocean.com/products/droplets/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- ADR-005: PostgreSQL + pgvector
- Infrastructure: `infrastructure/docker/`

---

## Review History

- **2025-10-17**: Initial version - Basic Droplet ($6/month) accepted
- **Status**: ✅ Accepted and ready for implementation

---

**Decision**: Use Digital Ocean Basic Droplet ($6/month) with Docker Compose  
**Confidence**: Very High (10/10)  
**Risk**: Low (proven approach)  
**Impact**: High (core infrastructure decision)  
**Cost Savings**: $300-400/year vs alternatives  
**Trade-off**: Manual management vs cost savings - **worth it**

