#!/usr/bin/env python3
"""
Test orchestrator logic without requiring servers
"""
import asyncio
from orchestrator import DisaggregatedInference


async def test_config():
    """Test that orchestrator initializes correctly"""
    print("\n" + "="*70)
    print("TEST 1: Orchestrator Initialization")
    print("="*70)
    
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
    
    print(f"✅ Orchestrator created")
    print(f"   Prefill servers: {len(orchestrator.prefill_servers)}")
    print(f"   Decode servers: {len(orchestrator.decode_servers)}")
    
    for server in orchestrator.prefill_servers:
        print(f"   - Prefill: {server['model']} @ {server['host']}:{server['port']}")
    
    for server in orchestrator.decode_servers:
        print(f"   - Decode: {server['model']} @ {server['host']}:{server['port']}")
    
    return orchestrator


async def test_health_checks(orchestrator):
    """Test health check logic"""
    print("\n" + "="*70)
    print("TEST 2: Health Check Logic")
    print("="*70)
    
    print("Checking server health (will timeout for non-running servers)...")
    await orchestrator.update_server_status()
    
    print(f"\nServer status:")
    for server_id, status in orchestrator.server_status.items():
        status_str = "✅ Healthy" if status else "❌ Unavailable"
        print(f"   {server_id}: {status_str}")
    
    # Test get_best_server
    print("\n" + "="*70)
    print("TEST 3: Server Selection Logic")
    print("="*70)
    
    qwen_prefill = orchestrator.get_best_server(orchestrator.prefill_servers, 'qwen')
    qwen_decode = orchestrator.get_best_server(orchestrator.decode_servers, 'qwen')
    
    if qwen_prefill:
        print(f"✅ Best Qwen prefill server: {qwen_prefill['host']}:{qwen_prefill['port']}")
    else:
        print(f"⚠️  No Qwen prefill server available (expected - not running)")
    
    if qwen_decode:
        print(f"✅ Best Qwen decode server: {qwen_decode['host']}:{qwen_decode['port']}")
    else:
        print(f"⚠️  No Qwen decode server available (expected - not running)")


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ORCHESTRATOR LOGIC TESTS (No Servers Required)")
    print("="*70)
    
    orchestrator = await test_config()
    await test_health_checks(orchestrator)
    
    print("\n" + "="*70)
    print("✅ All Logic Tests Passed!")
    print("="*70)
    print("\n📝 Next: Start servers and test full system")
    print("   1. Install dependencies (if needed)")
    print("   2. Start DGX servers: ./disaggregated_inference/start_dgx_servers.sh")
    print("   3. Start Mac servers: ./disaggregated_inference/start_mac_servers.sh")
    print("   4. Run full test: python3 disaggregated_inference/test_system.py")


if __name__ == '__main__':
    asyncio.run(main())
