# Quick Deployment Guide

## Server: 164.92.225.137

### Step 1: Upload deployment script

From your local machine (Windows):

```bash
# Copy deployment script to server
scp deploy_clean.sh root@164.92.225.137:/root/
```

Or manually:
1. SSH into server: `ssh root@164.92.225.137`
2. Create file: `nano /root/deploy_clean.sh`
3. Copy-paste content from `deploy_clean.sh`
4. Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 2: Run deployment

```bash
# SSH into server
ssh root@164.92.225.137

# Make script executable
chmod +x /root/deploy_clean.sh

# Run deployment
./deploy_clean.sh
```

The script will:
- Stop and remove all old containers
- Clean old project files
- Update system
- Install Docker, Git, etc.
- Clone new project from GitHub
- Create .env template
- Start all services

### Step 3: Configure API keys

After deployment, edit .env file:

```bash
cd /root/business-planner
nano .env
```

Update these values:
```env
TELEGRAM_BOT_TOKEN=your_real_token_from_botfather
OPENAI_API_KEY=your_real_openai_key
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 4: Restart and verify

```bash
# Restart app with new config
docker-compose restart app

# Check logs
docker-compose logs -f app

# In another terminal, test health
curl http://localhost:8000/health
```

Should return:
```json
{"status":"healthy","database":"connected"}
```

### Step 5: Set up Telegram webhook

```bash
# Set webhook
curl -X POST http://localhost:8000/webhook/telegram/set-webhook

# Verify
curl http://localhost:8000/webhook/telegram/webhook-info
```

### Step 6: Test Telegram bot

Open Telegram and send `/start` to your bot!

---

## Useful Commands

### View logs
```bash
cd /root/business-planner
docker-compose logs -f app          # App logs
docker-compose logs -f postgres     # Database logs
docker-compose logs --tail=100      # Last 100 lines
```

### Restart services
```bash
docker-compose restart app      # Restart app only
docker-compose restart          # Restart all
docker-compose down && docker-compose up -d  # Full restart
```

### Check status
```bash
docker-compose ps               # Service status
docker ps                       # All containers
curl http://localhost:8000/health  # Health check
```

### Database access
```bash
# Connect to PostgreSQL
docker exec -it planner_postgres psql -U planner -d planner

# Inside psql:
\dt                            # List tables
SELECT * FROM businesses;      # View businesses
SELECT * FROM tasks LIMIT 10;  # View tasks
\q                            # Quit
```

### Update code (after GitHub push)
```bash
cd /root/business-planner
git pull origin main
docker-compose restart app
```

### Full cleanup and redeploy
```bash
./deploy_clean.sh
```

---

## Troubleshooting

### App won't start
```bash
# Check logs for errors
docker-compose logs app

# Check if PostgreSQL is running
docker ps | grep postgres

# Restart everything
docker-compose down
docker-compose up -d
```

### Database connection error
```bash
# Check database logs
docker-compose logs postgres

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Recreate containers
docker-compose down
docker-compose up -d
```

### Telegram bot not responding
```bash
# Check if bot token is correct
cat .env | grep TELEGRAM

# Check webhook
curl http://localhost:8000/webhook/telegram/webhook-info

# Reset webhook
curl -X POST http://localhost:8000/webhook/telegram/set-webhook
```

---

## API Keys Required

Before the bot works, you need:

### 1. Telegram Bot Token
1. Open Telegram
2. Message @BotFather
3. Send `/newbot`
4. Follow instructions
5. Copy token to .env

### 2. OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to .env

---

## Cost Estimate

- Digital Ocean Droplet: $6/month
- OpenAI API (GPT-4o-mini + Whisper): ~$3-6/month
- **Total: ~$9-12/month**
