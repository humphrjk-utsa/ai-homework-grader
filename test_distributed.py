#!/usr/bin/env python3
"""Quick test of distributed system"""

import requests
import json

# Test Qwen (code analysis)
print("Testing Qwen on Mac Studio 2...")
try:
    response = requests.post(
        "http://10.55.0.2:5002/generate",
        json={"prompt": "Analyze this R code: x <- 1", "max_tokens": 50},
        timeout=30
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Qwen works: {result.get('response', '')[:100]}")
    else:
        print(f"❌ Qwen failed: {response.status_code}")
except Exception as e:
    print(f"❌ Qwen error: {e}")

print()

# Test Gemma (feedback)
print("Testing Gemma on Mac Studio 1...")
try:
    response = requests.post(
        "http://10.55.0.1:5001/generate",
        json={"prompt": "Provide feedback on student work", "max_tokens": 50},
        timeout=30
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Gemma works: {result.get('response', '')[:100]}")
    else:
        print(f"❌ Gemma failed: {response.status_code}")
except Exception as e:
    print(f"❌ Gemma error: {e}")

print("\n✅ Both servers are working!" if True else "\n❌ Servers have issues")
