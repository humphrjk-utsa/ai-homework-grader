#!/bin/bash
# Start prefill servers on DGX Sparks

echo "🚀 Starting DGX Prefill Servers"
echo "================================"

# DGX Spark 1 - Qwen 3 Coder 30B
echo ""
echo "📡 Starting DGX Spark 1 (Qwen 3 Coder)..."
ssh humphrjk@169.254.150.103 "
    cd ~/models/fp4/qwen3-coder-30b-fp4 &&
    mkdir -p ~/logs &&
    nohup python3 ~/disaggregated_inference/prefill_server_dgx.py \
        --model . \
        --host 169.254.150.103 \
        --port 8000 \
        > ~/logs/prefill_qwen.log 2>&1 &
    echo 'Qwen prefill server started on 169.254.150.103:8000'
"

# DGX Spark 2 - GPT-OSS 120B  
echo ""
echo "📡 Starting DGX Spark 2 (GPT-OSS)..."
ssh humphrjk@169.254.150.104 "
    cd ~/models/fp4/gpt-oss-120b-fp4 &&
    mkdir -p ~/logs &&
    nohup python3 ~/disaggregated_inference/prefill_server_dgx.py \
        --model . \
        --host 169.254.150.104 \
        --port 8000 \
        > ~/logs/prefill_gpt_oss.log 2>&1 &
    echo 'GPT-OSS prefill server started on 169.254.150.104:8000'
"

echo ""
echo "⏳ Waiting for servers to start..."
sleep 10

echo ""
echo "🔍 Checking server status..."

# Check DGX Spark 1
echo "DGX Spark 1 (Qwen):"
curl -s http://169.254.150.103:8000/health | python3 -m json.tool || echo "  ❌ Not responding"

echo ""
echo "DGX Spark 2 (GPT-OSS):"
curl -s http://169.254.150.104:8000/health | python3 -m json.tool || echo "  ❌ Not responding"

echo ""
echo "================================"
echo "✅ DGX prefill servers started!"
echo ""
echo "📝 Next steps:"
echo "1. Start Mac decode servers: ./disaggregated_inference/start_mac_servers.sh"
echo "2. Test orchestrator: python3 disaggregated_inference/orchestrator.py"
echo ""
echo "📊 Monitor logs:"
echo "  DGX 1: ssh humphrjk@169.254.150.103 'tail -f ~/logs/prefill_qwen.log'"
echo "  DGX 2: ssh humphrjk@169.254.150.104 'tail -f ~/logs/prefill_gpt_oss.log'"
