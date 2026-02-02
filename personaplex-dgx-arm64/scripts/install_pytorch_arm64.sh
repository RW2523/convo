#!/bin/bash

# Install PyTorch for ARM64 with CUDA support
# This script handles ARM64-specific PyTorch installation

set -e

echo "=========================================="
echo "Installing PyTorch for ARM64"
echo "=========================================="

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "Warning: This script is for ARM64 (aarch64) architecture"
    echo "Current architecture: $ARCH"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

# Check CUDA version
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/')
    echo "CUDA version: $CUDA_VERSION"
else
    echo "Warning: nvcc not found, CUDA may not be properly installed"
    CUDA_VERSION="12.1"  # Default for DGX Spark
fi

# Try to install PyTorch for ARM64
echo "Attempting to install PyTorch for ARM64..."

# Method 1: Try from PyTorch official (if ARM64 wheels available)
echo "Method 1: Trying official PyTorch repository..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 2>&1 | tee /tmp/pytorch_install.log || \
echo "Official PyTorch ARM64 wheels may not be available"

# Method 2: Try building from source (fallback)
if ! python3 -c "import torch; print(torch.__version__)" 2>/dev/null; then
    echo "Method 2: PyTorch not found, checking if we need to build from source..."
    echo "For ARM64, you may need to:"
    echo "1. Build PyTorch from source, OR"
    echo "2. Use NVIDIA's pre-built containers with PyTorch, OR"
    echo "3. Use conda-forge which has ARM64 support"
    echo ""
    echo "Recommended: Use NVIDIA's NGC containers that include PyTorch for ARM64"
fi

# Verify installation
if python3 -c "import torch; print(f'PyTorch {torch.__version__} installed'); print(f'CUDA available: {torch.cuda.is_available()}')" 2>/dev/null; then
    echo "✅ PyTorch installed successfully!"
    python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"
else
    echo "❌ PyTorch installation failed or not found"
    echo "Please install PyTorch manually for ARM64"
    echo "See: https://pytorch.org/get-started/locally/"
    exit 1
fi
