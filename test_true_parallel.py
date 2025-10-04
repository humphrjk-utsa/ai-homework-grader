#!/usr/bin/env python3
"""
Test if we're getting true parallel processing
"""

import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

def quick_qwen_test():
    """Quick Qwen test"""
    start = time.time()
    print(f"🔄 [{time.strftime('%H:%M:%S')}] Qwen starting...")
    
    response = requests.post("http://10.55.0.1:5001/generate", 
                           json={"prompt": "def hello():", "max_tokens": 50}, 
                           timeout=60)
    
    duration = time.time() - start
    print(f"✅ [{time.strftime('%H:%M:%S')}] Qwen done in {duration:.1f}s")
    return duration

def quick_gemma_test():
    """Quick Gemma test"""
    start = time.time()
    print(f"🔄 [{time.strftime('%H:%M:%S')}] Gemma starting...")
    
    response = requests.post("http://10.55.0.2:5002/generate", 
                           json={"prompt": "Provide feedback:", "max_tokens": 50}, 
                           timeout=60)
    
    duration = time.time() - start
    print(f"✅ [{time.strftime('%H:%M:%S')}] Gemma done in {duration:.1f}s")
    return duration

def test_parallel_timing():
    """Test actual parallel timing"""
    print("🧪 Testing True Parallel Execution")
    print("=" * 40)
    
    # Wait for Gemma to be ready
    print("⏳ Waiting for Gemma server to be ready...")
    time.sleep(10)
    
    try:
        health = requests.get("http://10.55.0.2:5002/health", timeout=5)
        if health.status_code != 200:
            print("❌ Gemma not ready")
            return
    except:
        print("❌ Gemma not accessible")
        return
    
    print("✅ Both servers ready")
    
    # Test parallel execution
    total_start = time.time()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        print(f"\n🚀 [{time.strftime('%H:%M:%S')}] Starting parallel requests...")
        
        qwen_future = executor.submit(quick_qwen_test)
        gemma_future = executor.submit(quick_gemma_test)
        
        qwen_time = qwen_future.result()
        gemma_time = gemma_future.result()
    
    total_time = time.time() - total_start
    
    print(f"\n📊 Results:")
    print(f"   Qwen time:  {qwen_time:.1f}s")
    print(f"   Gemma time: {gemma_time:.1f}s")
    print(f"   Total time: {total_time:.1f}s")
    print(f"   Expected sequential: {qwen_time + gemma_time:.1f}s")
    print(f"   Speedup: {(qwen_time + gemma_time) / total_time:.2f}x")
    
    if total_time < (qwen_time + gemma_time) * 0.8:
        print("✅ TRUE PARALLEL PROCESSING WORKING!")
    else:
        print("❌ NOT PARALLEL - Running sequentially")

if __name__ == "__main__":
    test_parallel_timing()