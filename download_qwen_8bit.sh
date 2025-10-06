#!/bin/bash
# Download Qwen 8-bit model using Python

echo "📥 Downloading Qwen 8-bit model..."
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
# Create Python script to download
cat > /tmp/download_model.py << 'PYTHON'
from huggingface_hub import snapshot_download
import os

model_name = "mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit"
cache_dir = os.path.expanduser("~/.cache/huggingface/hub")

print(f"📥 Downloading {model_name}...")
print(f"📁 Cache directory: {cache_dir}")
print("")
print("This will take 5-10 minutes depending on your connection...")
print("")

try:
    path = snapshot_download(
        repo_id=model_name,
        cache_dir=cache_dir,
        resume_download=True
    )
    print(f"\n✅ Model downloaded successfully to: {path}")
except Exception as e:
    print(f"\n❌ Download failed: {e}")
    exit(1)
PYTHON

# Run the download
python3 /tmp/download_model.py

# Clean up
rm /tmp/download_model.py
EOF

echo ""
echo "✅ Download complete!"
