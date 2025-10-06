#!/bin/bash
# Start Qwen server on Mac Studio 2

echo "🚀 Starting Qwen server on Mac Studio 2..."
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
# Check if already running
if pgrep -f qwen_server.py > /dev/null; then
    echo "⚠️  Qwen server is already running"
    ps aux | grep qwen_server.py | grep -v grep
    exit 0
fi

# Start the server
echo "Starting Qwen server..."
cd ~/homework_grader/servers
nohup python3 qwen_server.py > ~/qwen.log 2>&1 &

sleep 3

# Check if it started
if pgrep -f qwen_server.py > /dev/null; then
    echo "✅ Qwen server started successfully"
    echo ""
    echo "Process info:"
    ps aux | grep qwen_server.py | grep -v grep
else
    echo "❌ Failed to start Qwen server"
    echo ""
    echo "Last 20 lines of log:"
    tail -20 ~/qwen.log
fi
EOF

echo ""
echo "Checking server health..."
sleep 5
curl -s http://10.55.0.2:5002/health

echo ""
echo "✅ Done! Wait 30 seconds for model to fully load, then try grading again."
