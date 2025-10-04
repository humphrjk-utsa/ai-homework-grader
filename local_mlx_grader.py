#!/usr/bin/env python3
"""
Local MLX grader running both models on Mac Studio 1
More reliable than distributed setup
"""

import time
import os
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

class LocalMLXGrader:
    """Run both MLX models locally on Mac Studio 1"""
    
    def __init__(self):
        self.qwen_model = None
        self.qwen_tokenizer = None
        self.gemma_model = None
        self.gemma_tokenizer = None
        self.models_loaded = False
        
    def load_models(self):
        """Load both models locally"""
        if self.models_loaded:
            return True
            
        try:
            from mlx_lm import load
            
            print("🔄 Loading Qwen 3.0 Coder locally...")
            self.qwen_model, self.qwen_tokenizer = load('mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16')
            print("✅ Qwen loaded!")
            
            print("🔄 Loading Gemma 3.0 locally...")
            self.gemma_model, self.gemma_tokenizer = load('mlx-community/gemma-3-27b-it-bf16')
            print("✅ Gemma loaded!")
            
            self.models_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return False
    
    def generate_qwen(self, prompt: str, max_tokens: int = 800) -> Optional[str]:
        """Generate with Qwen locally"""
        if not self.models_loaded:
            return None
            
        try:
            from mlx_lm import generate
            
            print(f"🔄 Qwen generating ({max_tokens} tokens)...")
            start_time = time.time()
            
            response_generator = generate(
                model=self.qwen_model,
                tokenizer=self.qwen_tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False
            )
            
            response = ''.join(response_generator)
            duration = time.time() - start_time
            
            print(f"✅ Qwen done in {duration:.1f}s")
            return response
            
        except Exception as e:
            print(f"❌ Qwen generation failed: {e}")
            return None
    
    def generate_gemma(self, prompt: str, max_tokens: int = 1200) -> Optional[str]:
        """Generate with Gemma locally"""
        if not self.models_loaded:
            return None
            
        try:
            from mlx_lm import generate
            
            print(f"🔄 Gemma generating ({max_tokens} tokens)...")
            start_time = time.time()
            
            response_generator = generate(
                model=self.gemma_model,
                tokenizer=self.gemma_tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False
            )
            
            response = ''.join(response_generator)
            duration = time.time() - start_time
            
            print(f"✅ Gemma done in {duration:.1f}s")
            return response
            
        except Exception as e:
            print(f"❌ Gemma generation failed: {e}")
            return None
    
    def generate_parallel(self, code_prompt: str, feedback_prompt: str) -> Dict[str, Any]:
        """Generate both responses in parallel locally"""
        
        if not self.models_loaded:
            if not self.load_models():
                return {'error': 'Models not loaded'}
        
        print("⚡ Starting parallel local generation...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            qwen_future = executor.submit(self.generate_qwen, code_prompt, 800)
            gemma_future = executor.submit(self.generate_gemma, feedback_prompt, 1200)
            
            qwen_result = qwen_future.result(timeout=120)
            gemma_result = gemma_future.result(timeout=180)
        
        total_time = time.time() - start_time
        
        return {
            'code_analysis': qwen_result,
            'feedback': gemma_result,
            'parallel_time': total_time,
            'success': qwen_result is not None and gemma_result is not None
        }

# Test the local grader
if __name__ == "__main__":
    print("🧪 Testing Local MLX Grader")
    print("=" * 30)
    
    grader = LocalMLXGrader()
    
    if grader.load_models():
        result = grader.generate_parallel(
            "def analyze_data(): # Complete this R function",
            "Provide feedback on student's R code approach"
        )
        
        if result['success']:
            print(f"\n✅ Success! Total time: {result['parallel_time']:.1f}s")
            print(f"Code: {result['code_analysis'][:100]}...")
            print(f"Feedback: {result['feedback'][:100]}...")
        else:
            print("❌ Generation failed")
    else:
        print("❌ Model loading failed")