#!/usr/bin/env python3
"""
Download Qwen 3.0 Models for PC Homework Grader
Focuses on the latest Qwen 3.0 series with high precision
"""

import subprocess
import sys
import os
from pathlib import Path

# Qwen 3.0 & Gemma 3 Model Commands using llama-cli
MODELS = {
    "qwen3_coder_30b_q8": {
        "name": "Qwen 3.0 Coder 30B A3B (Q8_0 - CODE SPECIALIST)",
        "size": "~30GB",
        "use_case": "Advanced code analysis and technical review",
        "command": [
            "./llama-cli", "--hf-repo", "ggml-org/Qwen3-Coder-30B-A3B-Instruct-Q8_0-GGUF",
            "--hf-file", "qwen3-coder-30b-a3b-instruct-q8_0.gguf"
        ],
        "output_file": "qwen3-coder-30b-a3b-instruct-q8_0.gguf"
    },
    
    "gemma3_27b_q8": {
        "name": "Gemma 3 27B IT (Q8_0 - FEEDBACK SPECIALIST)",
        "size": "~27GB",
        "use_case": "High-quality feedback generation and reasoning",
        "command": [
            "./llama-cli", "--hf-repo", "ggml-org/gemma-3-27b-it-Q8_0-GGUF",
            "--hf-file", "gemma-3-27b-it-q8_0.gguf"
        ],
        "output_file": "gemma-3-27b-it-q8_0.gguf"
    },
    
    "qwen3_14b_q8": {
        "name": "Qwen 3.0 14B Instruct (Q8_0 - BALANCED)",
        "size": "~14GB",
        "use_case": "Balanced performance for general tasks",
        "command": [
            "./llama-cli", "--hf-repo", "ggml-org/Qwen3-14B-Instruct-Q8_0-GGUF",
            "--hf-file", "qwen3-14b-instruct-q8_0.gguf"
        ],
        "output_file": "qwen3-14b-instruct-q8_0.gguf"
    },
    
    "qwen3_coder_14b_q8": {
        "name": "Qwen 3.0 Coder 14B (Q8_0 - CODE BALANCED)",
        "size": "~14GB",
        "use_case": "Code analysis for lighter systems",
        "command": [
            "./llama-cli", "--hf-repo", "ggml-org/Qwen3-Coder-14B-Instruct-Q8_0-GGUF",
            "--hf-file", "qwen3-coder-14b-instruct-q8_0.gguf"
        ],
        "output_file": "qwen3-coder-14b-instruct-q8_0.gguf"
    },
    
    "qwen3_7b_q8": {
        "name": "Qwen 3.0 7B Instruct (Q8_0 - FAST)",
        "size": "~7GB",
        "use_case": "Fast inference for testing",
        "command": [
            "./llama-cli", "--hf-repo", "ggml-org/Qwen3-7B-Instruct-Q8_0-GGUF",
            "--hf-file", "qwen3-7b-instruct-q8_0.gguf"
        ],
        "output_file": "qwen3-7b-instruct-q8_0.gguf"
    },
    
    "gemma3_9b_q8": {
        "name": "Gemma 3 9B IT (Q8_0 - LIGHTWEIGHT)",
        "size": "~9GB",
        "use_case": "Lightweight feedback generation",
        "command": [
            "./llama-cli", "--hf-repo", "ggml-org/gemma-3-9b-it-Q8_0-GGUF",
            "--hf-file", "gemma-3-9b-it-q8_0.gguf"
        ],
        "output_file": "gemma-3-9b-it-q8_0.gguf"
    }
}

def check_prerequisites():
    """Check if prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check llama-cli
    llama_cli_paths = [
        "./llama-cli",
        "./llama-cli.exe", 
        "llama-cli",
        "llama-cli.exe"
    ]
    
    llama_cli_found = False
    for cli_path in llama_cli_paths:
        try:
            result = subprocess.run([cli_path, "--help"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 or "llama-cli" in result.stderr.lower():
                print(f"✅ llama-cli found: {cli_path}")
                llama_cli_found = True
                break
        except Exception:
            continue
    
    if not llama_cli_found:
        print("❌ llama-cli not found")
        print("💡 Download llama-cli from: https://github.com/ggerganov/llama.cpp/releases")
        print("💡 Or build from source: https://github.com/ggerganov/llama.cpp")
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
    print(f"🎯 Use case: {config['use_case']}")
    print(f"🔧 Command: {' '.join(config['command'])}")
    
    try:
        # Change to models directory for download
        original_dir = os.getcwd()
        models_dir = Path("./models")
        os.chdir(models_dir)
        
        # Adjust command for current directory
        cmd = config['command'].copy()
        if cmd[0] == "./llama-cli":
            cmd[0] = "../llama-cli"  # Adjust path from models directory
        
        # Run the download command
        result = subprocess.run(cmd, check=True)
        
        # Check if file was downloaded
        output_file = config.get('output_file')
        if output_file and Path(output_file).exists():
            file_size = Path(output_file).stat().st_size / (1024**3)  # GB
            print(f"✅ Successfully downloaded {config['name']}")
            print(f"📁 File: {output_file} ({file_size:.1f}GB)")
        else:
            print(f"✅ Download command completed for {config['name']}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️ Download interrupted")
        return False
    finally:
        # Return to original directory
        os.chdir(original_dir)

def interactive_download():
    """Interactive download process"""
    print("\n🤖 Qwen 3.0 & Gemma 3 Models Available:")
    print("=" * 60)
    
    for i, (key, config) in enumerate(MODELS.items(), 1):
        print(f"{i}. {config['name']} ({config['size']})")
        print(f"   🎯 {config['use_case']}")
        print()
    
    print(f"{len(MODELS) + 1}. Download OPTIMAL PAIR (Qwen3 Coder 30B + Gemma 3 27B) - ~57GB")
    print(f"{len(MODELS) + 2}. Download BALANCED PAIR (Qwen3 Coder 14B + Gemma 3 9B) - ~23GB")
    print(f"{len(MODELS) + 3}. Download FAST PAIR (Qwen3 7B + Gemma 3 9B) - ~16GB")
    print("0. Exit")
    
    while True:
        try:
            choice = input(f"\nSelect option (0-{len(MODELS) + 3}): ").strip()
            
            if choice == "0":
                return
            
            elif choice == str(len(MODELS) + 1):
                # Download optimal pair
                print("\n🎯 Downloading OPTIMAL pair for maximum quality...")
                success1 = run_download_command("qwen3_coder_30b_q8", MODELS["qwen3_coder_30b_q8"])
                success2 = run_download_command("gemma3_27b_q8", MODELS["gemma3_27b_q8"])
                
                if success1 and success2:
                    print("\n🎉 Successfully downloaded OPTIMAL pair!")
                    print("💡 Qwen 3.0 Coder 30B for code analysis")
                    print("💡 Gemma 3 27B for feedback generation")
                    print("💡 Perfect for RTX Pro 6000 with 97GB VRAM")
                    print("💡 Run 'python test_pc_setup.py' to verify setup")
                return
            
            elif choice == str(len(MODELS) + 2):
                # Download balanced pair
                print("\n⚖️ Downloading BALANCED pair...")
                success1 = run_download_command("qwen3_coder_14b_q8", MODELS["qwen3_coder_14b_q8"])
                success2 = run_download_command("gemma3_9b_q8", MODELS["gemma3_9b_q8"])
                
                if success1 and success2:
                    print("\n🎉 Successfully downloaded BALANCED pair!")
                    print("💡 Good balance of quality and speed")
                return
            
            elif choice == str(len(MODELS) + 3):
                # Download fast pair
                print("\n⚡ Downloading FAST pair...")
                success1 = run_download_command("qwen3_7b_q8", MODELS["qwen3_7b_q8"])
                success2 = run_download_command("gemma3_9b_q8", MODELS["gemma3_9b_q8"])
                
                if success1 and success2:
                    print("\n🎉 Successfully downloaded FAST pair!")
                    print("💡 Great for testing and development")
                return
            
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(MODELS):
                    key = list(MODELS.keys())[choice_idx]
                    config = MODELS[key]
                    
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
    print("🚀 Qwen 3.0 Model Downloader for PC")
    print("=" * 40)
    print("Downloads the latest Qwen 3.0 models for homework grading\n")
    
    if not check_prerequisites():
        return False
    
    print("\n💡 Recommended for RTX Pro 6000 (97GB VRAM):")
    print("   • OPTIMAL: Qwen 3.0 Coder 30B + Gemma 3 27B (~57GB total)")
    print("   • Uses Q8_0 quantization for best quality/size balance")
    print("   • Perfect for parallel processing on your GPU")
    print("   • Latest models with superior performance")
    
    interactive_download()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")