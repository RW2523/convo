# Tokenizer Fix - Using SentencePiece Model File

## Discovery
The PersonaPlex model repository contains:
- ✅ `tokenizer_spm_32k_3.model` - SentencePiece model file (552KB)
- ✅ `tokenizer-e351c8d8-checkpoint125.safetensors` - Tokenizer checkpoint
- ❌ No `tokenizer.json` or `tokenizer_config.json` (standard transformers format)

## Solution
The code now:
1. **Downloads the SentencePiece model file** explicitly using `hf_hub_download`
2. **Loads tokenizer** using `AutoTokenizer.from_pretrained` with `trust_remote_code=True`
3. **Falls back** to different loading strategies if needed

## How It Works
Transformers library can automatically detect and use SentencePiece model files when:
- The file is named correctly (e.g., `tokenizer_spm_32k_3.model`)
- `trust_remote_code=True` is set
- The model config specifies the tokenizer type

## Rebuild Required
```bash
docker compose down
docker build --no-cache -f Dockerfile.ngc -t personaplex-arm64:latest .
docker compose up -d
docker compose logs -f
```

## Expected Behavior
After rebuild, you should see:
1. ✅ "Downloading SentencePiece model file..."
2. ✅ "Downloaded SentencePiece model to: /path/to/tokenizer_spm_32k_3.model"
3. ✅ "Tokenizer loaded successfully"

## If Still Failing
If the tokenizer still fails to load, check:
1. **HF_TOKEN** is set correctly in environment
2. Model files are downloaded (check cache directory)
3. SentencePiece is properly installed
4. The custom PersonaPlex tokenizer class is loaded via `trust_remote_code=True`
