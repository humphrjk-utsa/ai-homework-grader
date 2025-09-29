#!/usr/bin/env python3
"""
Check what MLX models are available for homework grading
"""

from pathlib import Path
import time

def check_models():
    """Check what models are ready"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    if not cache_dir.exists():
        print("📭 No models cached yet")
        return []
    
    models = []
    total_size = 0
    
    for model_dir in cache_dir.iterdir():
        if model_dir.is_dir() and model_dir.name.startswith('models--'):
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            
            # Get size
            size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
            size_gb = size / (1024**3)
            total_size += size_gb
            
            models.append({
                'name': model_name,
                'size_gb': size_gb
            })
    
    return models, total_size

def main():
    """Show available models"""
    print("📚 Available MLX Models for Homework Grading")
    print("=" * 60)
    
    models, total_size = check_models()
    
    if not models:
        print("📭 No models found")
        print("💡 Models may still be downloading...")
        return
    
    print(f"📊 Total: {len(models)} models, {total_size:.1f}GB")
    print()
    
    # Sort by size (largest first)
    models.sort(key=lambda x: x['size_gb'], reverse=True)
    
    for i, model in enumerate(models, 1):
        print(f"{i:2d}. {model['name']}")
        print(f"    Size: {model['size_gb']:.1f}GB")
        
        # Identify model type
        name_lower = model['name'].lower()
        if 'gpt-oss' in name_lower:
            if '120b' in name_lower:
                print("    🎯 Perfect for detailed homework grading")
            elif '20b' in name_lower:
                print("    ⚡ Good for faster grading")
        elif 'gemma' in name_lower:
            print("    🔬 Google's Gemma model")
        elif 'llama' in name_lower:
            print("    🦙 Meta's Llama model")
        elif 'qwen' in name_lower:
            print("    🚀 Alibaba's Qwen model")
        
        print()
    
    print("💡 Once downloads complete, you can:")
    print("   • Start homework grader: python start.py")
    print("   • Test a model: python -c \"from mlx_lm import load; load('MODEL_NAME')\"")

if __name__ == "__main__":
    main()