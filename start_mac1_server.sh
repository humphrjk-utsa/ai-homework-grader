#!/bin/bash
# Mac Studio 1 - Qwen Coder Server Startup
echo "🖥️ Starting Qwen Coder Server on Mac Studio 1..."
echo "📡 Server will be available at: http://10.55.0.1:5001"

cd "$(dirname "$0")"
export PYTHONPATH="$PWD:$PYTHONPATH"

python servers/qwen_server.py
