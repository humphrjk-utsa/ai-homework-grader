#!/usr/bin/env python3
"""
Simple test of distributed system without Streamlit
"""

import sys
sys.path.append('.')

from models.distributed_mlx_client import DistributedMLXClient
import json

def test_distributed():
    print("🧪 Simple Distributed Test")
    print("=" * 30)
    
    # Load config
    with open('distributed_config.json', 'r') as f:
        config = json.load(f)
    
    qwen_url = config['urls']['qwen_server']
    gemma_url = config['urls']['gemma_server']
    
    print(f"Qwen URL: {qwen_url}")
    print(f"Gemma URL: {gemma_url}")
    
    # Create client
    client = DistributedMLXClient(qwen_url, gemma_url)
    
    # Test individual generation
    print("\n1. Testing Qwen (Code Analysis)...")
    code_result = client.generate_code_analysis("def hello(): # Complete this function", max_tokens=50)
    if code_result:
        print(f"✅ Qwen result: {code_result[:100]}...")
    else:
        print("❌ Qwen failed")
    
    print("\n2. Testing Gemma (Feedback)...")
    feedback_result = client.generate_feedback("Provide feedback on this code", max_tokens=50)
    if feedback_result:
        print(f"✅ Gemma result: {feedback_result[:100]}...")
    else:
        print("❌ Gemma failed")
    
    # Test parallel generation
    print("\n3. Testing Parallel Generation...")
    try:
        result = client.generate_parallel_sync(
            "def analyze_data(): # Complete this R data analysis function",
            "Provide constructive feedback on the student's approach to data analysis"
        )
        
        if result.get('code_analysis') and result.get('feedback'):
            print("✅ Parallel generation successful!")
            print(f"   Code analysis: {result['code_analysis'][:50]}...")
            print(f"   Feedback: {result['feedback'][:50]}...")
            print(f"   Parallel time: {result.get('parallel_time', 0):.2f}s")
            print(f"   Efficiency: {result.get('parallel_efficiency', 0):.2f}x")
        else:
            print("❌ Parallel generation failed")
            print(f"   Error: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ Parallel test exception: {e}")

if __name__ == "__main__":
    test_distributed()