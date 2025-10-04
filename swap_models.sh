#!/bin/bash
# Automated script to swap models between Mac Studios
# Mac Studio 1: Gemma (feedback)
# Mac Studio 2: Qwen (code analysis)

set -e  # Exit on error

echo "🔄 Swapping models between Mac Studios..."
echo "================================================"
echo ""

# Configuration
MAC1_USER="user"  # Change this to your username
MAC2_USER="user"  # Change this to your username
MAC1_IP="10.55.0.1"
MAC2_IP="10.55.0.2"
MAC1_PATH="~/homework-grader"
MAC2_PATH="~/homework-grader"

# Stop servers
echo "⏹️  Step 1: Stopping current servers..."
ssh ${MAC1_USER}@${MAC1_IP} "pkill -f 'gemma_server.py|qwen_server.py' || true"
ssh ${MAC2_USER}@${MAC2_IP} "pkill -f 'gemma_server.py|qwen_server.py' || true"
echo "✅ Servers stopped"
sleep 2

# Copy updated configs
echo ""
echo "📋 Step 2: Updating configurations..."
scp mac_studio_deployment/mac_studio_1/distributed_config.json ${MAC1_USER}@${MAC1_IP}:${MAC1_PATH}/
scp mac_studio_deployment/mac_studio_2/distributed_config.json ${MAC2_USER}@${MAC2_IP}:${MAC2_PATH}/
echo "✅ Configurations updated"

# Start Mac Studio 1 with Gemma (feedback generation)
echo ""
echo "🚀 Step 3: Starting Mac Studio 1 with Gemma (feedback)..."
ssh ${MAC1_USER}@${MAC1_IP} "cd ${MAC1_PATH}/mac_studio_deployment/mac_studio_1/servers && nohup python gemma_server.py > gemma.log 2>&1 &"
echo "✅ Mac Studio 1 starting..."

# Start Mac Studio 2 with Qwen (code analysis)
echo ""
echo "🚀 Step 4: Starting Mac Studio 2 with Qwen (code analysis)..."
ssh ${MAC2_USER}@${MAC2_IP} "cd ${MAC2_PATH}/mac_studio_deployment/mac_studio_2/servers && nohup python qwen_server.py > qwen.log 2>&1 &"
echo "✅ Mac Studio 2 starting..."

# Wait for servers to initialize
echo ""
echo "⏳ Waiting for servers to initialize (30 seconds)..."
sleep 30

# Verify servers
echo ""
echo "✅ Step 5: Verifying servers..."
echo ""

if curl -s http://${MAC1_IP}:5001/health > /dev/null 2>&1; then
    echo "✅ Mac Studio 1 (Gemma) is responding at http://${MAC1_IP}:5001"
else
    echo "⚠️  Mac Studio 1 (Gemma) not responding yet - may still be loading"
fi

if curl -s http://${MAC2_IP}:5002/health > /dev/null 2>&1; then
    echo "✅ Mac Studio 2 (Qwen) is responding at http://${MAC2_IP}:5002"
else
    echo "⚠️  Mac Studio 2 (Qwen) not responding yet - may still be loading"
fi

echo ""
echo "================================================"
echo "🎉 Model swap complete!"
echo ""
echo "📱 Next steps:"
echo "   1. Restart Streamlit: pkill -f streamlit && streamlit run app.py"
echo "   2. Check sidebar shows:"
echo "      - Mac Studio 1: gemma-3-27b-it-bf16 (Feedback)"
echo "      - Mac Studio 2: Qwen3-Coder-30B (Code Analysis)"
echo ""
echo "💡 If servers aren't responding, wait 1-2 minutes for models to load"
echo "   Check logs: ssh user@${MAC1_IP} 'tail -f ${MAC1_PATH}/mac_studio_deployment/mac_studio_1/servers/gemma.log'"
