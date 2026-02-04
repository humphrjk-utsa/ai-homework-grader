#!/usr/bin/env bash
# Quick setup using EXISTING models on DGX Sparks

set -e

echo "════════════════════════════════════════════════════════════════════"
echo "QUICK SETUP: Using Existing Models"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Found models on DGX
QWEN_DGX3="/home/humphrjk/models/qwen3-coder-30b-q8.gguf"
GPT_OSS_DGX4="/home/humphrjk/models/gpt-oss-120b-q8.gguf"

echo "Found models:"
echo "  ✓ DGX Spark 3: $QWEN_DGX3"
echo "  ✓ DGX Spark 4: $GPT_OSS_DGX4"
echo ""

# Install llama-cpp-python on all machines
echo "Installing llama-cpp-python on all machines..."
echo ""

# Mac Studio 2 (Qwen decode)
echo "Mac Studio 2 (169.254.150.102):"
ssh humphrjk@169.254.150.102 "CMAKE_ARGS='-DLLAMA_METAL=on' pip3 install --upgrade llama-cpp-python" && echo "  ✓ Installed" || echo "  ✗ Failed"

# Mac Studio 1 (GPT-OSS decode) - has SSH key issue
echo "Mac Studio 1 (169.254.150.101):"
echo "  Skipping - SSH key verification issue. Fix with: ssh-keyscan 169.254.150.101 >> ~/.ssh/known_hosts"

# DGX Spark 3 (Qwen prefill)
echo "DGX Spark 3 (169.254.150.105):"
ssh humphrjk@169.254.150.105 "CMAKE_ARGS='-DLLAMA_CUBLAS=on' pip3 install --upgrade llama-cpp-python" && echo "  ✓ Installed" || echo "  ✗ Failed"

# DGX Spark 4 (GPT-OSS prefill)
echo "DGX Spark 4 (169.254.150.106):"
ssh humphrjk@169.254.150.106 "CMAKE_ARGS='-DLLAMA_CUBLAS=on' pip3 install --upgrade llama-cpp-python" && echo "  ✓ Installed" || echo "  ✗ Failed"

echo ""
echo "Copying models to Mac Studios..."
echo ""

# Copy Qwen to Mac Studio 2
echo "Copying Qwen to Mac Studio 2..."
ssh humphrjk@169.254.150.102 "mkdir -p ~/models/gguf"
scp humphrjk@169.254.150.105:$QWEN_DGX3 humphrjk@169.254.150.102:~/models/gguf/ && echo "  ✓ Copied" || echo "  ✗ Failed"

# Copy GPT-OSS to Mac Studio 1 (skip due to SSH issue)
echo "Mac Studio 1: Skipping due to SSH issue"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "SETUP COMPLETE"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Models configured:"
echo "  Pair 1 (Qwen):"
echo "    DGX Spark 3: $QWEN_DGX3"
echo "    Mac Studio 2: ~/models/gguf/qwen3-coder-30b-q8.gguf"
echo ""
echo "  Pair 2 (GPT-OSS):"  
echo "    DGX Spark 4: $GPT_OSS_DGX4"
echo "    Mac Studio 1: (manual copy needed)"
echo ""
echo "Next: Update server scripts to use these exact paths"
echo ""
