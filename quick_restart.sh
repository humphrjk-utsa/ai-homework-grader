#!/bin/bash
# Quick restart script that doesn't block

# Kill streamlit
pkill -9 -f "streamlit run app.py"

# Wait a moment
sleep 2

# Start in background and detach completely
cd /Users/humphrjk/GitHub/ai-homework-grader-clean
nohup streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &

# Give it a moment to start
sleep 3

# Quick status check
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Streamlit restarted successfully"
else
    echo "⚠️ Streamlit may still be starting..."
fi
