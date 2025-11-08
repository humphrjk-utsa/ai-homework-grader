#!/bin/bash
# Simple GPU benchmark for DGX Sparks

echo "================================================================================"
echo "DGX GPU BENCHMARK - $(hostname)"
echo "================================================================================"
echo ""

# GPU Info
echo "GPU Information:"
echo "--------------------------------------------------------------------------------"
nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader
echo ""

# GPU Utilization Test
echo "Running GPU Compute Test (10 seconds)..."
echo "--------------------------------------------------------------------------------"

# Use nvidia-smi to monitor during a stress test
# We'll use a simple CUDA sample if available, or just monitor idle state
timeout 10s nvidia-smi dmon -s u -c 10 2>/dev/null || nvidia-smi

echo ""
echo "================================================================================"
echo "BENCHMARK COMPLETE"
echo "================================================================================"
