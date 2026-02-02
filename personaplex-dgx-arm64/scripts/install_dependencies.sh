#!/bin/bash

# Install system dependencies for PersonaPlex on ARM64

set -e

echo "Installing system dependencies..."

# Update package list
sudo apt-get update

# Install Python 3.12 if not present
if ! command -v python3.12 &> /dev/null; then
    echo "Installing Python 3.12..."
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.12 python3.12-dev python3.12-venv
fi

# Install build dependencies
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    libssl-dev \
    libffi-dev \
    libsndfile1 \
    ffmpeg

# Install Python pip if not present
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    sudo apt-get install -y python3-pip
fi

# Upgrade pip
python3 -m pip install --upgrade pip setuptools wheel

echo "System dependencies installed successfully!"
