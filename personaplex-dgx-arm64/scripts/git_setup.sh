#!/bin/bash

# Git setup script for PersonaPlex ARM64 project

set -e

echo "=========================================="
echo "Git Repository Setup"
echo "=========================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed. Please install git first."
    exit 1
fi

# Check if already a git repository
if [ -d ".git" ]; then
    echo "Git repository already initialized."
    read -p "Do you want to reinitialize? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing git repository."
        exit 0
    fi
    rm -rf .git
fi

# Initialize git repository
echo "Initializing git repository..."
git init

# Add all files
echo "Adding files to git..."
git add .

# Create initial commit
echo "Creating initial commit..."
git commit -m "Initial PersonaPlex ARM64 setup for DGX Spark"

# Ask for remote repository
echo ""
read -p "Do you want to add a remote repository? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter remote repository URL: " REMOTE_URL
    if [ -n "$REMOTE_URL" ]; then
        git remote add origin "$REMOTE_URL"
        echo "Remote repository added: $REMOTE_URL"
        
        read -p "Do you want to push to remote? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
            git push -u origin "$BRANCH"
            echo "Pushed to remote repository"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "Git setup completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. If you haven't added a remote, do it now:"
echo "   git remote add origin <your-repo-url>"
echo ""
echo "2. Push to remote:"
echo "   git push -u origin main"
echo ""
echo "3. On DGX Spark, clone the repository:"
echo "   git clone <your-repo-url>"
echo "   cd personaplex-dgx-arm64"
echo "   ./setup.sh"
