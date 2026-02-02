# Quick Start Guide

Get PersonaPlex running on DGX Spark ARM64 in 5 minutes!

## On Your Local System

```bash
# 1. Navigate to project directory
cd personaplex-dgx-arm64

# 2. Initialize git (if not already done)
./scripts/git_setup.sh

# 3. Push to your git repository
git remote add origin <your-repo-url>
git push -u origin main
```

## On DGX Spark

```bash
# 1. Clone repository
git clone <your-repo-url>
cd personaplex-dgx-arm64

# 2. Run setup
./setup.sh

# 3. Login to HuggingFace
huggingface-cli login

# 4. Build and run
docker-compose up -d

# 5. Verify it's working
curl http://localhost:8000/health
```

That's it! The service is now running at `http://localhost:8000`

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Generate text
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'
```

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop service
docker-compose down

# Restart service
docker-compose restart

# Check status
docker-compose ps
```

## Need Help?

- Full documentation: See `README.md`
- Deployment guide: See `DEPLOYMENT.md`
- Verify setup: `./scripts/verify_setup.sh`
