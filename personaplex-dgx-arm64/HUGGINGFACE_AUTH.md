# HuggingFace Authentication Guide

Since we're using Docker and avoiding system-wide Python package installation, here are several ways to authenticate with HuggingFace:

## Option 1: Use Virtual Environment (Recommended for Local Auth)

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate

# Install huggingface-cli
pip install huggingface_hub[cli]

# Login
huggingface-cli login

# Enter your token when prompted
# Get token from: https://huggingface.co/settings/tokens

# Deactivate when done
deactivate
```

## Option 2: Use pipx (If Available)

```bash
# Install pipx if not available
sudo apt-get install -y pipx
pipx ensurepath

# Install huggingface-cli
pipx install huggingface_hub[cli]

# Login
huggingface-cli login
```

## Option 3: Authenticate in Docker Container (Easiest)

```bash
# Build the Docker image first
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .

# Run huggingface-cli login in container
docker run -it --rm \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  personaplex-arm64:latest \
  huggingface-cli login

# Enter your token when prompted
```

## Option 4: Set Environment Variable (For Docker Compose)

```bash
# Get your HuggingFace token from: https://huggingface.co/settings/tokens

# Set it as environment variable
export HF_TOKEN=your_token_here

# Or add to docker-compose.yml environment section
# Then run:
docker-compose up -d
```

## Option 5: Manual Token Setup

```bash
# Create HuggingFace cache directory
mkdir -p ~/.cache/huggingface

# Create token file manually
echo "your_token_here" > ~/.cache/huggingface/token

# Or set as environment variable for Docker
export HF_TOKEN=your_token_here
```

## Quick Start (Recommended)

For the easiest setup, use **Option 3** (Docker container):

```bash
# 1. Build Docker image
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .

# 2. Authenticate in container
docker run -it --rm \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  personaplex-arm64:latest \
  huggingface-cli login

# 3. Start services (token will be used from cache)
docker-compose up -d
```

## Get Your HuggingFace Token

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it a name (e.g., "DGX Spark")
4. Select "Read" permission (or "Write" if you need to upload)
5. Copy the token

## Verify Authentication

```bash
# Check if token is saved
cat ~/.cache/huggingface/token

# Or test in Docker container
docker run -it --rm \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  personaplex-arm64:latest \
  huggingface-cli whoami
```

## For Docker Compose

If using docker-compose, you can set the token in the environment:

```bash
# Set token
export HF_TOKEN=your_token_here

# Or create .env file
echo "HF_TOKEN=your_token_here" > .env

# Then start
docker-compose up -d
```

The token will be passed to the container and used automatically.
