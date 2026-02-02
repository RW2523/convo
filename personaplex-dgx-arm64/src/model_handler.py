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
            
            # Ensure sentencepiece and tiktoken are installed
            try:
                import sentencepiece
                logger.info("sentencepiece is available")
            except ImportError:
                logger.warning("sentencepiece not found, installing...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "sentencepiece", "tiktoken"])
                logger.info("sentencepiece and tiktoken installed")
            
            # Load model config first to understand tokenizer requirements
            from transformers import AutoConfig
            try:
                logger.info("Loading model configuration...")
                model_config = AutoConfig.from_pretrained(
                    model_name,
                    cache_dir=self.config.get('huggingface', {}).get('cache_dir'),
                    trust_remote_code=True
                )
                logger.info(f"Model config loaded. Model type: {model_config.model_type if hasattr(model_config, 'model_type') else 'unknown'}")
                
                # Check if tokenizer class is specified in config
                tokenizer_class_name = None
                if hasattr(model_config, 'tokenizer_class'):
                    tokenizer_class_name = model_config.tokenizer_class
                    logger.info(f"Tokenizer class from config: {tokenizer_class_name}")
            except Exception as e:
                logger.warning(f"Could not load model config: {e}")
                model_config = None
            
            # Try loading tokenizer with multiple fallback strategies
            tokenizer_loaded = False
            last_error = None
            
            # Strategy 1: Try loading from config.json tokenizer_class if available
            if model_config and hasattr(model_config, 'tokenizer_class') and model_config.tokenizer_class:
                try:
                    logger.info(f"Attempting to load tokenizer using class from config: {model_config.tokenizer_class}")
                    # Import the tokenizer class dynamically
                    from transformers import AutoTokenizer
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        cache_dir=self.config.get('huggingface', {}).get('cache_dir'),
                        trust_remote_code=True,
                        use_fast=False,  # Force slow tokenizer for custom classes
                        local_files_only=False
                    )
                    tokenizer_loaded = True
                    logger.info("Tokenizer loaded successfully using config tokenizer class")
                except Exception as e1:
                    last_error = e1
                    logger.warning(f"Strategy 1 (config-based) failed: {e1}")
            
            # Strategy 2: Try with use_fast=False (slow tokenizer) - bypass fast tokenizer conversion
            if not tokenizer_loaded:
                try:
                    logger.info("Attempting to load tokenizer with use_fast=False (slow tokenizer)...")
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        cache_dir=self.config.get('huggingface', {}).get('cache_dir'),
                        trust_remote_code=True,
                        use_fast=False,
                        local_files_only=False,
                        revision="main"  # Explicitly use main branch
                    )
                    tokenizer_loaded = True
                    logger.info("Tokenizer loaded successfully with use_fast=False")
                except Exception as e2:
                    last_error = e2
                    logger.warning(f"Strategy 2 (use_fast=False) failed: {e2}")
            
            # Strategy 3: Try loading tokenizer class directly from transformers
            if not tokenizer_loaded:
                try:
                    logger.info("Attempting to load tokenizer by instantiating class directly...")
                    # Try to get tokenizer class from model type
                    if model_config and hasattr(model_config, 'model_type'):
                        from transformers import AutoTokenizer
                        # Force use of slow tokenizer by setting use_fast=False
                        self.tokenizer = AutoTokenizer.from_pretrained(
                            model_name,
                            cache_dir=self.config.get('huggingface', {}).get('cache_dir'),
                            trust_remote_code=True,
                            use_fast=False,
                            local_files_only=False
                        )
                    else:
                        raise ValueError("Cannot determine tokenizer class")
                    tokenizer_loaded = True
                    logger.info("Tokenizer loaded successfully by direct instantiation")
                except Exception as e3:
                    last_error = e3
                    logger.warning(f"Strategy 3 (direct instantiation) failed: {e3}")
            
            # Strategy 4: Last resort - try without any restrictions
            if not tokenizer_loaded:
                try:
                    logger.info("Attempting to load tokenizer without restrictions...")
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        cache_dir=self.config.get('huggingface', {}).get('cache_dir'),
                        trust_remote_code=True,
                        local_files_only=False
                    )
                    tokenizer_loaded = True
                    logger.info("Tokenizer loaded successfully without restrictions")
                except Exception as e4:
                    last_error = e4
                    logger.warning(f"Strategy 4 (no restrictions) failed: {e4}")
            
            if not tokenizer_loaded:
                error_msg = (
                    f"All tokenizer loading strategies failed. Last error: {last_error}\n"
                    f"The PersonaPlex model may require a custom tokenizer implementation.\n"
                    f"Please check:\n"
                    f"1. Model repository structure on HuggingFace: https://huggingface.co/{model_name}\n"
                    f"2. Official PersonaPlex documentation for tokenizer requirements\n"
                    f"3. Whether the model needs to be downloaded manually or requires special setup"
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
