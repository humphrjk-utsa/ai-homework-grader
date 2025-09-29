#!/usr/bin/env python3
"""
Simple MLX client with NO fallbacks - uses only specified models
"""

import time
from typing import Optional

class SimpleMLXClient:
    """Simple MLX client that uses ONLY the specified model, no fallbacks"""
    
    def __init__(self, model_name: str):
        """Initialize with specific model - no fallbacks allowed"""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.model_loaded_in_memory = False
        
        print(f"🎯 Simple MLX Client: {model_name}")
        print("⚠️  NO FALLBACKS - will use this model or fail")
    
    def _load_model(self):
        """Load the specified model - no fallbacks"""
        if self.model_loaded_in_memory:
            return True
            
        try:
            from mlx_lm import load
            print(f"📥 Loading {self.model_name}...")
            
            # Load the model - let it download if needed
            self.model, self.tokenizer = load(self.model_name)
            self.model_loaded_in_memory = True
            
            print(f"✅ {self.model_name} loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load {self.model_name}: {e}")
            print("🚫 NO FALLBACKS - stopping here")
            raise e
    
    def generate_response(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Generate response using the specified model only"""
        
        # Load model if not loaded
        if not self.model_loaded_in_memory:
            self._load_model()
        
        try:
            from mlx_lm import generate
            
            # Generate response
            response = generate(
                self.model, 
                self.tokenizer, 
                prompt=prompt, 
                max_tokens=max_tokens,
                verbose=False
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Generation failed with {self.model_name}: {e}")
            raise e
    
    def is_available(self) -> bool:
        """Check if the model can be loaded"""
        try:
            self._load_model()
            return True
        except:
            return False