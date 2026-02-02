"""
Model Handler for PersonaPlex
Handles model loading, inference, and management
"""

import os
import torch
import yaml
import subprocess
import sys
from typing import Optional, Dict, Any
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
from pathlib import Path
import logging
from huggingface_hub import hf_hub_download

logger = logging.getLogger(__name__)


class PersonaPlexModelHandler:
    """Handles PersonaPlex model loading and inference"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize model handler with configuration"""
        # Ensure we have the full path to the config file, not just the directory
        if os.path.isdir(config_path):
            config_path = os.path.join(config_path, 'config.yaml')
        self.config = self._load_config(config_path)
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.device = self._setup_device()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _setup_device(self) -> torch.device:
        """Setup CUDA device for ARM64"""
        if torch.cuda.is_available():
            device_id = self.config.get('gpu', {}).get('device_ids', [0])[0]
            device = torch.device(f"cuda:{device_id}")
            logger.info(f"Using CUDA device: {device}")
            
            # Set CUDA architecture for ARM64
            os.environ['CUDA_ARCHITECTURES'] = '121-real'
            
            return device
        else:
            logger.warning("CUDA not available, using CPU")
            return torch.device("cpu")
    
    def load_model(self):
        """Load the PersonaPlex model"""
        try:
            model_name = self.config['model']['name']
            model_path = self.config['model'].get('path', None)
            
            logger.info(f"Loading model: {model_name}")
            
            # Determine dtype
            dtype_str = self.config['model'].get('dtype', 'float16')
            if dtype_str == 'float16':
                dtype = torch.float16
            elif dtype_str == 'bfloat16':
                dtype = torch.bfloat16
            else:
                dtype = torch.float32
            
            # Load tokenizer and processor
            logger.info("Loading tokenizer and processor...")
            
            # Ensure sentencepiece is installed
            try:
                import sentencepiece as spm
                logger.info("sentencepiece is available")
            except ImportError:
                logger.warning("sentencepiece not found, installing...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "sentencepiece", "tiktoken"])
                import sentencepiece as spm
                logger.info("sentencepiece and tiktoken installed")
            
            # PersonaPlex uses a SentencePiece model file: tokenizer_spm_32k_3.model
            # We need to load it directly using sentencepiece or create a tokenizer from it
            tokenizer_loaded = False
            last_error = None
            
            # Strategy 1: Download SentencePiece model first, then load tokenizer
            # PersonaPlex has tokenizer_spm_32k_3.model - we need to ensure it's downloaded
            cache_dir = self.config.get('huggingface', {}).get('cache_dir')
            try:
                logger.info("Downloading SentencePiece model file (tokenizer_spm_32k_3.model)...")
                spm_model_path = hf_hub_download(
                    repo_id=model_name,
                    filename="tokenizer_spm_32k_3.model",
                    cache_dir=cache_dir,
                    token=os.getenv('HF_TOKEN')
                )
                logger.info(f"Downloaded SentencePiece model to: {spm_model_path}")
            except Exception as e_download:
                logger.warning(f"Could not download SentencePiece model: {e_download}")
                spm_model_path = None
            
            # Strategy 1: Try loading tokenizer normally (transformers should auto-detect SPM file)
            try:
                logger.info("Attempting to load tokenizer (transformers should auto-detect SentencePiece model)...")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=cache_dir,
                    trust_remote_code=True,
                    local_files_only=False
                )
                tokenizer_loaded = True
                logger.info("Tokenizer loaded successfully with auto-detection")
            except Exception as e1:
                last_error = e1
                logger.warning(f"Strategy 1 (auto-detect) failed: {e1}")
            
            # Strategy 2: Try with use_fast=False (force slow tokenizer)
            if not tokenizer_loaded:
                try:
                    logger.info("Attempting to load tokenizer with use_fast=False...")
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        cache_dir=cache_dir,
                        trust_remote_code=True,
                        use_fast=False,
                        local_files_only=False
                    )
                    tokenizer_loaded = True
                    logger.info("Tokenizer loaded successfully with use_fast=False")
                except Exception as e2:
                    last_error = e2
                    logger.warning(f"Strategy 2 (use_fast=False) failed: {e2}")
            
            # Strategy 3: Try with local_files_only=True (use already downloaded files)
            if not tokenizer_loaded and spm_model_path:
                try:
                    logger.info("Attempting to load tokenizer from cached files...")
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        cache_dir=cache_dir,
                        trust_remote_code=True,
                        local_files_only=True
                    )
                    tokenizer_loaded = True
                    logger.info("Tokenizer loaded successfully from cached files")
                except Exception as e3:
                    last_error = e3
                    logger.warning(f"Strategy 3 (cached files) failed: {e3}")
            
            if not tokenizer_loaded:
                error_msg = (
                    f"All tokenizer loading strategies failed. Last error: {last_error}\n"
                    f"PersonaPlex uses tokenizer_spm_32k_3.model (SentencePiece).\n"
                    f"Please ensure:\n"
                    f"1. HuggingFace token is set (HF_TOKEN environment variable)\n"
                    f"2. Model files are downloaded correctly\n"
                    f"3. SentencePiece is properly installed"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            try:
                self.processor = AutoProcessor.from_pretrained(
                    model_name,
                    cache_dir=self.config.get('huggingface', {}).get('cache_dir'),
                    trust_remote_code=True
                )
            except Exception as e:
                logger.warning(f"Processor not available: {e}")
                self.processor = None
            
            # Load model
            logger.info("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=dtype,
                device_map="auto",
                cache_dir=self.config.get('huggingface', {}).get('cache_dir'),
                trust_remote_code=True
            )
            
            # Move to device if not using device_map
            if not isinstance(self.model, torch.nn.Module):
                self.model = self.model.to(self.device)
            
            # Set to evaluation mode
            self.model.eval()
            
            # Compile model if requested (PyTorch 2.0+)
            if self.config.get('performance', {}).get('compile_model', False):
                try:
                    logger.info("Compiling model...")
                    self.model = torch.compile(self.model)
                except Exception as e:
                    logger.warning(f"Model compilation failed: {e}")
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate(self, 
                 input_text: Optional[str] = None,
                 input_audio: Optional[Any] = None,
                 **kwargs) -> Dict[str, Any]:
        """Generate response from model"""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Prepare inputs
            if input_text:
                inputs = self.tokenizer(input_text, return_tensors="pt")
            elif input_audio and self.processor:
                inputs = self.processor(input_audio, return_tensors="pt")
            else:
                raise ValueError("Either input_text or input_audio must be provided")
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get generation parameters from config
            generation_config = {
                'max_length': self.config['model'].get('max_length', 2048),
                'temperature': self.config['model'].get('temperature', 0.7),
                'top_p': self.config['model'].get('top_p', 0.9),
                'top_k': self.config['model'].get('top_k', 50),
                **kwargs
            }
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    **generation_config
                )
            
            # Decode output
            if input_text:
                output_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                output_text = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            return {
                'output': output_text,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                'output': None,
                'success': False,
                'error': str(e)
            }
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.is_loaded():
            return {'loaded': False}
        
        return {
            'loaded': True,
            'model_name': self.config['model']['name'],
            'device': str(self.device),
            'dtype': self.config['model'].get('dtype', 'float16'),
            'cuda_available': torch.cuda.is_available(),
            'cuda_device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
