#!/bin/bash
# Simple script to restart servers with correct models
# No need to move models - they're already on the right machines

set -e

echo "🔄 Restarting servers with correct models..."
echo "================================================"
echo ""

# Update these with your actual username
MAC1_USER="humphrjk"  # Change if different
MAC2_USER="humphrjk"  # Change if different
MAC1_IP="10.55.0.1"
MAC2_IP="10.55.0.2"

echo "⏹️  Stopping current servers..."
ssh ${MAC1_USER}@${MAC1_IP} "pkill -f 'server.py' || true" &
ssh ${MAC2_USER}@${MAC2_IP} "pkill -f 'server.py' || true" &
wait
echo "✅ Servers stopped"
sleep 2

echo ""
echo "🚀 Starting Mac Studio 1 with Gemma (already downloaded)..."
ssh ${MAC1_USER}@${MAC1_IP} "cd ~/ai-homework-grader-clean/mac_studio_deployment/mac_studio_1/servers && nohup python gemma_server.py > gemma.log 2>&1 &"

echo "🚀 Starting Mac Studio 2 with Qwen (already running)..."
ssh ${MAC2_USER}@${MAC2_IP} "cd ~/ai-homework-grader-clean/mac_studio_deployment/mac_studio_2/servers && nohup python qwen_server.py > qwen.log 2>&1 &"

echo ""
echo "⏳ Waiting 30 seconds for models to load..."
sleep 30

echo ""
echo "✅ Verifying servers..."
curl -s http://${MAC1_IP}:5001/health && echo "✅ Mac Studio 1 (Gemma) is up" || echo "⚠️  Mac Studio 1 still loading..."
curl -s http://${MAC2_IP}:5002/health && echo "✅ Mac Studio 2 (Qwen) is up" || echo "⚠️  Mac Studio 2 still loading..."

echo ""
echo "🎉 Done! Now restart Streamlit:"
echo "   streamlit run app.py"
