#!/bin/bash
# Mac Studio 2 - Gemma Server Startup
echo "🖥️ Starting Gemma Server on Mac Studio 2..."
echo "📡 Server will be available at: http://10.55.0.2:5002"

cd "$(dirname "$0")"
export PYTHONPATH="$PWD:$PYTHONPATH"

python servers/gemma_server.py
