# Quick Fix for PEP 668 Error

## Problem
Python 3.12 on DGX Spark has PEP 668 protection, preventing system-wide package installation.

## Solution

Since we're using **Docker**, you don't need to install Python packages on the host system!

### Option 1: Skip Local Installation (Recommended)

The setup script has been updated to skip local Python package installation by default. Just run:

```bash
./setup.sh
```

It will skip Python package installation and focus on Docker setup.

### Option 2: Use Virtual Environment (For Local Development)

If you need Python packages locally for development:

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Option 3: Use Docker Only (Best Practice)

Since everything runs in Docker, you don't need local Python packages:

```bash
# Just build and run Docker
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .
docker-compose up -d
```

## Updated Setup Script

The setup script now:
- ✅ Skips local Python package installation by default
- ✅ Focuses on Docker setup (recommended)
- ✅ Only installs local packages if `INSTALL_LOCAL_DEPS=true` is set
- ✅ Creates virtual environment if local installation is requested

## Quick Start (After Fix)

```bash
# 1. Run setup (will skip Python packages)
./setup.sh

# 2. Build Docker image
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .

# 3. Authenticate with HuggingFace (in Docker container)
docker run -it --rm \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  personaplex-arm64:latest \
  huggingface-cli login

# 4. Start services
docker-compose up -d

# 5. Check status
docker-compose ps
curl http://localhost:8000/health
```

That's it! No need to install Python packages on the host system.

## HuggingFace Authentication

Since `huggingface-cli` is not installed locally, authenticate in Docker:

```bash
# After building the image
docker run -it --rm \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  personaplex-arm64:latest \
  huggingface-cli login
```

Or use environment variable:
```bash
export HF_TOKEN=your_token_here
docker-compose up -d
```

See `HUGGINGFACE_AUTH.md` for all authentication options.
