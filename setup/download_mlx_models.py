#!/usr/bin/env python3
"""
Download MLX versions of your existing Ollama models
"""

import os
from mlx_lm import load
import time

# Your original models and their MLX equivalents
MODEL_MAPPINGS = {
    "gpt-oss:120b": {
        "mlx_model": "lmstudio-community/gpt-oss-120b-MLX-8bit",
        "size": "~65GB",
        "priority": 1,  # Highest priority for homework grading
        "description": "Your main 120B model for detailed grading"
    },
    "gpt-oss:20b": {
        "mlx_model": "mlx-community/gpt-oss-20b-MXFP4-Q8", 
        "size": "~13GB",
        "priority": 2,  # Good backup/faster option
        "description": "Faster 20B model for quick grading"
    },
    "gemma3:27b": {
        "mlx_model": "lmstudio-community/gemma-3n-E4B-it-MLX-8bit",
        "size": "~17GB", 
        "priority": 3,
        "description": "Google's Gemma model"
    },
    "llama4:latest": {
        "mlx_model": "mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit",
        "size": "~17GB",
        "priority": 4,
        "description": "Meta's Llama 4 model"
    },
    "deepseek-r1:70b": {
        "mlx_model": "lmstudio-community/DeepSeek-R1-0528-Qwen3-8B-MLX-8bit",
        "size": "~8GB",
        "priority": 5,
        "description": "DeepSeek reasoning model"
    }
}

def check_model_cached(model_name):
    """Check if model is already cached locally"""
    import os
    from pathlib import Path
    
    # Check HuggingFace cache
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    model_cache = cache_dir / f"models--{model_name.replace('/', '--')}"
    
    if model_cache.exists():
        # Check size
        total_size = sum(f.stat().st_size for f in model_cache.rglob('*') if f.is_file())
        size_gb = total_size / (1024**3)
        return True, size_gb
    
    return False, 0

def download_model(model_info, original_name):
    """Download and test a single MLX model"""
    mlx_model = model_info["mlx_model"]
    
    print(f"\n{'='*60}")
    print(f"🔄 DOWNLOADING: {original_name}")
    print(f"   MLX Model: {mlx_model}")
    print(f"   Expected Size: {model_info['size']}")
    print(f"   Description: {model_info['description']}")
    print(f"{'='*60}")
    
    # Check if already cached
    is_cached, cached_size = check_model_cached(mlx_model)
    if is_cached:
        print(f"   ✅ Model already cached ({cached_size:.1f}GB)")
        print("   ⚡ Loading from cache...")
    else:
        print("   📥 Model not cached - downloading from HuggingFace...")
        print("   ⏳ This may take several minutes depending on size...")
    
    try:
        start_time = time.time()
        
        # Show progress dots while loading
        import threading
        import sys
        
        loading = True
        def show_progress():
            dots = 0
            while loading:
                sys.stdout.write(f"\r   {'.' * (dots % 4):<4} Loading")
                sys.stdout.flush()
                time.sleep(0.5)
                dots += 1
        
        progress_thread = threading.Thread(target=show_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Load model (this downloads it if not cached)
        model, tokenizer = load(mlx_model)
        
        loading = False
        progress_thread.join(timeout=0.1)
        
        download_time = time.time() - start_time
        print(f"\r   ✅ Loaded successfully in {download_time:.1f}s")
        
        # Quick test
        print("   🧪 Testing generation...")
        test_start = time.time()
        
        from mlx_lm import generate
        response = generate(
            model=model,
            tokenizer=tokenizer, 
            prompt="Test:",
            max_tokens=3,
            verbose=False
        )
        
        test_time = time.time() - test_start
        print(f"   ✅ Test response: '{response.strip()}' ({test_time:.2f}s)")
        
        # Check final cache size
        _, final_size = check_model_cached(mlx_model)
        print(f"   💾 Cached size: {final_size:.1f}GB")
        
        return True, download_time, test_time
        
    except Exception as e:
        loading = False
        print(f"\r   ❌ Failed: {e}")
        return False, 0, 0

def main():
    """Download MLX models based on priority"""
    print("🚀 MLX Model Download Manager")
    print("Converting your Ollama models to MLX format")
    print("=" * 50)
    
    # Sort by priority
    sorted_models = sorted(MODEL_MAPPINGS.items(), 
                          key=lambda x: x[1]["priority"])
    
    successful_downloads = []
    failed_downloads = []
    
    for original_name, model_info in sorted_models:
        success, download_time, test_time = download_model(model_info, original_name)
        
        if success:
            successful_downloads.append({
                "original": original_name,
                "mlx": model_info["mlx_model"],
                "download_time": download_time,
                "test_time": test_time
            })
        else:
            failed_downloads.append(original_name)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Download Summary")
    print(f"✅ Successful: {len(successful_downloads)}")
    print(f"❌ Failed: {len(failed_downloads)}")
    
    if successful_downloads:
        print("\n🎉 Successfully downloaded MLX models:")
        for model in successful_downloads:
            print(f"  • {model['original']} → {model['mlx']}")
            print(f"    Download: {model['download_time']:.1f}s, Test: {model['test_time']:.2f}s")
    
    if failed_downloads:
        print(f"\n⚠️  Failed downloads: {', '.join(failed_downloads)}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if successful_downloads:
        fastest_model = min(successful_downloads, key=lambda x: x['test_time'])
        print(f"  • Fastest model: {fastest_model['mlx']} ({fastest_model['test_time']:.2f}s)")
        
        largest_model = max(successful_downloads, 
                           key=lambda x: MODEL_MAPPINGS[x['original']]['priority'] == 1)
        if MODEL_MAPPINGS[largest_model['original']]['priority'] == 1:
            print(f"  • Best for detailed grading: {largest_model['mlx']}")
    
    print(f"  • Total models ready for homework grading: {len(successful_downloads)}")

if __name__ == "__main__":
    main()