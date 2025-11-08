#!/usr/bin/env python3
"""
Download FP4 models for disaggregated inference
Downloads to Mac Studio 1, then distribute to other machines
"""

from huggingface_hub import snapshot_download
import os
from pathlib import Path

# Base directory for models
MODELS_DIR = Path.home() / "models" / "fp4"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("FP4 MODEL DOWNLOAD FOR DISAGGREGATED INFERENCE")
print("="*80)
print(f"Download location: {MODELS_DIR}")
print()

# Models to download
models = [
    {
        "name": "Qwen 3 Coder 30B FP4 (NVIDIA)",
        "repo": "NVFP4/Qwen3-Coder-30B-A3B-Instruct-FP4",
        "local_dir": MODELS_DIR / "qwen3-coder-30b-fp4",
        "size": "~15GB",
        "use": "Code analysis - prefill on DGX, decode on Mac"
    },
    {
        "name": "GPT-OSS 120B FP4 (NVIDIA)",
        "repo": "shanjiaz/gpt-oss-120b-nvfp4-modelopt",
        "local_dir": MODELS_DIR / "gpt-oss-120b-fp4",
        "size": "~60GB",
        "use": "Feedback generation - prefill on DGX, decode on Mac"
    }
]

def download_model(model_info):
    """Download a model from HuggingFace"""
    print(f"\n{'='*80}")
    print(f"📥 Downloading: {model_info['name']}")
    print(f"{'='*80}")
    print(f"Repository: {model_info['repo']}")
    print(f"Size: {model_info['size']}")
    print(f"Use: {model_info['use']}")
    print(f"Local path: {model_info['local_dir']}")
    print()
    
    if model_info['local_dir'].exists():
        print(f"⚠️  Model already exists at {model_info['local_dir']}")
        response = input("Download anyway? (y/n): ")
        if response.lower() != 'y':
            print("⏭️  Skipping...")
            return
    
    try:
        print("🚀 Starting download...")
        snapshot_download(
            repo_id=model_info['repo'],
            local_dir=str(model_info['local_dir']),
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print(f"✅ Downloaded successfully to {model_info['local_dir']}")
    except Exception as e:
        print(f"❌ Error downloading {model_info['name']}: {e}")
        return False
    
    return True

def main():
    print("\n🎯 This script will download FP4 models for disaggregated inference")
    print("📍 Location: Mac Studio 1")
    print("📤 After download, distribute to:")
    print("   - Mac Studio 2 (via Thunderbolt)")
    print("   - DGX Spark 1 (via 10GbE)")
    print("   - DGX Spark 2 (via 10GbE)")
    print()
    
    response = input("Continue with download? (y/n): ")
    if response.lower() != 'y':
        print("❌ Download cancelled")
        return
    
    # Download each model
    success_count = 0
    for model in models:
        if download_model(model):
            success_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("DOWNLOAD SUMMARY")
    print("="*80)
    print(f"✅ Successfully downloaded: {success_count}/{len(models)} models")
    print(f"📁 Models location: {MODELS_DIR}")
    print()
    print("📤 Next steps:")
    print("1. Distribute models to other machines:")
    print(f"   rsync -avz --progress {MODELS_DIR}/ mac2:/path/to/models/")
    print(f"   rsync -avz --progress {MODELS_DIR}/ dgx1:/path/to/models/")
    print(f"   rsync -avz --progress {MODELS_DIR}/ dgx2:/path/to/models/")
    print()
    print("2. Set up disaggregated inference servers")
    print("3. Configure prefill (DGX) and decode (Mac) endpoints")
    print("="*80)

if __name__ == "__main__":
    main()
