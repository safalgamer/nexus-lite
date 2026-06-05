#!/usr/bin/env python3
"""
Basic test to verify the NEXUS-Lite structure is working.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that we can import the main modules."""
    try:
        # Test config import
        from nexus.core.config import ModelConfig, NexusConfig
        print("✓ Config modules imported successfully")
        
        # Test model import
        from nexus.core.model import NexusModel
        print("✓ Model module imported successfully")
        
        # Test consciousness import
        from nexus.consciousness.metacognition import MetacognitionModule, MetacognitiveState
        print("✓ Consciousness module imported successfully")
        
        # Test that we can create a config
        config = ModelConfig()
        print("✓ ModelConfig instantiated successfully")
        
        print("\\nAll basic imports successful! ✓")
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
