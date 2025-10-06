#!/bin/bash
# Switch Qwen server to 8-bit quantized model

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Switching to Qwen 8-bit Model"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

MODEL_NAME="mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit"

echo "📥 Step 1: Download 8-bit model on Mac Studio 2..."
ssh jamiehumphries@10.55.0.2 << EOF
echo "Downloading $MODEL_NAME..."
/Users/jamiehumphries/Library/Python/3.9/bin/huggingface-cli download $MODEL_NAME

if [ \$? -eq 0 ]; then
    echo "✅ Model downloaded successfully"
else
    echo "❌ Download failed"
    exit 1
fi
EOF

echo ""
echo "🛑 Step 2: Stop current Qwen server..."
ssh jamiehumphries@10.55.0.2 << 'EOF'
pkill -f qwen_server.py
sleep 3
echo "✅ Server stopped"
EOF

echo ""
echo "📝 Step 3: Update server configuration..."
ssh jamiehumphries@10.55.0.2 << 'EOF'
cd ~/homework_grader/servers

# Backup current server
if [ -f qwen_server.py ]; then
    cp qwen_server.py qwen_server.py.backup
    echo "✅ Backed up current server"
fi

# Update model name in server file
sed -i '' 's/Qwen3-Coder-30B-A3B-Instruct-bf16/Qwen3-Coder-30B-A3B-Instruct-8bit/g' qwen_server.py

echo "✅ Configuration updated"
EOF

echo ""
echo "🚀 Step 4: Start Qwen server with 8-bit model..."
ssh jamiehumphries@10.55.0.2 << 'EOF'
cd ~/homework_grader/servers
nohup python3 qwen_server.py > ~/qwen.log 2>&1 &
sleep 5

if pgrep -f qwen_server.py > /dev/null; then
    echo "✅ Server started"
else
    echo "❌ Server failed to start"
    echo "Last 20 lines of log:"
    tail -20 ~/qwen.log
    exit 1
fi
EOF

echo ""
echo "⏳ Step 5: Waiting for model to load (30 seconds)..."
sleep 30

echo ""
echo "🔍 Step 6: Testing server health..."
if curl -s http://10.55.0.2:5002/health | grep -q "healthy"; then
    echo "✅ Server is healthy!"
else
    echo "⚠️  Server may still be loading..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SWITCH COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Expected improvements:"
echo "  • RAM usage: 57GB → ~38GB (33% reduction)"
echo "  • Free RAM: 68GB → 87GB (more headroom)"
echo "  • Inference speed: Similar or faster"
echo "  • Quality: Minimal difference (8-bit vs bf16)"
echo ""
echo "🚀 Ready to grade! Try batch grading now."
