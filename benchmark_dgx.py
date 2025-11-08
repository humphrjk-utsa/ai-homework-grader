#!/usr/bin/env python3
"""
Quick ML/Neural Network Benchmark for DGX Sparks
Tests GPU performance with PyTorch
"""

import torch
import time
import sys

def benchmark_gpu():
    """Benchmark GPU performance"""
    
    print("="*80)
    print("DGX GPU BENCHMARK")
    print("="*80)
    
    # Check CUDA availability
    if not torch.cuda.is_available():
        print("❌ CUDA not available!")
        return
    
    device = torch.device("cuda")
    print(f"✅ CUDA available")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"PyTorch Version: {torch.__version__}")
    print()
    
    # Test 1: Matrix Multiplication
    print("Test 1: Large Matrix Multiplication")
    print("-" * 80)
    sizes = [1000, 5000, 10000]
    
    for size in sizes:
        # Create random matrices
        a = torch.randn(size, size, device=device)
        b = torch.randn(size, size, device=device)
        
        # Warm up
        _ = torch.matmul(a, b)
        torch.cuda.synchronize()
        
        # Benchmark
        start = time.time()
        for _ in range(10):
            c = torch.matmul(a, b)
        torch.cuda.synchronize()
        elapsed = time.time() - start
        
        gflops = (2 * size**3 * 10) / (elapsed * 1e9)
        print(f"  {size}x{size}: {elapsed/10:.4f}s per matmul, {gflops:.2f} GFLOPS")
    
    print()
    
    # Test 2: Neural Network Training
    print("Test 2: Simple Neural Network Training")
    print("-" * 80)
    
    # Create a simple model
    model = torch.nn.Sequential(
        torch.nn.Linear(1000, 5000),
        torch.nn.ReLU(),
        torch.nn.Linear(5000, 5000),
        torch.nn.ReLU(),
        torch.nn.Linear(5000, 1000),
    ).to(device)
    
    optimizer = torch.optim.Adam(model.parameters())
    criterion = torch.nn.MSELoss()
    
    # Create dummy data
    batch_size = 128
    x = torch.randn(batch_size, 1000, device=device)
    y = torch.randn(batch_size, 1000, device=device)
    
    # Warm up
    for _ in range(5):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
    
    torch.cuda.synchronize()
    
    # Benchmark
    iterations = 100
    start = time.time()
    
    for _ in range(iterations):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
    
    torch.cuda.synchronize()
    elapsed = time.time() - start
    
    print(f"  {iterations} training iterations: {elapsed:.2f}s")
    print(f"  {iterations/elapsed:.2f} iterations/sec")
    print(f"  {elapsed/iterations*1000:.2f}ms per iteration")
    
    print()
    
    # Test 3: Memory Bandwidth
    print("Test 3: GPU Memory Bandwidth")
    print("-" * 80)
    
    # Test different sizes
    for size_mb in [100, 500, 1000, 5000]:
        elements = (size_mb * 1024 * 1024) // 4  # 4 bytes per float32
        
        a = torch.randn(elements, device=device)
        b = torch.randn(elements, device=device)
        
        # Warm up
        _ = a + b
        torch.cuda.synchronize()
        
        # Benchmark
        start = time.time()
        for _ in range(100):
            c = a + b
        torch.cuda.synchronize()
        elapsed = time.time() - start
        
        bandwidth_gb = (size_mb * 2 * 100) / (elapsed * 1024)  # Read A + B
        print(f"  {size_mb}MB: {bandwidth_gb:.2f} GB/s")
    
    print()
    
    # GPU Info
    print("GPU Memory Info")
    print("-" * 80)
    print(f"  Total Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print(f"  Allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
    print(f"  Cached: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
    
    print()
    print("="*80)
    print("BENCHMARK COMPLETE")
    print("="*80)

if __name__ == "__main__":
    try:
        benchmark_gpu()
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
