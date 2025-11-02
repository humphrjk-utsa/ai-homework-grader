#!/usr/bin/env python3
"""
Test connection to DGX Spark cluster
"""
import requests
import json

DGX_HOST = "169.254.100.1"
DGX_PORT = 1025

print(f"Testing DGX Spark at {DGX_HOST}:{DGX_PORT}")
print("-" * 50)

# Test health endpoint
try:
    response = requests.get(f"http://{DGX_HOST}:{DGX_PORT}/health", timeout=5)
    print(f"✅ Health check: {response.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test models endpoint
try:
    response = requests.get(f"http://{DGX_HOST}:{DGX_PORT}/v1/models", timeout=5)
    print(f"✅ Models endpoint: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"❌ Models endpoint failed: {e}")

print("\nDGX Spark connection test complete")
