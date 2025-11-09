#!/usr/bin/env python3
"""
Quick status check for all disaggregated inference servers
"""
import requests
import sys
from typing import Dict, List


def check_server(name: str, host: str, port: int) -> Dict:
    """Check a single server"""
    try:
        url = f"http://{host}:{port}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'name': name,
                'host': host,
                'port': port,
                'status': '✅ Healthy',
                'loaded': data.get('loaded', False),
                'details': data
            }
        else:
            return {
                'name': name,
                'host': host,
                'port': port,
                'status': f'⚠️  HTTP {response.status_code}',
                'loaded': False
            }
    except requests.exceptions.Timeout:
        return {
            'name': name,
            'host': host,
            'port': port,
            'status': '❌ Timeout',
            'loaded': False
        }
    except requests.exceptions.ConnectionError:
        return {
            'name': name,
            'host': host,
            'port': port,
            'status': '❌ Connection Failed',
            'loaded': False
        }
    except Exception as e:
        return {
            'name': name,
            'host': host,
            'port': port,
            'status': f'❌ Error: {str(e)}',
            'loaded': False
        }


def main():
    """Check all servers"""
    servers = [
        # Prefill servers (DGX)
        ('DGX Spark 1 (Qwen Prefill)', '169.254.150.103', 8000),
        ('DGX Spark 2 (GPT-OSS Prefill)', '169.254.150.104', 8000),
        
        # Decode servers (Mac)
        ('Mac Studio 1 (Qwen Decode)', '169.254.150.101', 8001),
        ('Mac Studio 2 (GPT-OSS Decode)', '169.254.150.102', 8001),
    ]
    
    print("\n" + "="*80)
    print("DISAGGREGATED INFERENCE SYSTEM STATUS")
    print("="*80)
    
    results = []
    for name, host, port in servers:
        print(f"\nChecking {name}...")
        result = check_server(name, host, port)
        results.append(result)
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    print("\n📡 PREFILL SERVERS (DGX)")
    print("-" * 80)
    for result in results[:2]:
        print(f"{result['name']:40} {result['status']:20}")
        if result['loaded']:
            print(f"  └─ {result['host']}:{result['port']}")
    
    print("\n🖥️  DECODE SERVERS (Mac)")
    print("-" * 80)
    for result in results[2:]:
        print(f"{result['name']:40} {result['status']:20}")
        if result['loaded']:
            print(f"  └─ {result['host']}:{result['port']}")
    
    # Overall status
    all_healthy = all(r['loaded'] for r in results)
    prefill_healthy = all(r['loaded'] for r in results[:2])
    decode_healthy = all(r['loaded'] for r in results[2:])
    
    print("\n" + "="*80)
    print("SYSTEM STATUS")
    print("="*80)
    
    if all_healthy:
        print("✅ All systems operational - Disaggregated inference ready!")
        print("\n📝 Next steps:")
        print("  python3 disaggregated_inference/test_system.py")
        return 0
    elif prefill_healthy and decode_healthy:
        print("✅ All systems operational - Disaggregated inference ready!")
        return 0
    elif decode_healthy:
        print("⚠️  Prefill servers unavailable - Fallback to Mac-only mode")
        print("\n📝 To start prefill servers:")
        print("  ./disaggregated_inference/start_dgx_servers.sh")
        return 1
    elif prefill_healthy:
        print("⚠️  Decode servers unavailable - Cannot complete inference")
        print("\n📝 To start decode servers:")
        print("  ./disaggregated_inference/start_mac_servers.sh")
        return 1
    else:
        print("❌ System not operational - No servers available")
        print("\n📝 To start all servers:")
        print("  ./disaggregated_inference/start_dgx_servers.sh")
        print("  ./disaggregated_inference/start_mac_servers.sh")
        return 1


if __name__ == '__main__':
    sys.exit(main())
