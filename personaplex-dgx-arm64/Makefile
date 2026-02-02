# Makefile for PersonaPlex ARM64 Setup

.PHONY: help setup install build run stop clean verify test

help:
	@echo "PersonaPlex ARM64 - Available commands:"
	@echo "  make setup      - Run complete setup"
	@echo "  make install    - Install Python dependencies"
	@echo "  make build      - Build Docker image"
	@echo "  make run        - Run with docker-compose"
	@echo "  make stop       - Stop docker-compose"
	@echo "  make clean      - Clean up containers and images"
	@echo "  make verify     - Verify setup"
	@echo "  make test       - Run tests"
	@echo "  make git-init   - Initialize git repository"

setup:
	@chmod +x setup.sh scripts/*.sh
	@./setup.sh

install:
	@python3 -m pip install --upgrade pip setuptools wheel
	@python3 -m pip install -r requirements.txt

build:
	@docker build -t personaplex-arm64:latest -f Dockerfile.arm64 .

run:
	@docker-compose up -d
	@echo "Service running at http://localhost:8000"

stop:
	@docker-compose down

clean:
	@docker-compose down -v
	@docker rmi personaplex-arm64:latest || true
	@echo "Cleaned up Docker resources"

verify:
	@chmod +x scripts/verify_setup.sh
	@./scripts/verify_setup.sh

check-compat:
	@chmod +x scripts/check_compatibility.sh
	@./scripts/check_compatibility.sh

test:
	@python3 -m pytest tests/ || echo "No tests directory found"

git-init:
	@chmod +x scripts/git_setup.sh
	@./scripts/git_setup.sh

download-model:
	@python3 scripts/download_model.py

logs:
	@docker-compose logs -f

status:
	@docker-compose ps
