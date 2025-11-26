# Deployment Guide - Business Planner

## Quick Deploy to Digital Ocean

### Prerequisites
- Digital Ocean account
- SSH access to your droplet
- GitHub repository (this repo)

### 1. Create Digital Ocean Droplet

```bash
# Create $6/month droplet (Basic, 1GB RAM, 1 vCPU)
# OS: Ubuntu 22.04 LTS
# Region: Choose closest to Almaty (Frankfurt or Amsterdam recommended)
```

### 2. Initial Server Setup

```bash
# SSH into your droplet
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y git docker.io docker-compose python3-pip

# Start Docker
systemctl start docker
systemctl enable docker

# Add user for deployment (optional but recommended)
adduser planner
usermod -aG sudo planner
usermod -aG docker planner
```

### 3. Clone Repository

```bash
# Switch to deployment user
su - planner

# Clone the repo
git clone https://github.com/YOUR_USERNAME/business-planner.git
cd business-planner
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Required variables:
# - TELEGRAM_BOT_TOKEN (from @BotFather)
# - OPENAI_API_KEY (from OpenAI)
# - DATABASE_URL (keep default for Docker setup)
```

### 5. Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# The app should be running on port 8000
```

### 6. Initialize Database

```bash
# Run database initialization
docker exec -i business-planner-postgres psql -U planner -d planner < docs/02-database/schema.sql
```

### 7. Set up Telegram Webhook

```bash
# Set webhook (replace YOUR_DOMAIN with actual domain or IP)
curl -X POST "http://localhost:8000/webhook/telegram/set-webhook"
```

## Update/Redeploy Process

### Method 1: Manual Git Pull (Simple)

```bash
# SSH into server
ssh planner@your_droplet_ip

# Navigate to project
cd business-planner

# Pull latest changes
git pull origin main

# Restart services
docker-compose restart app

# Check logs
docker-compose logs -f app
```

### Method 2: Deployment Script (Recommended)

Create deploy script on server:

```bash
# Create deployment script
nano ~/deploy.sh
```

Add this content:

```bash
#!/bin/bash
cd /home/planner/business-planner
git pull origin main
docker-compose down
docker-compose up -d --build
docker-compose logs -f
```

Make it executable:

```bash
chmod +x ~/deploy.sh
```

Now you can deploy with:

```bash
~/deploy.sh
```

### Method 3: GitHub Actions (Advanced - Auto-deploy)

See `.github/workflows/deploy.yml` for automatic deployment on push to main.

## Workflow: Development → Production

### 1. Local Development (Windows)
```bash
# Make changes locally
# Test what you can without DB

# Commit changes
git add .
git commit -m "Your commit message"
git push origin main
```

### 2. Deploy to Server
```bash
# SSH into server
ssh planner@your_droplet_ip

# Run deploy script
~/deploy.sh

# Or manually:
cd business-planner
git pull origin main
docker-compose restart app
```

### 3. Test on Server
```bash
# Check logs
docker-compose logs -f app

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/businesses

# Test Telegram bot
# Send message to your bot
```

## Common Commands

### Check Status
```bash
docker-compose ps
docker-compose logs app
docker-compose logs postgres
```

### Restart Services
```bash
docker-compose restart app      # Restart only app
docker-compose restart postgres # Restart DB
docker-compose restart          # Restart all
```

### View Logs
```bash
docker-compose logs -f app      # Follow app logs
docker-compose logs --tail=100  # Last 100 lines
```

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it business-planner-postgres psql -U planner -d planner

# Run queries
SELECT * FROM businesses;
SELECT * FROM members;
SELECT * FROM tasks LIMIT 10;
```

### Backup Database
```bash
# Backup
docker exec business-planner-postgres pg_dump -U planner planner > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i business-planner-postgres psql -U planner -d planner < backup_20251018.sql
```

## Troubleshooting

### App won't start
```bash
# Check logs
docker-compose logs app

# Check env variables
docker-compose config

# Rebuild
docker-compose up -d --build
```

### Database connection issues
```bash
# Check if Postgres is running
docker ps | grep postgres

# Check connection from app
docker exec business-planner-app python -c "import asyncpg; print('OK')"

# Restart database
docker-compose restart postgres
```

### Telegram bot not responding
```bash
# Check webhook status
curl http://localhost:8000/webhook/telegram/webhook-info

# Re-set webhook
curl -X POST http://localhost:8000/webhook/telegram/set-webhook

# Check bot token in .env
```

## Monitoring

### Resource Usage
```bash
# Check disk space
df -h

# Check memory
free -h

# Check Docker resources
docker stats
```

### Application Health
```bash
# Health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","checks":{"database":true,...}}
```

## Security Notes

1. **Never commit .env file** - It's in .gitignore for a reason
2. **Use environment variables** - Set secrets on server only
3. **Firewall setup** - Only expose necessary ports (22, 80, 443, 8000)
4. **Regular updates** - Keep system and Docker images updated
5. **Backup database** - Schedule regular backups

## Support

For issues or questions, check:
- [START_HERE.md](START_HERE.md) - Project overview
- [docs/](docs/) - Detailed documentation
- [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) - Implementation status
