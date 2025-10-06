#!/bin/bash
# Start Qwen 8-bit model server on Mac 2

echo "🚀 Starting Qwen3-Coder-30B-A3B-Instruct-8bit on Mac 2..."
echo "📍 Server will run on http://10.55.0.2:5002"

ssh jamiehumphries@10.55.0.2 "cd ~ && nohup python3 -m mlx_lm server \
  --model mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit \
  --host 0.0.0.0 \
  --port 5002 \
  --max-tokens 4096 \
  > qwen_8bit_server.log 2>&1 &"

echo "✅ Server started!"
echo "📊 Check logs: ssh jamiehumphries@10.55.0.2 'tail -f ~/qwen_8bit_server.log'"
echo "🔍 Test: curl http://10.55.0.2:5002/health"
