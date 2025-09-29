#!/usr/bin/env python3
"""
Simple test to see MLX download progress
"""

import time
import os
from pathlib import Path

def monitor_cache_size():
    """Monitor HuggingFace cache size during download"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    print(f"📁 Monitoring cache directory: {cache_dir}")
    
    if not cache_dir.exists():
        print("   Cache directory doesn't exist yet...")
        return
    
    # Get initial size
    initial_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
    initial_gb = initial_size / (1024**3)
    
    print(f"   Initial cache size: {initial_gb:.2f}GB")
    
    # Monitor for changes
    for i in range(30):  # Monitor for 30 seconds
        current_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
        current_gb = current_size / (1024**3)
        
        if current_gb > initial_gb:
            diff = current_gb - initial_gb
            print(f"   📈 Cache growing: +{diff:.2f}GB (total: {current_gb:.2f}GB)")
        
        time.sleep(1)

def test_small_model():
    """Test with a small model first"""
    print("🧪 Testing with small model first...")
    
    try:
        from mlx_lm import load
        
        # Use a very small model for testing
        small_model = "mlx-community/Llama-3.2-1B-Instruct-4bit"
        
        print(f"📥 Loading: {small_model}")
        print("   This should be ~1GB and download quickly...")
        
        start_time = time.time()
        model, tokenizer = load(small_model)
        load_time = time.time() - start_time
        
        print(f"✅ Loaded in {load_time:.1f}s")
        
        # Test generation
        from mlx_lm import generate
        response = generate(model, tokenizer, "Hello", max_tokens=5, verbose=False)
        print(f"🧪 Test response: '{response}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run download test"""
    print("🔍 MLX Download Test")
    print("=" * 40)
    
    # Test with small model first
    if test_small_model():
        print("\n✅ Small model test successful!")
        print("💡 MLX is working - ready for larger models")
        
        # Show cache info
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        if cache_dir.exists():
            total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            total_gb = total_size / (1024**3)
            print(f"📊 Current cache size: {total_gb:.2f}GB")
            
            # List cached models
            model_dirs = [d for d in cache_dir.iterdir() if d.is_dir() and d.name.startswith('models--')]
            print(f"📚 Cached models: {len(model_dirs)}")
            for model_dir in model_dirs[:5]:  # Show first 5
                model_name = model_dir.name.replace('models--', '').replace('--', '/')
                print(f"   • {model_name}")
    else:
        print("\n❌ Small model test failed")
        print("💡 Check MLX installation: pip install mlx-lm")

if __name__ == "__main__":
    main()