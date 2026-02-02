#!/usr/bin/env python3
"""
Download PersonaPlex model from HuggingFace
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_model(model_name: str = "nvidia/personaplex-7b-v1", 
                   cache_dir: str = None):
    """Download model from HuggingFace"""
    
    if cache_dir is None:
        cache_dir = os.path.expanduser("~/.cache/huggingface")
    
    logger.info(f"Downloading model: {model_name}")
    logger.info(f"Cache directory: {cache_dir}")
    
    try:
        # Check if already downloaded
        model_path = Path(cache_dir) / "hub" / model_name.replace("/", "--")
        if model_path.exists():
            logger.info(f"Model already exists at {model_path}")
            response = input("Re-download? (y/N): ")
            if response.lower() != 'y':
                logger.info("Skipping download")
                return str(model_path)
        
        # Download model
        logger.info("Starting download...")
        downloaded_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            resume_download=True
        )
        
        logger.info(f"Model downloaded successfully to: {downloaded_path}")
        return downloaded_path
        
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        logger.error("Make sure you're authenticated with HuggingFace:")
        logger.error("  huggingface-cli login")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download PersonaPlex model")
    parser.add_argument(
        "--model",
        default="nvidia/personaplex-7b-v1",
        help="Model name on HuggingFace"
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Cache directory for models"
    )
    
    args = parser.parse_args()
    
    download_model(args.model, args.cache_dir)
