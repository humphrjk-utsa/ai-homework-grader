#!/bin/bash
# Check what Qwen models are available

echo "🔍 Checking Qwen models on Mac Studio 2..."
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
echo "📁 Models in cache:"
ls -lh ~/.cache/huggingface/hub/ 2>/dev/null | grep -i qwen || echo "No Qwen models found in cache"

echo ""
echo "📁 Models in mlx_models:"
ls -lh ~/mlx_models/ 2>/dev/null | grep -i qwen || echo "No mlx_models directory"

echo ""
echo "🔍 Checking server log for model loading:"
tail -30 ~/qwen.log 2>/dev/null | grep -i "model\|error\|loading" || echo "No recent log entries"

echo ""
echo "🌐 Server status:"
curl -s http://localhost:5002/health 2>/dev/null || echo "Server not responding"
EOF
