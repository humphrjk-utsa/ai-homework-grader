#!/bin/bash
# Run DGX Spark benchmarks in sequence

echo "🚀 DGX SPARK BENCHMARK SUITE"
echo "="*80

# 1. Single GPU benchmark
echo ""
echo "📊 Step 1: Single GPU Benchmark"
echo "Testing individual GPU performance..."
python3 benchmarks/dgx_spark_ml_benchmark.py

# 2. Single GPU distributed mode (baseline)
echo ""
echo "📊 Step 2: Single GPU (Distributed Mode)"
echo "Testing distributed framework overhead..."
python3 benchmarks/dgx_distributed_benchmark.py --mode single

# 3. Multi-GPU distributed (if available)
NUM_GPUS=$(python3 -c "import torch; print(torch.cuda.device_count())")
echo ""
echo "📊 Step 3: Distributed Training ($NUM_GPUS GPUs)"
echo "Testing cluster performance over ConnectX-7..."
python3 benchmarks/dgx_distributed_benchmark.py --mode distributed --gpus $NUM_GPUS

echo ""
echo "="*80
echo "✅ All benchmarks complete!"
echo "📁 Results saved to:"
echo "   - dgx_spark_benchmark_results.json"
echo "   - dgx_distributed_benchmark_${NUM_GPUS}gpu.json"
