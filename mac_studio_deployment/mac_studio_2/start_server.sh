#!/bin/bash
# Mac Studio 2 - Start Gemma Server
echo "🚀 Starting Gemma Server on Mac Studio 2..."
echo "📡 Server will be available at: http://10.55.0.2:5002"
echo "Press Ctrl+C to stop"

export PYTHONPATH="$PWD:$PYTHONPATH"
python3 servers/gemma_server.py
