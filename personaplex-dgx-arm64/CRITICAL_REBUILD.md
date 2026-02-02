# ⚠️ CRITICAL: Rebuild Required

## Current Issue
The tokenizer error persists because **the Docker image needs to be rebuilt** with the latest fixes.

## What Was Fixed

1. ✅ **Dockerfile.ngc**: Now explicitly installs and verifies sentencepiece/tiktoken
2. ✅ **model_handler.py**: Added runtime installation fallback and multiple loading strategies
3. ✅ **requirements.txt**: Added tiktoken

## ⚠️ YOU MUST REBUILD THE IMAGE

The fixes are in the code, but the running container was built with the old code. You need to rebuild:

```bash
# Stop current container
docker compose down

# Rebuild with NO CACHE to ensure fresh installation
docker build --no-cache -f Dockerfile.ngc -t personaplex-arm64:latest .

# Start again
docker compose up -d

# Check logs
docker compose logs -f
```

## Why --no-cache?

Using `--no-cache` ensures:
- Fresh installation of sentencepiece/tiktoken
- Verification steps run
- No cached layers with missing dependencies

## Expected Behavior After Rebuild

You should see in logs:
1. ✅ "sentencepiece version: X.X.X" during build
2. ✅ "tiktoken installed" during build
3. ✅ "Tokenizer dependencies verified" during build
4. ✅ "sentencepiece is available" at runtime
5. ✅ "Tokenizer loaded successfully" at runtime

## If Still Failing After Rebuild

If the error persists after rebuild, the issue may be:
1. **Model-specific**: PersonaPlex model may need special tokenizer handling
2. **Missing model files**: Tokenizer files may not be in the repository
3. **Custom tokenizer**: May need to use a different loading method

In that case, check:
- Model repository structure on HuggingFace
- Official PersonaPlex documentation for tokenizer requirements
- Consider using a different base tokenizer if PersonaPlex provides one

## Quick Test

After rebuild, test in container:

```bash
docker exec -it personaplex-arm64 python3 -c "import sentencepiece; import tiktoken; print('OK')"
```

If this fails, sentencepiece/tiktoken are not installed properly.
