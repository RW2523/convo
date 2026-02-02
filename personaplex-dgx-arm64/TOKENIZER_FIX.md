# Tokenizer Fix - SentencePiece Missing

## Issue
**Error**: `You need to have sentencepiece or tiktoken installed to convert a slow tokenizer to a fast one.`

The PersonaPlex model requires `sentencepiece` or `tiktoken` for tokenizer support, but it's not being installed properly in the Docker container.

## Fixes Applied

### 1. Ensure SentencePiece Installation
Updated `Dockerfile.ngc` to explicitly install `sentencepiece` and `tiktoken` before other requirements:

```dockerfile
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir sentencepiece tiktoken && \
    pip3 install --no-cache-dir -r requirements.txt
```

### 2. Tokenizer Fallback
Updated `src/model_handler.py` to use slow tokenizer as fallback if fast tokenizer files are not available:

- First tries with `use_fast=False` (slow tokenizer)
- Falls back to `use_fast=True` if that fails

### 3. Docker Compose Version Warning
Removed obsolete `version: '3.8'` from `docker-compose.yml` to eliminate warning.

## Rebuild and Test

```bash
# Rebuild with fixes
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .

# Restart services
docker compose down
docker compose up -d

# Check logs
docker compose logs -f
```

## Note on Tokenizer Files

The model repository may not have standard tokenizer files (tokenizer.json, tokenizer.model, etc.), which is why we're using the slow tokenizer fallback. This is normal for some custom models.

## Additional Notes

- `sentencepiece>=0.1.99` is already in requirements.txt
- The explicit installation in Dockerfile ensures it's available
- `tiktoken` is added as a backup option
- Slow tokenizer will work even if fast tokenizer files are missing
