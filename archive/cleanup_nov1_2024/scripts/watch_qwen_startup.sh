#!/bin/bash
# Watch Qwen server startup in real-time

echo "👀 Watching Qwen server startup..."
echo "Press Ctrl+C to stop"
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
echo "📝 Last 50 lines of log:"
tail -50 ~/qwen.log

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Live log (Ctrl+C to stop):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -f ~/qwen.log
EOF
