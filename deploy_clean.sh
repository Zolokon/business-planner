#!/bin/bash
# Clean deployment script for Business Planner
# This script will completely clean the server and install the new project

set -e  # Exit on any error

echo "======================================"
echo "Business Planner - Clean Deployment"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Stop and remove old containers
echo -e "${YELLOW}[1/8] Stopping and removing old Docker containers...${NC}"
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
echo -e "${GREEN}✓ Old containers removed${NC}"
echo ""

# Step 2: Remove old images (optional, saves space)
echo -e "${YELLOW}[2/8] Removing old Docker images...${NC}"
docker image prune -af 2>/dev/null || true
echo -e "${GREEN}✓ Old images removed${NC}"
echo ""

# Step 3: Clean up old project files
echo -e "${YELLOW}[3/8] Removing old project files...${NC}"
cd /root
rm -rf business-planner 2>/dev/null || true
rm -rf planner 2>/dev/null || true
rm -rf app 2>/dev/null || true
echo -e "${GREEN}✓ Old files removed${NC}"
echo ""

# Step 4: Update system
echo -e "${YELLOW}[4/8] Updating system packages...${NC}"
apt update -qq
apt upgrade -y -qq
echo -e "${GREEN}✓ System updated${NC}"
echo ""

# Step 5: Install dependencies
echo -e "${YELLOW}[5/8] Installing dependencies...${NC}"
apt install -y git docker.io docker-compose python3-pip curl nano -qq
systemctl start docker
systemctl enable docker
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 6: Clone new project
echo -e "${YELLOW}[6/8] Cloning Business Planner from GitHub...${NC}"
cd /root
git clone https://github.com/Zolokon/business-planner.git
cd business-planner
echo -e "${GREEN}✓ Project cloned${NC}"
echo ""

# Step 7: Create .env file
echo -e "${YELLOW}[7/8] Creating .env configuration file...${NC}"
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql+asyncpg://planner:planner123@postgres:5432/planner
POSTGRES_USER=planner
POSTGRES_PASSWORD=planner123
POSTGRES_DB=planner

# API Keys (YOU MUST UPDATE THESE!)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Vector DB Configuration
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_DIMENSIONS=1536
EOF
echo -e "${GREEN}✓ .env file created${NC}"
echo ""
echo -e "${RED}⚠️  IMPORTANT: You need to edit .env and add your API keys!${NC}"
echo -e "${YELLOW}Run: nano /root/business-planner/.env${NC}"
echo ""

# Step 8: Start services
echo -e "${YELLOW}[8/8] Starting Docker services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for services to start
echo -e "${YELLOW}Waiting for services to start (10 seconds)...${NC}"
sleep 10

# Check service status
echo ""
echo "======================================"
echo "Deployment Status:"
echo "======================================"
docker-compose ps
echo ""

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
docker exec planner_postgres psql -U planner -d planner -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

echo "======================================"
echo -e "${GREEN}Deployment Complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   nano /root/business-planner/.env"
echo ""
echo "2. Update these values:"
echo "   - TELEGRAM_BOT_TOKEN"
echo "   - OPENAI_API_KEY"
echo ""
echo "3. Restart the app:"
echo "   cd /root/business-planner"
echo "   docker-compose restart app"
echo ""
echo "4. Check logs:"
echo "   docker-compose logs -f app"
echo ""
echo "5. Test health endpoint:"
echo "   curl http://localhost:8000/health"
echo ""
echo "Server IP: $(curl -s ifconfig.me)"
echo "Project location: /root/business-planner"
echo ""
