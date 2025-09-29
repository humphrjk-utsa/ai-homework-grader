#!/usr/bin/env python3
"""
Guide for copying MLX models from another PC
"""

from pathlib import Path
import os

def show_copy_instructions():
    """Show how to copy models from another PC"""
    
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    print("📋 How to Copy MLX Models from Another PC")
    print("=" * 60)
    
    print("\n🖥️  ON THE SOURCE PC (where models are downloaded):")
    print("   1. Find the HuggingFace cache directory:")
    print("      • Windows: C:\\Users\\[username]\\.cache\\huggingface\\hub")
    print("      • Mac/Linux: ~/.cache/huggingface/hub")
    print("      • Or run: python -c \"from pathlib import Path; print(Path.home() / '.cache' / 'huggingface' / 'hub')\"")
    
    print("\n   2. Look for model directories starting with 'models--':")
    print("      • models--mlx-community--gpt-oss-20b-MXFP4-Q8")
    print("      • models--lmstudio-community--gpt-oss-120b-MLX-8bit")
    print("      • models--mlx-community--gemma-2-27b-it-4bit")
    
    print("\n   3. Copy the entire model directories to external drive/USB")
    
    print(f"\n💻 ON THIS MAC:")
    print(f"   1. Your cache directory is: {cache_dir}")
    print(f"   2. Create it if it doesn't exist: mkdir -p {cache_dir}")
    print(f"   3. Copy the model directories into: {cache_dir}")
    
    print("\n📁 Example copy commands:")
    print("   # If copying from external drive:")
    print(f"   cp -r /Volumes/YourDrive/models--* {cache_dir}/")
    print("   ")
    print("   # If copying from network location:")
    print(f"   rsync -av /path/to/models/ {cache_dir}/")
    
    print("\n✅ After copying:")
    print("   • Run: python check_available_models.py")
    print("   • Models should appear immediately")
    print("   • No download needed!")
    
    return cache_dir

def check_copy_status():
    """Check if any models have been copied"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    print(f"\n🔍 Checking: {cache_dir}")
    
    if not cache_dir.exists():
        print("❌ Cache directory doesn't exist yet")
        print(f"💡 Create it: mkdir -p {cache_dir}")
        return
    
    model_dirs = [d for d in cache_dir.iterdir() if d.is_dir() and d.name.startswith('models--')]
    
    if not model_dirs:
        print("📭 No models found")
        print("💡 Copy model directories here")
    else:
        print(f"✅ Found {len(model_dirs)} models:")
        for model_dir in model_dirs:
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
            size_gb = size / (1024**3)
            print(f"   • {model_name} ({size_gb:.1f}GB)")

def create_copy_script():
    """Create a script to help with copying"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    script_content = f"""#!/bin/bash
# MLX Model Copy Script
# Usage: ./copy_models.sh /path/to/source/models

SOURCE_DIR="$1"
TARGET_DIR="{cache_dir}"

if [ -z "$SOURCE_DIR" ]; then
    echo "Usage: $0 /path/to/source/models"
    echo "Example: $0 /Volumes/MyDrive/huggingface/hub"
    exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory does not exist: $SOURCE_DIR"
    exit 1
fi

echo "📁 Copying MLX models..."
echo "   From: $SOURCE_DIR"
echo "   To: $TARGET_DIR"

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy all model directories
for model_dir in "$SOURCE_DIR"/models--*; do
    if [ -d "$model_dir" ]; then
        model_name=$(basename "$model_dir")
        echo "📥 Copying: $model_name"
        cp -r "$model_dir" "$TARGET_DIR/"
    fi
done

echo "✅ Copy complete!"
echo "💡 Run: python check_available_models.py"
"""
    
    script_path = Path("copy_models.sh")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    print(f"📜 Created copy script: {script_path}")
    print("💡 Usage: ./copy_models.sh /path/to/source/models")

def main():
    """Main function"""
    cache_dir = show_copy_instructions()
    check_copy_status()
    
    print(f"\n🛠️  Want a copy script?")
    response = input("Create copy_models.sh script? (y/n): ").strip().lower()
    if response == 'y':
        create_copy_script()
    
    print(f"\n💡 Pro tips:")
    print(f"   • Models are just files - copying is much faster than downloading")
    print(f"   • You can copy from Windows, Mac, or Linux")
    print(f"   • Make sure to copy the entire 'models--' directories")
    print(f"   • MLX will recognize them immediately")

if __name__ == "__main__":
    main()