"""
FastAPI Server for PersonaPlex
Provides REST API for speech-to-speech conversation
"""

import os
import sys
import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_handler import PersonaPlexModelHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NVIDIA PersonaPlex API",
    description="Speech-to-Speech Conversational AI API for ARM64",
    version="1.0.0"
)

# Global model handler
model_handler: Optional[PersonaPlexModelHandler] = None


class TextRequest(BaseModel):
    """Text input request model"""
    text: str
    temperature: Optional[float] = None
    max_length: Optional[int] = None


class Response(BaseModel):
    """Response model"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None


def load_config() -> Dict[str, Any]:
    """Load configuration"""
    config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    global model_handler
    
    try:
        logger.info("Initializing PersonaPlex model...")
        config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
        model_handler = PersonaPlexModelHandler(config_path=config_path)
        model_handler.load_model()
        logger.info("Model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_handler
    if model_handler:
        logger.info("Shutting down model handler...")
        model_handler = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "NVIDIA PersonaPlex API",
        "version": "1.0.0",
        "architecture": "ARM64",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model_handler and model_handler.is_loaded():
        return {
            "status": "healthy",
            "model_loaded": True
        }
    else:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "model_loaded": False
            }
        )


@app.get("/info")
async def get_info():
    """Get model and system information"""
    if not model_handler:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    info = model_handler.get_model_info()
    return info


@app.post("/generate", response_model=Response)
async def generate_text(request: TextRequest):
    """Generate response from text input"""
    if not model_handler or not model_handler.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare generation parameters
        gen_kwargs = {}
        if request.temperature is not None:
            gen_kwargs['temperature'] = request.temperature
        if request.max_length is not None:
            gen_kwargs['max_length'] = request.max_length
        
        # Generate response
        result = model_handler.generate(
            input_text=request.text,
            **gen_kwargs
        )
        
        if result['success']:
            return Response(
                success=True,
                output=result['output']
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Generation failed')
            )
            
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/audio")
async def generate_from_audio(audio: UploadFile = File(...)):
    """Generate response from audio input"""
    if not model_handler or not model_handler.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Read audio file
        audio_data = await audio.read()
        
        # Process audio (simplified - you may need to add audio processing)
        result = model_handler.generate(input_audio=audio_data)
        
        if result['success']:
            return Response(
                success=True,
                output=result['output']
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Generation failed')
            )
            
    except Exception as e:
        logger.error(f"Audio generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point"""
    config = load_config()
    server_config = config.get('server', {})
    
    host = os.getenv('HOST', server_config.get('host', '0.0.0.0'))
    port = int(os.getenv('PORT', server_config.get('port', 8000)))
    workers = int(os.getenv('WORKERS', server_config.get('workers', 1)))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "src.server:app",
        host=host,
        port=port,
        workers=workers,
        log_level="info"
    )


if __name__ == "__main__":
    main()
