#!/usr/bin/env python3
"""
Test Qwen 3 Coder disaggregated inference
Spark 1 (prefill) -> Mac 2 (decode)
"""
import asyncio
from orchestrator import DisaggregatedInference


async def test_qwen_disaggregated():
    """Test Qwen with disaggregated inference"""
    
    config = {
        'prefill_servers': [
            {'host': '169.254.150.103', 'port': 8000, 'model': 'qwen'},
        ],
        'decode_servers': [
            {'host': '169.254.150.102', 'port': 5002, 'model': 'qwen'},
        ]
    }
    
    orchestrator = DisaggregatedInference(config)
    
    print("\n" + "="*70)
    print("QWEN 3 CODER 30B - DISAGGREGATED INFERENCE TEST")
    print("="*70)
    print("Prefill: DGX Spark 1 (Ollama Q4)")
    print("Decode:  Mac Studio 2 (MLX 8-bit)")
    print("="*70)
    
    # Check server health
    await orchestrator.update_server_status()
    
    print("\nServer Status:")
    for server_id, status in orchestrator.server_status.items():
        status_str = "✅ Healthy" if status else "❌ Unavailable"
        print(f"  {server_id}: {status_str}")
    
    # Test generation
    print("\n" + "="*70)
    print("Testing Code Generation")
    print("="*70)
    
    prompt = "def fibonacci(n):"
    print(f"\nPrompt: {prompt}")
    
    result = await orchestrator.generate(
        prompt=prompt,
        model_type="qwen",
        max_tokens=100
    )
    
    print(f"\nMethod: {result.get('method', 'N/A')}")
    
    if result.get('method') == 'disaggregated':
        print(f"Prefill Server: {result.get('prefill_server', 'N/A')}")
        print(f"Decode Server: {result.get('decode_server', 'N/A')}")
        print(f"Prefill Time: {result.get('prefill_time', 0):.3f}s")
        print(f"Decode Time: {result.get('decode_time', 0):.3f}s")
        print(f"Total Time: {result.get('total_time', 0):.3f}s")
        if 'tokens_per_sec' in result:
            print(f"Speed: {result['tokens_per_sec']:.1f} tok/s")
    
    print(f"\nGenerated Code:")
    print("-" * 70)
    print(result.get('response', 'N/A'))
    print("-" * 70)
    
    print("\n" + "="*70)
    print("✅ Test Complete!")
    print("="*70)


if __name__ == '__main__':
    asyncio.run(test_qwen_disaggregated())
