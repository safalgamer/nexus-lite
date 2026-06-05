import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MetacognitiveState:
    """Represents the metacognitive state of the model."""
    confidence: float  # 0-1 confidence in current reasoning
    knowledge_gap: bool  # Whether the model detects a knowledge gap
    uncertainty_sources: List[str]  # Specific sources of uncertainty
    self_critique: str  # Internal critique of current reasoning
    correction_suggestions: List[str]  # Suggestions for improvement
    planning_quality: float  # Quality of current plan (0-1)
    emotional_state: Dict[str, float]  # Simulated emotional state

class MetacognitionModule(nn.Module):
    """
    Monitors the model's own hidden states to generate metacognitive feedback.
    This enables the model to think about its own thinking.
    """
    
    def __init__(self, config):
        """
        Initialize the metacognition module.
        
        Args:
            config: Model configuration object
        """
        super().__init__()
        if hasattr(config, 'model'):
            self.config = config.model
        else:
            self.config = config
        
        self.hidden_size = self.config.hidden_size
        
        # Confidence estimator - predicts how certain the model is about its output
        self.confidence_estimator = nn.Sequential(
            nn.Linear(self.hidden_size, self.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(self.hidden_size // 2, 1),
            nn.Sigmoid()
        )
        
        # Knowledge gap detector - flags when the model "doesn't know"
        self.knowledge_gap_detector = nn.Sequential(
            nn.Linear(self.hidden_size, self.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(self.hidden_size // 2, 1),
            nn.Sigmoid()
        )
        
        # Uncertainty source identifier
        self.uncertainty_identifier = nn.Sequential(
            nn.Linear(self.hidden_size, self.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(self.hidden_size // 2, self.hidden_size // 4),
            nn.ReLU(),
            nn.Linear(self.hidden_size // 4, 10)  # 10 common uncertainty types
        )
        
        # Self-critique generator (simplified - in practice this would be more complex)
        self.self_critique_generator = nn.Sequential(
            nn.Linear(self.hidden_size, self.hidden_size),
            nn.ReLU(),
            nn.Linear(self.hidden_size, self.hidden_size // 2)
        )
        
        # Planning quality assessor
        self.planning_quality_assessor = nn.Sequential(
            nn.Linear(self.hidden_size, self.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(self.hidden_size // 2, 1),
            nn.Sigmoid()
        )
        
        # Emotional state simulator (simplified)
        self.emotional_state_simulator = nn.Sequential(
            nn.Linear(self.hidden_size, self.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(self.hidden_size // 2, 6)  # 6 basic emotions: joy, sadness, anger, fear, surprise, disgust
        )
        
        logger.info("MetacognitionModule initialized")
    
    def forward(self, hidden_states: torch.Tensor) -> MetacognitiveState:
        """
        Process hidden states to generate metacognitive feedback.
        
        Args:
            hidden_states: Tensor of shape (batch_size, seq_len, hidden_size)
            
        Returns:
            MetacognitiveState object
        """
        # Use the final token's hidden state for metacognitive assessment
        final_hidden = hidden_states[:, -1, :]  # (batch_size, hidden_size)
        
        # Estimate confidence
        confidence = self.confidence_estimator(final_hidden).squeeze(-1)
        
        # Detect knowledge gaps
        knowledge_gap_prob = self.knowledge_gap_detector(final_hidden).squeeze(-1)
        knowledge_gap = knowledge_gap_prob > 0.5
        
        # Identify uncertainty sources
        uncertainty_logits = self.uncertainty_identifier(final_hidden)
        uncertainty_probs = torch.sigmoid(uncertainty_logits)
        # Convert to list of uncertainty source names (simplified)
        uncertainty_sources = []
        source_names = [
            "lack_of_knowledge", "ambiguous_input", "conflicting_information",
            "complex_reasoning", "novel_situation", "potential_error",
            "ethical_uncertainty", "missing_context", "time_pressure",
            "resource_limitations"
        ]
        for i, prob in enumerate(uncertainty_probs[0]):
            if prob > 0.3:  # Threshold for including uncertainty source
                uncertainty_sources.append(source_names[i])
        
        # Generate self-critique (simplified representation)
        self_critique_vector = self.self_critique_generator(final_hidden)
        # In a full implementation, this would be decoded to text
        self_critique = f"Self-critique vector of norm {torch.norm(self_critique_vector).item():.3f}"
        
        # Generate correction suggestions (simplified)
        correction_suggestions = [
            "Seek additional information",
            "Break problem into smaller steps",
            "Consider alternative approaches",
            "Verify assumptions",
            "Consult external knowledge base"
        ]
        
        # Assess planning quality
        planning_quality = self.planning_quality_assessor(final_hidden).squeeze(-1)
        
        # Simulate emotional state
        emotional_logits = self.emotional_state_simulator(final_hidden)
        emotional_probs = torch.softmax(emotional_logits, dim=-1)
        emotional_state = {
            "joy": emotional_probs[0][0].item(),
            "sadness": emotional_probs[0][1].item(),
            "anger": emotional_probs[0][2].item(),
            "fear": emotional_probs[0][3].item(),
            "surprise": emotional_probs[0][4].item(),
            "disgust": emotional_probs[0][5].item()
        }
        
        return MetacognitiveState(
            confidence=confidence.item(),
            knowledge_gap=knowledge_gap.item(),
            uncertainty_sources=uncertainty_sources,
            self_critique=self_critique,
            correction_suggestions=correction_suggestions,
            planning_quality=planning_quality.item(),
            emotional_state=emotional_state
        )
    
    def get_confidence_threshold(self) -> float:
        """Get the confidence threshold for triggering self-correction."""
        # This would typically come from config
        return 0.7
    
    def should_trigger_self_correction(self, metacognitive_state: MetacognitiveState) -> bool:
        """Determine if self-correction should be triggered based on metacognitive state."""
        return (
            metacognitive_state.confidence < self.get_confidence_threshold() or
            metacognitive_state.knowledge_gap or
            len(metacognitive_state.uncertainty_sources) > 2
        )
