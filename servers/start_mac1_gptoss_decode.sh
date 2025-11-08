#!/bin/bash
# Start GPT-OSS Decode Server on Mac Studio 1
# Run this on Mac Studio 1 (169.254.150.101)

echo "🖥️ Starting GPT-OSS Decode Server on Mac Studio 1..."
echo "📡 Port: 8003 (Decode endpoint for disaggregated inference)"
echo "🎯 Purpose: Feedback Generation Decode"
echo ""

cd "$(dirname "$0")"
python3 gpt_oss_server_working.py --decode-port
