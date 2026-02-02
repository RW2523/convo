# Final Tokenizer Fix - SentencePiece Installation

## Issue
Even after adding sentencepiece to Dockerfile, the error persists: "You need to have sentencepiece or tiktoken installed"

## Root Cause
The error occurs because:
1. The model doesn't have standard tokenizer files (tokenizer.json, tokenizer.model, etc.)
2. Transformers is trying to convert a slow tokenizer to fast, which requires sentencepiece
3. Even with `use_fast=False`, transformers may still attempt conversion

## Comprehensive Fix Applied

### 1. Enhanced Dockerfile.ngc
- Explicitly installs sentencepiece and tiktoken BEFORE other requirements
- Verifies installation with Python checks
- Ensures they're available before model loading

### 2. Improved model_handler.py
- Checks if sentencepiece is installed at runtime
- Installs it if missing (runtime fallback)
- Multiple tokenizer loading strategies:
  - Strategy 1: `use_fast=False` (slow tokenizer)
  - Strategy 2: No use_fast parameter (let transformers decide)
  - Strategy 3: `use_fast=True` (fast tokenizer)
- Better error messages and logging

### 3. Runtime Installation Fallback
If sentencepiece is not found at runtime, the code will:
- Detect the missing dependency
- Install it automatically
- Retry tokenizer loading

## Rebuild Required

**IMPORTANT**: You must rebuild the Docker image for the fixes to take effect:

```bash
# Rebuild with no cache to ensure fresh installation
docker build --no-cache -f Dockerfile.ngc -t personaplex-arm64:latest .

# Restart services
docker compose down
docker compose up -d

# Check logs
docker compose logs -f
```

## Verification

After rebuild, check logs for:
- "sentencepiece is available" or "sentencepiece and tiktoken installed"
- "Tokenizer loaded successfully"
- No more "sentencepiece or tiktoken installed" errors

## Alternative: Check Installation in Container

If issues persist, verify installation:

```bash
# Enter container
docker exec -it personaplex-arm64 bash

# Check if sentencepiece is installed
python3 -c "import sentencepiece; print('OK')"
python3 -c "import tiktoken; print('OK')"

# If not, install manually
pip install sentencepiece tiktoken
```

## Note on PersonaPlex Model

The PersonaPlex model may have non-standard tokenizer files. The multiple fallback strategies should handle this, but if all fail, you may need to:
1. Check the model repository structure on HuggingFace
2. Use a different model loading approach
3. Contact NVIDIA support for PersonaPlex-specific loading instructions
