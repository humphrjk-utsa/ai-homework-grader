#!/usr/bin/env python3
"""
Test the Qwen 3 Coder pair (DGX Spark 1 prefill + Mac Studio 2 decode)
"""
import requests
import time

print("\n" + "="*70)
print("TESTING QWEN 3 CODER DISAGGREGATED INFERENCE")
print("="*70)

# Test prefill on DGX Spark 1
print("\n1️⃣ Testing Prefill (DGX Spark 1)...")
prefill_url = "http://169.254.150.103:8000/prefill"
prompt = "def fibonacci(n):"

start = time.time()
response = requests.post(prefill_url, json={'prompt': prompt}, timeout=30)
prefill_time = time.time() - start

if response.status_code == 200:
    prefill_result = response.json()
    print(f"   ✅ Prefill successful in {prefill_time:.3f}s")
    print(f"   Model: {prefill_result.get('model')}")
    print(f"   Backend: {prefill_result.get('backend')}")
else:
    print(f"   ❌ Prefill failed: {response.status_code}")
    exit(1)

# Test decode on Mac Studio 2
print("\n2️⃣ Testing Decode (Mac Studio 2)...")
decode_url = "http://169.254.150.102:8001/decode"

start = time.time()
response = requests.post(decode_url, json={
    'prompt': prefill_result.get('prompt'),
    'context': prefill_result.get('context'),
    'max_new_tokens': 100
}, timeout=60)
decode_time = time.time() - start

if response.status_code == 200:
    decode_result = response.json()
    print(f"   ✅ Decode successful in {decode_time:.3f}s")
    print(f"   Model: {decode_result.get('model')}")
    print(f"   Tokens/sec: ~{decode_result.get('tokens_per_sec', 0):.1f}")
    print(f"\n📝 Generated Code:")
    print(f"   {decode_result.get('generated_text', '')[:200]}...")
else:
    print(f"   ❌ Decode failed: {response.status_code}")
    exit(1)

print("\n" + "="*70)
print("✅ DISAGGREGATED INFERENCE TEST PASSED!")
print(f"   Total time: {prefill_time + decode_time:.3f}s")
print(f"   Prefill: {prefill_time:.3f}s | Decode: {decode_time:.3f}s")
print("="*70)
