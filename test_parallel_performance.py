#!/usr/bin/env python3
"""
Test actual parallel performance of distributed MLX system
"""

import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import threading

def test_qwen_speed():
    """Test Qwen server speed"""
    start_time = time.time()
    
    payload = {
        "prompt": "def analyze_data():\n    # Complete this R data analysis function\n    data <- read.csv('file.csv')",
        "max_tokens": 200
    }
    
    print(f"🔄 [{threading.current_thread().name}] Starting Qwen request...")
    response = requests.post("http://10.55.0.1:5001/generate", 
                           json=payload, 
                           timeout=120)
    
    end_time = time.time()
    duration = end_time - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ [{threading.current_thread().name}] Qwen completed in {duration:.2f}s")
        return duration, result.get('response', '')[:100]
    else:
        print(f"❌ [{threading.current_thread().name}] Qwen failed: {response.status_code}")
        return duration, None

def test_gemma_speed():
    """Test Gemma server speed"""
    start_time = time.time()
    
    payload = {
        "prompt": "Provide constructive feedback for a business analytics student on their R code approach and data analysis methodology.",
        "max_tokens": 200
    }
    
    print(f"🔄 [{threading.current_thread().name}] Starting Gemma request...")
    response = requests.post("http://10.55.0.2:5002/generate", 
                           json=payload, 
                           timeout=120)
    
    end_time = time.time()
    duration = end_time - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ [{threading.current_thread().name}] Gemma completed in {duration:.2f}s")
        return duration, result.get('response', '')[:100]
    else:
        print(f"❌ [{threading.current_thread().name}] Gemma failed: {response.status_code}")
        return duration, None

def test_sequential():
    """Test sequential execution"""
    print("\n🔄 Testing Sequential Execution")
    print("=" * 40)
    
    total_start = time.time()
    
    qwen_time, qwen_result = test_qwen_speed()
    gemma_time, gemma_result = test_gemma_speed()
    
    total_time = time.time() - total_start
    
    print(f"\n📊 Sequential Results:")
    print(f"   Qwen time: {qwen_time:.2f}s")
    print(f"   Gemma time: {gemma_time:.2f}s")
    print(f"   Total time: {total_time:.2f}s")
    
    return total_time, qwen_time, gemma_time

def test_parallel():
    """Test parallel execution"""
    print("\n⚡ Testing Parallel Execution")
    print("=" * 40)
    
    total_start = time.time()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        qwen_future = executor.submit(test_qwen_speed)
        gemma_future = executor.submit(test_gemma_speed)
        
        qwen_time, qwen_result = qwen_future.result()
        gemma_time, gemma_result = gemma_future.result()
    
    total_time = time.time() - total_start
    
    print(f"\n📊 Parallel Results:")
    print(f"   Qwen time: {qwen_time:.2f}s")
    print(f"   Gemma time: {gemma_time:.2f}s")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Efficiency: {(qwen_time + gemma_time) / total_time:.2f}x speedup")
    
    return total_time, qwen_time, gemma_time

def main():
    print("🧪 MLX Distributed Performance Test")
    print("=" * 50)
    
    # Test individual server responsiveness first
    print("\n🏥 Health Check:")
    try:
        qwen_health = requests.get("http://10.55.0.1:5001/health", timeout=5)
        gemma_health = requests.get("http://10.55.0.2:5002/health", timeout=5)
        
        print(f"   Qwen: {'✅ Healthy' if qwen_health.status_code == 200 else '❌ Unhealthy'}")
        print(f"   Gemma: {'✅ Healthy' if gemma_health.status_code == 200 else '❌ Unhealthy'}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test sequential vs parallel
    seq_total, seq_qwen, seq_gemma = test_sequential()
    par_total, par_qwen, par_gemma = test_parallel()
    
    print(f"\n🎯 Performance Summary:")
    print(f"=" * 30)
    print(f"Sequential total: {seq_total:.2f}s")
    print(f"Parallel total:   {par_total:.2f}s")
    print(f"Speedup:          {seq_total / par_total:.2f}x")
    print(f"Efficiency:       {((seq_qwen + seq_gemma) / par_total):.2f}x")
    
    if par_total > 60:
        print(f"\n⚠️  WARNING: {par_total:.1f}s is quite slow for MLX on Apple Silicon")
        print("   Expected: 15-30s for this test")
        print("   Possible issues:")
        print("   - Models not fully optimized for MLX")
        print("   - Memory constraints")
        print("   - Network latency between Mac Studios")
        print("   - Models running in CPU mode instead of GPU")

if __name__ == "__main__":
    main()