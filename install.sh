#!/bin/bash

# My - Universal AI App Generator
# Installation Script

set -e

echo "🌟 Welcome to My - Universal AI App Generator! 🌟"
echo ""
echo "This script will install My on your system."
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -d "/data/data/com.termux" ]; then
        OS="termux"
    else
        OS="linux"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo "Detected OS: $OS"
echo ""

# Install dependencies based on OS
install_deps() {
    case $OS in
        termux)
            echo "📱 Installing for Termux..."
            pkg update
            pkg install -y git python nodejs
            ;;
        linux)
            echo "🐧 Installing for Linux..."
            sudo apt update
            sudo apt install -y git python3 python3-pip nodejs npm
            ;;
        mac)
            echo "🍎 Installing for macOS..."
            if ! command -v brew &> /dev/null; then
                echo "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install git python node
            ;;
        windows)
            echo "🪟 Installing for Windows..."
            echo "Please install Git, Python, and Node.js manually:"
            echo "- Git: https://git-scm.com/download/win"
            echo "- Python: https://www.python.org/downloads/"
            echo "- Node.js: https://nodejs.org/"
            read -p "Press Enter after installation..."
            ;;
    esac
}

# Check if My is already cloned
if [ -d "My" ]; then
    echo "✅ My is already cloned!"
    cd My
else
    echo "📥 Cloning My repository..."
    git clone https://github.com/Johnshah/My.git
    cd My
fi

echo ""
echo "🔧 Setting up backend..."
cd backend

# Install Python packages
if command -v pip3 &> /dev/null; then
    PIP=pip3
else
    PIP=pip
fi

echo "Installing Python dependencies..."
$PIP install -r requirements.txt

echo ""
echo "🎨 Setting up frontend..."
cd ../frontend

echo "Installing Node.js dependencies..."
npm install

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To start My:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd My/backend"
echo "  python main.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd My/frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser!"
echo ""
echo "📖 For detailed instructions, see docs/COMPLETE_GUIDE.md"
echo ""
echo "🌟 Happy building! 🌟"
