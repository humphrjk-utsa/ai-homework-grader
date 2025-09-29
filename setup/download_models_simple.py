#!/usr/bin/env python3
"""
Simple Model Downloader using Python
Downloads Qwen 3.0 and Gemma 3 models directly
"""

import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

# Model configurations
MODELS = {
    "qwen3_coder_32b": {
        "name": "Qwen 3.0 Coder 32B (Q8_0)",
        "repo": "bartowski/Qwen2.5-Coder-32B-Instruct-GGUF",
        "filename": "Qwen2.5-Coder-32B-Instruct-Q8_0.gguf",
        "size": "~32GB",
        "use_case": "Code analysis specialist"
    },
    
    "gemma3_27b": {
        "name": "Gemma 2 27B IT (Q8_0)",
        "repo": "bartowski/gemma-2-27b-it-GGUF", 
        "filename": "gemma-2-27b-it-Q8_0.gguf",
        "size": "~27GB",
        "use_case": "Feedback generation specialist"
    },
    
    "qwen3_14b": {
        "name": "Qwen 2.5 14B Instruct (Q8_0)",
        "repo": "bartowski/Qwen2.5-14B-Instruct-GGUF",
        "filename": "Qwen2.5-14B-Instruct-Q8_0.gguf", 
        "size": "~14GB",
        "use_case": "Balanced general model"
    },
    
    "qwen3_coder_14b": {
        "name": "Qwen 2.5 Coder 14B (Q8_0)",
        "repo": "bartowski/Qwen2.5-Coder-14B-Instruct-GGUF",
        "filename": "Qwen2.5-Coder-14B-Instruct-Q8_0.gguf",
        "size": "~14GB", 
        "use_case": "Balanced code analysis"
    },
    
    "llama31_70b": {
        "name": "Llama 3.1 70B Instruct (Q8_0)",
        "repo": "bartowski/Meta-Llama-3.1-70B-Instruct-GGUF",
        "filename": "Meta-Llama-3.1-70B-Instruct-Q8_0.gguf",
        "size": "~70GB",
        "use_case": "Premium feedback generation"
    },
    
    "llama31_8b": {
        "name": "Llama 3.1 8B Instruct (Q8_0)",
        "repo": "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
        "filename": "Meta-Llama-3.1-8B-Instruct-Q8_0.gguf",
        "size": "~8GB",
        "use_case": "Fast general model"
    }
}

def download_model(key, config):
    """Download a single model"""
    print(f"\n🚀 Downloading {config['name']} ({config['size']})...")
    print(f"🎯 Use case: {config['use_case']}")
    
    try:
        # Create models directory
        models_dir = Path("./models")
        models_dir.mkdir(exist_ok=True)
        
        # Download the model
        print(f"📥 Downloading from {config['repo']}...")
        
        downloaded_path = hf_hub_download(
            repo_id=config['repo'],
            filename=config['filename'],
            local_dir=models_dir,
            local_dir_use_symlinks=False
        )
        
        # Check file size
        if Path(downloaded_path).exists():
            file_size = Path(downloaded_path).stat().st_size / (1024**3)  # GB
            print(f"✅ Successfully downloaded {config['name']}")
            print(f"📁 File: {Path(downloaded_path).name} ({file_size:.1f}GB)")
            return True
        else:
            print(f"❌ Download failed - file not found")
            return False
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def interactive_download():
    """Interactive download process"""
    print("\n🤖 Available Models (Q8_0 High Quality):")
    print("=" * 60)
    
    for i, (key, config) in enumerate(MODELS.items(), 1):
        print(f"{i}. {config['name']} ({config['size']})")
        print(f"   🎯 {config['use_case']}")
        print()
    
    print(f"{len(MODELS) + 1}. Download OPTIMAL PAIR (Qwen2.5 Coder 32B + Llama 3.1 70B) - ~102GB")
    print(f"{len(MODELS) + 2}. Download BALANCED PAIR (Qwen2.5 Coder 14B + Gemma 2 27B) - ~41GB")
    print(f"{len(MODELS) + 3}. Download FAST PAIR (Qwen2.5 14B + Llama 3.1 8B) - ~22GB")
    print("0. Exit")
    
    while True:
        try:
            choice = input(f"\nSelect option (0-{len(MODELS) + 3}): ").strip()
            
            if choice == "0":
                return
            
            elif choice == str(len(MODELS) + 1):
                # Download optimal pair
                print("\n🎯 Downloading OPTIMAL pair for maximum quality...")
                success1 = download_model("qwen3_coder_32b", MODELS["qwen3_coder_32b"])
                success2 = download_model("llama31_70b", MODELS["llama31_70b"])
                
                if success1 and success2:
                    print("\n🎉 Successfully downloaded OPTIMAL pair!")
                    print("💡 Qwen2.5 Coder 32B for code analysis")
                    print("💡 Llama 3.1 70B for feedback generation")
                    print("💡 Perfect for RTX Pro 6000 with 97GB VRAM")
                return
            
            elif choice == str(len(MODELS) + 2):
                # Download balanced pair
                print("\n⚖️ Downloading BALANCED pair...")
                success1 = download_model("qwen3_coder_14b", MODELS["qwen3_coder_14b"])
                success2 = download_model("gemma3_27b", MODELS["gemma3_27b"])
                
                if success1 and success2:
                    print("\n🎉 Successfully downloaded BALANCED pair!")
                    print("💡 Good balance of quality and speed")
                return
            
            elif choice == str(len(MODELS) + 3):
                # Download fast pair
                print("\n⚡ Downloading FAST pair...")
                success1 = download_model("qwen3_14b", MODELS["qwen3_14b"])
                success2 = download_model("llama31_8b", MODELS["llama31_8b"])
                
                if success1 and success2:
                    print("\n🎉 Successfully downloaded FAST pair!")
                    print("💡 Great for testing and development")
                return
            
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(MODELS):
                    key = list(MODELS.keys())[choice_idx]
                    config = MODELS[key]
                    
                    if download_model(key, config):
                        print(f"\n🎉 Download complete!")
                    return
                else:
                    print("❌ Invalid choice")
        
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return

def main():
    """Main function"""
    print("🚀 Simple Model Downloader")
    print("=" * 40)
    print("Downloads Q8_0 models for homework grading\n")
    
    print("💡 Recommended for RTX Pro 6000 (97GB VRAM):")
    print("   • OPTIMAL: Qwen2.5 Coder 32B + Llama 3.1 70B (~102GB total)")
    print("   • BALANCED: Qwen2.5 Coder 14B + Gemma 2 27B (~41GB total)")
    print("   • Uses Q8_0 quantization for excellent quality")
    
    interactive_download()
    
    print("\n💡 After download, run: python test_pc_setup.py")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")