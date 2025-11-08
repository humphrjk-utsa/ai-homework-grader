#!/usr/bin/env python3
"""
Test script for disaggregated inference setup
Tests all 4 servers and both pipelines
"""

import requests
import time
import json

# Server configurations
SERVERS = {
    'dgx_spark1_prefill': 'http://169.254.150.103:8000',
    'dgx_spark2_prefill': 'http://169.254.150.104:8000',
    'mac1_decode': 'http://169.254.150.101:8003',  # Decode endpoint on port 8003
    'mac2_decode': 'http://169.254.150.102:5002'
}

def test_health_checks():
    """Test health endpoints for all servers"""
    print("="*80)
    print("TESTING SERVER HEALTH CHECKS")
    print("="*80)
    
    for name, url in SERVERS.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: {data.get('status', 'unknown')}")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
    print()

def test_qwen_pipeline():
    """Test Qwen pipeline (DGX Spark 1 → Mac Studio 2)"""
    print("="*80)
    print("TESTING QWEN PIPELINE (Code Analysis)")
    print("DGX Spark 1 (prefill) → Mac Studio 2 (decode)")
    print("="*80)
    
    test_prompt = """Analyze this Python code:

def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total

Provide technical feedback."""
    
    try:
        # Step 1: Prefill on DGX Spark 1
        print("📤 Step 1: Prefill on DGX Spark 1...")
        start_time = time.time()
        
        response = requests.post(
            f"{SERVERS['dgx_spark1_prefill']}/prefill",
            json={'prompt': test_prompt},
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Prefill failed: HTTP {response.status_code}")
            return
        
        prefill_result = response.json()
        prefill_time = time.time() - start_time
        print(f"✅ Prefill completed in {prefill_time:.2f}s")
        print(f"   Tokens processed: {prefill_result.get('metrics', {}).get('prompt_eval_count', 0)}")
        
        # Step 2: Decode on Mac Studio 2
        print("📥 Step 2: Decode on Mac Studio 2...")
        decode_start = time.time()
        
        response = requests.post(
            f"{SERVERS['mac2_decode']}/decode",
            json={
                'prompt': prefill_result.get('prompt'),
                'context': prefill_result.get('context', []),
                'max_new_tokens': 500,
                'temperature': 0.2
            },
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Decode failed: HTTP {response.status_code}")
            return
        
        decode_result = response.json()
        decode_time = time.time() - decode_start
        total_time = time.time() - start_time
        
        print(f"✅ Decode completed in {decode_time:.2f}s")
        print(f"   Tokens/sec: {decode_result.get('tokens_per_sec', 0):.1f}")
        print(f"⏱️ Total pipeline time: {total_time:.2f}s")
        print(f"\n📝 Generated response preview:")
        print(decode_result.get('generated_text', '')[:200] + "...")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
    
    print()

def test_gptoss_pipeline():
    """Test GPT-OSS pipeline (DGX Spark 2 → Mac Studio 1)"""
    print("="*80)
    print("TESTING GPT-OSS PIPELINE (Feedback Generation)")
    print("DGX Spark 2 (prefill) → Mac Studio 1 (decode)")
    print("="*80)
    
    test_prompt = """Generate personalized feedback for this student submission:

The student completed 8 out of 10 sections. Their code is mostly correct but has some minor issues with variable naming and missing comments.

Provide encouraging, constructive feedback."""
    
    try:
        # Step 1: Prefill on DGX Spark 2
        print("📤 Step 1: Prefill on DGX Spark 2...")
        start_time = time.time()
        
        response = requests.post(
            f"{SERVERS['dgx_spark2_prefill']}/prefill",
            json={'prompt': test_prompt},
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Prefill failed: HTTP {response.status_code}")
            return
        
        prefill_result = response.json()
        prefill_time = time.time() - start_time
        print(f"✅ Prefill completed in {prefill_time:.2f}s")
        print(f"   Tokens processed: {prefill_result.get('metrics', {}).get('prompt_eval_count', 0)}")
        
        # Step 2: Decode on Mac Studio 1
        print("📥 Step 2: Decode on Mac Studio 1...")
        decode_start = time.time()
        
        response = requests.post(
            f"{SERVERS['mac1_decode']}/decode",
            json={
                'prompt': prefill_result.get('prompt'),
                'context': prefill_result.get('context', []),
                'max_new_tokens': 800,
                'temperature': 0.3
            },
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Decode failed: HTTP {response.status_code}")
            return
        
        decode_result = response.json()
        decode_time = time.time() - decode_start
        total_time = time.time() - start_time
        
        print(f"✅ Decode completed in {decode_time:.2f}s")
        print(f"   Tokens/sec: {decode_result.get('tokens_per_sec', 0):.1f}")
        print(f"⏱️ Total pipeline time: {total_time:.2f}s")
        print(f"\n📝 Generated response preview:")
        print(decode_result.get('generated_text', '')[:200] + "...")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
    
    print()

def test_parallel_execution():
    """Test both pipelines running in parallel"""
    print("="*80)
    print("TESTING PARALLEL EXECUTION")
    print("Both pipelines running simultaneously")
    print("="*80)
    
    import concurrent.futures
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_qwen = executor.submit(test_qwen_pipeline)
        future_gptoss = executor.submit(test_gptoss_pipeline)
        
        # Wait for both to complete
        concurrent.futures.wait([future_qwen, future_gptoss])
    
    total_time = time.time() - start_time
    print(f"⏱️ Total parallel execution time: {total_time:.2f}s")
    print("✅ Both pipelines completed!")
    print()

if __name__ == '__main__':
    print("\n🧪 DISAGGREGATED INFERENCE TEST SUITE\n")
    
    # Test 1: Health checks
    test_health_checks()
    
    # Test 2: Individual pipelines
    test_qwen_pipeline()
    test_gptoss_pipeline()
    
    # Test 3: Parallel execution
    # Uncomment to test parallel execution
    # test_parallel_execution()
    
    print("="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)
