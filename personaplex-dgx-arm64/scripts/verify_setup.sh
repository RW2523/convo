#!/bin/bash

# Verify PersonaPlex setup on ARM64

set -e

echo "=========================================="
echo "Verifying PersonaPlex Setup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Check architecture
echo -n "Checking architecture... "
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    echo -e "${GREEN}✓${NC} $ARCH"
else
    echo -e "${YELLOW}⚠${NC} $ARCH (expected aarch64)"
fi

# Check CUDA
echo -n "Checking CUDA... "
if command -v nvidia-smi &> /dev/null; then
    CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n1)
    echo -e "${GREEN}✓${NC} CUDA available (Driver: $CUDA_VERSION)"
else
    echo -e "${RED}✗${NC} CUDA not found"
    ERRORS=$((ERRORS + 1))
fi

# Check Python
echo -n "Checking Python... "
if command -v python3.12 &> /dev/null; then
    PYTHON_VERSION=$(python3.12 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${YELLOW}⚠${NC} $PYTHON_VERSION (Python 3.12 recommended)"
else
    echo -e "${RED}✗${NC} Python not found"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker not found"
    ERRORS=$((ERRORS + 1))
fi

# Check Python packages
echo -n "Checking Python packages... "
if python3 -c "import torch; import transformers; import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Core packages installed"
else
    echo -e "${YELLOW}⚠${NC} Some packages missing (run: pip install -r requirements.txt)"
fi

# Check HuggingFace CLI
echo -n "Checking HuggingFace CLI... "
if command -v huggingface-cli &> /dev/null; then
    echo -e "${GREEN}✓${NC} HuggingFace CLI installed"
else
    echo -e "${YELLOW}⚠${NC} HuggingFace CLI not found (run: pip install huggingface_hub[cli])"
fi

# Check directories
echo -n "Checking directories... "
if [ -d "config" ] && [ -d "src" ] && [ -d "scripts" ]; then
    echo -e "${GREEN}✓${NC} Project structure OK"
else
    echo -e "${RED}✗${NC} Project structure incomplete"
    ERRORS=$((ERRORS + 1))
fi

# Check configuration files
echo -n "Checking configuration... "
if [ -f "config/config.yaml" ] && [ -f "config/model_config.json" ]; then
    echo -e "${GREEN}✓${NC} Configuration files present"
else
    echo -e "${RED}✗${NC} Configuration files missing"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}Setup verification passed!${NC}"
    exit 0
else
    echo -e "${RED}Setup verification failed with $ERRORS error(s)${NC}"
    exit 1
fi
