# Project Structure

Complete overview of the PersonaPlex ARM64 project structure.

```
personaplex-dgx-arm64/
│
├── README.md                    # Main documentation
├── QUICKSTART.md                # Quick start guide
├── DEPLOYMENT.md                # Detailed deployment guide
├── PROJECT_STRUCTURE.md         # This file
│
├── Dockerfile.arm64             # Docker image for ARM64
├── docker-compose.yml           # Docker Compose configuration
├── Makefile                     # Convenience commands
│
├── setup.sh                     # Main setup script
├── requirements.txt             # Python dependencies
│
├── .gitignore                   # Git ignore rules
├── .gitattributes               # Git attributes
├── .dockerignore                # Docker ignore rules
│
├── config/                      # Configuration files
│   ├── config.yaml             # Main application config
│   └── model_config.json       # Model-specific config
│
├── src/                         # Source code
│   ├── __init__.py             # Package init
│   ├── server.py               # FastAPI server
│   └── model_handler.py        # Model loading and inference
│
└── scripts/                     # Utility scripts
    ├── install_dependencies.sh # System dependencies installer
    ├── verify_setup.sh         # Setup verification
    ├── download_model.py       # Model downloader
    ├── git_setup.sh            # Git repository setup
    └── test_api.sh             # API testing script
```

## File Descriptions

### Documentation
- **README.md**: Main project documentation with overview and setup instructions
- **QUICKSTART.md**: Quick 5-minute setup guide
- **DEPLOYMENT.md**: Detailed step-by-step deployment instructions
- **PROJECT_STRUCTURE.md**: This file - project structure overview

### Docker Files
- **Dockerfile.arm64**: Docker image definition optimized for ARM64 architecture
- **docker-compose.yml**: Docker Compose configuration for easy deployment
- **.dockerignore**: Files to exclude from Docker build context

### Configuration
- **config/config.yaml**: Main application configuration (model, server, GPU settings)
- **config/model_config.json**: Model-specific configuration and metadata

### Source Code
- **src/server.py**: FastAPI server with REST API endpoints
- **src/model_handler.py**: Model loading, inference, and management
- **src/__init__.py**: Package initialization

### Scripts
- **setup.sh**: Main setup script that checks system and installs dependencies
- **scripts/install_dependencies.sh**: Installs system-level dependencies
- **scripts/verify_setup.sh**: Verifies that setup is correct
- **scripts/download_model.py**: Downloads model from HuggingFace
- **scripts/git_setup.sh**: Initializes git repository
- **scripts/test_api.sh**: Tests API endpoints

### Build & Dependencies
- **requirements.txt**: Python package dependencies
- **Makefile**: Convenience commands for common tasks

### Git
- **.gitignore**: Files and directories to exclude from git
- **.gitattributes**: Git file attributes for line endings

## Directory Usage

### `/config`
Contains all configuration files. Edit these to customize:
- Model settings (dtype, temperature, etc.)
- Server settings (port, workers)
- GPU settings (device IDs, memory)

### `/src`
Contains the main application code:
- Server implementation
- Model handling logic
- API endpoints

### `/scripts`
Utility scripts for setup, verification, and testing.

### Generated Directories (not in git)
- `/models`: Downloaded models (gitignored)
- `/data`: Data files (gitignored)
- `/logs`: Application logs (gitignored)

## Workflow

1. **Setup**: Run `./setup.sh` to install dependencies
2. **Configure**: Edit files in `config/` directory
3. **Build**: Use `make build` or `docker-compose build`
4. **Run**: Use `make run` or `docker-compose up`
5. **Test**: Use `./scripts/test_api.sh` to verify

## Customization Points

- **Model settings**: `config/config.yaml` → `model:` section
- **Server settings**: `config/config.yaml` → `server:` section
- **GPU settings**: `config/config.yaml` → `gpu:` section
- **API endpoints**: `src/server.py`
- **Model logic**: `src/model_handler.py`
