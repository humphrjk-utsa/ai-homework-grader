#!/usr/bin/env python3
"""
Test performance with optimized token counts
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor

def test_optimized_qwen():
    """Test Qwen with 800 tokens"""
    start = time.time()
    print(f"🔄 [{time.strftime('%H:%M:%S')}] Qwen (800 tokens) starting...")
    
    response = requests.post("http://10.55.0.1:5001/generate", 
                           json={"prompt": "def analyze_data():\n    # Complete this R data analysis function\n    data <- read.csv('file.csv')\n    # Analyze the data", "max_tokens": 800}, 
                           timeout=120)
    
    duration = time.time() - start
    print(f"✅ [{time.strftime('%H:%M:%S')}] Qwen done in {duration:.1f}s")
    return duration

def test_optimized_gemma():
    """Test Gemma with 1200 tokens"""
    start = time.time()
    print(f"🔄 [{time.strftime('%H:%M:%S')}] Gemma (1200 tokens) starting...")
    
    response = requests.post("http://10.55.0.2:5002/generate", 
                           json={"prompt": "Provide comprehensive feedback for a business analytics student on their R code approach and data analysis methodology. Include strengths, areas for improvement, and learning recommendations.", "max_tokens": 1200}, 
                           timeout=120)
    
    duration = time.time() - start
    print(f"✅ [{time.strftime('%H:%M:%S')}] Gemma done in {duration:.1f}s")
    return duration

def test_optimized_parallel():
    """Test optimized parallel execution"""
    print("🚀 Testing Optimized Parallel Execution")
    print("=" * 45)
    
    total_start = time.time()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        print(f"\n⚡ [{time.strftime('%H:%M:%S')}] Starting optimized parallel requests...")
        
        qwen_future = executor.submit(test_optimized_qwen)
        gemma_future = executor.submit(test_optimized_gemma)
        
        qwen_time = qwen_future.result()
        gemma_time = gemma_future.result()
    
    total_time = time.time() - total_start
    
    print(f"\n📊 Optimized Results:")
    print(f"   Qwen (800 tokens):   {qwen_time:.1f}s")
    print(f"   Gemma (1200 tokens): {gemma_time:.1f}s")
    print(f"   Total parallel time: {total_time:.1f}s")
    print(f"   Sequential would be: {qwen_time + gemma_time:.1f}s")
    print(f"   Speedup: {(qwen_time + gemma_time) / total_time:.2f}x")
    
    if total_time < 30:
        print("✅ MUCH BETTER! Under 30 seconds")
    elif total_time < 60:
        print("⚠️  Acceptable - Under 1 minute")
    else:
        print("❌ Still too slow")

if __name__ == "__main__":
    test_optimized_parallel()