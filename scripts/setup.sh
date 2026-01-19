#!/bin/bash

# AI Company Setup Script
# Sets up both backend and frontend environments

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}AI Company Setup${NC}"
echo "=================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed${NC}"
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is required but not installed${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "\n${GREEN}Creating Python virtual environment...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "\n${GREEN}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install Python dependencies
echo -e "\n${GREEN}Installing Python dependencies...${NC}"
pip install -e ".[dev]"

# Create data directory
echo -e "\n${GREEN}Creating data directories...${NC}"
mkdir -p data/chroma

# Setup .env file
if [ ! -f ".env" ]; then
    echo -e "\n${GREEN}Creating .env file from example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env and add your API keys${NC}"
fi

# Install frontend dependencies
echo -e "\n${GREEN}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

echo ""
echo "=================="
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Run: ./scripts/run_dev.sh"
echo ""
echo "Or manually:"
echo "  Backend:  python -m uvicorn src.api.server:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo "=================="
