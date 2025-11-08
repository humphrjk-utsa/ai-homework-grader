#!/bin/bash
# Distribute FP4 models from Mac Studio 1 to all cluster machines

SOURCE_DIR=~/models/fp4/
TOTAL_SIZE="80GB"

echo "="*80
echo "🚀 DISTRIBUTING FP4 MODELS ACROSS CLUSTER"
echo "="*80
echo "Source: Mac Studio 1 (this machine)"
echo "Models: Qwen 3 Coder 30B FP4 (17GB) + GPT-OSS 120B FP4 (63GB)"
echo "Total size: $TOTAL_SIZE"
echo ""

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source directory not found: $SOURCE_DIR"
    exit 1
fi

echo "📁 Source directory: $SOURCE_DIR"
echo ""

# Define target machines
# Format: "name:user@host:path"
# Network topology:
# - Mac Studio 1: 169.254.150.101 (has models)
# - Mac Studio 2: 169.254.150.102 (has models)
# - DGX Spark 1: 169.254.150.103
# - DGX Spark 2: 169.254.150.104
TARGETS=(
    "DGX Spark 1:humphrjk@169.254.150.103:~/models/fp4/"
    "DGX Spark 2:humphrjk@169.254.150.104:~/models/fp4/"
)

echo "🎯 Target machines:"
for target in "${TARGETS[@]}"; do
    name=$(echo $target | cut -d: -f1)
    echo "  • $name"
done
echo ""

read -p "Continue with distribution? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Distribution cancelled"
    exit 0
fi

echo ""
echo "🚀 Starting distribution..."
echo ""

# Distribute to each target
for target in "${TARGETS[@]}"; do
    name=$(echo $target | cut -d: -f1)
    host=$(echo $target | cut -d: -f2)
    dest=$(echo $target | cut -d: -f3)
    
    echo "="*80
    echo "📤 Distributing to: $name ($host)"
    echo "="*80
    
    # Create destination directory
    echo "Creating destination directory..."
    ssh $host "mkdir -p $dest" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: Could not create directory on $name"
        echo "   Trying to continue anyway..."
    fi
    
    # Rsync with progress
    echo "Transferring files..."
    rsync -avz --progress \
        --stats \
        $SOURCE_DIR \
        $host:$dest
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully distributed to $name"
    else
        echo "❌ Failed to distribute to $name"
    fi
    
    echo ""
done

echo "="*80
echo "📊 DISTRIBUTION SUMMARY"
echo "="*80
echo "Checking models on each machine..."
echo ""

# Verify on each machine
for target in "${TARGETS[@]}"; do
    name=$(echo $target | cut -d: -f1)
    host=$(echo $target | cut -d: -f2)
    dest=$(echo $target | cut -d: -f3)
    
    echo "🔍 $name:"
    ssh $host "du -sh $dest* 2>/dev/null" || echo "  ⚠️  Could not verify"
    echo ""
done

echo "="*80
echo "✅ Distribution complete!"
echo ""
echo "📝 Next steps:"
echo "1. Verify models on each machine"
echo "2. Set up disaggregated inference servers"
echo "3. Configure prefill (DGX) and decode (Mac) endpoints"
echo "="*80
