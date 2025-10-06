#!/bin/bash
# Find what's eating memory on Mac Studio 2

echo "🔍 Checking Mac Studio 2 Memory Usage..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
echo "💾 Total Memory Usage:"
top -l 1 | grep PhysMem

echo ""
echo "🔝 Top 10 Memory-Hungry Processes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | sort -nrk 4 | head -10 | awk '{printf "%-20s %8s %8s %s\n", $1, $3"%", $4"%", $11}'

echo ""
echo "🐍 Python Processes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep python | grep -v grep | awk '{printf "PID: %-8s CPU: %6s MEM: %6s CMD: %s\n", $2, $3"%", $4"%", $11}'

echo ""
echo "📊 Memory Breakdown:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-20s % 16.2f MB\n", "$1:", $2 * $size / 1048576);'

echo ""
echo "🔍 Checking for memory leaks or stuck processes..."
ps aux | awk '$4 > 10 {print "⚠️  Process using >10% RAM: " $11 " (PID: " $2 ", MEM: " $4 "%)"}'

EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 If you see multiple Python processes or high memory usage,"
echo "   you may need to restart the Qwen server to free up RAM."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
