#!/usr/bin/env python3
"""
Test both disaggregated inference pairs
"""
import requests
import time

print("\n" + "="*70)
print("TESTING BOTH DISAGGREGATED INFERENCE PAIRS")
print("="*70)

# Test Pair 1: DGX Spark 1 (Qwen prefill) + Mac Studio 2 (Qwen decode)
print("\n" + "="*70)
print("PAIR 1: Qwen 3 Coder 30B")
print("  Prefill: DGX Spark 1 (169.254.150.103:8000)")
print("  Decode:  Mac Studio 2 (169.254.150.102:8001)")
print("="*70)

prompt = "def fibonacci(n):"

# Prefill
print("\n1️⃣ Prefill on DGX Spark 1...")
start = time.time()
response = requests.post("http://169.254.150.103:8000/prefill", json={'prompt': prompt}, timeout=30)
prefill_time = time.time() - start

if response.status_code == 200:
    prefill_result = response.json()
    print(f"   ✅ Success in {prefill_time:.3f}s")
    print(f"   Model: {prefill_result.get('model')}")
    
    # Decode
    print("\n2️⃣ Decode on Mac Studio 2...")
    start = time.time()
    response = requests.post("http://169.254.150.102:8001/decode", json={
        'prompt': prefill_result.get('prompt'),
        'context': prefill_result.get('context'),
        'max_new_tokens': 100
    }, timeout=60)
    decode_time = time.time() - start
    
    if response.status_code == 200:
        decode_result = response.json()
        print(f"   ✅ Success in {decode_time:.3f}s")
        print(f"   Model: {decode_result.get('model')}")
        print(f"   Speed: ~{decode_result.get('tokens_per_sec', 0):.1f} tok/s")
        print(f"\n   Total: {prefill_time + decode_time:.3f}s")
        print(f"   ✅ PAIR 1 PASSED")
    else:
        print(f"   ❌ Decode failed: {response.status_code}")
else:
    print(f"   ❌ Prefill failed: {response.status_code}")

# Test Pair 2: DGX Spark 2 (GPT-OSS prefill) + Mac Studio 1 (GPT-OSS decode)
print("\n" + "="*70)
print("PAIR 2: GPT-OSS 120B")
print("  Prefill: DGX Spark 2 (169.254.150.104:8000)")
print("  Decode:  Mac Studio 1 (169.254.150.101:8001)")
print("="*70)

prompt = "Write a Python function to calculate prime numbers:"

# Prefill
print("\n1️⃣ Prefill on DGX Spark 2...")
try:
    start = time.time()
    response = requests.post("http://169.254.150.104:8000/prefill", json={'prompt': prompt}, timeout=30)
    prefill_time = time.time() - start
    
    if response.status_code == 200:
        prefill_result = response.json()
        print(f"   ✅ Success in {prefill_time:.3f}s")
        print(f"   Model: {prefill_result.get('model')}")
        
        # Decode
        print("\n2️⃣ Decode on Mac Studio 1...")
        start = time.time()
        response = requests.post("http://169.254.150.101:8001/decode", json={
            'prompt': prefill_result.get('prompt'),
            'context': prefill_result.get('context'),
            'max_new_tokens': 100
        }, timeout=60)
        decode_time = time.time() - start
        
        if response.status_code == 200:
            decode_result = response.json()
            print(f"   ✅ Success in {decode_time:.3f}s")
            print(f"   Model: {decode_result.get('model')}")
            print(f"   Speed: ~{decode_result.get('tokens_per_sec', 0):.1f} tok/s")
            print(f"\n   Total: {prefill_time + decode_time:.3f}s")
            print(f"   ✅ PAIR 2 PASSED")
        else:
            print(f"   ❌ Decode failed: {response.status_code}")
            print(f"   Note: Mac Studio 1 decode server may not be running")
    else:
        print(f"   ❌ Prefill failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   Note: DGX Spark 2 or Mac Studio 1 may not be running")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
