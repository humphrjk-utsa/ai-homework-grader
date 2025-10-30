#!/bin/bash
while true; do
    echo "Starting Qwen server at $(date)"
    python3 ~/qwen_8bit_server.py
    echo "Qwen crashed at $(date), restarting in 5 seconds..."
    sleep 5
done
