#!/bin/bash
# Clear locks and download 8-bit model

echo "🔧 Fixing lock issue and downloading 8-bit model..."
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
echo "1. Stopping Qwen server..."
pkill -f qwen_server.py
sleep 3

echo "2. Clearing lock files..."
rm -rf ~/.cache/huggingface/hub/.locks/models--mlx-community--Qwen3-Coder-30B-A3B-Instruct-8bit/
echo "✅ Locks cleared"

echo ""
echo "3. Downloading 8-bit model..."
/Users/jamiehumphries/Library/Python/3.9/bin/huggingface-cli download mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit

if [ $? -eq 0 ]; then
    echo "✅ Download complete!"
else
    echo "❌ Download failed"
    exit 1
fi

echo ""
echo "4. Starting Qwen server with 8-bit model..."
cd ~/homework_grader/servers
nohup python3 qwen_server.py > ~/qwen.log 2>&1 &
sleep 5

echo "✅ Server started"
EOF

echo ""
echo "⏳ Waiting for model to load (30 seconds)..."
sleep 30

echo ""
echo "🔍 Testing server..."
curl -s http://10.55.0.2:5002/health

echo ""
echo "✅ Done!"
