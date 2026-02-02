# Complete Setup Instructions

## Step-by-Step Guide

### Phase 1: Local System Setup

#### 1.1 Initialize Git Repository

```bash
cd /path/to/personaplex-dgx-arm64

# Make scripts executable
chmod +x setup.sh scripts/*.sh

# Initialize git repository
./scripts/git_setup.sh

# Or manually:
git init
git add .
git commit -m "Initial PersonaPlex ARM64 setup for DGX Spark"
```

#### 1.2 Push to Remote Repository

```bash
# Add your remote repository
git remote add origin https://github.com/yourusername/personaplex-dgx-arm64.git

# Or if using GitLab/Bitbucket:
# git remote add origin https://gitlab.com/yourusername/personaplex-dgx-arm64.git

# Push to remote
git branch -M main
git push -u origin main
```

### Phase 2: DGX Spark Setup

#### 2.1 Clone Repository on DGX Spark

```bash
# SSH into your DGX Spark system
ssh user@dgx-spark-ip

# Clone the repository
git clone https://github.com/yourusername/personaplex-dgx-arm64.git
cd personaplex-dgx-arm64
```

#### 2.2 Run Setup Script

```bash
# Make scripts executable
chmod +x setup.sh scripts/*.sh

# Run the setup script
./setup.sh
```

The setup script will:
- ✅ Check system architecture (should be aarch64)
- ✅ Verify CUDA installation
- ✅ Check Python 3.12
- ✅ Verify Docker installation
- ✅ Install Python dependencies
- ✅ Create necessary directories
- ✅ Setup HuggingFace CLI

#### 2.3 Authenticate with HuggingFace

```bash
# Login to HuggingFace (required for model access)
huggingface-cli login

# Enter your HuggingFace token
# Get token from: https://huggingface.co/settings/tokens
```

#### 2.4 Verify Setup

```bash
# Run verification script
./scripts/verify_setup.sh
```

Expected output:
- ✓ Architecture: aarch64
- ✓ CUDA available
- ✓ Python installed
- ✓ Docker installed
- ✓ Core packages installed
- ✓ Project structure OK

### Phase 3: Build and Deploy

#### 3.1 Build Docker Image

```bash
# Option 1: Using docker-compose (recommended)
docker-compose build

# Option 2: Using Docker directly
docker build -t personaplex-arm64:latest -f Dockerfile.arm64 .

# Option 3: Using Makefile
make build
```

#### 3.2 Start Services

```bash
# Option 1: Using docker-compose (recommended)
docker-compose up -d

# Option 2: Using Makefile
make run

# Check if running
docker-compose ps
```

#### 3.3 Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Service info
curl http://localhost:8000/

# Model info
curl http://localhost:8000/info

# Or use test script
./scripts/test_api.sh
```

### Phase 4: Usage

#### 4.1 Test Text Generation

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "temperature": 0.7
  }'
```

#### 4.2 Monitor Logs

```bash
# View logs
docker-compose logs -f

# Or
docker logs -f personaplex-arm64
```

#### 4.3 Monitor GPU Usage

```bash
# Watch GPU usage
watch -n 1 nvidia-smi
```

## Common Commands Reference

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Rebuild
docker-compose build --no-cache
```

### Makefile Commands

```bash
make setup      # Run complete setup
make install    # Install Python dependencies
make build      # Build Docker image
make run        # Run with docker-compose
make stop       # Stop docker-compose
make clean      # Clean up containers
make verify     # Verify setup
make logs       # View logs
make status     # Check status
```

### Git Commands

```bash
# Pull latest changes
git pull origin main

# Make changes and commit
git add .
git commit -m "Your changes"
git push origin main

# On DGX Spark, pull updates
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Issue: Setup Script Fails

**Check:**
- System architecture: `uname -m` (should be aarch64)
- CUDA: `nvidia-smi`
- Python: `python3.12 --version`
- Docker: `docker --version`

### Issue: Model Download Fails

**Solution:**
```bash
# Ensure you're logged in
huggingface-cli login

# Manually download
python3 scripts/download_model.py
```

### Issue: Docker Build Fails

**Solution:**
```bash
# Check Docker platform
docker buildx inspect --bootstrap

# Rebuild with no cache
docker-compose build --no-cache
```

### Issue: Service Won't Start

**Solution:**
```bash
# Check logs
docker-compose logs

# Check if port is in use
sudo lsof -ti:8000

# Restart Docker daemon
sudo systemctl restart docker
```

## Next Steps

1. ✅ Setup complete
2. ✅ Service running
3. 📝 Configure for your use case (edit `config/config.yaml`)
4. 📝 Set up monitoring
5. 📝 Configure reverse proxy (nginx) for production
6. 📝 Set up SSL/TLS certificates

## Support Resources

- **README.md**: Main documentation
- **QUICKSTART.md**: Quick 5-minute guide
- **DEPLOYMENT.md**: Detailed deployment guide
- **PROJECT_STRUCTURE.md**: Project structure overview

## Important Notes

- Model will be downloaded on first run (can take time)
- Ensure sufficient disk space for model (~14GB+)
- GPU memory requirements: Check model specifications
- Network access to HuggingFace required for model download
