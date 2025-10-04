#!/bin/bash
# Mac Studio 1 Installation Script
echo "🖥️ Setting up Mac Studio 1 (Qwen Coder Server)"
echo "================================================"

# Check if we're on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "❌ This script requires Apple Silicon Mac"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Download Qwen model if not present
echo "🔄 Checking for Qwen model..."
python3 -c "
from mlx_lm import load
try:
    print('Loading Qwen model...')
    model, tokenizer = load('mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16')
    print('✅ Qwen model ready!')
except Exception as e:
    print(f'❌ Model loading failed: {e}')
    print('💡 Model will be downloaded on first use')
"

echo "✅ Mac Studio 1 setup complete!"
echo "🚀 Run: ./start_server.sh to start the Qwen server"
