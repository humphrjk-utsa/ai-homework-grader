#!/bin/bash
# Check Mac Studio 2 Status
echo "🔍 Mac Studio 2 Status Check"
echo "============================"

# Check if server is running
if curl -s http://10.55.0.2:5002/health > /dev/null; then
    echo "✅ Gemma server is running"
    curl -s http://10.55.0.2:5002/status | python3 -m json.tool
else
    echo "❌ Gemma server is not running"
    echo "💡 Run: ./start_server.sh"
fi
