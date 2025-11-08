#!/bin/bash
# Start Qwen Prefill Server on DGX Spark 1
# Run this on DGX Spark 1 (169.254.150.103)

echo "🖥️ Starting Qwen Prefill Server on DGX Spark 1..."
echo "📡 Port: 8000"
echo "🎯 Purpose: Code Analysis Prefill"
echo ""

cd "$(dirname "$0")"
python3 qwen_prefill_server_dgx.py
