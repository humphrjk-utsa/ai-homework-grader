#!/usr/bin/env python3
"""
DGX Spark Distributed ML Benchmark
Tests single GPU vs distributed training across ConnectX-7 cluster
"""

import torch
import torch.nn as nn
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
import time
import json
import os
import argparse

class DistributedBenchmark:
    """Benchmark for distributed training performance"""
    
    def __init__(self, rank, world_size):
        self.rank = rank
        self.world_size = world_size
        self.device = f'cuda:{rank}'
        
        print(f"[Rank {rank}] Initialized on {self.device}")
        print(f"[Rank {rank}] GPU: {torch.cuda.get_device_name(rank)}")
    
    def benchmark_single_gpu_training(self):
        """Benchmark training on single GPU"""
        print(f"\n[Rank {self.rank}] " + "="*70)
        print(f"[Rank {self.rank}] SINGLE GPU TRAINING BENCHMARK")
        print(f"[Rank {self.rank}] " + "="*70)
        
        # ResNet-50 model
        model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=False)
        model = model.to(self.device)
        
        batch_size = 128
        data = torch.randn(batch_size, 3, 224, 224, device=self.device)
        labels = torch.randint(0, 1000, (batch_size,), device=self.device)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
        
        # Warmup
        for _ in range(10):
            outputs = model(data)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        # Benchmark
        torch.cuda.synchronize()
        start = time.time()
        
        iterations = 100
        for _ in range(iterations):
            outputs = model(data)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        torch.cuda.synchronize()
        total_time = time.time() - start
        
        time_per_iter = total_time / iterations
        images_per_sec = batch_size / time_per_iter
        
        print(f"\n[Rank {self.rank}] 📈 Single GPU Performance:")
        print(f"[Rank {self.rank}]   ⚡ Time per iteration: {time_per_iter*1000:.2f}ms")
        print(f"[Rank {self.rank}]   🖼️  Images/sec: {images_per_sec:.1f}")
        print(f"[Rank {self.rank}]   📦 Batch size: {batch_size}")
        
        return {
            "time_per_iter_ms": time_per_iter * 1000,
            "images_per_sec": images_per_sec,
            "batch_size": batch_size
        }
    
    def benchmark_distributed_training(self):
        """Benchmark distributed training across cluster"""
        print(f"\n[Rank {self.rank}] " + "="*70)
        print(f"[Rank {self.rank}] DISTRIBUTED TRAINING BENCHMARK")
        print(f"[Rank {self.rank}] World size: {self.world_size}")
        print(f"[Rank {self.rank}] " + "="*70)
        
        # ResNet-50 with DDP
        model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=False)
        model = model.to(self.device)
        model = DDP(model, device_ids=[self.rank])
        
        # Each GPU gets same batch size, so total batch = batch_size * world_size
        batch_size = 128
        data = torch.randn(batch_size, 3, 224, 224, device=self.device)
        labels = torch.randint(0, 1000, (batch_size,), device=self.device)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
        
        # Warmup
        for _ in range(10):
            outputs = model(data)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        # Synchronize all GPUs before benchmark
        dist.barrier()
        
        # Benchmark
        torch.cuda.synchronize()
        start = time.time()
        
        iterations = 100
        for _ in range(iterations):
            outputs = model(data)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        torch.cuda.synchronize()
        dist.barrier()  # Wait for all GPUs
        total_time = time.time() - start
        
        time_per_iter = total_time / iterations
        # Total throughput = batch_size * world_size / time
        total_images_per_sec = (batch_size * self.world_size) / time_per_iter
        
        if self.rank == 0:
            print(f"\n[Rank 0] 📈 Distributed Performance:")
            print(f"[Rank 0]   ⚡ Time per iteration: {time_per_iter*1000:.2f}ms")
            print(f"[Rank 0]   🖼️  Total images/sec: {total_images_per_sec:.1f}")
            print(f"[Rank 0]   📦 Batch per GPU: {batch_size}")
            print(f"[Rank 0]   📦 Total batch: {batch_size * self.world_size}")
            print(f"[Rank 0]   🌐 GPUs: {self.world_size}")
        
        return {
            "time_per_iter_ms": time_per_iter * 1000,
            "total_images_per_sec": total_images_per_sec,
            "batch_per_gpu": batch_size,
            "total_batch": batch_size * self.world_size,
            "num_gpus": self.world_size
        }
    
    def benchmark_communication(self):
        """Benchmark inter-GPU communication over ConnectX-7"""
        print(f"\n[Rank {self.rank}] " + "="*70)
        print(f"[Rank {self.rank}] COMMUNICATION BENCHMARK (ConnectX-7)")
        print(f"[Rank {self.rank}] " + "="*70)
        
        sizes_mb = [1, 10, 100, 1000]  # Message sizes in MB
        results = {}
        
        for size_mb in sizes_mb:
            size = int(size_mb * 1024 * 1024 / 4)  # Convert MB to float32 elements
            tensor = torch.randn(size, device=self.device)
            
            # Warmup
            for _ in range(5):
                dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
            
            # Benchmark
            torch.cuda.synchronize()
            dist.barrier()
            start = time.time()
            
            iterations = 20
            for _ in range(iterations):
                dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
            
            torch.cuda.synchronize()
            dist.barrier()
            total_time = time.time() - start
            
            time_per_op = total_time / iterations
            bandwidth = size_mb / time_per_op  # MB/s
            
            if self.rank == 0:
                print(f"\n[Rank 0] 📊 Message size: {size_mb} MB")
                print(f"[Rank 0]   ⚡ Time per all-reduce: {time_per_op*1000:.2f}ms")
                print(f"[Rank 0]   📡 Bandwidth: {bandwidth:.2f} MB/s ({bandwidth/1000:.2f} GB/s)")
            
            results[f"{size_mb}mb"] = {
                "time_ms": time_per_op * 1000,
                "bandwidth_mbs": bandwidth,
                "bandwidth_gbs": bandwidth / 1000
            }
        
        return results
    
    def run_all(self):
        """Run all benchmarks"""
        results = {}
        
        # Single GPU benchmark (all ranks run independently)
        single_gpu_results = self.benchmark_single_gpu_training()
        results['single_gpu'] = single_gpu_results
        
        # Distributed training benchmark
        dist_results = self.benchmark_distributed_training()
        if self.rank == 0:
            results['distributed'] = dist_results
        
        # Communication benchmark
        comm_results = self.benchmark_communication()
        if self.rank == 0:
            results['communication'] = comm_results
        
        # Calculate speedup
        if self.rank == 0:
            speedup = dist_results['total_images_per_sec'] / single_gpu_results['images_per_sec']
            efficiency = speedup / self.world_size * 100
            
            print(f"\n" + "="*70)
            print("📊 PERFORMANCE SUMMARY")
            print("="*70)
            print(f"Single GPU: {single_gpu_results['images_per_sec']:.1f} images/sec")
            print(f"Distributed ({self.world_size} GPUs): {dist_results['total_images_per_sec']:.1f} images/sec")
            print(f"Speedup: {speedup:.2f}x")
            print(f"Efficiency: {efficiency:.1f}%")
            print("="*70)
            
            results['summary'] = {
                "speedup": speedup,
                "efficiency": efficiency
            }
            
            # Save results
            with open(f'dgx_distributed_benchmark_{self.world_size}gpu.json', 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✅ Results saved to: dgx_distributed_benchmark_{self.world_size}gpu.json")

def setup_distributed(rank, world_size, backend='nccl'):
    """Initialize distributed training"""
    os.environ['MASTER_ADDR'] = os.environ.get('MASTER_ADDR', 'localhost')
    os.environ['MASTER_PORT'] = os.environ.get('MASTER_PORT', '12355')
    
    dist.init_process_group(backend, rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def cleanup_distributed():
    """Cleanup distributed training"""
    dist.destroy_process_group()

def run_benchmark(rank, world_size):
    """Run benchmark on a single process"""
    setup_distributed(rank, world_size)
    
    benchmark = DistributedBenchmark(rank, world_size)
    benchmark.run_all()
    
    cleanup_distributed()

def main():
    parser = argparse.ArgumentParser(description='DGX Spark Distributed Benchmark')
    parser.add_argument('--mode', type=str, default='single', 
                       choices=['single', 'distributed'],
                       help='Benchmark mode: single GPU or distributed')
    parser.add_argument('--gpus', type=int, default=None,
                       help='Number of GPUs to use (default: all available)')
    
    args = parser.parse_args()
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available!")
        return
    
    num_gpus = args.gpus if args.gpus else torch.cuda.device_count()
    
    print("="*70)
    print("🚀 DGX SPARK DISTRIBUTED ML BENCHMARK")
    print("="*70)
    print(f"Mode: {args.mode}")
    print(f"GPUs available: {torch.cuda.device_count()}")
    print(f"GPUs to use: {num_gpus}")
    print()
    
    if args.mode == 'single':
        # Run on single GPU (rank 0)
        print("Running single GPU benchmark...")
        setup_distributed(0, 1)
        benchmark = DistributedBenchmark(0, 1)
        benchmark.benchmark_single_gpu_training()
        cleanup_distributed()
    else:
        # Run distributed across all GPUs
        print(f"Running distributed benchmark on {num_gpus} GPUs...")
        mp.spawn(run_benchmark, args=(num_gpus,), nprocs=num_gpus, join=True)

if __name__ == "__main__":
    main()
