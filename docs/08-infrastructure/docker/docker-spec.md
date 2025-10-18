# Docker Configuration Specification - Business Planner

> **Containerization strategy**  
> **Created**: 2025-10-17  
> **Tool**: Docker + Docker Compose  
> **Reference**: ADR-006 (All-in-one Droplet)

---

## 🎯 Docker Strategy

**All-in-one** approach:
- All services in Docker containers
- Orchestrated with Docker Compose
- Single server deployment
- Easy development → production transition

---

## 📁 Docker File Structure

```
infrastructure/docker/
├── Dockerfile              # Production image
├── Dockerfile.dev          # Development image
├── docker-compose.yml      # Development setup
├── docker-compose.prod.yml # Production setup
├── .dockerignore           # What to exclude
├── nginx/
│   └── nginx.conf         # Nginx configuration
└── scripts/
    ├── wait-for-it.sh     # Wait for services
    └── entrypoint.sh      # Container entrypoint
```

---

## 🐳 Dockerfile (Production)

### Multi-Stage Build

```dockerfile
# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY alembic.ini ./
COPY migrations/ ./migrations/

# Create non-root user
RUN useradd -m -u 1000 planner && \
    chown -R planner:planner /app

USER planner

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Entrypoint
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Size**: ~300MB (optimized)

---

## 🐳 Docker Compose (Development)

### docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL with pgvector
  postgres:
    image: ankane/pgvector:latest
    container_name: planner_postgres_dev
    environment:
      POSTGRES_DB: planner
      POSTGRES_USER: planner
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U planner"]
      interval: 5s
      timeout: 5s
      retries: 5
  
  # Redis
  redis:
    image: redis:7-alpine
    container_name: planner_redis_dev
    command: redis-server --maxmemory 50mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data_dev:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
  
  # FastAPI Backend
  backend:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.dev
    container_name: planner_backend_dev
    environment:
      - DATABASE_URL=postgresql+asyncpg://planner:devpassword@postgres:5432/planner
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ENVIRONMENT=development
      - DEBUG=true
    ports:
      - "8000:8000"
    volumes:
      - ../../src:/app/src  # Mount source for hot reload
      - ../../migrations:/app/migrations
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data_dev:
  redis_data_dev:

networks:
  default:
    name: planner_network_dev
```

---

## 🐳 Docker Compose (Production)

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  # Nginx (Reverse Proxy)
  nginx:
    image: nginx:alpine
    container_name: planner_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - letsencrypt:/etc/letsencrypt:ro
      - nginx_cache:/var/cache/nginx
    depends_on:
      - backend
    restart: unless-stopped
    mem_limit: 32m
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  
  # PostgreSQL
  postgres:
    image: ankane/pgvector:latest
    container_name: planner_postgres
    environment:
      POSTGRES_DB: planner
      POSTGRES_USER: planner
      POSTGRES_PASSWORD: ${DB_PASSWORD}
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
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  
  # Redis
  redis:
    image: redis:7-alpine
    container_name: planner_redis
    command: redis-server --maxmemory 50mb --maxmemory-policy allkeys-lru --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    mem_limit: 64m
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "2"
  
  # FastAPI Backend
  backend:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile
    container_name: planner_backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://planner:${DB_PASSWORD}@postgres:5432/planner
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_SECRET_TOKEN=${TELEGRAM_SECRET_TOKEN}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=INFO
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    mem_limit: 256m
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"

volumes:
  postgres_data:
  redis_data:
  letsencrypt:
  nginx_cache:

networks:
  default:
    name: planner_network
```

---

## 📝 .dockerignore

```
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build

# Virtual env
venv
env
.venv

# IDE
.vscode
.idea
*.swp

# Testing
.pytest_cache
.coverage
htmlcov

# Docs (not needed in container)
docs/
planning/
*.md
!README.md

# Environment
.env
.env.local

# Other
*.log
.DS_Store
Thumbs.db
```

---

## 🔧 Nginx Configuration

### nginx.conf

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/m;
    limit_req_status 429;
    
    # Upstream
    upstream backend {
        server backend:8000;
    }
    
    # HTTP → HTTPS redirect
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }
    
    # HTTPS
    server {
        listen 443 ssl http2;
        server_name planner.yourdomain.com;
        
        # SSL
        ssl_certificate /etc/letsencrypt/live/domain/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/domain/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers on;
        ssl_ciphers HIGH:!aNULL:!MD5;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Telegram webhook
        location /webhook/telegram {
            limit_req zone=api_limit burst=5;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_read_timeout 30s;
            proxy_connect_timeout 10s;
        }
        
        # API endpoints
        location /api {
            limit_req zone=api_limit burst=10;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Health check
        location /health {
            proxy_pass http://backend;
            access_log off;
        }
        
        # Future: Static files (Web UI)
        # location / {
        #     root /usr/share/nginx/html;
        #     try_files $uri $uri/ /index.html;
        # }
    }
}
```

---

## 🚀 Deployment Commands

### Development

```bash
# Start all services
cd infrastructure/docker
docker-compose up -d

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Stop all
docker-compose down

# Rebuild
docker-compose up -d --build
```

### Production

```bash
# Deploy
cd /opt/business-planner
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d

# Update
git pull origin main
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d --build

# View logs
docker-compose -f infrastructure/docker/docker-compose.prod.yml logs -f backend

# Database migration
docker-compose -f infrastructure/docker/docker-compose.prod.yml exec backend alembic upgrade head
```

---

## 📊 Resource Limits

All services have memory limits for safety:

| Service | RAM Limit | Typical Usage | CPU |
|---------|-----------|---------------|-----|
| Nginx | 32MB | ~20MB | 0.1 |
| Backend | 256MB | ~180MB | 0.5 |
| PostgreSQL | 384MB | ~250MB | 0.3 |
| Redis | 64MB | ~30MB | 0.1 |
| **Total** | **736MB** | **~480MB** | **1.0** |

**Droplet**: 1GB RAM available  
**Used**: ~480MB (48%)  
**Free**: ~520MB (52%) ✅

---

## 🔍 Health Checks

All services have health checks for reliability:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s      # Check every 30 seconds
  timeout: 10s       # Fail if no response in 10s
  retries: 3         # Try 3 times before marking unhealthy
  start_period: 40s  # Grace period on startup
```

**Benefits**:
- Automatic restart if unhealthy
- Docker Compose waits for healthy status
- Prevents cascading failures

---

## 📝 Environment Variables

### .env (Production)

```bash
# PostgreSQL
DB_PASSWORD=secure_random_password_here

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_SECRET_TOKEN=random-secret-for-webhook-validation

# Application
WEBHOOK_URL=https://planner.yourdomain.com/webhook/telegram
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Optional
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## 🔄 Restart Policies

```yaml
restart: unless-stopped
```

**Meaning**:
- Restart if crashes
- Restart on server reboot
- Don't restart if manually stopped

**Benefits**:
- Auto-recovery from errors
- Survives server restart
- Manual control when needed

---

## 📊 Logging Strategy

### Log Drivers

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"    # Max file size
    max-file: "5"      # Keep 5 files
```

**Total log storage**: 50MB × 5 = 250MB max per service

### Log Locations (on Droplet)

```
/var/lib/docker/containers/{container_id}/
└── {container_id}-json.log

# View logs
docker logs planner_backend
docker logs -f --tail 100 planner_backend
```

---

## 🛠️ Utility Scripts

### wait-for-it.sh

```bash
#!/bin/bash
# Wait for service to be ready

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  >&2 echo "Waiting for $host:$port..."
  sleep 1
done

>&2 echo "$host:$port is available"
exec $cmd
```

**Usage**: Ensure PostgreSQL ready before starting backend

---

### entrypoint.sh

```bash
#!/bin/bash
# Container entrypoint script

set -e

# Wait for PostgreSQL
./scripts/wait-for-it.sh postgres 5432

# Run migrations
alembic upgrade head

# Start application
exec "$@"
```

---

## 🧪 Testing Docker Setup

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check all services healthy
docker-compose ps

# Expected output:
# NAME               STATUS             PORTS
# planner_postgres   Up (healthy)       5432/tcp
# planner_redis      Up (healthy)       6379/tcp
# planner_backend    Up (healthy)       8000/tcp

# Test API
curl http://localhost:8000/health

# Test database
docker-compose exec postgres psql -U planner -c "SELECT version();"

# Test Redis
docker-compose exec redis redis-cli ping
```

---

## 📦 Image Registry (Optional)

### Docker Hub (Free)

```bash
# Build
docker build -t username/planner:latest .

# Push
docker push username/planner:latest

# Pull on Droplet
docker pull username/planner:latest
```

### Digital Ocean Container Registry

```bash
# Create registry (via Terraform)
resource "digitalocean_container_registry" "planner" {
  name = "planner"
  subscription_tier_slug = "basic"  # $5/month
}

# Push
docker tag planner registry.digitalocean.com/planner/backend:latest
docker push registry.digitalocean.com/planner/backend:latest
```

**Decision**: Not needed for now (simple git pull + build is fine)

---

## 🎯 Optimization Tips

### 1. Layer Caching

```dockerfile
# ✅ GOOD: Copy requirements first (cache layer)
COPY requirements.txt .
RUN pip install -r requirements.txt  # ← Cached if requirements.txt unchanged

COPY src/ ./src/  # ← Only re-copy if code changed

# ❌ BAD: Copy everything first
COPY . .
RUN pip install -r requirements.txt  # ← Re-runs even if only code changed
```

### 2. Multi-Stage Builds

Reduces final image size by ~40%

### 3. Health Checks

Prevents serving traffic until ready

---

## 📖 References

- Docker Docs: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- ADR-006: Digital Ocean Droplet
- Architecture: `docs/08-infrastructure/digital-ocean-architecture.md`

---

**Status**: ✅ Docker Configuration Specified  
**Images**: 4 containers (Nginx, Backend, PostgreSQL, Redis)  
**Total RAM**: ~480MB (fits in 1GB)  
**Next**: CI/CD Pipeline

