#!/usr/bin/env python3
"""
Download just Gemma3 27B and Qwen 3.0 MLX models
"""

import time
from mlx_lm import load, generate

# Just the two models you want
MODELS = [
    {
        "name": "Gemma3 27B",
        "mlx_model": "mlx-community/gemma-2-27b-it-4bit",
        "size": "~15GB"
    },
    {
        "name": "Qwen 3.0", 
        "mlx_model": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "size": "~4GB"
    }
]

def download_model(model_info):
    """Download and test one model"""
    print(f"\n📥 Downloading {model_info['name']}")
    print(f"   Model: {model_info['mlx_model']}")
    print(f"   Size: {model_info['size']}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        
        print("🔄 Loading model...")
        model, tokenizer = load(model_info['mlx_model'])
        
        load_time = time.time() - start_time
        print(f"✅ Loaded in {load_time:.1f}s")
        
        # Quick test
        print("🧪 Testing...")
        test_start = time.time()
        
        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt="Hello",
            max_tokens=5,
            verbose=False
        )
        
        test_time = time.time() - test_start
        print(f"✅ Test: '{response.strip()}' ({test_time:.2f}s)")
        
        return True, load_time, test_time
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False, 0, 0

def main():
    """Download the two models"""
    print("🚀 Downloading Gemma3 27B and Qwen 3.0")
    print("=" * 50)
    
    results = []
    
    for i, model in enumerate(MODELS, 1):
        print(f"\n[{i}/{len(MODELS)}] Starting...")
        
        success, load_time, test_time = download_model(model)
        
        results.append({
            "name": model['name'],
            "success": success,
            "load_time": load_time,
            "test_time": test_time
        })
        
        if success:
            print(f"🎉 {model['name']} ready!")
        else:
            print(f"⚠️ {model['name']} failed")
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 Summary")
    successful = [r for r in results if r['success']]
    print(f"✅ Downloaded: {len(successful)}/{len(MODELS)}")
    
    for result in successful:
        print(f"   • {result['name']} ({result['test_time']:.2f}s)")

if __name__ == "__main__":
    main()