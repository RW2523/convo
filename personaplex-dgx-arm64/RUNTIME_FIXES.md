# Runtime Fixes - Config Path and GPU Issues

## Issues Fixed

### 1. Config Path Error
**Problem**: `IsADirectoryError: [Errno 21] Is a directory: '/app/config'`

The code was trying to open `/app/config` as a file, but it's a directory. The config file is `/app/config/config.yaml`.

**Fix Applied**:
- Updated `src/server.py` to check if config_path is a directory and append `config.yaml`
- Updated `src/model_handler.py` to handle directory paths correctly
- Both now properly resolve to `/app/config/config.yaml`

### 2. FastAPI Deprecation Warning
**Problem**: `on_event is deprecated, use lifespan event handlers instead`

**Fix Applied**:
- Replaced `@app.on_event("startup")` and `@app.on_event("shutdown")` with modern `lifespan` context manager
- Uses `@asynccontextmanager` for proper async lifecycle management

### 3. GPU Detection and PyTorch Issues
**Problem**: 
- `WARNING: Detected NVIDIA GB10 GPU, which is not yet supported`
- `ERROR: No supported GPU(s) detected`
- PyTorch version mismatch warnings

**Fix Applied**:
- Added GPU optimization settings to `docker-compose.yml`:
  - `ipc: host` - Shared memory for PyTorch
  - `shm_size: '2gb'` - Increased shared memory
  - `ulimits` - Memory lock and stack size settings

## Files Changed

1. **src/server.py**:
   - Fixed config path resolution
   - Updated to use lifespan handlers instead of deprecated on_event
   - Properly handles CONFIG_PATH environment variable

2. **src/model_handler.py**:
   - Fixed config path resolution in `__init__` method
   - Handles both file paths and directory paths

3. **docker-compose.yml**:
   - Added GPU optimization settings
   - Added shared memory configuration
   - Added ulimits for PyTorch

## Testing

After these fixes, rebuild and restart:

```bash
# Rebuild the image
docker build -f Dockerfile.ngc -t personaplex-arm64:latest .

# Restart services
docker compose down
docker compose up -d

# Check logs
docker compose logs -f
```

The config path error should be resolved, and GPU detection should work better with the added settings.

## Note on GPU Warnings

The GB10 GPU warning may still appear if the PyTorch version in the NGC container doesn't fully support it yet. However, the container should still function. The added GPU settings help optimize performance.
