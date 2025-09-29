#!/usr/bin/env python3
"""
Download PC Models for llama.cpp homework grader
Downloads GGUF versions of Gemma 2 27B and Qwen2.5-Coder
"""

import os
import subprocess
import sys
from pathlib import Path

# Model configurations
MODELS_TO_DOWNLOAD = [
    {
        "name": "Gemma 2 27B IT (BF16 GGUF)",
        "repo": "google/gemma-2-27b-it-GGUF", 
        "files": [
            "gemma-2-27b-it.gguf",  # Full precision
            "gemma-2-27b-it-Q4_K_M.gguf",  # 4-bit quantized (recommended)
            "gemma-2-27b-it-Q5_K_M.gguf",  # 5-bit quantized
        ],
        "description": "Google's Gemma 2 27B model for general feedback generation",
        "use_case": "feedback_generation"
    },
    {
        "name": "Qwen2.5-Coder 32B (GGUF)",
        "repo": "Qwen/Qwen2.5-Coder-32B-Instruct-GGUF",
        "files": [
            "qwen2.5-coder-32b-instruct-q4_k_m.gguf",  # 4-bit (recommended)
            "qwen2.5-coder-32b-instruct-q5_k_m.gguf",  # 5-bit
            "qwen2.5-coder-32b-instruct-q6_k.gguf",    # 6-bit
        ],
        "description": "Qwen2.5-Coder 32B specialized for code analysis",
        "use_case": "code_analysis"
    },
    {
        "name": "Qwen2.5-Coder 14B (GGUF) - Lighter Alternative",
        "repo": "Qwen/Qwen2.5-Coder-14B-Instruct-GGUF", 
        "files": [
            "qwen2.5-coder-14b-instruct-q4_k_m.gguf",
            "qwen2.5-coder-14b-instruct-q5_k_m.gguf",
        ],
        "description": "Smaller Qwen2.5-Coder for systems with less RAM",
        "use_case": "code_analysis_light"
    }
]

def check_huggingface_cli():
    """Check if HuggingFace CLI is installed"""
    try:
        result = subprocess.run(['huggingface-cli', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ HuggingFace CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ HuggingFace CLI not working properly")
            return False
    except FileNotFoundError:
        print("❌ HuggingFace CLI not found")
        return False
    except Exception as e:
        print(f"❌ Error checking HuggingFace CLI: {e}")
        return False

def install_huggingface_cli():
    """Install HuggingFace CLI"""
    print("📦 Installing HuggingFace CLI...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'huggingface_hub[cli]'], 
                      check=True)
        print("✅ HuggingFace CLI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install HuggingFace CLI: {e}")
        return False

def get_model_directory():
    """Get or create model directory"""
    # Try common locations
    possible_dirs = [
        Path("./models"),
        Path("../models"), 
        Path.home() / "models",
        Path.home() / "Documents" / "models"
    ]
    
    for dir_path in possible_dirs:
        if dir_path.exists():
            print(f"📁 Using existing model directory: {dir_path}")
            return str(dir_path)
    
    # Create ./models directory
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    print(f"📁 Created model directory: {models_dir.absolute()}")
    return str(models_dir)

def estimate_download_size(model_config):
    """Estimate download size for a model"""
    size_estimates = {
        "gemma-2-27b-it.gguf": "54GB",
        "gemma-2-27b-it-Q4_K_M.gguf": "15GB", 
        "gemma-2-27b-it-Q5_K_M.gguf": "18GB",
        "qwen2.5-coder-32b-instruct-q4_k_m.gguf": "18GB",
        "qwen2.5-coder-32b-instruct-q5_k_m.gguf": "22GB",
        "qwen2.5-coder-32b-instruct-q6_k.gguf": "26GB",
        "qwen2.5-coder-14b-instruct-q4_k_m.gguf": "8GB",
        "qwen2.5-coder-14b-instruct-q5_k_m.gguf": "10GB"
    }
    
    total_size = 0
    for file in model_config["files"]:
        if file in size_estimates:
            size_str = size_estimates[file]
            size_gb = float(size_str.replace("GB", ""))
            total_size += size_gb
    
    return f"{total_size:.1f}GB"

def download_model(model_config, model_dir, selected_files=None):
    """Download a specific model"""
    print(f"\n🚀 Downloading {model_config['name']}...")
    print(f"📝 Description: {model_config['description']}")
    
    files_to_download = selected_files or model_config["files"]
    
    for file in files_to_download:
        print(f"\n📥 Downloading {file}...")
        
        cmd = [
            'huggingface-cli', 'download',
            model_config["repo"],
            file,
            '--local-dir', model_dir,
            '--local-dir-use-symlinks', 'False'  # Download actual files, not symlinks
        ]
        
        try:
            # Show the command being run
            print(f"🔧 Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, check=True, text=True, 
                                  capture_output=False)  # Show progress
            
            print(f"✅ Successfully downloaded {file}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download {file}: {e}")
            return False
        except KeyboardInterrupt:
            print(f"\n⚠️ Download interrupted by user")
            return False
    
    print(f"🎉 Completed downloading {model_config['name']}")
    return True

def interactive_model_selection():
    """Interactive model selection"""
    print("\n🤖 Available Models for Download:")
    print("=" * 60)
    
    for i, model in enumerate(MODELS_TO_DOWNLOAD, 1):
        size = estimate_download_size(model)
        print(f"{i}. {model['name']}")
        print(f"   📝 {model['description']}")
        print(f"   📊 Estimated size: {size}")
        print(f"   🎯 Use case: {model['use_case']}")
        print(f"   📁 Files: {len(model['files'])} variants")
        print()
    
    print("💡 Recommendations:")
    print("   • For code analysis: Qwen2.5-Coder (option 2 or 3)")
    print("   • For feedback: Gemma 2 27B (option 1)")
    print("   • Q4_K_M quantization offers best size/quality balance")
    print()
    
    while True:
        try:
            choice = input("Select models to download (e.g., '1,2' or 'all'): ").strip()
            
            if choice.lower() == 'all':
                return list(range(len(MODELS_TO_DOWNLOAD)))
            
            if choice.lower() in ['quit', 'exit', 'q']:
                return []
            
            # Parse comma-separated choices
            choices = [int(x.strip()) - 1 for x in choice.split(',')]
            
            # Validate choices
            valid_choices = []
            for c in choices:
                if 0 <= c < len(MODELS_TO_DOWNLOAD):
                    valid_choices.append(c)
                else:
                    print(f"⚠️ Invalid choice: {c + 1}")
            
            if valid_choices:
                return valid_choices
            else:
                print("❌ No valid choices selected")
                
        except ValueError:
            print("❌ Invalid input. Use numbers separated by commas (e.g., '1,2')")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return []

def select_quantization_level(model_config):
    """Select quantization level for a model"""
    print(f"\n📊 Select quantization for {model_config['name']}:")
    
    for i, file in enumerate(model_config["files"], 1):
        # Extract quantization info
        if "Q4_K_M" in file:
            quant_info = "4-bit (recommended - good balance)"
        elif "Q5_K_M" in file:
            quant_info = "5-bit (higher quality, larger size)"
        elif "Q6_K" in file:
            quant_info = "6-bit (near full quality)"
        elif ".gguf" in file and "q" not in file.lower():
            quant_info = "Full precision (largest, best quality)"
        else:
            quant_info = "Unknown quantization"
        
        print(f"   {i}. {file} - {quant_info}")
    
    while True:
        try:
            choice = input(f"Select files (1-{len(model_config['files'])}, or 'all'): ").strip()
            
            if choice.lower() == 'all':
                return model_config["files"]
            
            # Parse selection
            choices = [int(x.strip()) - 1 for x in choice.split(',')]
            selected_files = [model_config["files"][i] for i in choices 
                            if 0 <= i < len(model_config["files"])]
            
            if selected_files:
                return selected_files
            else:
                print("❌ No valid files selected")
                
        except ValueError:
            print("❌ Invalid input")
        except KeyboardInterrupt:
            return []

def main():
    """Main download function"""
    print("🖥️ PC Model Downloader for Homework Grader")
    print("=" * 50)
    print("This script downloads GGUF models for llama.cpp")
    print()
    
    # Check HuggingFace CLI
    if not check_huggingface_cli():
        print("\n💡 Installing HuggingFace CLI...")
        if not install_huggingface_cli():
            print("❌ Cannot proceed without HuggingFace CLI")
            return False
        
        # Check again after installation
        if not check_huggingface_cli():
            print("❌ HuggingFace CLI installation failed")
            return False
    
    # Get model directory
    model_dir = get_model_directory()
    
    # Interactive selection
    selected_indices = interactive_model_selection()
    
    if not selected_indices:
        print("👋 No models selected. Exiting.")
        return True
    
    # Download selected models
    success_count = 0
    total_count = len(selected_indices)
    
    for idx in selected_indices:
        model_config = MODELS_TO_DOWNLOAD[idx]
        
        # Select quantization level
        selected_files = select_quantization_level(model_config)
        
        if not selected_files:
            print(f"⚠️ Skipping {model_config['name']} - no files selected")
            continue
        
        # Download the model
        if download_model(model_config, model_dir, selected_files):
            success_count += 1
        else:
            print(f"❌ Failed to download {model_config['name']}")
    
    # Summary
    print(f"\n🎉 Download Summary:")
    print(f"✅ Successfully downloaded: {success_count}/{total_count} models")
    print(f"📁 Models saved to: {Path(model_dir).absolute()}")
    
    if success_count > 0:
        print(f"\n💡 Next steps:")
        print(f"   1. Run: python test_pc_setup.py")
        print(f"   2. Start grader: streamlit run pc_start.py")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)