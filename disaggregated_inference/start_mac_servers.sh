#!/bin/bash
# Start decode servers on Mac Studios

echo "🚀 Starting Mac Decode Servers"
echo "==============================="

# Create logs directory
mkdir -p ~/logs

# Mac Studio 1 - Qwen 3 Coder 30B
echo ""
echo "📡 Starting Mac Studio 1 (Qwen 3 Coder)..."
nohup python3 disaggregated_inference/decode_server_mac.py \
    --model ~/models/fp4/qwen3-coder-30b-fp4 \
    --host 169.254.150.101 \
    --port 8001 \
    > ~/logs/decode_qwen.log 2>&1 &
echo "Qwen decode server started on 169.254.150.101:8001"

# Mac Studio 2 - GPT-OSS 120B
echo ""
echo "📡 Starting Mac Studio 2 (GPT-OSS)..."
ssh humphrjk@169.254.150.102 "
    mkdir -p ~/logs &&
    nohup python3 ~/disaggregated_inference/decode_server_mac.py \
        --model ~/models/fp4/gpt-oss-120b-fp4 \
        --host 169.254.150.102 \
        --port 8001 \
        > ~/logs/decode_gpt_oss.log 2>&1 &
    echo 'GPT-OSS decode server started on 169.254.150.102:8001'
"

echo ""
echo "⏳ Waiting for servers to start..."
sleep 15

echo ""
echo "🔍 Checking server status..."

# Check Mac Studio 1
echo "Mac Studio 1 (Qwen):"
curl -s http://169.254.150.101:8001/health | python3 -m json.tool || echo "  ❌ Not responding"

echo ""
echo "Mac Studio 2 (GPT-OSS):"
curl -s http://169.254.150.102:8001/health | python3 -m json.tool || echo "  ❌ Not responding"

echo ""
echo "==============================="
echo "✅ Mac decode servers started!"
echo ""
echo "📝 Next steps:"
echo "1. Test orchestrator: python3 disaggregated_inference/orchestrator.py"
echo "2. Run benchmarks: ./benchmarks/run_dgx_benchmarks.sh"
echo ""
echo "📊 Monitor logs:"
echo "  Mac 1: tail -f ~/logs/decode_qwen.log"
echo "  Mac 2: ssh humphrjk@169.254.150.102 'tail -f ~/logs/decode_gpt_oss.log'"
