#!/bin/bash
# My - Universal AI App Generator
# Startup script for Linux/Mac/Termux

echo "🚀 Starting My - Universal AI App Generator..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in Termux
if [ -d "/data/data/com.termux" ]; then
    echo -e "${BLUE}📱 Detected Termux environment${NC}"
    IS_TERMUX=true
else
    echo -e "${BLUE}💻 Detected PC/Mac environment${NC}"
    IS_TERMUX=false
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo ""
echo -e "${YELLOW}Checking dependencies...${NC}"

if ! command_exists python && ! command_exists python3; then
    echo -e "${RED}❌ Python not found! Please install Python 3.11+${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Python found${NC}"
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found! Please install Node.js 18+${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Node.js found${NC}"
fi

if ! command_exists git; then
    echo -e "${YELLOW}⚠️  Git not found (optional but recommended)${NC}"
else
    echo -e "${GREEN}✅ Git found${NC}"
fi

# Get Python command (python3 or python)
if command_exists python3; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# Get PIP command
if command_exists pip3; then
    PIP_CMD=pip3
else
    PIP_CMD=pip
fi

echo ""
echo -e "${BLUE}📦 Installing dependencies...${NC}"

# Install backend dependencies
echo ""
echo -e "${YELLOW}Installing backend dependencies (Python)...${NC}"
cd backend
if [ ! -d "venv" ] && [ "$IS_TERMUX" = false ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
fi

$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Some packages failed to install. Continuing anyway...${NC}"
fi

cd ..

# Install frontend dependencies
echo ""
echo -e "${YELLOW}Installing frontend dependencies (Node.js)...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Frontend installation failed${NC}"
        exit 1
    fi
fi
cd ..

echo ""
echo -e "${GREEN}✅ All dependencies installed!${NC}"

# Create necessary directories
mkdir -p /tmp/my_workspace
mkdir -p /tmp/my_uploads
mkdir -p /tmp/my_database
mkdir -p /tmp/my_generated
mkdir -p /tmp/my_builds

echo ""
echo -e "${BLUE}🎯 Starting services...${NC}"
echo ""

# Start backend in background
echo -e "${YELLOW}Starting backend on http://localhost:8000${NC}"
cd backend
if [ "$IS_TERMUX" = false ] && [ -d "venv" ]; then
    source venv/bin/activate
fi
$PYTHON_CMD main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend in background
echo -e "${YELLOW}Starting frontend on http://localhost:3000${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
cd ..

# Wait for services to start
echo ""
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 5

# Check if services are running
if ps -p $BACKEND_PID > /dev/null && ps -p $FRONTEND_PID > /dev/null; then
    echo ""
    echo -e "${GREEN}✅ My is now running!${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 MY - UNIVERSAL AI APP GENERATOR${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}📱 Frontend:${NC}  http://localhost:3000"
    echo -e "${YELLOW}🔧 Backend:${NC}   http://localhost:8000"
    echo -e "${YELLOW}📚 API Docs:${NC}  http://localhost:8000/docs"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Logs:${NC}"
    echo "  Backend:  tail -f backend.log"
    echo "  Frontend: tail -f frontend.log"
    echo ""
    echo -e "${YELLOW}To stop:${NC}"
    echo "  ./stop.sh"
    echo "  or"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    
    # Save PIDs for stop script
    echo "$BACKEND_PID" > .backend.pid
    echo "$FRONTEND_PID" > .frontend.pid
    
    # Keep script running
    echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"
    echo ""
    
    # Trap Ctrl+C
    trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
    
    # Wait for both processes
    wait
else
    echo -e "${RED}❌ Failed to start services${NC}"
    echo "Check logs:"
    echo "  Backend:  cat backend.log"
    echo "  Frontend: cat frontend.log"
    exit 1
fi
