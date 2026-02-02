# Deployment Guide - PersonaPlex on DGX Spark ARM64

Complete step-by-step guide for deploying PersonaPlex on DGX Spark ARM64 architecture.

## Prerequisites Checklist

- [ ] DGX Spark system with ARM64 (aarch64) architecture
- [ ] CUDA 12.1+ installed and working
- [ ] Docker and Docker Compose installed
- [ ] Python 3.12 installed
- [ ] Git installed
- [ ] HuggingFace account and access token
- [ ] Network access to HuggingFace (for model download)

## Step 1: Prepare Your Local System

### 1.1 Clone or Create Repository

If you're starting fresh:

```bash
# Create project directory
mkdir personaplex-dgx-arm64
cd personaplex-dgx-arm64

# Copy all project files here
# (or use the files from this repository)
```

### 1.2 Initialize Git Repository

```bash
# Make scripts executable
chmod +x setup.sh scripts/*.sh

# Initialize git
./scripts/git_setup.sh

# Or manually:
git init
git add .
git commit -m "Initial PersonaPlex ARM64 setup"
```

### 1.3 Push to Remote Repository

```bash
# Add remote (replace with your repository URL)
git remote add origin https://github.com/yourusername/personaplex-dgx-arm64.git

# Push to remote
git branch -M main
git push -u origin main
```

## Step 2: Setup on DGX Spark

### 2.1 Clone Repository

```bash
# Clone your repository
git clone https://github.com/yourusername/personaplex-dgx-arm64.git
cd personaplex-dgx-arm64
```

### 2.2 Verify System Requirements

```bash
# Check architecture
uname -m  # Should show: aarch64

# Check CUDA
nvidia-smi

# Check Docker
docker --version
docker-compose --version

# Check Python
python3.12 --version  # Should be 3.12.x
```

### 2.3 Run Setup Script

```bash
# Make scripts executable
chmod +x setup.sh scripts/*.sh

# Run setup
./setup.sh
```

The setup script will:
- Check system architecture
- Verify CUDA installation
- Check Python version
- Verify Docker installation
- Install Python dependencies
- Create necessary directories
- Setup HuggingFace CLI

### 2.4 Authenticate with HuggingFace

```bash
# Login to HuggingFace
huggingface-cli login

# Enter your HuggingFace token when prompted
# You can get a token from: https://huggingface.co/settings/tokens
```

### 2.5 Verify Setup

```bash
# Run verification script
./scripts/verify_setup.sh
```

## Step 3: Build and Deploy

### Option A: Using Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Option B: Using Docker Directly

```bash
# Build image
docker build -t personaplex-arm64:latest -f Dockerfile.arm64 .

# Run container
docker run -d \
  --name personaplex \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e HF_TOKEN=your_token_here \
  personaplex-arm64:latest
```

### Option C: Using Makefile

```bash
# Build
make build

# Run
make run

# Check logs
make logs

# Check status
make status
```

## Step 4: Verify Deployment

### 4.1 Check Health

```bash
# Health check
curl http://localhost:8000/health

# Service info
curl http://localhost:8000/

# Model info
curl http://localhost:8000/info
```

### 4.2 Test API

```bash
# Test text generation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "temperature": 0.7
  }'
```

## Step 5: Configuration

### 5.1 Edit Configuration

Edit `config/config.yaml` to customize:

```yaml
# GPU settings
gpu:
  device_ids: [0]  # Use specific GPU(s)
  memory_fraction: 0.9

# Model settings
model:
  dtype: "float16"  # or "bfloat16"
  max_length: 2048
  temperature: 0.7

# Server settings
server:
  port: 8000
  workers: 1
```

### 5.2 Environment Variables

You can also set environment variables:

```bash
export HF_TOKEN=your_huggingface_token
export CUDA_VISIBLE_DEVICES=0
export PORT=8000
```

## Step 6: Monitoring and Maintenance

### 6.1 View Logs

```bash
# Docker Compose logs
docker-compose logs -f

# Or Docker logs
docker logs -f personaplex

# Application logs
tail -f logs/personaplex.log
```

### 6.2 Monitor GPU Usage

```bash
# Watch GPU usage
watch -n 1 nvidia-smi
```

### 6.3 Restart Service

```bash
# Using docker-compose
docker-compose restart

# Or using Docker
docker restart personaplex
```

## Troubleshooting

### Issue: Model Download Fails

**Solution:**
```bash
# Manually download model
python3 scripts/download_model.py

# Or use HuggingFace CLI
huggingface-cli download nvidia/personaplex-7b-v1
```

### Issue: CUDA Out of Memory

**Solution:**
- Reduce batch size in `config/config.yaml`
- Use float16 instead of float32
- Use a smaller model variant
- Set `memory_fraction` lower

### Issue: Port Already in Use

**Solution:**
```bash
# Change port in config/config.yaml or docker-compose.yml
# Or stop the service using the port
sudo lsof -ti:8000 | xargs kill -9
```

### Issue: Permission Denied

**Solution:**
```bash
# Make scripts executable
chmod +x setup.sh scripts/*.sh

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

### Issue: Architecture Mismatch

**Solution:**
- Verify you're on ARM64: `uname -m` should show `aarch64`
- Rebuild Docker image: `docker build --platform linux/arm64 ...`

## Performance Optimization

### 1. Enable Model Compilation

Edit `config/config.yaml`:
```yaml
performance:
  compile_model: true  # Requires PyTorch 2.0+
```

### 2. Use TensorRT (if available)

Uncomment TensorRT in `requirements.txt` and rebuild.

### 3. Adjust Batch Size

```yaml
performance:
  batch_size: 4  # Increase if you have enough GPU memory
```

## Updating

### Pull Latest Changes

```bash
# Pull from git
git pull origin main

# Rebuild if needed
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

## Backup

### Backup Configuration

```bash
# Backup config
tar -czf personaplex-config-backup.tar.gz config/

# Backup models (if stored locally)
tar -czf personaplex-models-backup.tar.gz models/
```

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify setup: `./scripts/verify_setup.sh`
3. Check NVIDIA documentation
4. Review GitHub issues

## Next Steps

- Set up reverse proxy (nginx) for production
- Configure SSL/TLS certificates
- Set up monitoring (Prometheus, Grafana)
- Implement authentication
- Set up load balancing for multiple instances
