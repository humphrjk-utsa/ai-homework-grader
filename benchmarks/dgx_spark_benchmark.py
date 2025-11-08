#!/usr/bin/env python3
"""
DGX Spark Benchmark Suite
Tests ML training and LLM text generation performance
"""

import torch
import time
import json
from datetime import datetime
from pathlib import Path

# Check GPU availability
print("="*80)
print("DGX SPARK BENCHMARK SUITE")
print("="*80)
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"    Memory: {torch.cuda.get_device_properties(i).total_memory / 1e9:.1f} GB")
print("="*80)

results = {
    "timestamp": datetime.now().isoformat(),
    "system": "DGX Spark",
    "pytorch_version": torch.__version__,
    "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
    "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    "benchmarks": {}
}

# ============================================================================
# BENCHMARK 1: Matrix Multiplication (GPU Compute)
# ============================================================================
def benchmark_matmul(size=8192, iterations=100):
    """Test raw GPU compute with large matrix multiplication"""
    print("\n[BENCHMARK 1: Matrix Multiplication]")
    print(f"Matrix size: {size}x{size}")
    print(f"Iterations: {iterations}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Create random matrices
    A = torch.randn(size, size, device=device)
    B = torch.randn(size, size, device=device)
    
    # Warmup
    for _ in range(10):
        C = torch.matmul(A, B)
    
    torch.cuda.synchronize()
    
    # Benchmark
    start = time.time()
    for _ in range(iterations):
        C = torch.matmul(A, B)
    torch.cuda.synchronize()
    elapsed = time.time() - start
    
    tflops = (2 * size**3 * iterations) / elapsed / 1e12
    
    print(f"✅ Time: {elapsed:.2f}s")
    print(f"✅ Performance: {tflops:.2f} TFLOPS")
    
    return {
        "matrix_size": size,
        "iterations": iterations,
        "time_seconds": elapsed,
        "tflops": tflops
    }

# ============================================================================
# BENCHMARK 2: CNN Training (ML Workload)
# ============================================================================
def benchmark_cnn_training(batch_size=128, iterations=100):
    """Test ML training with ResNet-like CNN"""
    print("\n[BENCHMARK 2: CNN Training]")
    print(f"Batch size: {batch_size}")
    print(f"Iterations: {iterations}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Simple ResNet-like model
    model = torch.nn.Sequential(
        torch.nn.Conv2d(3, 64, 7, stride=2, padding=3),
        torch.nn.BatchNorm2d(64),
        torch.nn.ReLU(),
        torch.nn.MaxPool2d(3, stride=2, padding=1),
        torch.nn.Conv2d(64, 128, 3, padding=1),
        torch.nn.BatchNorm2d(128),
        torch.nn.ReLU(),
        torch.nn.Conv2d(128, 256, 3, padding=1),
        torch.nn.BatchNorm2d(256),
        torch.nn.ReLU(),
        torch.nn.AdaptiveAvgPool2d((1, 1)),
        torch.nn.Flatten(),
        torch.nn.Linear(256, 1000)
    ).to(device)
    
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    criterion = torch.nn.CrossEntropyLoss()
    
    # Dummy data
    images = torch.randn(batch_size, 3, 224, 224, device=device)
    labels = torch.randint(0, 1000, (batch_size,), device=device)
    
    # Warmup
    for _ in range(10):
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    
    torch.cuda.synchronize()
    
    # Benchmark
    start = time.time()
    for _ in range(iterations):
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    torch.cuda.synchronize()
    elapsed = time.time() - start
    
    images_per_sec = (batch_size * iterations) / elapsed
    
    print(f"✅ Time: {elapsed:.2f}s")
    print(f"✅ Throughput: {images_per_sec:.1f} images/sec")
    
    return {
        "batch_size": batch_size,
        "iterations": iterations,
        "time_seconds": elapsed,
        "images_per_second": images_per_sec
    }

# ============================================================================
# BENCHMARK 3: Transformer Inference (LLM-like)
# ============================================================================
def benchmark_transformer_inference(seq_len=2048, batch_size=8, iterations=50):
    """Test transformer inference (simulates LLM prefill)"""
    print("\n[BENCHMARK 3: Transformer Inference]")
    print(f"Sequence length: {seq_len}")
    print(f"Batch size: {batch_size}")
    print(f"Iterations: {iterations}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Transformer encoder (simulates LLM layer)
    d_model = 4096
    nhead = 32
    num_layers = 4
    
    encoder_layer = torch.nn.TransformerEncoderLayer(
        d_model=d_model,
        nhead=nhead,
        dim_feedforward=d_model * 4,
        batch_first=True
    )
    model = torch.nn.TransformerEncoder(encoder_layer, num_layers=num_layers).to(device)
    model.eval()
    
    # Dummy input
    src = torch.randn(batch_size, seq_len, d_model, device=device)
    
    # Warmup
    with torch.no_grad():
        for _ in range(10):
            output = model(src)
    
    torch.cuda.synchronize()
    
    # Benchmark
    start = time.time()
    with torch.no_grad():
        for _ in range(iterations):
            output = model(src)
    torch.cuda.synchronize()
    elapsed = time.time() - start
    
    tokens_per_sec = (batch_size * seq_len * iterations) / elapsed
    
    print(f"✅ Time: {elapsed:.2f}s")
    print(f"✅ Throughput: {tokens_per_sec:.1f} tokens/sec")
    print(f"✅ Latency: {elapsed/iterations*1000:.1f} ms/batch")
    
    return {
        "sequence_length": seq_len,
        "batch_size": batch_size,
        "iterations": iterations,
        "time_seconds": elapsed,
        "tokens_per_second": tokens_per_sec,
        "latency_ms": elapsed/iterations*1000
    }

# ============================================================================
# BENCHMARK 4: Memory Bandwidth
# ============================================================================
def benchmark_memory_bandwidth(size_gb=10):
    """Test GPU memory bandwidth"""
    print("\n[BENCHMARK 4: Memory Bandwidth]")
    print(f"Data size: {size_gb} GB")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Create large tensor
    size = int(size_gb * 1e9 / 4)  # 4 bytes per float32
    data = torch.randn(size, device=device)
    
    # Warmup
    for _ in range(5):
        result = data * 2.0
    
    torch.cuda.synchronize()
    
    # Benchmark
    iterations = 20
    start = time.time()
    for _ in range(iterations):
        result = data * 2.0
    torch.cuda.synchronize()
    elapsed = time.time() - start
    
    bandwidth_gbps = (size_gb * 2 * iterations) / elapsed  # Read + Write
    
    print(f"✅ Time: {elapsed:.2f}s")
    print(f"✅ Bandwidth: {bandwidth_gbps:.1f} GB/s")
    
    return {
        "data_size_gb": size_gb,
        "iterations": iterations,
        "time_seconds": elapsed,
        "bandwidth_gbps": bandwidth_gbps
    }

# ============================================================================
# Run all benchmarks
# ============================================================================
def run_all_benchmarks():
    """Run complete benchmark suite"""
    
    if not torch.cuda.is_available():
        print("\n❌ CUDA not available! Benchmarks require GPU.")
        return
    
    print("\n🚀 Starting benchmark suite...")
    
    try:
        results["benchmarks"]["matmul"] = benchmark_matmul()
    except Exception as e:
        print(f"❌ Matrix multiplication failed: {e}")
    
    try:
        results["benchmarks"]["cnn_training"] = benchmark_cnn_training()
    except Exception as e:
        print(f"❌ CNN training failed: {e}")
    
    try:
        results["benchmarks"]["transformer_inference"] = benchmark_transformer_inference()
    except Exception as e:
        print(f"❌ Transformer inference failed: {e}")
    
    try:
        results["benchmarks"]["memory_bandwidth"] = benchmark_memory_bandwidth()
    except Exception as e:
        print(f"❌ Memory bandwidth failed: {e}")
    
    # Save results
    output_dir = Path("benchmarks/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"dgx_spark_benchmark_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*80)
    print("BENCHMARK COMPLETE")
    print("="*80)
    print(f"Results saved to: {output_file}")
    print("\nSummary:")
    if "matmul" in results["benchmarks"]:
        print(f"  Matrix Multiply: {results['benchmarks']['matmul']['tflops']:.2f} TFLOPS")
    if "cnn_training" in results["benchmarks"]:
        print(f"  CNN Training: {results['benchmarks']['cnn_training']['images_per_second']:.1f} images/sec")
    if "transformer_inference" in results["benchmarks"]:
        print(f"  Transformer: {results['benchmarks']['transformer_inference']['tokens_per_second']:.1f} tokens/sec")
    if "memory_bandwidth" in results["benchmarks"]:
        print(f"  Memory Bandwidth: {results['benchmarks']['memory_bandwidth']['bandwidth_gbps']:.1f} GB/s")
    print("="*80)

if __name__ == "__main__":
    run_all_benchmarks()
