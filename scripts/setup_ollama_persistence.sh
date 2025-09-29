#!/bin/bash

# Setup script for keeping Ollama models loaded on Mac Ultra M3
# With 512GB RAM, we can easily keep the 120B model loaded

echo "🚀 Setting up Ollama for persistent model loading..."

# Set environment variable to keep models loaded for 24 hours
export OLLAMA_KEEP_ALIVE=24h

# Alternative: Keep loaded indefinitely (until manual unload)
# export OLLAMA_KEEP_ALIVE=-1

echo "✅ OLLAMA_KEEP_ALIVE set to 24h"

# Check if Ollama is running
if pgrep -x "ollama" > /dev/null; then
    echo "📋 Ollama is running"
else
    echo "⚠️  Ollama is not running. Starting Ollama with persistence settings..."
    # Start Ollama with the environment variable
    OLLAMA_KEEP_ALIVE=24h ollama serve &
    sleep 3
fi

# Load the model to keep it in memory
echo "🔥 Loading gpt-oss:120b into memory..."
ollama run gpt-oss:120b "Ready for grading" --verbose

echo "✅ Setup complete! Model should stay loaded for 24 hours."
echo "💡 To make this permanent, add 'export OLLAMA_KEEP_ALIVE=24h' to your ~/.zshrc"