# Docker Build Fix - Python 3.12 Installation

## Issue Fixed
Python 3.12 is not available in Ubuntu 22.04 default repositories. The Dockerfile has been updated to install it from deadsnakes PPA.

## What Changed

The Dockerfile now:
1. Installs `software-properties-common` first
2. Adds deadsnakes PPA repository
3. Updates package list
4. Installs Python 3.12 from the PPA

## Build Again

Now you can build successfully:

```bash
# Build with fixed Dockerfile
docker build -t personaplex-arm64:latest -f Dockerfile.arm64 .

# OR use NGC container (recommended - has PyTorch pre-built)
docker build -t personaplex-arm64:latest -f Dockerfile.ngc .
```

## Docker Compose Issue

If you see `docker-compose: command not found`, you have two options:

### Option 1: Use Docker Compose Plugin (Recommended)

Modern Docker includes compose as a plugin. Use `docker compose` (without hyphen):

```bash
# Check if available
docker compose version

# If available, use:
docker compose up -d
docker compose logs -f
docker compose ps
```

### Option 2: Install docker-compose

```bash
# Install docker-compose
sudo apt-get update
sudo apt-get install -y docker-compose

# Verify
docker-compose --version
```

See `INSTALL_DOCKER_COMPOSE.md` for detailed instructions.

## Quick Start (After Fixes)

```bash
# 1. Build Docker image
docker build -t personaplex-arm64:latest -f Dockerfile.ngc .

# 2. Start services (use 'docker compose' if plugin available, else 'docker-compose')
docker compose up -d
# OR
docker-compose up -d

# 3. Check logs
docker compose logs -f
# OR
docker-compose logs -f

# 4. Verify
curl http://localhost:8000/health
```
