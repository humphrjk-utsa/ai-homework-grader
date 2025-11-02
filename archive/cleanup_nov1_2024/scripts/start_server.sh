#!/bin/bash
# Mac Studio 1 - Start Qwen Coder Server
echo "🚀 Starting Qwen Coder Server on Mac Studio 1..."
echo "📡 Server will be available at: http://10.55.0.1:5001"
echo "Press Ctrl+C to stop"

export PYTHONPATH="$PWD:$PYTHONPATH"
python3 servers/qwen_server.py
