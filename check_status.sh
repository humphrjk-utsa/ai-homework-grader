#!/bin/bash
# Check Mac Studio 1 Status
echo "🔍 Mac Studio 1 Status Check"
echo "============================"

# Check if server is running
if curl -s http://10.55.0.1:5001/health > /dev/null; then
    echo "✅ Qwen server is running"
    curl -s http://10.55.0.1:5001/status | python3 -m json.tool
else
    echo "❌ Qwen server is not running"
    echo "💡 Run: ./start_server.sh"
fi
