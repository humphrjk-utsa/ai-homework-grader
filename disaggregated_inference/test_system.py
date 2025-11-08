#!/usr/bin/env python3
"""
Test the disaggregated inference system
"""
import asyncio
import time
from orchestrator import DisaggregatedInference


async def test_basic_generation():
    """Test basic generation with both models"""
    config = {
        'prefill_servers': [
            {'host': '169.254.150.103', 'port': 8000, 'model': 'qwen'},
            {'host': '169.254.150.104', 'port': 8000, 'model': 'gpt-oss'}
        ],
        'decode_servers': [
            {'host': '169.254.150.101', 'port': 8001, 'model': 'qwen'},
            {'host': '169.254.150.102', 'port': 8001, 'model': 'gpt-oss'}
        ]
    }
    
    orchestrator = DisaggregatedInference(config)
    
    print("\n" + "="*70)
    print("DISAGGREGATED INFERENCE SYSTEM TEST")
    print("="*70)
    
    # Test 1: Qwen model
    print("\n📝 Test 1: Qwen 3 Coder 30B")
    print("-" * 70)
    result = await orchestrator.generate(
        prompt="def fibonacci(n):",
        model_type="qwen",
        max_tokens=100
    )
    
    print(f"Method: {result.get('method', 'N/A')}")
    if result.get('method') == 'disaggregated':
        print(f"Prefill Server: {result.get('prefill_server', 'N/A')}")
        print(f"Decode Server: {result.get('decode_server', 'N/A')}")
        print(f"Prefill Time: {result.get('prefill_time', 0):.3f}s")
        print(f"Decode Time: {result.get('decode_time', 0):.3f}s")
        print(f"Total Time: {result.get('total_time', 0):.3f}s")
        print(f"Speed: {result.get('tokens_per_sec', 0):.1f} tok/s")
    print(f"\nGenerated Code:\n{result.get('response', 'N/A')}")
    
    # Test 2: GPT-OSS model
    print("\n" + "="*70)
    print("\n📝 Test 2: GPT-OSS 120B")
    print("-" * 70)
    result = await orchestrator.generate(
        prompt="Write a Python function to calculate prime numbers:",
        model_type="gpt-oss",
        max_tokens=100
    )
    
    print(f"Method: {result.get('method', 'N/A')}")
    if result.get('method') == 'disaggregated':
        print(f"Prefill Server: {result.get('prefill_server', 'N/A')}")
        print(f"Decode Server: {result.get('decode_server', 'N/A')}")
        print(f"Prefill Time: {result.get('prefill_time', 0):.3f}s")
        print(f"Decode Time: {result.get('decode_time', 0):.3f}s")
        print(f"Total Time: {result.get('total_time', 0):.3f}s")
        print(f"Speed: {result.get('tokens_per_sec', 0):.1f} tok/s")
    print(f"\nGenerated Code:\n{result.get('response', 'N/A')}")
    
    print("\n" + "="*70)
    print("✅ Tests Complete!")
    print("="*70)


async def test_server_health():
    """Test server health checks"""
    config = {
        'prefill_servers': [
            {'host': '169.254.150.103', 'port': 8000, 'model': 'qwen'},
            {'host': '169.254.150.104', 'port': 8000, 'model': 'gpt-oss'}
        ],
        'decode_servers': [
            {'host': '169.254.150.101', 'port': 8001, 'model': 'qwen'},
            {'host': '169.254.150.102', 'port': 8001, 'model': 'gpt-oss'}
        ]
    }
    
    orchestrator = DisaggregatedInference(config)
    
    print("\n" + "="*70)
    print("SERVER HEALTH CHECK")
    print("="*70)
    
    await orchestrator.update_server_status()
    
    print("\nPrefill Servers (DGX):")
    for server in orchestrator.prefill_servers:
        server_id = f"{server['host']}:{server['port']}"
        status = "✅ Healthy" if orchestrator.server_status.get(server_id) else "❌ Unavailable"
        print(f"  {server['model']:10} @ {server_id:20} {status}")
    
    print("\nDecode Servers (Mac):")
    for server in orchestrator.decode_servers:
        server_id = f"{server['host']}:{server['port']}"
        status = "✅ Healthy" if orchestrator.server_status.get(server_id) else "❌ Unavailable"
        print(f"  {server['model']:10} @ {server_id:20} {status}")
    
    print("="*70)


async def main():
    """Run all tests"""
    # First check server health
    await test_server_health()
    
    # Then run generation tests
    await test_basic_generation()


if __name__ == '__main__':
    asyncio.run(main())
