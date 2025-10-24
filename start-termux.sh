#!/data/data/com.termux/files/usr/bin/bash
# My - Universal AI App Generator
# Special startup script optimized for Termux on Android

echo "📱 Starting My on Termux (Android)..."
echo ""
echo "Device: Poco X6 Pro (or similar)"
echo "Optimized for: 12GB RAM, MediaTek Dimensity 8300 Ultra"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if we have enough storage
AVAILABLE_SPACE=$(df -h ~ | awk 'NR==2 {print $4}' | sed 's/G//')
if (( $(echo "$AVAILABLE_SPACE < 5" | bc -l) )); then
    echo -e "${RED}⚠️  Warning: Low storage space!${NC}"
    echo "Available: ${AVAILABLE_SPACE}GB"
    echo "Recommended: At least 5GB free"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check dependencies
echo -e "${YELLOW}Checking Termux packages...${NC}"

PACKAGES_TO_INSTALL=""

if ! command -v python &> /dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL python"
fi

if ! command -v node &> /dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL nodejs"
fi

if ! command -v git &> /dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL git"
fi

if [ -n "$PACKAGES_TO_INSTALL" ]; then
    echo -e "${YELLOW}Installing missing packages:$PACKAGES_TO_INSTALL${NC}"
    pkg install -y $PACKAGES_TO_INSTALL
fi

echo -e "${GREEN}✅ All Termux packages ready${NC}"
echo ""

# Grant storage permission reminder
if [ ! -d "~/storage" ]; then
    echo -e "${YELLOW}⚠️  Storage permission needed!${NC}"
    echo "Run: termux-setup-storage"
    echo "Then grant permission in Android settings"
    read -p "Press Enter after granting permission..."
fi

# Install Python packages
echo -e "${BLUE}Installing Python packages...${NC}"
cd backend

# Use --no-cache-dir to save space on Android
pip install --no-cache-dir -r requirements.txt || {
    echo -e "${YELLOW}Some packages failed. Installing core packages only...${NC}"
    pip install --no-cache-dir fastapi uvicorn pydantic sqlalchemy aiosqlite
}

cd ..

# Install Node packages
echo -e "${BLUE}Installing Node.js packages...${NC}"
cd frontend

# Use --legacy-peer-deps if needed on Termux
npm install --legacy-peer-deps || npm install

cd ..

# Create directories in Termux home
mkdir -p ~/my_workspace
mkdir -p ~/my_uploads
mkdir -p ~/my_database
mkdir -p ~/my_generated
mkdir -p ~/my_builds

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""

# Performance tip for Poco X6 Pro
echo -e "${BLUE}💡 Performance Tips for Your Device:${NC}"
echo "1. Close other apps for best performance"
echo "2. Your 12GB RAM is excellent for AI models!"
echo "3. Keep phone plugged in for long generations"
echo "4. Use Deep Mode for production apps (takes 10-20 min)"
echo ""

# Start services
echo -e "${YELLOW}Starting backend...${NC}"
cd backend
python main.py > ~/my_backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
cd ..

sleep 3

echo -e "${YELLOW}Starting frontend...${NC}"
cd frontend
npm run dev > ~/my_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
cd ..

sleep 5

# Check if running
if ps -p $BACKEND_PID > /dev/null && ps -p $FRONTEND_PID > /dev/null; then
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 MY IS RUNNING ON YOUR PHONE!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}Open in browser:${NC}"
    echo "  http://localhost:3000"
    echo ""
    echo -e "${BLUE}API Docs:${NC}"
    echo "  http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}View Logs:${NC}"
    echo "  tail -f ~/my_backend.log"
    echo "  tail -f ~/my_frontend.log"
    echo ""
    echo -e "${YELLOW}To Stop:${NC}"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo "  or create new session and run:"
    echo "  pkill -f 'python.*main.py'"
    echo "  pkill -f 'node.*next'"
    echo ""
    echo -e "${GREEN}Ready to generate apps! 🚀${NC}"
    echo ""
    
    # Save PIDs
    echo "$BACKEND_PID" > ~/.my_backend.pid
    echo "$FRONTEND_PID" > ~/.my_frontend.pid
    
    # Keep running
    echo "Services running in background"
    echo "Swipe from left > NEW SESSION to use Termux"
    echo ""
else
    echo -e "${RED}❌ Services failed to start${NC}"
    echo "Check logs:"
    echo "  cat ~/my_backend.log"
    echo "  cat ~/my_frontend.log"
fi
