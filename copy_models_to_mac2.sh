#!/bin/bash
# Copy MLX models from Mac Studio 1 to Mac Studio 2
echo "📦 Copying MLX Models to Mac Studio 2"
echo "====================================="

# Source and destination paths
SOURCE_CACHE="$HOME/.cache/huggingface/hub/"
DEST_USER="jamiehumphries"
DEST_IP="10.55.0.2"
DEST_CACHE="/Users/$DEST_USER/.cache/huggingface/hub/"

# Models to copy
QWEN_MODEL="models--mlx-community--Qwen3-Coder-30B-A3B-Instruct-bf16"
GEMMA_MODEL="models--mlx-community--gemma-3-27b-it-bf16"

echo "🔍 Checking models on Mac Studio 1..."
if [ -d "$SOURCE_CACHE$QWEN_MODEL" ]; then
    echo "✅ Found Qwen model: $QWEN_MODEL"
else
    echo "❌ Qwen model not found"
fi

if [ -d "$SOURCE_CACHE$GEMMA_MODEL" ]; then
    echo "✅ Found Gemma model: $GEMMA_MODEL"
else
    echo "❌ Gemma model not found"
fi

echo ""
echo "📡 Creating cache directory on Mac Studio 2..."
ssh $DEST_USER@$DEST_IP "mkdir -p $DEST_CACHE"

echo ""
echo "📤 Copying Qwen model to Mac Studio 2..."
echo "   This may take several minutes (~60GB)..."
rsync -av --progress "$SOURCE_CACHE$QWEN_MODEL/" "$DEST_USER@$DEST_IP:$DEST_CACHE$QWEN_MODEL/"

if [ $? -eq 0 ]; then
    echo "✅ Qwen model copied successfully!"
else
    echo "❌ Qwen model copy failed"
fi

echo ""
echo "📤 Copying Gemma model to Mac Studio 2..."
echo "   This may take several minutes (~54GB)..."
rsync -av --progress "$SOURCE_CACHE$GEMMA_MODEL/" "$DEST_USER@$DEST_IP:$DEST_CACHE$GEMMA_MODEL/"

if [ $? -eq 0 ]; then
    echo "✅ Gemma model copied successfully!"
else
    echo "❌ Gemma model copy failed"
fi

echo ""
echo "🔍 Verifying models on Mac Studio 2..."
ssh $DEST_USER@$DEST_IP "ls -la $DEST_CACHE | grep -E '(gemma-3-27b-it-bf16|Qwen3-Coder-30B-A3B-Instruct-bf16)'"

echo ""
echo "🎉 Model copying complete!"
echo "💡 Models are now available locally on both Mac Studios"
echo "💡 No internet download required for model loading"