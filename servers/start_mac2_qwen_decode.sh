#!/bin/bash
# Start Qwen Decode Server on Mac Studio 2
# Run this on Mac Studio 2 (169.254.150.102)

echo "🖥️ Starting Qwen Decode Server on Mac Studio 2..."
echo "📡 Port: 5002"
echo "🎯 Purpose: Code Analysis Decode"
echo ""

cd "$(dirname "$0")"
python3 qwen_server.py
