#!/bin/bash
# Start GPT-OSS Prefill Server on DGX Spark 2
# Run this on DGX Spark 2 (169.254.150.104)

echo "🖥️ Starting GPT-OSS Prefill Server on DGX Spark 2..."
echo "📡 Port: 8000"
echo "🎯 Purpose: Feedback Generation Prefill"
echo ""

cd "$(dirname "$0")"
python3 gpt_oss_prefill_server_dgx.py
