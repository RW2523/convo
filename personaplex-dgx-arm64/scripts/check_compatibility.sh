#!/bin/bash

# Comprehensive compatibility check for PersonaPlex on DGX Spark ARM64

set -e

echo "=========================================="
echo "PersonaPlex ARM64 Compatibility Check"
echo "=========================================="

ERRORS=0
WARNINGS=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

check_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# 1. Architecture Check
echo ""
echo "1. Architecture Check"
echo "----------------------"
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    check_pass "Architecture: $ARCH (ARM64)"
else
    check_fail "Architecture: $ARCH (Expected: aarch64)"
fi

# 2. CUDA Check
echo ""
echo "2. CUDA Check"
echo "-------------"
if command -v nvidia-smi &> /dev/null; then
    CUDA_DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n1)
    CUDA_VERSION=$(nvidia-smi --query-gpu=cuda_version --format=csv,noheader | head -n1 2>/dev/null || echo "N/A")
    check_pass "CUDA Driver: $CUDA_DRIVER"
    check_info "CUDA Version: $CUDA_VERSION"
    
    if command -v nvcc &> /dev/null; then
        NVCC_VERSION=$(nvcc --version | grep "release" | sed 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/')
        check_pass "NVCC: $NVCC_VERSION"
    else
        check_warn "NVCC not found (may be in container)"
    fi
else
    check_fail "nvidia-smi not found"
fi

# 3. Python Check
echo ""
echo "3. Python Check"
echo "---------------"
if command -v python3.12 &> /dev/null; then
    PYTHON_VERSION=$(python3.12 --version)
    check_pass "Python: $PYTHON_VERSION"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    PYTHON_MAJOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1)
    PYTHON_MINOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
        check_pass "Python: $PYTHON_VERSION (3.12+ required)"
    else
        check_warn "Python: $PYTHON_VERSION (3.12+ recommended)"
    fi
else
    check_fail "Python 3 not found"
fi

# 4. PyTorch Check
echo ""
echo "4. PyTorch Check"
echo "----------------"
if python3 -c "import torch" 2>/dev/null; then
    TORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)" 2>/dev/null)
    CUDA_AVAILABLE=$(python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null)
    check_pass "PyTorch: $TORCH_VERSION"
    
    if [ "$CUDA_AVAILABLE" = "True" ]; then
        CUDA_PYTORCH=$(python3 -c "import torch; print(torch.version.cuda)" 2>/dev/null)
        check_pass "PyTorch CUDA: Available ($CUDA_PYTORCH)"
    else
        check_warn "PyTorch CUDA: Not available (may work in container)"
    fi
else
    check_warn "PyTorch: Not installed (will be installed in container)"
    check_info "  Note: PyTorch ARM64 may need special installation"
    check_info "  See: COMPATIBILITY_NOTES.md"
fi

# 5. Docker Check
echo ""
echo "5. Docker Check"
echo "---------------"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    check_pass "Docker: $DOCKER_VERSION"
    
    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        check_pass "Docker daemon: Running"
        
        # Check NVIDIA runtime
        if docker info 2>/dev/null | grep -q "nvidia"; then
            check_pass "NVIDIA runtime: Available"
        else
            check_warn "NVIDIA runtime: May not be configured"
        fi
    else
        check_fail "Docker daemon: Not running"
    fi
else
    check_fail "Docker: Not installed"
fi

# 6. Required Packages Check
echo ""
echo "6. Python Packages Check"
echo "------------------------"
REQUIRED_PACKAGES=("transformers" "fastapi" "uvicorn" "huggingface_hub" "yaml")
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import ${pkg//-/_}" 2>/dev/null; then
        check_pass "$pkg: Installed"
    else
        check_warn "$pkg: Not installed (will be installed in container)"
    fi
done

# 7. File Structure Check
echo ""
echo "7. File Structure Check"
echo "-----------------------"
REQUIRED_FILES=("Dockerfile.arm64" "docker-compose.yml" "requirements.txt" "src/server.py" "config/config.yaml")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file: Present"
    else
        check_fail "$file: Missing"
    fi
done

# 8. CUDA Architecture Check
echo ""
echo "8. CUDA Architecture Configuration"
echo "-----------------------------------"
if [ -f "config/config.yaml" ]; then
    if grep -q "121-real" config/config.yaml 2>/dev/null || grep -q "CUDA_ARCHITECTURES" Dockerfile.arm64 2>/dev/null; then
        check_pass "CUDA architecture: Configured for 121-real (DGX Spark)"
    else
        check_warn "CUDA architecture: May need explicit configuration"
    fi
fi

# 9. HuggingFace Check
echo ""
echo "9. HuggingFace Check"
echo "--------------------"
if command -v huggingface-cli &> /dev/null; then
    check_pass "HuggingFace CLI: Installed"
    
    # Check if logged in
    if [ -f ~/.huggingface/token ]; then
        check_pass "HuggingFace: Authenticated"
    else
        check_warn "HuggingFace: Not authenticated (run: huggingface-cli login)"
    fi
else
    check_warn "HuggingFace CLI: Not installed (will be installed)"
fi

# Summary
echo ""
echo "=========================================="
echo "Compatibility Check Summary"
echo "=========================================="
echo -e "Errors: ${RED}$ERRORS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed! System is ready.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ System is mostly compatible. Review warnings above.${NC}"
        echo ""
        echo "Recommendations:"
        echo "1. Review COMPATIBILITY_NOTES.md for ARM64-specific considerations"
        echo "2. Consider using Dockerfile.ngc for better PyTorch compatibility"
        echo "3. Ensure HuggingFace authentication before deployment"
        exit 0
    fi
else
    echo -e "${RED}✗ Compatibility issues found. Please fix errors above.${NC}"
    exit 1
fi
