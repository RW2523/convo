# Installing Docker Compose on DGX Spark

## Issue
`docker-compose` command not found on DGX Spark.

## Solutions

### Option 1: Install docker-compose-plugin (Recommended - Modern Docker)

Modern Docker includes compose as a plugin. Use `docker compose` (without hyphen):

```bash
# Check if plugin is available
docker compose version

# If available, use 'docker compose' instead of 'docker-compose'
docker compose up -d
docker compose logs -f
docker compose ps
```

### Option 2: Install Standalone docker-compose

```bash
# Install docker-compose
sudo apt-get update
sudo apt-get install -y docker-compose

# Verify installation
docker-compose --version
```

### Option 3: Install via pip (in virtual environment)

```bash
# Activate your venv (if you have one)
source venv/bin/activate

# Install docker-compose
pip install docker-compose

# Or install globally (not recommended due to PEP 668)
pip install --user docker-compose
```

### Option 4: Download Binary Directly

```bash
# Download latest docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

## Recommended: Use Docker Compose Plugin

Modern Docker installations include compose as a plugin. Just use:

```bash
# Instead of: docker-compose up -d
docker compose up -d

# Instead of: docker-compose logs -f
docker compose logs -f

# Instead of: docker-compose ps
docker compose ps
```

## Update Your Workflow

If you have `docker compose` (plugin), update commands:

```bash
# Build
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps

# Stop services
docker compose down
```

## Check What You Have

```bash
# Check Docker version
docker --version

# Check if compose plugin is available
docker compose version

# Check if standalone docker-compose is installed
docker-compose --version
```

Use whichever is available!
