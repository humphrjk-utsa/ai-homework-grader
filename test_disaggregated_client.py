#!/usr/bin/env python3
"""
Test the DisaggregatedClient with a simple prompt
"""
from disaggregated_client import DisaggregatedClient
import time

def test_qwen():
    """Test Qwen model"""
    print("="*80)
    print("Testing Qwen 3 Coder 30B (Disaggregated)")
    print("="*80)
    
    client = DisaggregatedClient()
    
    prompt = """def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    # Complete this function"""
    
    print(f"\nPrompt:\n{prompt}\n")
    print("Generating...")
    
    start = time.time()
    try:
        response, metrics = client.generate(
            model="qwen3-coder:30b",
            prompt=prompt,
            max_tokens=200
        )
        elapsed = time.time() - start
        
        print(f"\n✅ Generation completed in {elapsed:.2f}s")
        print(f"\nResponse:\n{response}\n")
        
        print("="*80)
        print("METRICS")
        print("="*80)
        print(f"Prefill Time: {metrics['prefill_time']:.3f}s")
        print(f"Decode Time: {metrics['decode_time']:.3f}s")
        print(f"Total Time: {metrics['total_time']:.3f}s")
        print(f"Prompt Tokens: {metrics['prompt_tokens']}")
        print(f"Completion Tokens: {metrics['completion_tokens']}")
        print(f"Total Tokens: {metrics['total_tokens']}")
        print(f"Prefill Speed: {metrics['prefill_speed']:.1f} tok/s")
        print(f"Decode Speed: {metrics['decode_speed']:.1f} tok/s")
        print(f"Method: {metrics['method']}")
        print(f"Prefill Server: {metrics['prefill_server']}")
        print(f"Decode Server: {metrics['decode_server']}")
        print("="*80)
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gpt_oss():
    """Test GPT-OSS model"""
    print("\n" + "="*80)
    print("Testing GPT-OSS 120B (Disaggregated)")
    print("="*80)
    
    client = DisaggregatedClient()
    
    prompt = """Explain the concept of machine learning in one paragraph."""
    
    print(f"\nPrompt:\n{prompt}\n")
    print("Generating...")
    
    start = time.time()
    try:
        response, metrics = client.generate(
            model="gpt-oss:120b",
            prompt=prompt,
            max_tokens=150
        )
        elapsed = time.time() - start
        
        print(f"\n✅ Generation completed in {elapsed:.2f}s")
        print(f"\nResponse:\n{response}\n")
        
        print("="*80)
        print("METRICS")
        print("="*80)
        print(f"Prefill Time: {metrics['prefill_time']:.3f}s")
        print(f"Decode Time: {metrics['decode_time']:.3f}s")
        print(f"Total Time: {metrics['total_time']:.3f}s")
        print(f"Decode Speed: {metrics['decode_speed']:.1f} tok/s")
        print("="*80)
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*80)
    print("DISAGGREGATED CLIENT TEST SUITE")
    print("="*80 + "\n")
    
    results = []
    
    # Test Qwen
    results.append(("Qwen 3 Coder 30B", test_qwen()))
    
    # Test GPT-OSS (optional, comment out if too slow)
    # results.append(("GPT-OSS 120B", test_gpt_oss()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    print("="*80)
    
    if all(r[1] for r in results):
        print("\n✅ All tests passed! Disaggregated system is working.")
    else:
        print("\n⚠️ Some tests failed. Check server logs.")

if __name__ == '__main__':
    main()
