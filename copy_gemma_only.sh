#!/bin/bash
# Copy only Gemma model to Mac Studio 2 (faster)
echo "📦 Copying Gemma Model to Mac Studio 2"
echo "======================================"

# Source and destination paths
SOURCE_CACHE="$HOME/.cache/huggingface/hub/"
DEST_USER="jamiehumphries"
DEST_IP="10.55.0.2"
DEST_CACHE="/Users/$DEST_USER/.cache/huggingface/hub/"

# Only Gemma model needed on Mac Studio 2
GEMMA_MODEL="models--mlx-community--gemma-3-27b-it-bf16"

echo "🔍 Checking Gemma model on Mac Studio 1..."
if [ -d "$SOURCE_CACHE$GEMMA_MODEL" ]; then
    echo "✅ Found Gemma model: $GEMMA_MODEL"
    
    # Get model size
    MODEL_SIZE=$(du -sh "$SOURCE_CACHE$GEMMA_MODEL" | cut -f1)
    echo "📊 Model size: $MODEL_SIZE"
else
    echo "❌ Gemma model not found"
    exit 1
fi

echo ""
echo "📡 Creating cache directory on Mac Studio 2..."
ssh $DEST_USER@$DEST_IP "mkdir -p $DEST_CACHE"

echo ""
echo "📤 Copying Gemma model to Mac Studio 2..."
echo "   Size: $MODEL_SIZE - This will take a few minutes via Thunderbolt..."
echo "   Progress will be shown below:"

# Use rsync with progress and compression for faster transfer
rsync -avz --progress "$SOURCE_CACHE$GEMMA_MODEL/" "$DEST_USER@$DEST_IP:$DEST_CACHE$GEMMA_MODEL/"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Gemma model copied successfully!"
    
    # Verify on Mac Studio 2
    echo "🔍 Verifying model on Mac Studio 2..."
    ssh $DEST_USER@$DEST_IP "ls -la $DEST_CACHE$GEMMA_MODEL/"
    
    echo ""
    echo "🎉 Copy complete!"
    echo "💡 Gemma model is now available locally on Mac Studio 2"
    echo "💡 No internet download required!"
    
else
    echo "❌ Gemma model copy failed"
    exit 1
fi