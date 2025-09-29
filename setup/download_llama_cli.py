#!/usr/bin/env python3
"""
Download llama-cli for Windows
"""

import requests
import zipfile
import os
import sys
from pathlib import Path

def download_llama_cli():
    """Download llama-cli for Windows"""
    print("🚀 Downloading llama-cli for Windows...")
    
    # Try multiple possible URLs for Windows builds
    urls = [
        "https://github.com/ggerganov/llama.cpp/releases/download/b4268/llama-b4268-bin-win-cuda-cu12.2.0-x64.zip",
        "https://github.com/ggerganov/llama.cpp/releases/download/b4268/llama-b4268-bin-win-x64.zip",
        "https://github.com/ggerganov/llama.cpp/releases/download/b4268/llama-b4268-bin-win-cuda-x64.zip"
    ]
    
    # Try each URL until one works
    for url in urls:
        try:
            print(f"📥 Trying: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed: {e}")
            continue
    else:
        print("❌ All download URLs failed")
        return False
    
    try:
        
        zip_path = "llama-cpp-windows.zip"
        
        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r📊 Progress: {progress:.1f}%", end='', flush=True)
        
        print(f"\n✅ Downloaded {zip_path}")
        
        # Extract the zip file
        print("📦 Extracting llama-cli...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract only the llama-cli executable
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('llama-cli.exe'):
                    # Extract to current directory
                    file_info.filename = 'llama-cli.exe'
                    zip_ref.extract(file_info, '.')
                    print(f"✅ Extracted {file_info.filename}")
                    break
        
        # Clean up zip file
        os.remove(zip_path)
        print("🧹 Cleaned up zip file")
        
        # Make executable (not needed on Windows but good practice)
        if Path('llama-cli.exe').exists():
            print("✅ llama-cli.exe is ready!")
            return True
        else:
            print("❌ Failed to extract llama-cli.exe")
            return False
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def test_llama_cli():
    """Test if llama-cli works"""
    try:
        import subprocess
        result = subprocess.run(['./llama-cli.exe', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 or 'llama-cli' in result.stderr.lower():
            print("✅ llama-cli.exe is working!")
            return True
        else:
            print("❌ llama-cli.exe test failed")
            return False
    except Exception as e:
        print(f"❌ llama-cli.exe test error: {e}")
        return False

def main():
    """Main function"""
    print("🖥️ llama-cli Downloader for Windows")
    print("=" * 40)
    
    # Check if already exists
    if Path('llama-cli.exe').exists():
        print("📁 llama-cli.exe already exists")
        if test_llama_cli():
            print("🎉 llama-cli.exe is ready to use!")
            return True
        else:
            print("⚠️ Existing llama-cli.exe not working, re-downloading...")
    
    # Download llama-cli
    if download_llama_cli():
        if test_llama_cli():
            print("\n🎉 llama-cli.exe setup complete!")
            print("💡 You can now run: python download_qwen3_models.py")
            return True
        else:
            print("\n❌ llama-cli.exe setup failed")
            return False
    else:
        print("\n❌ Failed to download llama-cli.exe")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Download interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)