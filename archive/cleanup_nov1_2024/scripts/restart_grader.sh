#!/bin/bash
# Restart the grading system with all new fixes

echo "🔄 Restarting AI Homework Grader..."
echo ""

# Stop Streamlit
echo "Stopping Streamlit..."
pkill -f "streamlit run app.py"
sleep 2

# Start Streamlit
echo "Starting Streamlit..."
nohup streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &
sleep 4

# Check status
echo ""
echo "✅ Checking system status..."
curl -s http://localhost:8501 > /dev/null && echo "  ✅ Streamlit: Running" || echo "  ❌ Streamlit: Failed"
curl -s http://10.55.0.1:5001/health > /dev/null && echo "  ✅ GPT-OSS: Running" || echo "  ❌ GPT-OSS: Down"
curl -s http://10.55.0.2:5002/health > /dev/null && echo "  ✅ Qwen: Running" || echo "  ❌ Qwen: Down"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 System restarted with new fixes!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔧 New Features:"
echo "  ✅ More aggressive score boosting (85-90% minimum)"
echo "  ✅ No smart quotes clutter in reports"
echo "  ✅ Only shows real syntax errors"
echo ""
echo "📊 Expected for Hillary:"
echo "  Old: 27.7/37.5 (73.9%)"
echo "  New: 32-34/37.5 (85-90%)"
echo ""
echo "🚀 Open http://localhost:8501 and regrade!"
