#!/usr/bin/env python3
import requests
import time
import json

def test_distributed_system():
    print("🧪 Testing Distributed MLX System")
    print("=" * 40)
    
    qwen_url = "http://10.55.0.1:5001"
    gemma_url = "http://10.55.0.2:5002"
    
    # Test Qwen server
    print("\n1. Testing Qwen Coder Server...")
    try:
        response = requests.get(f"{qwen_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Qwen server is healthy")
            data = response.json()
            print(f"   Model: {data.get('model', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print("❌ Qwen server health check failed")
    except Exception as e:
        print(f"❌ Cannot connect to Qwen server: {e}")
    
    # Test Gemma server
    print("\n2. Testing Gemma Server...")
    try:
        response = requests.get(f"{gemma_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Gemma server is healthy")
            data = response.json()
            print(f"   Model: {data.get('model', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print("❌ Gemma server health check failed")
    except Exception as e:
        print(f"❌ Cannot connect to Gemma server: {e}")
    
    # Test parallel generation
    print("\n3. Testing Parallel Generation...")
    try:
        from models.distributed_mlx_client import DistributedMLXClient
        
        client = DistributedMLXClient(qwen_url, gemma_url)
        
        code_prompt = "Analyze this R code: x <- c(1,2,3); mean(x)"
        feedback_prompt = "Provide feedback on data analysis approach"
        
        start_time = time.time()
        result = client.generate_parallel_sync(code_prompt, feedback_prompt)
        total_time = time.time() - start_time
        
        if result.get('code_analysis') and result.get('feedback'):
            print("✅ Parallel generation successful!")
            print(f"   Total time: {total_time:.2f}s")
            print(f"   Parallel efficiency: {result.get('parallel_efficiency', 0):.2f}x")
        else:
            print("❌ Parallel generation failed")
            print(f"   Error: {result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Parallel test failed: {e}")

if __name__ == "__main__":
    test_distributed_system()
