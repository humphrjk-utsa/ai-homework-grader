#!/usr/bin/env python3
"""
DGX Spark ML/Neural Network Benchmark Suite
Tests typical ML workloads: training, inference, matrix operations
"""

import torch
import torch.nn as nn
import time
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
import json

class MLBenchmark:
    """Benchmark suite for ML/Neural Network performance"""
    
    def __init__(self, device='cuda'):
        self.device = device
        self.results = {}
        
        print(f"🖥️  Device: {device}")
        if device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
            print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        print()
    
    def benchmark_matrix_ops(self):
        """Benchmark basic matrix operations"""
        print("="*80)
        print("1. MATRIX OPERATIONS BENCHMARK")
        print("="*80)
        
        sizes = [1024, 2048, 4096, 8192]
        results = {}
        
        for size in sizes:
            print(f"\n📊 Matrix size: {size}x{size}")
            
            # Matrix multiplication
            A = torch.randn(size, size, device=self.device)
            B = torch.randn(size, size, device=self.device)
            
            torch.cuda.synchronize() if self.device == 'cuda' else None
            start = time.time()
            C = torch.matmul(A, B)
            torch.cuda.synchronize() if self.device == 'cuda' else None
            matmul_time = time.time() - start
            
            # Calculate TFLOPS
            flops = 2 * size**3  # Matrix multiply FLOPs
            tflops = flops / matmul_time / 1e12
            
            print(f"  ⚡ Matrix Multiply: {matmul_time*1000:.2f}ms ({tflops:.2f} TFLOPS)")
            
            results[f"matmul_{size}"] = {
                "time_ms": matmul_time * 1000,
                "tflops": tflops
            }
        
        self.results['matrix_ops'] = results
        return results
    
    def benchmark_cnn_training(self):
        """Benchmark CNN training (ResNet-like)"""
        print("\n" + "="*80)
        print("2. CNN TRAINING BENCHMARK (ResNet-18)")
        print("="*80)
        
        # Simple ResNet-18 style model
        model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=False)
        model = model.to(self.device)
        
        # Dummy data
        batch_size = 64
        data = torch.randn(batch_size, 3, 224, 224, device=self.device)
        labels = torch.randint(0, 1000, (batch_size,), device=self.device)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        
        # Warmup
        for _ in range(5):
            outputs = model(data)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        # Benchmark
        torch.cuda.synchronize() if self.device == 'cuda' else None
        start = time.time()
        
        iterations = 50
        for _ in range(iterations):
            outputs = model(data)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        torch.cuda.synchronize() if self.device == 'cuda' else None
        total_time = time.time() - start
        
        time_per_iter = total_time / iterations
        images_per_sec = batch_size / time_per_iter
        
        print(f"\n📈 Training Performance:")
        print(f"  ⚡ Time per iteration: {time_per_iter*1000:.2f}ms")
        print(f"  🖼️  Images/sec: {images_per_sec:.1f}")
        print(f"  📦 Batch size: {batch_size}")
        
        self.results['cnn_training'] = {
            "time_per_iter_ms": time_per_iter * 1000,
            "images_per_sec": images_per_sec,
            "batch_size": batch_size
        }
    
    def benchmark_cnn_inference(self):
        """Benchmark CNN inference"""
        print("\n" + "="*80)
        print("3. CNN INFERENCE BENCHMARK (ResNet-50)")
        print("="*80)
        
        model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=False)
        model = model.to(self.device)
        model.eval()
        
        batch_sizes = [1, 8, 32, 64]
        results = {}
        
        with torch.no_grad():
            for bs in batch_sizes:
                data = torch.randn(bs, 3, 224, 224, device=self.device)
                
                # Warmup
                for _ in range(10):
                    _ = model(data)
                
                # Benchmark
                torch.cuda.synchronize() if self.device == 'cuda' else None
                start = time.time()
                
                iterations = 100
                for _ in range(iterations):
                    _ = model(data)
                
                torch.cuda.synchronize() if self.device == 'cuda' else None
                total_time = time.time() - start
                
                time_per_image = total_time / (iterations * bs) * 1000
                throughput = (iterations * bs) / total_time
                
                print(f"\n📊 Batch size: {bs}")
                print(f"  ⚡ Time per image: {time_per_image:.2f}ms")
                print(f"  🚀 Throughput: {throughput:.1f} images/sec")
                
                results[f"batch_{bs}"] = {
                    "time_per_image_ms": time_per_image,
                    "throughput": throughput
                }
        
        self.results['cnn_inference'] = results
    
    def benchmark_transformer(self):
        """Benchmark Transformer training"""
        print("\n" + "="*80)
        print("4. TRANSFORMER TRAINING BENCHMARK")
        print("="*80)
        
        # Small transformer model
        d_model = 512
        nhead = 8
        num_layers = 6
        
        model = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers,
            dim_feedforward=2048
        ).to(self.device)
        
        # Dummy data
        batch_size = 32
        seq_len = 128
        src = torch.randn(seq_len, batch_size, d_model, device=self.device)
        tgt = torch.randn(seq_len, batch_size, d_model, device=self.device)
        
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters())
        
        # Warmup
        for _ in range(5):
            output = model(src, tgt)
            loss = criterion(output, tgt)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        # Benchmark
        torch.cuda.synchronize() if self.device == 'cuda' else None
        start = time.time()
        
        iterations = 50
        for _ in range(iterations):
            output = model(src, tgt)
            loss = criterion(output, tgt)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        torch.cuda.synchronize() if self.device == 'cuda' else None
        total_time = time.time() - start
        
        time_per_iter = total_time / iterations
        
        print(f"\n📈 Transformer Training:")
        print(f"  ⚡ Time per iteration: {time_per_iter*1000:.2f}ms")
        print(f"  📦 Batch size: {batch_size}, Seq length: {seq_len}")
        print(f"  🔧 Model: {d_model}d, {nhead} heads, {num_layers} layers")
        
        self.results['transformer_training'] = {
            "time_per_iter_ms": time_per_iter * 1000,
            "batch_size": batch_size,
            "seq_len": seq_len
        }
    
    def benchmark_memory_bandwidth(self):
        """Benchmark GPU memory bandwidth"""
        print("\n" + "="*80)
        print("5. MEMORY BANDWIDTH BENCHMARK")
        print("="*80)
        
        sizes_gb = [1, 2, 4, 8]
        results = {}
        
        for size_gb in sizes_gb:
            size = int(size_gb * 1e9 / 4)  # Convert GB to float32 elements
            
            print(f"\n📊 Transfer size: {size_gb} GB")
            
            # Host to Device
            data_cpu = torch.randn(size)
            torch.cuda.synchronize() if self.device == 'cuda' else None
            start = time.time()
            data_gpu = data_cpu.to(self.device)
            torch.cuda.synchronize() if self.device == 'cuda' else None
            h2d_time = time.time() - start
            h2d_bandwidth = size_gb / h2d_time
            
            # Device to Host
            torch.cuda.synchronize() if self.device == 'cuda' else None
            start = time.time()
            data_cpu = data_gpu.cpu()
            torch.cuda.synchronize() if self.device == 'cuda' else None
            d2h_time = time.time() - start
            d2h_bandwidth = size_gb / d2h_time
            
            print(f"  ⬆️  Host→Device: {h2d_bandwidth:.2f} GB/s")
            print(f"  ⬇️  Device→Host: {d2h_bandwidth:.2f} GB/s")
            
            results[f"{size_gb}gb"] = {
                "h2d_bandwidth_gbs": h2d_bandwidth,
                "d2h_bandwidth_gbs": d2h_bandwidth
            }
        
        self.results['memory_bandwidth'] = results
    
    def run_all(self):
        """Run all benchmarks"""
        print("\n" + "="*80)
        print("🚀 DGX SPARK ML/NEURAL NETWORK BENCHMARK SUITE")
        print("="*80)
        print()
        
        self.benchmark_matrix_ops()
        self.benchmark_cnn_training()
        self.benchmark_cnn_inference()
        self.benchmark_transformer()
        self.benchmark_memory_bandwidth()
        
        # Summary
        print("\n" + "="*80)
        print("📊 BENCHMARK SUMMARY")
        print("="*80)
        print(json.dumps(self.results, indent=2))
        
        # Save results
        with open('dgx_spark_benchmark_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("\n✅ Results saved to: dgx_spark_benchmark_results.json")

if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    if device == 'cpu':
        print("⚠️  WARNING: CUDA not available, running on CPU")
        print("This benchmark is designed for GPU testing")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            exit()
    
    benchmark = MLBenchmark(device=device)
    benchmark.run_all()
