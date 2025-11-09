#!/usr/bin/env python3
"""
Test script to verify disaggregated inference setup
"""
import requests
import json

def check_server(name, host, port, endpoint='/health'):
    """Check if a server is responding"""
    try:
        url = f"http://{host}:{port}{endpoint}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: {host}:{port}")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Model: {data.get('model', 'unknown')}")
            print(f"   Backend: {data.get('backend', 'unknown')}")
            return True
        else:
            print(f"❌ {name}: {host}:{port} - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {host}:{port} - {e}")
        return False

def main():
    print("="*80)
    print("DISAGGREGATED INFERENCE SYSTEM STATUS CHECK")
    print("="*80)
    
    # Load config
    try:
        with open('disaggregated_inference/config_current.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    print("\n[PREFILL SERVERS - DGX Sparks]")
    print("-"*80)
    prefill_status = []
    for server in config['prefill_servers']:
        status = check_server(
            f"{server['name']} ({server['model']})",
            server['host'],
            server['port']
        )
        prefill_status.append(status)
        print()
    
    print("\n[DECODE SERVERS - Mac Studios]")
    print("-"*80)
    decode_status = []
    for server in config['decode_servers']:
        status = check_server(
            f"{server['name']} ({server['model']})",
            server['host'],
            server['port']
        )
        decode_status.append(status)
        print()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Prefill Servers: {sum(prefill_status)}/{len(prefill_status)} online")
    print(f"Decode Servers: {sum(decode_status)}/{len(decode_status)} online")
    
    if all(prefill_status) and all(decode_status):
        print("\n✅ All servers online! Disaggregated system ready.")
        print("\nNext steps:")
        print("1. Test with: python test_disaggregated_client.py")
        print("2. Run grader with disaggregated system")
    else:
        print("\n⚠️ Some servers offline. Start them with:")
        if not all(prefill_status):
            print("   ./disaggregated_inference/start_dgx_servers_ollama.sh")
        if not all(decode_status):
            print("   ./disaggregated_inference/start_mac_servers_ollama.sh")
    print("="*80)

if __name__ == '__main__':
    main()
