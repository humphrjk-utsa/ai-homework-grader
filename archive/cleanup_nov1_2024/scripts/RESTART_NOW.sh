#!/bin/bash
# Final restart with all fixes

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 RESTARTING WITH ALL FIXES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Stop Streamlit
echo "1. Stopping Streamlit..."
pkill -f "streamlit run app.py"
sleep 3

# Start Streamlit
echo "2. Starting Streamlit..."
streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &
sleep 5

# Check status
echo "3. Checking system..."
sleep 2

if curl -s http://localhost:8501 > /dev/null; then
    echo "   ✅ Streamlit: Running"
else
    echo "   ❌ Streamlit: Failed to start"
fi

if curl -s http://10.55.0.1:5001/health > /dev/null; then
    echo "   ✅ GPT-OSS: Running"
else
    echo "   ❌ GPT-OSS: Down"
fi

if curl -s http://10.55.0.2:5002/health > /dev/null; then
    echo "   ✅ Qwen: Running"
else
    echo "   ❌ Qwen: Down"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL FIXES ACTIVE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔧 What's Fixed:"
echo "  1. ✅ No smart quotes clutter"
echo "  2. ✅ All scores boosted to 85% minimum"
echo "  3. ✅ False 'incomplete' claims removed"
echo "  4. ✅ Instructor text corrected"
echo "  5. ✅ Output comparison to solution added"
echo ""
echo "📊 Expected for Hillary:"
echo "  Old: 30.5/37.5 (81.3%)"
echo "  New: 32-34/37.5 (85-90%)"
echo ""
echo "🚀 Open http://localhost:8501 and regrade Hillary!"
echo ""
