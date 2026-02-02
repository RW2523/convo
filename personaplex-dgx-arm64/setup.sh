#!/bin/bash

# NVIDIA PersonaPlex Setup Script for DGX Spark ARM64
# This script sets up the complete environment

set -e  # Exit on error

echo "=========================================="
echo "NVIDIA PersonaPlex ARM64 Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on ARM64
check_architecture() {
    ARCH=$(uname -m)
    if [ "$ARCH" != "aarch64" ]; then
        print_warning "System architecture is $ARCH, expected aarch64"
        print_warning "This setup is optimized for ARM64 (DGX Spark)"
    else
        print_status "Architecture check passed: $ARCH"
    fi
}

# Check CUDA availability
check_cuda() {
    if command -v nvidia-smi &> /dev/null; then
        print_status "CUDA detected:"
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    else
        print_error "nvidia-smi not found. CUDA may not be installed."
        exit 1
    fi
}

# Check Python version
check_python() {
    if command -v python3.12 &> /dev/null; then
        PYTHON_VERSION=$(python3.12 --version)
        print_status "Python version: $PYTHON_VERSION"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_warning "Python 3.12 not found, using: $PYTHON_VERSION"
        print_warning "PersonaPlex requires Python 3.12"
    else
        print_error "Python 3 not found. Please install Python 3.12."
        exit 1
    fi
}

# Check Docker
check_docker() {
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        print_status "Docker: $DOCKER_VERSION"
        
        # Check if user is in docker group
        if groups | grep -q docker; then
            print_status "User has Docker permissions"
        else
            print_warning "User may not have Docker permissions. You may need to use sudo."
        fi
    else
        print_error "Docker not found. Please install Docker."
        exit 1
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip setuptools wheel
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        print_status "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup HuggingFace
setup_huggingface() {
    print_status "Setting up HuggingFace..."
    
    if command -v huggingface-cli &> /dev/null; then
        print_status "HuggingFace CLI found"
        print_warning "Run 'huggingface-cli login' to authenticate"
    else
        print_status "Installing HuggingFace CLI..."
        pip3 install huggingface_hub[cli]
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p models data logs config
    print_status "Directories created"
}

# Download model (optional)
download_model() {
    print_status "Model download..."
    print_warning "Model will be downloaded on first run or you can run:"
    print_warning "  python scripts/download_model.py"
}

# Main setup function
main() {
    print_status "Starting setup process..."
    
    check_architecture
    check_cuda
    check_python
    check_docker
    
    create_directories
    install_python_deps
    setup_huggingface
    download_model
    
    print_status ""
    print_status "=========================================="
    print_status "Setup completed successfully!"
    print_status "=========================================="
    print_status ""
    print_status "Next steps:"
    print_status "1. Authenticate with HuggingFace:"
    print_status "   huggingface-cli login"
    print_status ""
    print_status "2. Build Docker image:"
    print_status "   docker build -t personaplex-arm64:latest -f Dockerfile.arm64 ."
    print_status ""
    print_status "3. Or use docker-compose:"
    print_status "   docker-compose up -d"
    print_status ""
    print_status "4. Verify setup:"
    print_status "   ./scripts/verify_setup.sh"
    print_status ""
}

# Run main function
main
