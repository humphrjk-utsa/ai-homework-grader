#!/usr/bin/env python3
"""
Fresh MLX download - clean slate approach
Download MLX versions of your original Ollama models
"""

import time
import os
from pathlib import Path
from mlx_lm import load, generate

# Your original Ollama models → MLX equivalents
MODELS_TO_DOWNLOAD = [
    {
        "name": "gpt-oss:120b",
        "mlx_model": "lmstudio-community/gpt-oss-120b-MLX-8bit",
        "size": "~65GB → ~4GB (8-bit quantized)",
        "priority": 1,
        "description": "Main homework grading model - 120B parameters"
    },
    {
        "name": "gpt-oss:20b", 
        "mlx_model": "mlx-community/gpt-oss-20b-MXFP4-Q8",
        "size": "~13GB → ~2GB (quantized)",
        "priority": 2,
        "description": "Faster backup model - 20B parameters"
    },
    {
        "name": "gemma3:27b",
        "mlx_model": "mlx-community/gemma-2-27b-it-4bit",
        "size": "~17GB → ~3GB (4-bit)",
        "priority": 3,
        "description": "Google Gemma 27B model"
    },
    {
        "name": "llama4:latest",
        "mlx_model": "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit",
        "size": "~67GB → ~8GB (4-bit)",
        "priority": 4,
        "description": "Meta Llama 70B model"
    },
    {
        "name": "deepseek-r1:70b",
        "mlx_model": "mlx-community/DeepSeek-R1-Distill-Llama-70B-4bit",
        "size": "~42GB → ~5GB (4-bit)",
        "priority": 5,
        "description": "DeepSeek reasoning model"
    }
]

def get_cache_size():
    """Get current HuggingFace cache size"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    if not cache_dir.exists():
        return 0
    
    total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
    return total_size / (1024**3)  # GB

def download_and_test_model(model_info):
    """Download and test a single model"""
    print(f"\n{'='*70}")
    print(f"📥 DOWNLOADING: {model_info['name']}")
    print(f"   MLX Model: {model_info['mlx_model']}")
    print(f"   Size: {model_info['size']}")
    print(f"   Priority: {model_info['priority']}")
    print(f"   Description: {model_info['description']}")
    print(f"{'='*70}")
    
    initial_cache = get_cache_size()
    print(f"   📊 Cache size before: {initial_cache:.1f}GB")
    
    try:
        start_time = time.time()
        
        print("   🔄 Downloading from HuggingFace...")
        print("   ⏳ This may take several minutes...")
        
        # Download and load model
        model, tokenizer = load(model_info['mlx_model'])
        
        download_time = time.time() - start_time
        final_cache = get_cache_size()
        downloaded_size = final_cache - initial_cache
        
        print(f"   ✅ Downloaded in {download_time:.1f}s")
        print(f"   📊 Downloaded size: {downloaded_size:.1f}GB")
        print(f"   📊 Total cache: {final_cache:.1f}GB")
        
        # Test the model
        print("   🧪 Testing model...")
        test_start = time.time()
        
        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt="Grade this R code: x <- 5",
            max_tokens=10,
            verbose=False
        )
        
        test_time = time.time() - test_start
        print(f"   ✅ Test successful: '{response.strip()}' ({test_time:.2f}s)")
        
        return {
            "success": True,
            "model": model_info['mlx_model'],
            "download_time": download_time,
            "test_time": test_time,
            "size_gb": downloaded_size
        }
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return {
            "success": False,
            "model": model_info['mlx_model'],
            "error": str(e)
        }

def main():
    """Download all MLX models"""
    print("🚀 Fresh MLX Model Download")
    print("Starting with clean cache...")
    print("=" * 70)
    
    initial_total_cache = get_cache_size()
    print(f"📊 Starting cache size: {initial_total_cache:.1f}GB")
    
    results = []
    successful = 0
    failed = 0
    
    # Download in priority order
    for model_info in MODELS_TO_DOWNLOAD:
        result = download_and_test_model(model_info)
        results.append(result)
        
        if result['success']:
            successful += 1
        else:
            failed += 1
        
        # Show progress
        total = len(MODELS_TO_DOWNLOAD)
        completed = successful + failed
        print(f"\n   📈 Progress: {completed}/{total} models processed")
        
        # Brief pause between downloads
        if completed < total:
            print("   ⏸️  Pausing 3 seconds before next download...")
            time.sleep(3)
    
    # Final summary
    print(f"\n{'='*70}")
    print("📋 DOWNLOAD SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    final_total_cache = get_cache_size()
    total_downloaded = final_total_cache - initial_total_cache
    print(f"📊 Total downloaded: {total_downloaded:.1f}GB")
    print(f"📊 Final cache size: {final_total_cache:.1f}GB")
    
    if successful > 0:
        print(f"\n🎉 Successfully downloaded {successful} MLX models!")
        print("\n📚 Available models for homework grading:")
        
        for result in results:
            if result['success']:
                print(f"   ✅ {result['model']}")
                print(f"      Size: {result['size_gb']:.1f}GB, Test: {result['test_time']:.2f}s")
        
        # Find fastest model
        successful_results = [r for r in results if r['success']]
        if successful_results:
            fastest = min(successful_results, key=lambda x: x['test_time'])
            print(f"\n⚡ Fastest model: {fastest['model']} ({fastest['test_time']:.2f}s)")
    
    if failed > 0:
        print(f"\n⚠️  Failed downloads:")
        for result in results:
            if not result['success']:
                print(f"   ❌ {result['model']}: {result['error']}")
    
    print(f"\n💡 Next steps:")
    print(f"   • Models are ready for homework grading")
    print(f"   • Start the grader: python start.py")
    print(f"   • MLX will use Apple Silicon optimization")

if __name__ == "__main__":
    main()