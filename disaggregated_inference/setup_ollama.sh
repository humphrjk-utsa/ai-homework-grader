#!/bin/bash
# Setup Ollama on all machines

echo "🔧 Setting up Ollama on all machines"
echo "====================================="

# Mac Studio 1 (local) - Already has Ollama, just pull models
echo ""
echo "📡 Mac Studio 1 (local) - Pulling models..."
echo "  Pulling qwen2.5-coder:32b..."
ollama pull qwen2.5-coder:32b &
PID1=$!

echo "  Pulling gpt-oss:120b..."
ollama pull gpt-oss:120b &
PID2=$!

# DGX Spark 2 - Install Ollama
echo ""
echo "📡 DGX Spark 2 - Installing Ollama..."
ssh humphrjk@169.254.150.104 "
    echo 'Installing Ollama...'
    curl -fsSL https://ollama.com/install.sh | sh
    echo 'Ollama installed!'
"

# Mac Studio 2 - Install Ollama
echo ""
echo "📡 Mac Studio 2 - Installing Ollama..."
ssh humphrjk@169.254.150.102 "
    echo 'Installing Ollama...'
    curl -fsSL https://ollama.com/install.sh | sh
    echo 'Ollama installed!'
"

# Wait for Mac Studio 1 pulls to complete
echo ""
echo "⏳ Waiting for Mac Studio 1 model pulls to complete..."
wait $PID1
echo "  ✅ qwen2.5-coder:32b downloaded"
wait $PID2
echo "  ✅ gpt-oss:120b downloaded"

# Pull models on DGX Spark 2
echo ""
echo "📡 DGX Spark 2 - Pulling models..."
ssh humphrjk@169.254.150.104 "
    echo 'Pulling qwen2.5-coder:32b...'
    ollama pull qwen2.5-coder:32b &
    echo 'Pulling gpt-oss:120b...'
    ollama pull gpt-oss:120b &
    wait
    echo 'Models downloaded!'
"

# Pull models on Mac Studio 2
echo ""
echo "📡 Mac Studio 2 - Pulling models..."
ssh humphrjk@169.254.150.102 "
    echo 'Pulling qwen2.5-coder:32b...'
    ollama pull qwen2.5-coder:32b &
    echo 'Pulling gpt-oss:120b...'
    ollama pull gpt-oss:120b &
    wait
    echo 'Models downloaded!'
"

echo ""
echo "====================================="
echo "✅ Ollama setup complete!"
echo ""
echo "📝 Verify with:"
echo "  ollama list"
echo "  ssh humphrjk@169.254.150.103 'ollama list'"
echo "  ssh humphrjk@169.254.150.104 'ollama list'"
echo "  ssh humphrjk@169.254.150.102 'ollama list'"
