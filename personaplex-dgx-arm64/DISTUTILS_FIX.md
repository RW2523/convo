# Distutils Fix for Python 3.12

## Issue
Python 3.12 from deadsnakes PPA doesn't include `distutils` by default, which is required by pip.

## Fix Applied

The Dockerfile has been updated to:

1. **Install python3.12-distutils** - Provides distutils module
2. **Use ensurepip or get-pip.py** - Properly installs pip for Python 3.12
3. **Use python3.12 explicitly** - Ensures we're using the correct Python version

## What Changed

```dockerfile
# Added python3.12-distutils package
python3.12-distutils \

# Install pip properly using ensurepip or get-pip.py
RUN python3.12 -m ensurepip --upgrade || \
    (curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12) && \
    python3.12 -m pip install --no-cache-dir --upgrade pip setuptools wheel
```

## Build Again

Now you can build successfully:

```bash
docker build -t personaplex-arm64:latest -f Dockerfile.arm64 .
```

## Alternative: Use Dockerfile.ngc (Recommended)

The NGC container already has everything configured:

```bash
docker build -t personaplex-arm64:latest -f Dockerfile.ngc .
```

This avoids all Python 3.12 installation issues since PyTorch and Python are pre-configured.
