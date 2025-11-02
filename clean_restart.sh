#!/bin/bash
# Clean Restart Script - Clears cache and restarts grading system

echo "🧹 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "🗑️  Clearing model cache..."
rm -rf models/.cache/* 2>/dev/null || true

echo "📊 Checking running processes..."
ps aux | grep -E "streamlit|app.py" | grep -v grep | grep -v monitor

echo ""
echo "✅ Cache cleared!"
echo ""
echo "🚀 To start the grading interface:"
echo "   streamlit run app.py --server.port 8501"
echo ""
echo "📊 To start the monitor:"
echo "   streamlit run monitor_app.py --server.port 8502"
echo ""
echo "🔍 To test the validator:"
echo "   python test_validator_fix.py"
echo ""
echo "✅ To verify the fix:"
echo "   python -c 'from business_analytics_grader import BusinessAnalyticsGrader; print(\"✅ Import successful\")'"
echo ""
