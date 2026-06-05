#!/usr/bin/env python3
"""
Script to download and test the Qwen2.5-1.5B-Instruct model with 4-bit quantization.
"""

import os
import sys
import torch
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nexus.core.model import NexusModel
from nexus.core.config import ModelConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_download():
    """Test downloading and loading the model."""
    logger.info("Starting model download test...")
    
    # Create model config
    config = ModelConfig(
        backbone="Qwen2.5-1.5B-Instruct",
        quantization="nf4",
        max_seq_length=2048,
        lora_rank=16,
        lora_alpha=32
    )
    
    # Initialize model handler
    model_handler = NexusModel(config)
    
    try:
        # Load the model
        logger.info("Loading model with 4-bit quantization...")
        model, tokenizer = model_handler.load_model()
        
        logger.info("Model loaded successfully!")
        logger.info(f"Model type: {type(model)}")
        logger.info(f"Tokenizer vocab size: {len(tokenizer)}")
        
        # Test simple generation
        logger.info("Testing text generation...")
        prompt = "Hello, I am NEXUS-Lite, a self-evolving AI. "
        generated = model_handler.generate(
            prompt=prompt,
            max_new_tokens=50,
            temperature=0.7,
            do_sample=True
        )
        
        logger.info(f"Generated text: {generated}")
        
        # Check VRAM usage if CUDA is available
        if torch.cuda.is_available():
            vram_used = torch.cuda.memory_allocated() / 1024**3
            vram_reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"VRAM used: {vram_used:.2f} GB")
            logger.info(f"VRAM reserved: {vram_reserved:.2f} GB")
        
        logger.info("Model download and test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during model test: {e}")
        return False
    finally:
        # Clean up
        model_handler.shutdown()

if __name__ == "__main__":
    success = test_model_download()
    sys.exit(0 if success else 1)
