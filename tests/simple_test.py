#!/usr/bin/env python3
"""
Simple test using models that definitely exist
"""

import time
import sys
sys.path.append('.')

def test_existing_models():
    """Test with models we know are fully downloaded"""
    
    print("🔍 Testing with existing models only...")
    
    # Use the GPT-OSS model we know works
    try:
        from mlx_ai_client import MLXAIClient
        
        print("🧪 Testing GPT-OSS-120B (known working model)")
        start = time.time()
        
        client = MLXAIClient("lmstudio-community/gpt-oss-120b-MLX-8bit")
        
        # Simple test prompt
        response = client.generate_response("What is 2+2?", max_tokens=50)
        
        total_time = time.time() - start
        
        print(f"✅ Success! Time: {total_time:.1f}s")
        print(f"📄 Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_model_files():
    """Check what model files actually exist"""
    import os
    import glob
    
    hf_cache = os.path.expanduser('~/.cache/huggingface/hub/')
    
    print("\n🔍 Checking model file completeness...")
    
    # Check Qwen model
    qwen_dir = os.path.join(hf_cache, "models--mlx-community--Qwen3-Coder-30B-A3B-Instruct-bf16")
    if os.path.exists(qwen_dir):
        files = glob.glob(os.path.join(qwen_dir, "**", "*.safetensors"), recursive=True)
        print(f"📁 Qwen model: {len(files)} safetensor files found")
        
        # Check if complete
        if len(files) >= 10:  # Should have multiple files for 30B model
            print("✅ Qwen model appears complete")
        else:
            print("⚠️  Qwen model may be incomplete")
    else:
        print("❌ Qwen model directory not found")
    
    # Check Gemma model  
    gemma_dir = os.path.join(hf_cache, "models--mlx-community--gemma-3-27b-it-bf16")
    if os.path.exists(gemma_dir):
        files = glob.glob(os.path.join(gemma_dir, "**", "*.safetensors"), recursive=True)
        print(f"📁 Gemma model: {len(files)} safetensor files found")
        
        if len(files) >= 5:  # Should have multiple files for 27B model
            print("✅ Gemma model appears complete")
        else:
            print("⚠️  Gemma model may be incomplete")
    else:
        print("❌ Gemma model directory not found")

if __name__ == "__main__":
    print("🎯 Simple Model Test (No Downloads)")
    print("=" * 50)
    
    # First check what we have
    check_model_files()
    
    # Then test a known working model
    test_existing_models()