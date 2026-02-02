# NVIDIA PersonaPlex - DGX Spark ARM64 Setup

Complete setup for running NVIDIA PersonaPlex on DGX Spark ARM64 architecture.

## Overview

PersonaPlex is NVIDIA's real-time speech-to-speech conversational AI model. This repository contains everything needed to deploy it on DGX Spark ARM64 systems.

## Prerequisites

- DGX Spark system with ARM64 architecture (aarch64)
- CUDA 12.1+ installed (pre-installed on DGX Spark)
- Docker and Docker Compose
- Python 3.12
- Git
- HuggingFace account and token

## ⚠️ Important Notes

### ARM64 Compatibility
**PyTorch Installation**: PyTorch ARM64 wheels may require special handling. See `COMPATIBILITY_NOTES.md` for details.

**Recommended**: Use `Dockerfile.ngc` which uses NVIDIA NGC containers with pre-built PyTorch for ARM64:
```bash
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .
```

### Common Issues Fixed

1. **PEP 668 Error**: Setup script skips local Python package installation (uses Docker instead)
2. **HuggingFace CLI**: Use `python scripts/hf_login.py` instead of `huggingface-cli login`
3. **Python 3.12**: Dockerfile now installs from deadsnakes PPA with distutils support
4. **Docker Compose**: Use `docker compose` (plugin) or install `docker-compose` (standalone)

See troubleshooting section below for details.

## Quick Start

### 1. Clone and Setup

```bash
# On your local system
git clone <your-repo-url>
cd personaplex-dgx-arm64

# Commit and push to your git repository
git add .
git commit -m "Initial PersonaPlex ARM64 setup"
git push origin main
```

### 2. On DGX Spark System

```bash
# Clone the repository
git clone <your-repo-url>
cd personaplex-dgx-arm64

# Run setup script (skips local Python packages - uses Docker instead)
chmod +x setup.sh
./setup.sh

# Note: Setup script skips local Python package installation to avoid PEP 668 errors
# All dependencies are installed in Docker container - no need for local packages!
```

**What the setup script does:**
- ✅ Checks system architecture (ARM64)
- ✅ Verifies CUDA installation
- ✅ Checks Python and Docker
- ✅ Creates necessary directories
- ⏭️ **Skips** local Python package installation (avoids PEP 668 error)
- ✅ All Python packages will be installed in Docker container

### 3. Authenticate with HuggingFace

Since `huggingface-cli` is not installed locally (to avoid PEP 668 issues), use one of these methods:

**Option A: In Docker Container (Recommended)**
```bash
# First build the image
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .

# Then authenticate in container
docker run -it --rm \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  personaplex-arm64:latest \
  huggingface-cli login
```

**Option B: Using Virtual Environment (Recommended for Local Auth)**
```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install huggingface_hub
pip install huggingface_hub[cli]

# Login using Python script (works even if CLI command not found)
python scripts/hf_login.py

# OR use Python API directly
python -c "from huggingface_hub import login; login()"

# Deactivate when done
deactivate
```

**Option C: Set Environment Variable**
```bash
# Get token from: https://huggingface.co/settings/tokens
export HF_TOKEN=your_token_here
# Token will be used by Docker container
```

**Note**: The `huggingface-cli` command may not be available even after installation. Use the Python script method (`python scripts/hf_login.py`) which always works.

See `HUGGINGFACE_AUTH.md` for detailed instructions.

### 4. Build and Run

```bash
# Option A: Build with NGC container (RECOMMENDED - easiest, has PyTorch pre-built)
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .

# Option B: Build with standard Dockerfile (fixed for Python 3.12 + distutils)
docker build -f Dockerfile.arm64 -t personaplex-arm64:latest .

# Start services
# Try 'docker compose' first (plugin version - modern Docker)
docker compose up -d

# OR if not available, use 'docker-compose' (standalone)
docker-compose up -d

# Check logs
docker compose logs -f
# OR
docker-compose logs -f

# Check status
docker compose ps
# OR
docker-compose ps
```

**Notes**:
- **Docker Compose**: Modern Docker includes `docker compose` (plugin). If not available, install `docker-compose` or see `INSTALL_DOCKER_COMPOSE.md`
- **Python 3.12**: Dockerfile.arm64 now properly installs Python 3.12 with distutils from deadsnakes PPA
- **NGC Container**: `Dockerfile.ngc` is recommended as it avoids all Python installation issues

## ⚠️ Important: PEP 668 Fix

**If you get "externally-managed-environment" error**: This is normal! The setup script has been updated to skip local Python package installation since we use Docker. All Python dependencies are installed in the Docker container, so you don't need to install them on the host system.

See `QUICK_FIX.md` for details.

### 4. Access the Service

The service will be available at:
- API: `http://localhost:8000`
- Health check: `http://localhost:8000/health`

### 5. Verify Compatibility (Recommended)

Before deployment, run the compatibility check:
```bash
./scripts/check_compatibility.sh
```

This will verify:
- Architecture (ARM64)
- CUDA installation
- Python version
- PyTorch compatibility
- Docker configuration
- Required packages

## Project Structure

```
personaplex-dgx-arm64/
├── README.md                 # This file
├── Dockerfile.arm64          # ARM64 Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── setup.sh                  # Main setup script
├── requirements.txt          # Python dependencies
├── config/
│   ├── config.yaml          # Application configuration
│   └── model_config.json    # Model configuration
├── scripts/
│   ├── install_dependencies.sh
│   ├── verify_setup.sh
│   └── download_model.sh
├── src/
│   ├── __init__.py
│   ├── server.py            # Main server application
│   └── model_handler.py     # Model loading and inference
├── .gitignore
└── .dockerignore
```

## Configuration

Edit `config/config.yaml` to customize:
- Model path
- Server port
- GPU settings
- Batch size
- Other runtime parameters

## Troubleshooting

### Issue: PEP 668 Error (externally-managed-environment)

**Problem**: `error: externally-managed-environment` when installing Python packages

**Solution**: This is expected! The setup script skips local Python package installation. All packages are installed in Docker container.

```bash
# Just run setup - it will skip Python packages
./setup.sh

# All dependencies are installed in Docker, not on host
```

See `QUICK_FIX.md` for details.

### Issue: HuggingFace CLI Not Found

**Problem**: `huggingface-cli: command not found` even after installation

**Solution**: Use the Python script instead (always works):

```bash
# In virtual environment
python scripts/hf_login.py

# OR use Python API directly
python -c "from huggingface_hub import login; login()"
```

See `HUGGINGFACE_AUTH.md` for all authentication methods.

### Issue: Python 3.12 Not Found in Docker Build

**Problem**: `E: Unable to locate package python3.12` during Docker build

**Solution**: Fixed! Dockerfile.arm64 now installs from deadsnakes PPA with distutils:

```bash
# Build with fixed Dockerfile
docker build -f Dockerfile.arm64 -t personaplex-arm64:latest .

# OR use NGC container (recommended - avoids all Python issues)
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .
```

See `BUILD_FIX.md` and `DISTUTILS_FIX.md` for details.

### Issue: Docker Compose Not Found

**Problem**: `Command 'docker-compose' not found`

**Solution**: Use Docker Compose plugin or install standalone:

```bash
# Option 1: Try plugin version (modern Docker)
docker compose version
docker compose up -d

# Option 2: Install standalone
sudo apt-get install -y docker-compose
docker-compose up -d
```

See `INSTALL_DOCKER_COMPOSE.md` for detailed instructions.

### Issue: Distutils Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'distutils'` during Docker build

**Solution**: Fixed! Dockerfile now installs `python3.12-distutils` package.

```bash
# Rebuild with fixed Dockerfile
docker build -f Dockerfile.arm64 -t personaplex-arm64:latest .
```

See `DISTUTILS_FIX.md` for details.

### Issue: Tokenizer Loading Fails (SentencePiece Missing)

**Problem**: `You need to have sentencepiece or tiktoken installed to convert a slow tokenizer to a fast one`

**Solution**: Fixed! Dockerfile now installs sentencepiece and tiktoken, and code has runtime fallback.

**⚠️ CRITICAL: You MUST rebuild the image for this fix to work:**

```bash
# Rebuild with NO CACHE
docker compose down
docker build --no-cache -f Dockerfile.ngc -t personaplex-arm64:latest .
docker compose up -d
```

The code now:
- Installs sentencepiece/tiktoken in Dockerfile with verification
- Checks and installs at runtime if missing
- Uses multiple tokenizer loading strategies with fallbacks

See `TOKENIZER_FIX_FINAL.md` and `CRITICAL_REBUILD.md` for details.

### ARM64 Compatibility Issues

If you encounter architecture-specific issues:

```bash
# Verify architecture
uname -m  # Should show aarch64

# Check CUDA
nvidia-smi

# Verify Docker platform
docker buildx inspect --bootstrap
```

### Model Download Issues

If model download fails:

```bash
# Manually download model (in Docker container)
docker run -it --rm \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  personaplex-arm64:latest \
  python scripts/download_model.py

# Or use HuggingFace CLI in container
docker run -it --rm \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  personaplex-arm64:latest \
  python -c "from huggingface_hub import snapshot_download; snapshot_download('nvidia/personaplex-7b-v1')"
```

## Development

### Local Development (x86-64)

For local development on x86-64 systems:

```bash
# Use cross-compilation Dockerfile
docker build -t personaplex-arm64:dev -f Dockerfile.cross-compile .
```

### Testing

```bash
# Run tests
python -m pytest tests/

# Verify setup
./scripts/verify_setup.sh
```

## Git Workflow

### Initial Setup

```bash
# Initialize git (if not already done)
git init
git remote add origin <your-repo-url>

# Add all files
git add .
git commit -m "Initial PersonaPlex ARM64 setup"
git push -u origin main
```

### On DGX Spark

```bash
# Pull latest changes
git pull origin main

# Make changes and commit
git add .
git commit -m "Your changes"
git push origin main
```

## Performance Tuning

For optimal performance on DGX Spark:

1. Adjust batch size in `config/config.yaml`
2. Set appropriate CUDA device IDs
3. Enable TensorRT optimization (if available)
4. Monitor GPU utilization with `nvidia-smi`

## Quick Reference: Common Commands

```bash
# Setup
./setup.sh

# Authenticate HuggingFace
python scripts/hf_login.py  # In venv

# Build Docker image
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .  # Recommended
# OR
docker build -f Dockerfile.arm64 -t personaplex-arm64:latest .

# Start services
docker compose up -d  # Plugin version
# OR
docker-compose up -d  # Standalone

# View logs
docker compose logs -f
# OR
docker-compose logs -f

# Check status
docker compose ps
# OR
docker-compose ps

# Stop services
docker compose down
# OR
docker-compose down

# Health check
curl http://localhost:8000/health
```

## Documentation Files

- `README.md` - This file (main documentation)
- `QUICK_FIX.md` - PEP 668 error fix
- `HUGGINGFACE_AUTH.md` - HuggingFace authentication guide
- `BUILD_FIX.md` - Docker build issues and fixes
- `DISTUTILS_FIX.md` - Python distutils fix
- `INSTALL_DOCKER_COMPOSE.md` - Docker Compose installation
- `COMPATIBILITY_NOTES.md` - ARM64 compatibility details
- `DEPLOYMENT.md` - Detailed deployment guide
- `QUICKSTART.md` - 5-minute quick start

## Support

For issues specific to:
- **PersonaPlex**: Check [NVIDIA PersonaPlex Documentation](https://deepwiki.com/NVIDIA/personaplex)
- **DGX Spark**: Check [DGX Spark Documentation](https://docs.nvidia.com/dgx/dgx-spark/)
- **ARM64**: Check [DGX Spark Porting Guide](https://docs.nvidia.com/dgx/dgx-spark-porting-guide/)

## Known Issues and Fixes

All common issues have been fixed and documented:

1. ✅ **PEP 668 Error** - Setup script skips local package installation
2. ✅ **HuggingFace CLI** - Python script alternative provided
3. ✅ **Python 3.12 Installation** - Dockerfile fixed with deadsnakes PPA
4. ✅ **Distutils Missing** - Added python3.12-distutils package
5. ✅ **Docker Compose** - Both plugin and standalone options documented

## License

Check NVIDIA's license terms for PersonaPlex usage.
