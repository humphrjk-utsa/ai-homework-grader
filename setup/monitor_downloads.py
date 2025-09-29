#!/usr/bin/env python3
"""
Monitor what's downloading in real-time
"""

import time
import os
from pathlib import Path

def get_cache_info():
    """Get current cache information"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    if not cache_dir.exists():
        return [], 0
    
    models = []
    total_size = 0
    
    for model_dir in cache_dir.iterdir():
        if model_dir.is_dir() and model_dir.name.startswith('models--'):
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            
            # Get size
            size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
            size_gb = size / (1024**3)
            total_size += size_gb
            
            # Check if actively downloading (recent file changes)
            recent_files = []
            try:
                for f in model_dir.rglob('*'):
                    if f.is_file():
                        age = time.time() - f.stat().st_mtime
                        if age < 60:  # Modified in last minute
                            recent_files.append(f.name)
            except:
                pass
            
            models.append({
                'name': model_name,
                'size_gb': size_gb,
                'downloading': len(recent_files) > 0,
                'recent_files': recent_files[:3]  # Show first 3
            })
    
    return models, total_size

def main():
    """Monitor downloads in real-time"""
    print("📊 MLX Download Monitor")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)
    
    last_total = 0
    
    try:
        while True:
            models, total_size = get_cache_info()
            
            # Clear screen (simple version)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("📊 MLX Download Monitor")
            print(f"🕐 {time.strftime('%H:%M:%S')}")
            print("=" * 60)
            
            if not models:
                print("📭 No models in cache yet")
            else:
                print(f"📚 Total models: {len(models)}")
                print(f"💾 Total cache size: {total_size:.1f}GB")
                
                if total_size > last_total:
                    growth = total_size - last_total
                    print(f"📈 Growing: +{growth:.2f}GB since last check")
                
                print("\n🔍 Model Details:")
                print("-" * 60)
                
                for model in sorted(models, key=lambda x: x['size_gb'], reverse=True):
                    status = "🔄 DOWNLOADING" if model['downloading'] else "✅ Complete"
                    print(f"{status} {model['name']}")
                    print(f"         Size: {model['size_gb']:.1f}GB")
                    
                    if model['downloading'] and model['recent_files']:
                        print(f"         Recent: {', '.join(model['recent_files'])}")
                    print()
            
            last_total = total_size
            
            print("Press Ctrl+C to stop monitoring...")
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print(f"\n👋 Monitoring stopped")
        
        # Final summary
        models, total_size = get_cache_info()
        if models:
            print(f"\n📋 Final Status:")
            print(f"   Models: {len(models)}")
            print(f"   Total size: {total_size:.1f}GB")
            
            downloading = [m for m in models if m['downloading']]
            if downloading:
                print(f"   Still downloading: {len(downloading)}")
                for m in downloading:
                    print(f"     • {m['name']}")
            else:
                print("   ✅ All downloads appear complete")

if __name__ == "__main__":
    main()