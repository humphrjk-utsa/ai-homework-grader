#!/bin/bash
# Start prefill servers on DGX Sparks using Ollama

echo "🚀 Starting DGX Prefill Servers (Ollama)"
echo "========================================"

# DGX Spark 1 - Qwen 3 Coder (Q8)
echo ""
echo "📡 Starting DGX Spark 1 (Qwen 3 Coder 30B)..."
ssh humphrjk@169.254.150.103 "
    mkdir -p ~/logs &&
    nohup python3 ~/disaggregated_inference/prefill_server_ollama.py \
        --model qwen3-coder:30b \
        --host 169.254.150.103 \
        --port 8000 \
        > ~/logs/prefill_qwen.log 2>&1 &
    echo 'Qwen prefill server started on 169.254.150.103:8000'
"

# DGX Spark 2 - GPT-OSS 120B (Q4)
echo ""
echo "📡 Starting DGX Spark 2 (GPT-OSS 120B Q4)..."
ssh humphrjk@169.254.150.104 "
    mkdir -p ~/logs &&
    nohup python3 ~/disaggregated_inference/prefill_server_ollama.py \
        --model gpt-oss:120b \
        --host 169.254.150.104 \
        --port 8000 \
        > ~/logs/prefill_gpt_oss.log 2>&1 &
    echo 'GPT-OSS prefill server started on 169.254.150.104:8000'
"

echo ""
echo "⏳ Waiting for servers to start..."
sleep 5

echo ""
echo "🔍 Checking server status..."

# Check DGX Spark 1
echo "DGX Spark 1 (Qwen 3 Coder 30B):"
curl -s http://169.254.150.103:8000/health | python3 -m json.tool || echo "  ❌ Not responding"

echo ""
echo "DGX Spark 2 (GPT-OSS Q4):"
curl -s http://169.254.150.104:8000/health | python3 -m json.tool || echo "  ❌ Not responding"

echo ""
echo "========================================"
echo "✅ DGX prefill servers started!"
echo ""
echo "📝 Next steps:"
echo "1. Start Mac decode servers: ./disaggregated_inference/start_mac_servers_ollama.sh"
echo "2. Test orchestrator: python3 disaggregated_inference/test_system.py"
echo ""
echo "📊 Monitor logs:"
echo "  DGX 1: ssh humphrjk@169.254.150.103 'tail -f ~/logs/prefill_qwen.log'"
echo "  DGX 2: ssh humphrjk@169.254.150.104 'tail -f ~/logs/prefill_gpt_oss.log'"
