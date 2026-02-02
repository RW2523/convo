#!/usr/bin/env python3
"""
HuggingFace Login Script
Alternative to huggingface-cli when CLI is not available
"""

import sys
from huggingface_hub import login

def main():
    """Login to HuggingFace"""
    try:
        print("HuggingFace Login")
        print("=" * 50)
        print("Get your token from: https://huggingface.co/settings/tokens")
        print()
        
        # Login (will prompt for token)
        login()
        
        print()
        print("✅ Login successful!")
        print("Token saved to ~/.cache/huggingface/token")
        
    except KeyboardInterrupt:
        print("\n❌ Login cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
