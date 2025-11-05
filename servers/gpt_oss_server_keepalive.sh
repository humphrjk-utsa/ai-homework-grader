#!/bin/bash
# GPT-OSS Server with Auto-Restart
# This script will automatically restart the server if it crashes

echo "🖥️ Starting GPT-OSS Server with Auto-Restart..."
echo "📡 Server: http://10.55.0.1:5001"
echo "🔄 Will automatically restart if crashed"
echo "Press Ctrl+C to stop permanently"
echo ""

# Counter for restarts
RESTART_COUNT=0

while true; do
    if [ $RESTART_COUNT -gt 0 ]; then
        echo ""
        echo "🔄 Restart #$RESTART_COUNT - $(date)"
        echo "⏳ Waiting 5 seconds before restart..."
        sleep 5
    fi
    
    echo "🚀 Starting GPT-OSS server..."
    python3 servers/gpt_oss_server_working.py
    
    EXIT_CODE=$?
    RESTART_COUNT=$((RESTART_COUNT + 1))
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Server stopped cleanly (exit code 0)"
        break
    else
        echo "❌ Server crashed with exit code $EXIT_CODE"
        echo "🔄 Auto-restarting..."
    fi
done

echo ""
echo "👋 GPT-OSS Server stopped"
