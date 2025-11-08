#!/bin/bash
# Stop all disaggregated inference servers

echo "🛑 Stopping All Servers"
echo "======================="

# Stop DGX prefill servers
echo ""
echo "Stopping DGX Spark 1 (Qwen)..."
ssh humphrjk@169.254.150.103 "pkill -f 'prefill_server_dgx.py.*8000'"

echo "Stopping DGX Spark 2 (GPT-OSS)..."
ssh humphrjk@169.254.150.104 "pkill -f 'prefill_server_dgx.py.*8000'"

# Stop Mac decode servers
echo ""
echo "Stopping Mac Studio 1 (Qwen)..."
pkill -f 'decode_server_mac.py.*8001'

echo "Stopping Mac Studio 2 (GPT-OSS)..."
ssh humphrjk@169.254.150.102 "pkill -f 'decode_server_mac.py.*8001'"

echo ""
echo "======================="
echo "✅ All servers stopped!"
