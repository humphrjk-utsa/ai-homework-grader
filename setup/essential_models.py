#!/usr/bin/env python3
"""
Download only essential models for homework grading
Avoiding DeepSeek and focusing on core models
"""

import time
import sys
from pathlib import Path

# Essential models only - no DeepSeek
ESSENTIAL_MODELS = [
    {
        "name": "gpt-oss-120b (Main grading model)",
        "mlx_model": "lmstudio-community/gpt-oss-120b-MLX-8bit",
        "size": "~4GB",
        "essential": True
    },
    {
        "name": "gpt-oss-20b (Backup/faster model)", 
        "mlx_model": "mlx-community/gpt-oss-20b-MXFP4-Q8",
        "size": "~2GB",
        "essential": True
    },
    {
        "name": "Llama-3.1-8B (Alternative)",
        "mlx_model": "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
        "size": "~5GB",
        "essential": False
    }
]

def check_network():
    """Quick network check"""
    print("🌐 Checking network connection...")
    try:
        import requests
        response = requests.get("https://huggingface.co", timeout=10)
        if response.status_code == 200:
            print("✅ Network connection OK")
            return True
        else:
            print(f"⚠️ Network issue: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def download_one_model(model_info):
    """Download a single model with clear feedback"""
    print(f"\n{'='*60}")
    print(f"📥 DOWNLOADING: {model_info['name']}")
    print(f"   Model: {model_info['mlx_model']}")
    print(f"   Size: {model_info['size']}")
    print(f"{'='*60}")
    
    # Check if already exists
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    model_cache = cache_dir / f"models--{model_info['mlx_model'].replace('/', '--')}"
    
    if model_cache.exists():
        print("✅ Model already cached - loading from disk...")
    else:
        print("📡 Downloading from HuggingFace...")
        print("   (This may take several minutes - please wait)")
    
    try:
        from mlx_lm import load
        
        start_time = time.time()
        
        # Show we're working
        print("   🔄 Loading...", end="", flush=True)
        
        model, tokenizer = load(model_info['mlx_model'])
        
        load_time = time.time() - start_time
        print(f"\r   ✅ Loaded successfully in {load_time:.1f}s")
        
        # Quick test
        print("   🧪 Testing model...", end="", flush=True)
        
        from mlx_lm import generate
        test_start = time.time()
        
        response = generate(
            model=model, 
            tokenizer=tokenizer,
            prompt="Test",
            max_tokens=2,
            verbose=False
        )
        
        test_time = time.time() - test_start
        print(f"\r   ✅ Test passed: '{response.strip()}' ({test_time:.2f}s)")
        
        return True, load_time, test_time
        
    except Exception as e:
        print(f"\r   ❌ FAILED: {e}")
        
        # Check for common issues
        if "rate limit" in str(e).lower():
            print("   💡 Rate limited - try again in a few minutes")
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            print("   💡 Network issue - check internet connection")
        elif "not found" in str(e).lower():
            print("   💡 Model not found - may have been moved/renamed")
        
        return False, 0, 0

def main():
    """Download essential models only"""
    print("🚀 Essential MLX Models for Homework Grading")
    print("(Skipping DeepSeek as requested)")
    print("=" * 60)
    
    # Network check first
    if not check_network():
        print("❌ Network issues detected. Please check connection and try again.")
        return
    
    successful = []
    failed = []
    
    for i, model_info in enumerate(ESSENTIAL_MODELS, 1):
        print(f"\n[{i}/{len(ESSENTIAL_MODELS)}] Starting download...")
        
        success, load_time, test_time = download_one_model(model_info)
        
        if success:
            successful.append({
                "name": model_info['name'],
                "model": model_info['mlx_model'],
                "load_time": load_time,
                "test_time": test_time
            })
            print(f"   ✅ SUCCESS - Ready for homework grading!")
        else:
            failed.append(model_info['name'])
            
            # Ask if user wants to continue
            if i < len(ESSENTIAL_MODELS):
                print(f"\n   Continue to next model? (y/n): ", end="")
                try:
                    response = input().strip().lower()
                    if response != 'y':
                        print("   Stopping downloads.")
                        break
                except KeyboardInterrupt:
                    print("\n   Download cancelled by user.")
                    break
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 DOWNLOAD SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        print(f"\n🎉 Ready for homework grading with {len(successful)} models:")
        for model in successful:
            print(f"   ✅ {model['name']}")
            print(f"      Load: {model['load_time']:.1f}s, Test: {model['test_time']:.2f}s")
        
        # Recommend fastest
        fastest = min(successful, key=lambda x: x['test_time'])
        print(f"\n⚡ Fastest model: {fastest['name']} ({fastest['test_time']:.2f}s)")
        
        print(f"\n💡 Next steps:")
        print(f"   • Start homework grader: python start.py")
        print(f"   • Models will use Apple Silicon optimization")
    
    if failed:
        print(f"\n⚠️ Failed models: {', '.join(failed)}")
        print(f"   • Try again later if rate limited")
        print(f"   • Check network connection")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n👋 Download cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"💡 Try running: python simple_test.py first")