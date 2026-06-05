from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import yaml
import os

@dataclass
class ModelConfig:
    """Configuration for the base transformer model."""
    # Model architecture
    backbone: str = "Qwen2.5-1.5B-Instruct"
    quantization: str = "nf4"  # 4-bit quantization
    max_seq_length: int = 2048
    use_flash_attention: bool = True
    rope_theta: float = 10000.0
    hidden_size: int = 1536
    num_attention_heads: int = 12
    num_hidden_layers: int = 28
    intermediate_size: int = 8960
    rms_norm_eps: float = 1e-5
    vocab_size: int = 151936
    
    # LoRA configuration for consciousness adapter
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: list = field(default_factory=lambda: [
        "q_proj", "v_proj", "o_proj", 
        "gate_proj", "up_proj", "down_proj"
    ])
    
    # Hardware configuration
    gpu_vram_gb: int = 6
    system_ram_gb: int = 16
    use_cpu_offload: bool = True
    max_cpu_memory_gb: int = 12
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'ModelConfig':
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Extract model configuration
        model_config = config.get('model', {})
        hardware_config = config.get('hardware', {})
        lora_config = config.get('lora', {})
        
        return cls(
            # Model architecture
            backbone=model_config.get('backbone', 'Qwen2.5-1.5B-Instruct'),
            quantization=model_config.get('quantization', 'nf4'),
            max_seq_length=model_config.get('max_seq_length', 2048),
            use_flash_attention=model_config.get('use_flash_attention', True),
            rope_theta=model_config.get('rope_theta', 10000.0),
            hidden_size=model_config.get('hidden_size', 1536),
            num_attention_heads=model_config.get('num_attention_heads', 12),
            num_hidden_layers=model_config.get('num_hidden_layers', 28),
            intermediate_size=model_config.get('intermediate_size', 8960),
            rms_norm_eps=model_config.get('rms_norm_eps', 1e-5),
            vocab_size=model_config.get('vocab_size', 151936),
            
            # LoRA configuration
            lora_rank=lora_config.get('rank', 16),
            lora_alpha=lora_config.get('alpha', 32),
            lora_dropout=lora_config.get('dropout', 0.05),
            lora_target_modules=lora_config.get('target_modules', [
                "q_proj", "v_proj", "o_proj", 
                "gate_proj", "up_proj", "down_proj"
            ]),
            
            # Hardware configuration
            gpu_vram_gb=hardware_config.get('gpu_vram_gb', 6),
            system_ram_gb=hardware_config.get('system_ram_gb', 16),
            use_cpu_offload=hardware_config.get('use_cpu_offload', True),
            max_cpu_memory_gb=hardware_config.get('max_cpu_memory_gb', 12)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            # Model architecture
            'backbone': self.backbone,
            'quantization': self.quantization,
            'max_seq_length': self.max_seq_length,
            'use_flash_attention': self.use_flash_attention,
            'rope_theta': self.rope_theta,
            'hidden_size': self.hidden_size,
            'num_attention_heads': self.num_attention_heads,
            'num_hidden_layers': self.num_hidden_layers,
            'intermediate_size': self.intermediate_size,
            'rms_norm_eps': self.rms_norm_eps,
            'vocab_size': self.vocab_size,
            
            # LoRA configuration
            'lora_rank': self.lora_rank,
            'lora_alpha': self.lora_alpha,
            'lora_dropout': self.lora_dropout,
            'lora_target_modules': self.lora_target_modules,
            
            # Hardware configuration
            'gpu_vram_gb': self.gpu_vram_gb,
            'system_ram_gb': self.system_ram_gb,
            'use_cpu_offload': self.use_cpu_offload,
            'max_cpu_memory_gb': self.max_cpu_memory_gb
        }

@dataclass
class NexusConfig:
    """Main configuration class for NEXUS-Lite system."""
    model: ModelConfig = field(default_factory=ModelConfig)
    consciousness: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    evolution: Dict[str, Any] = field(default_factory=dict)
    safety: Dict[str, Any] = field(default_factory=dict)
    api: Dict[str, Any] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'NexusConfig':
        """Load complete configuration from YAML file."""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Create model config
        model_config = ModelConfig.from_yaml(config_path)
        
        # Create main config
        config = cls(
            model=model_config,
            consciousness=config_data.get('consciousness', {}),
            memory=config_data.get('memory', {}),
            evolution=config_data.get('evolution', {}),
            safety=config_data.get('safety', {}),
            api=config_data.get('api', {}),
            logging=config_data.get('logging', {})
        )
        
        return config
