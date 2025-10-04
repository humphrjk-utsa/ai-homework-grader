#!/usr/bin/env python3
"""
Quick Download Commands for PC Models
Direct HuggingFace CLI commands for Gemma 2 27B and Qwen2.5-Coder
"""

import subprocess
import sys
import os
from pathlib import Path

# Direct download commands - Q8_0 (8-BIT) HIGH QUALITY VERSIONS
DOWNLOAD_COMMANDS = {
    "gemma_2_27b_q8": {
        "name": "Gemma 2 27B IT (Q8_0 - HIGH QUALITY)",
        "size": "~27GB",
        "command": [
            "python", "-m", "huggingface_hub.commands.huggingface_cli", "download",
            "bartowski/gemma-2-27b-it-GGUF",
            "gemma-2-27b-it-Q8_0.gguf",
            "--local-dir", "./models"
        ]
    },
    
    "qwen_coder_32b_q8": {
        "name": "Qwen2.5-Coder 32B (Q8_0 - HIGH QUALITY)", 
        "size": "~32GB",
        "command": [
            "python", "-m", "huggingface_hub.commands.huggingface_cli", "download",
            "bartowski/Qwen2.5-Coder-32B-Instruct-GGUF",
            "Qwen2.5-Coder-32B-Instruct-Q8_0.gguf",
            "--local-dir", "./models"
        ]
    },
    
    "qwen_coder_14b_q8": {
        "name": "Qwen2.5-Coder 14B (Q8_0 - HIGH QUALITY, Lighter)",
        "size": "~14GB", 
        "command": [
            "python", "-m", "huggingface_hub.commands.huggingface_cli", "download",
            "bartowski/Qwen2.5-Coder-14B-Instruct-GGUF",
            "Qwen2.5-Coder-14B-Instruct-Q8_0.gguf",
            "--local-dir", "./models"
        ]
    },
    
    "qwen_coder_7b_q8": {
        "name": "Qwen2.5-Coder 7B (Q8_0 - Good Quality, Fastest)",
        "size": "~7GB",
        "command": [
            "python", "-m", "huggingface_hub.commands.huggingface_cli", "download",
            "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
            "Qwen2.5-Coder-7B-Instruct-Q8_0.gguf",
            "--local-dir", "./models"
        ]
    },
    
    "llama_31_70b_q8": {
        "name": "Llama 3.1 70B Instruct (Q8_0 - EXCELLENT QUALITY)",
        "size": "~70GB",
        "command": [
            "python", "-m", "huggingface_hub.commands.huggingface_cli", "download",
            "bartowski/Meta-Llama-3.1-70B-Instruct-GGUF",
            "Meta-Llama-3.1-70B-Instruct-Q8_0.gguf",
            "--local-dir", "./models"
        ]
    },
    
    "llama_31_8b_q8": {
        "name": "Llama 3.1 8B Instruct (Q8_0 - Good Quality)",
        "size": "~8GB",
        "command": [
            "python", "-m", "huggingface_hub.commands.huggingface_cli", "download",
            "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
            "Meta-Llama-3.1-8B-Instruct-Q8_0.gguf",
            "--local-dir", "./models"
        ]
    }
}

def check_prerequisites():
    """Check if prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check HuggingFace CLI
    try:
        result = subprocess.run(['huggingface-cli', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ HuggingFace CLI: {result.stdout.strip()}")
        else:
            print("❌ HuggingFace CLI not working")
            return False
    except FileNotFoundError:
        print("❌ HuggingFace CLI not found")
        print("💡 Install with: pip install huggingface_hub[cli]")
        return False
    
    # Check/create models directory
    models_dir = Path("./models")
    if not models_dir.exists():
        models_dir.mkdir()
        print(f"📁 Created models directory: {models_dir.absolute()}")
    else:
        print(f"📁 Models directory exists: {models_dir.absolute()}")
    
    return True

def run_download_command(key, config):
    """Run a single download command"""
    print(f"\n🚀 Downloading {config['name']} ({config['size']})...")
    print(f"🔧 Command: {' '.join(config['command'])}")
    
    try:
        # Run the download command
        result = subprocess.run(config['command'], check=True)
        print(f"✅ Successfully downloaded {config['name']}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️ Download interrupted")
        return False

def print_manual_commands():
    """Print manual commands for copy-paste"""
    print("\n📋 Manual Download Commands:")
    print("=" * 50)
    print("Copy and paste these commands in your terminal:\n")
    
    # First install HuggingFace CLI if needed
    print("# Install HuggingFace CLI (if not installed)")
    print("pip install huggingface_hub[cli]\n")
    
    # Create models directory
    print("# Create models directory")
    print("mkdir models\n")
    
    for key, config in DOWNLOAD_COMMANDS.items():
        print(f"# {config['name']} ({config['size']})")
        print(" ".join(config['command']))
        print()

def interactive_download():
    """Interactive download process"""
    print("\n🤖 Select models to download:")
    print("=" * 40)
    
    for i, (key, config) in enumerate(DOWNLOAD_COMMANDS.items(), 1):
        print(f"{i}. {config['name']} ({config['size']})")
    
    print(f"{len(DOWNLOAD_COMMANDS) + 1}. Download OPTIMAL pair (Qwen2.5-Coder 32B Q8 + Llama 3.1 70B Q8) - ~102GB")
    print(f"{len(DOWNLOAD_COMMANDS) + 2}. Download BALANCED pair (Qwen2.5-Coder 14B Q8 + Llama 3.1 8B Q8) - ~22GB")
    print(f"{len(DOWNLOAD_COMMANDS) + 3}. Download FAST pair (Qwen2.5-Coder 7B Q8 + Llama 3.1 8B Q8) - ~15GB")
    print(f"{len(DOWNLOAD_COMMANDS) + 4}. Show manual commands")
    print("0. Exit")
    
    while True:
        try:
            choice = input(f"\nSelect option (0-{len(DOWNLOAD_COMMANDS) + 2}): ").strip()
            
            if choice == "0":
                return
            
            elif choice == str(len(DOWNLOAD_COMMANDS) + 1):
                # Download recommended pair
                print("\n🎯 Downloading recommended pair...")
                success1 = run_download_command("gemma_2_27b_q4", DOWNLOAD_COMMANDS["gemma_2_27b_q4"])
                success2 = run_download_command("qwen_coder_32b_q4", DOWNLOAD_COMMANDS["qwen_coder_32b_q4"])
                
                if success1 and success2:
                    print("\n🎉 Successfully downloaded recommended model pair!")
                    print("💡 Run 'python test_pc_setup.py' to verify setup")
                return
            
            elif choice == str(len(DOWNLOAD_COMMANDS) + 2):
                print_manual_commands()
                return
            
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(DOWNLOAD_COMMANDS):
                    key = list(DOWNLOAD_COMMANDS.keys())[choice_idx]
                    config = DOWNLOAD_COMMANDS[key]
                    
                    if run_download_command(key, config):
                        print(f"\n🎉 Download complete!")
                        print("💡 Run 'python test_pc_setup.py' to verify setup")
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
    print("🖥️ Quick PC Model Downloader")
    print("=" * 40)
    print("Downloads GGUF models for PC homework grader\n")
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install HuggingFace CLI first:")
        print("pip install huggingface_hub[cli]")
        return False
    
    print("\n💡 Recommended models for homework grading:")
    print("   • Gemma 2 27B IT (Q4_K_M) - For feedback generation")
    print("   • Qwen2.5-Coder 32B (Q4_K_M) - For code analysis")
    print("   • Total download: ~33GB")
    
    interactive_download()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")