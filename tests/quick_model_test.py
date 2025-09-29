#!/usr/bin/env python3
"""
Quick test of both models individually
"""

import time
import sys
sys.path.append('.')

from mlx_ai_client import MLXAIClient

def test_model(model_name, test_prompt):
    """Test a single model with timing"""
    print(f"\n🧪 Testing: {model_name}")
    print("=" * 60)
    
    try:
        # Initialize client
        start_init = time.time()
        client = MLXAIClient(model_name)
        init_time = time.time() - start_init
        print(f"⚡ Initialization: {init_time:.2f}s")
        
        # Test inference
        print(f"📝 Prompt: {test_prompt[:100]}...")
        start_inference = time.time()
        
        response = client.generate_response(test_prompt, max_tokens=100)
        
        inference_time = time.time() - start_inference
        print(f"⏱️  Inference: {inference_time:.2f}s")
        print(f"📄 Response: {response[:200]}...")
        
        return {
            'model': model_name,
            'init_time': init_time,
            'inference_time': inference_time,
            'total_time': init_time + inference_time,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            'model': model_name,
            'error': str(e),
            'success': False
        }

def main():
    print("🎯 Quick Model Test")
    print("Testing both models with simple prompts")
    
    # Test prompts
    code_prompt = """
    Analyze this R code for correctness:
    
    ```r
    data <- read.csv("file.csv")
    summary(data)
    ```
    
    Is this code correct? Provide a brief analysis.
    """
    
    feedback_prompt = """
    A student wrote this R code. Provide encouraging educational feedback:
    
    ```r
    data <- read.csv("file.csv")
    summary(data)
    ```
    
    Focus on what they did well and suggestions for improvement.
    """
    
    results = []
    
    # Test Code Analyzer (Qwen)
    results.append(test_model(
        "mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16",
        code_prompt
    ))
    
    # Test Feedback Generator (Gemma)
    results.append(test_model(
        "mlx-community/gemma-3-27b-it-bf16", 
        feedback_prompt
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    for result in results:
        if result['success']:
            print(f"✅ {result['model']}")
            print(f"   Init: {result['init_time']:.1f}s | Inference: {result['inference_time']:.1f}s | Total: {result['total_time']:.1f}s")
        else:
            print(f"❌ {result['model']}: {result['error']}")
    
    # Performance assessment
    successful = [r for r in results if r['success']]
    if len(successful) == 2:
        total_time = sum(r['total_time'] for r in successful)
        print(f"\n🎯 Combined Performance: {total_time:.1f}s for both models")
        
        if total_time < 60:
            print("🚀 EXCELLENT: Very fast!")
        elif total_time < 120:
            print("✅ GOOD: Reasonable speed")
        elif total_time < 180:
            print("⚠️  ACCEPTABLE: A bit slow")
        else:
            print("🐌 SLOW: May need optimization")

if __name__ == "__main__":
    main()