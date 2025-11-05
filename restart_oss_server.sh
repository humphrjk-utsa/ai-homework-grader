#!/bin/bash
# Restart GPT-OSS Server Script

echo "🔄 Restarting GPT-OSS Server..."

# Kill existing server
pkill -f "gpt_oss_server_working.py"
sleep 2

# Start new server
echo "🚀 Starting GPT-OSS server..."
python3 servers/gpt_oss_server_working.py &

echo "✅ Server restart initiated"
echo "⏳ Model loading... (this takes ~30 seconds for 120B model)"
echo "📡 Check status: curl http://10.55.0.1:5001/health"
