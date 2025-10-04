#!/usr/bin/env python3
"""
Test both Qwen and Gemma servers working together
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor

def test_qwen():
    """Test Qwen server (now on Mac Studio 2)"""
    start = time.time()
    print(f"🔄 [{time.strftime('%H:%M:%S')}] Testing Qwen (Mac Studio 2)...")
    
    response = requests.post("http://10.55.0.2:5002/generate", 
                           json={"prompt": "def analyze_data():\n    # Complete this function", "max_tokens": 500}, 
                           timeout=90)
    
    duration = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ [{time.strftime('%H:%M:%S')}] Qwen success in {duration:.1f}s")
        return True, duration, result.get('response', '')[:100]
    else:
        print(f"❌ [{time.strftime('%H:%M:%S')}] Qwen failed: {response.status_code}")
        return False, duration, None

def test_gpt_oss():
    """Test GPT-OSS server (now on Mac Studio 1)"""
    start = time.time()
    print(f"🔄 [{time.strftime('%H:%M:%S')}] Testing GPT-OSS (Mac Studio 1)...")
    
    response = requests.post("http://10.55.0.1:5001/generate", 
                           json={"prompt": "Provide feedback on student code", "max_tokens": 500}, 
                           timeout=90)
    
    duration = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ [{time.strftime('%H:%M:%S')}] Gemma success in {duration:.1f}s")
        return True, duration, result.get('response', '')[:100]
    else:
        print(f"❌ [{time.strftime('%H:%M:%S')}] Gemma failed: {response.status_code}")
        return False, duration, None

def test_parallel():
    """Test both servers in parallel"""
    print("🧪 Testing Both Servers in Parallel")
    print("=" * 40)
    
    total_start = time.time()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        print(f"⚡ [{time.strftime('%H:%M:%S')}] Starting parallel requests...")
        
        qwen_future = executor.submit(test_qwen)
        gpt_future = executor.submit(test_gpt_oss)
        
        qwen_success, qwen_time, qwen_result = qwen_future.result()
        gpt_success, gpt_time, gpt_result = gpt_future.result()
    
    total_time = time.time() - total_start
    
    print(f"\n📊 Results:")
    print(f"   Qwen (Mac Studio 2):   {'✅' if qwen_success else '❌'} {qwen_time:.1f}s")
    print(f"   GPT-OSS (Mac Studio 1): {'✅' if gpt_success else '❌'} {gpt_time:.1f}s")
    print(f"   Total parallel time: {total_time:.1f}s")
    print(f"   Sequential would be: {qwen_time + gpt_time:.1f}s")
    
    if qwen_success and gpt_success:
        speedup = (qwen_time + gpt_time) / total_time
        print(f"   Speedup: {speedup:.2f}x")
        
        if total_time < 30:
            print("✅ EXCELLENT: Under 30 seconds!")
        elif total_time < 60:
            print("✅ GOOD: Under 1 minute")
        else:
            print("⚠️ SLOW: Over 1 minute")
            
        return True
    else:
        print("❌ One or both servers failed")
        return False

if __name__ == "__main__":
    success = test_parallel()
    
    if success:
        print("\n🎉 Both servers working! Ready for homework grading.")
    else:
        print("\n❌ Servers not ready for production use.")