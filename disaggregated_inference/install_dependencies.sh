#!/bin/bash
# Install dependencies on all machines

echo "📦 Installing Dependencies on All Machines"
echo "=========================================="

# DGX Spark 1
echo ""
echo "📡 Installing on DGX Spark 1 (169.254.150.103)..."
ssh humphrjk@169.254.150.103 "pip install flask torch transformers accelerate"

# DGX Spark 2
echo ""
echo "📡 Installing on DGX Spark 2 (169.254.150.104)..."
ssh humphrjk@169.254.150.104 "pip install flask torch transformers accelerate"

# Mac Studio 2
echo ""
echo "📡 Installing on Mac Studio 2 (169.254.150.102)..."
ssh humphrjk@169.254.150.102 "pip install flask mlx mlx-lm"

echo ""
echo "=========================================="
echo "✅ Dependencies installed!"
echo ""
echo "📝 Verify with: ./disaggregated_inference/deploy_to_machines.sh"
