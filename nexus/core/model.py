import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import logging
from pathlib import Path
from typing import Optional, Tuple
import yaml

logger = logging.getLogger(__name__)

class NexusModel:
    """Handles the base model loading with 4-bit quantization and LoRA adapters."""
    
    def __init__(self, config):
        """
        Initialize the NexusModel with configuration.
        
        Args:
            config: Configuration object or dictionary
        """
        if hasattr(config, 'model'):
            # If it's a NexusConfig object
            self.config = config.model
        else:
            # If it's already a model config dict or ModelConfig object
            self.config = config
            
        self.model = None
        self.tokenizer = None
        self.device = None
        self._is_loaded = False
        
    def load_model(self) -> Tuple[torch.nn.Module, AutoTokenizer]:
        """
        Load the base model with 4-bit quantization and prepare for LoRA.
        
        Returns:
            Tuple of (model, tokenizer)
        """
        try:
            logger.info(f"Loading base model: {self.config.backbone}")
            logger.info(f"Using 4-bit quantization: {self.config.quantization}")
            
            # Determine device
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                self.device = torch.device("cpu")
                logger.warning("CUDA not available, using CPU (will be slow)")
            
            # Configure 4-bit quantization
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=self.config.quantization,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.backbone,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add special tokens for consciousness and reasoning
            special_tokens = [
                "[THINK]", "[/THINK]", 
                "[REFLECT]", "[/REFLECT]",
                "[MEMORY]", "[/MEMORY]",
                "[EVOLVE]", "[/EVOLVE]",
                "[FEEL]", "[/FEEL]",
                "[META]", "[/META]",
                "[DREAM]", "[/DREAM]",
                "[GOAL]", "[/GOAL]",
                "[PLAN]", "[/PLAN]",
                "[EVALUATE]", "[/EVALUATE]",
                "[IMAGINE]", "[/IMAGINE]"
            ]
            
            # Add tokens that don't already exist
            existing_tokens = set(self.tokenizer.get_vocab().keys())
            new_tokens = [token for token in special_tokens if token not in existing_tokens]
            
            if new_tokens:
                logger.info(f"Adding {len(new_tokens)} special tokens: {new_tokens}")
                self.tokenizer.add_tokens(new_tokens)
            
            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load base model with quantization
            logger.info("Loading base model with 4-bit quantization...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.backbone,
                quantization_config=bnb_config,
                device_map="auto" if self.device.type == "cuda" else None,
                trust_remote_code=True,
                torch_dtype=torch.bfloat16 if self.device.type == "cuda" else torch.float32,
            )
            
            # Resize token embeddings to accommodate new special tokens
            if len(new_tokens) > 0:
                logger.info(f"Resizing token embeddings from {self.model.config.vocab_size} to {self.model.config.vocab_size + len(new_tokens)}")
                self.model.resize_token_embeddings(len(self.tokenizer))
            
            # Prepare model for k-bit training (LoRA)
            logger.info("Preparing model for k-bit training (LoRA)...")
            self.model = prepare_model_for_kbit_training(self.model)
            
            # Configure LoRA
            logger.info(f"Configuring LoRA with rank={self.config.lora_rank}, alpha={self.config.lora_alpha}")
            lora_config = LoraConfig(
                r=self.config.lora_rank,
                lora_alpha=self.config.lora_alpha,
                target_modules=self.config.lora_target_modules,
                lora_dropout=self.config.lora_dropout,
                bias="none",
                task_type="CAUSAL_LM",
            )
            
            # Apply LoRA to model
            self.model = get_peft_model(self.model, lora_config)
            self.model.print_trainable_parameters()
            
            # Set model to evaluation mode by default
            self.model.eval()
            
            self._is_loaded = True
            logger.info("Model loading completed successfully!")
            
            return self.model, self.tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate(self, 
                 prompt: str, 
                 max_new_tokens: int = 512,
                 temperature: float = 0.7,
                 top_p: float = 0.9,
                 do_sample: bool = True,
                 **kwargs) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            do_sample: Whether to use sampling
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text string
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_seq_length - max_new_tokens
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                **kwargs
            )
        
        # Decode output
        generated_text = self.tokenizer.decode(
            outputs[0], 
            skip_special_tokens=False  # Keep special tokens for consciousness processing
        )
        
        return generated_text
    
    def get_trainable_parameters(self):
        """Get trainable parameters for LoRA adapter."""
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        return [p for p in self.model.parameters() if p.requires_grad]
    
    def save_lora_adapter(self, path: str):
        """Save only the LoRA adapter weights."""
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        logger.info(f"Saving LoRA adapter to {path}")
        self.model.save_pretrained(path)
    
    def load_lora_adapter(self, path: str):
        """Load LoRA adapter weights."""
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        logger.info(f"Loading LoRA adapter from {path}")
        # The PEFT model should already be set up, we just load the adapter weights
        from peft import PeftModel
        self.model = PeftModel.from_pretrained(self.model, path)
        self.model.print_trainable_parameters()
    
    def merge_and_unload(self):
        """Merge LoRA weights with base model and unload LoRA for faster inference."""
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        logger.info("Merging LoRA weights with base model...")
        self.model = self.model.merge_and_unload()
        logger.info("LoRA weights merged successfully.")
    
    def shutdown(self):
        """Clean up resources."""
        logger.info("Shutting down model...")
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self._is_loaded = False
        logger.info("Model shutdown complete.")
