#!/bin/bash
# Check status of Mac Studio 2 (Qwen server)

echo "🔍 Checking Mac Studio 2 Status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
echo "📊 System Resources:"
echo "CPU Usage:"
top -l 1 | grep "CPU usage" | head -1

echo ""
echo "Memory Usage:"
top -l 1 | grep "PhysMem" | head -1

echo ""
echo "🔥 Temperature & Fan Status:"
# Check if powermetrics is available
if command -v powermetrics &> /dev/null; then
    sudo powermetrics --samplers smc -i1 -n1 2>/dev/null | grep -E "Fan|CPU die temperature" | head -5
else
    echo "  (powermetrics not available)"
fi

echo ""
echo "🤖 Python Processes:"
ps aux | grep python | grep -v grep | head -5

echo ""
echo "📝 Recent Qwen Log (last 20 lines):"
tail -20 ~/qwen.log 2>/dev/null || echo "  (No log file found)"

echo ""
echo "🌐 Server Health:"
curl -s http://localhost:5002/health 2>/dev/null || echo "  ❌ Server not responding"
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
