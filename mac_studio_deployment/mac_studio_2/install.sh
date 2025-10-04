#!/bin/bash
# Mac Studio 2 Installation Script
echo "🖥️ Setting up Mac Studio 2 (Gemma Server)"
echo "==========================================="

# Check if we're on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "❌ This script requires Apple Silicon Mac"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install MLX and Flask specifically
echo "📦 Installing MLX and Flask..."
pip3 install mlx-lm flask aiohttp

# Download Gemma model if not present
echo "🔄 Checking for Gemma model..."
python3 -c "
try:
    from mlx_lm import load
    print('Loading Gemma model...')
    model, tokenizer = load('mlx-community/gemma-3-27b-it-bf16')
    print('✅ Gemma model ready!')
except ImportError:
    print('❌ MLX not installed properly')
except Exception as e:
    print(f'❌ Model loading failed: {e}')
    print('💡 Model will be downloaded on first use')
"

echo "✅ Mac Studio 2 setup complete!"
echo "🚀 Run: ./start_server.sh to start the Gemma server"
