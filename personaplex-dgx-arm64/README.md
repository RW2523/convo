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

## ⚠️ Important: ARM64 Compatibility

**PyTorch Installation**: PyTorch ARM64 wheels may require special handling. See `COMPATIBILITY_NOTES.md` for details.

**Recommended**: Use `Dockerfile.ngc` which uses NVIDIA NGC containers with pre-built PyTorch for ARM64:
```bash
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .
```

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

# Run setup script
chmod +x setup.sh
./setup.sh

# Authenticate with HuggingFace
huggingface-cli login
# Enter your HuggingFace token when prompted
```

### 3. Build and Run

```bash
# Build Docker image for ARM64
docker build -t personaplex-arm64:latest -f Dockerfile.arm64 .

# Or use docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

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
# Manually download model
python scripts/download_model.py

# Or use HuggingFace CLI
huggingface-cli download nvidia/personaplex-7b-v1
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

## Support

For issues specific to:
- PersonaPlex: Check [NVIDIA PersonaPlex Documentation](https://deepwiki.com/NVIDIA/personaplex)
- DGX Spark: Check [DGX Spark Documentation](https://docs.nvidia.com/dgx/dgx-spark/)
- ARM64: Check [DGX Spark Porting Guide](https://docs.nvidia.com/dgx/dgx-spark-porting-guide/)

## License

Check NVIDIA's license terms for PersonaPlex usage.
