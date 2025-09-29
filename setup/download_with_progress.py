#!/usr/bin/env python3
"""
MLX download with real-time progress monitoring
"""

import time
import threading
import sys
from pathlib import Path
from mlx_lm import load

def monitor_download_progress(model_name, stop_event):
    """Monitor cache directory for download progress"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    model_cache_name = f"models--{model_name.replace('/', '--')}"
    
    print(f"   📁 Monitoring: {model_cache_name}")
    
    start_time = time.time()
    last_size = 0
    
    while not stop_event.is_set():
        try:
            model_dir = cache_dir / model_cache_name
            if model_dir.exists():
                current_size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
                current_gb = current_size / (1024**3)
                
                if current_gb > last_size:
                    elapsed = time.time() - start_time
                    speed = (current_gb - last_size) / 1 if elapsed > 0 else 0  # GB per second
                    
                    print(f"\r   📈 Downloaded: {current_gb:.2f}GB ({speed:.1f}MB/s) - {elapsed:.0f}s", end="", flush=True)
                    last_size = current_gb
            else:
                elapsed = time.time() - start_time
                print(f"\r   ⏳ Connecting... {elapsed:.0f}s", end="", flush=True)
        
        except Exception:
            pass
        
        time.sleep(1)

def download_single_model(model_name):
    """Download a single model with progress monitoring"""
    print(f"\n🔄 Starting download: {model_name}")
    
    # Start progress monitor
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=monitor_download_progress, 
        args=(model_name, stop_event)
    )
    monitor_thread.daemon = True
    monitor_thread.start()
    
    try:
        start_time = time.time()
        
        # Download model
        model, tokenizer = load(model_name)
        
        # Stop monitoring
        stop_event.set()
        monitor_thread.join(timeout=1)
        
        download_time = time.time() - start_time
        print(f"\n   ✅ Download complete in {download_time:.1f}s")
        
        # Quick test
        print("   🧪 Testing...")
        from mlx_lm import generate
        
        test_start = time.time()
        response = generate(model, tokenizer, "Hello", max_tokens=3, verbose=False)
        test_time = time.time() - test_start
        
        print(f"   ✅ Test: '{response.strip()}' ({test_time:.2f}s)")
        
        return True, download_time, test_time
        
    except Exception as e:
        stop_event.set()
        print(f"\n   ❌ Failed: {e}")
        return False, 0, 0

def main():
    """Download models one by one with progress"""
    
    # Start with a small model to test
    models = [
        "mlx-community/Llama-3.2-1B-Instruct-4bit",  # Small test model
        "lmstudio-community/gpt-oss-120b-MLX-8bit",   # Your main model
        "mlx-community/gpt-oss-20b-MXFP4-Q8",         # Backup model
    ]
    
    print("🚀 MLX Model Download with Progress")
    print("=" * 50)
    
    for i, model in enumerate(models, 1):
        print(f"\n[{i}/{len(models)}] {model}")
        
        success, download_time, test_time = download_single_model(model)
        
        if success:
            print(f"   ✅ Ready for use!")
        else:
            print(f"   ❌ Skipping to next model...")
            continue
        
        # Ask if user wants to continue
        if i < len(models):
            print(f"\n   Continue to next model? (y/n): ", end="")
            response = input().strip().lower()
            if response != 'y':
                print("   Stopping downloads.")
                break
    
    print(f"\n🎉 Download session complete!")
    
    # Show what's available
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    if cache_dir.exists():
        model_dirs = [d for d in cache_dir.iterdir() if d.is_dir() and 'mlx' in d.name.lower()]
        print(f"\n📚 Available MLX models: {len(model_dirs)}")
        
        for model_dir in model_dirs:
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
            size_gb = size / (1024**3)
            print(f"   • {model_name} ({size_gb:.1f}GB)")

if __name__ == "__main__":
    main()