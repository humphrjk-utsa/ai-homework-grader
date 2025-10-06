#!/bin/bash
# Monitor Mac Studio temperatures, GPU, and performance

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🖥️  MAC STUDIO MONITORING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to monitor a Mac
monitor_mac() {
    local name=$1
    local user=$2
    local ip=$3
    
    echo "┌─────────────────────────────────────────────────────────────────────────┐"
    echo "│ $name ($ip)"
    echo "└─────────────────────────────────────────────────────────────────────────┘"
    
    ssh $user@$ip << 'EOF'
# CPU Usage
echo "📊 CPU Usage:"
top -l 1 | grep "CPU usage" | awk '{print "  User: " $3 " System: " $5 " Idle: " $7}'

# Memory
echo ""
echo "💾 Memory:"
top -l 1 | grep "PhysMem" | awk '{print "  Used: " $2 " Wired: " $4 " Unused: " $6}'

# GPU (if available)
echo ""
echo "🎮 GPU:"
if command -v ioreg &> /dev/null; then
    # Try to get GPU info
    ioreg -l | grep -i "PerformanceStatistics" | head -1 | awk '{print "  Active"}'
else
    echo "  (GPU monitoring not available)"
fi

# Temperature & Fans
echo ""
echo "🌡️  Temperature & Fans:"
if command -v powermetrics &> /dev/null; then
    sudo powermetrics --samplers smc -i1 -n1 2>/dev/null | grep -E "Fan|CPU die temperature|GPU die temperature" | head -10
else
    echo "  (Requires sudo powermetrics)"
fi

# Python processes
echo ""
echo "🐍 Python Processes:"
ps aux | grep python | grep -v grep | awk '{print "  " $11 " (CPU: " $3 "%, MEM: " $4 "%)"}'

# Server status
echo ""
echo "🌐 Server Status:"
if curl -s http://localhost:5001/health &> /dev/null; then
    echo "  ✅ Port 5001: Running"
else
    echo "  ❌ Port 5001: Down"
fi

if curl -s http://localhost:5002/health &> /dev/null; then
    echo "  ✅ Port 5002: Running"
else
    echo "  ❌ Port 5002: Down"
fi

EOF
    
    echo ""
}

# Monitor Mac Studio 1 (GPT-OSS)
monitor_mac "Mac Studio 1 (GPT-OSS)" "jamiehumphries" "10.55.0.1"

# Monitor Mac Studio 2 (Qwen)
monitor_mac "Mac Studio 2 (Qwen)" "jamiehumphries" "10.55.0.2"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏱️  Monitoring complete at $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Tip: Run 'watch -n 5 ./monitor_macs.sh' for continuous monitoring"
