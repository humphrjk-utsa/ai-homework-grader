#!/bin/bash
# Restart Qwen server on Mac Studio 2

echo "🔄 Restarting Qwen server on Mac Studio 2..."
echo ""

# SSH to Mac Studio 2 and restart Qwen
ssh jamiehumphries@10.55.0.2 << 'EOF'
echo "Stopping Qwen server..."
pkill -f qwen_server.py
sleep 3

echo "Starting Qwen server..."
cd ~/homework_grader/servers
nohup python3 qwen_server.py > ~/qwen.log 2>&1 &
sleep 5

echo "✅ Qwen server restarted"
EOF

echo ""
echo "Checking server health..."
sleep 3
curl -s http://10.55.0.2:5002/health

echo ""
echo "✅ Done! Wait 30 seconds for the model to fully load, then try grading again."
