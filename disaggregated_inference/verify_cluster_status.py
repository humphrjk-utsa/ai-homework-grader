#!/usr/bin/env python3
"""
Comprehensive Cluster Status Verification
Checks all DGX Sparks and Mac Studios for proper configuration
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path
from typing import Dict, List
import subprocess

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class ClusterVerifier:
    """Verifies the distributed AI grader cluster"""

    def __init__(self, config_path: str = "config_current.json"):
        self.config_path = config_path
        self.config = None
        self.results = {
            'prefill_servers': {},
            'decode_servers': {},
            'orchestration_valid': False,
            'models_verified': {},
            'network_connectivity': {},
            'overall_status': 'UNKNOWN'
        }

    def load_config(self) -> bool:
        """Load cluster configuration"""
        try:
            config_file = Path(__file__).parent / self.config_path
            with open(config_file, 'r') as f:
                self.config = json.load(f)

            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Configuration loaded from {config_file}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Failed to load configuration: {e}")
            return False

    async def check_server_health(self, server: Dict) -> Dict:
        """Check health of a single server"""
        server_id = f"{server['host']}:{server['port']}"
        server_name = server.get('name', server_id)
        model_type = server.get('model', 'unknown')

        result = {
            'name': server_name,
            'host': server['host'],
            'port': server['port'],
            'model_type': model_type,
            'healthy': False,
            'loaded': False,
            'error': None,
            'response_data': None
        }

        try:
            url = f"http://{server['host']}:{server['port']}/health"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        result['healthy'] = True
                        result['loaded'] = data.get('loaded', False)
                        result['response_data'] = data
                    else:
                        result['error'] = f"HTTP {response.status}"
        except asyncio.TimeoutError:
            result['error'] = "Connection timeout"
        except aiohttp.ClientConnectorError:
            result['error'] = "Connection refused - server may not be running"
        except Exception as e:
            result['error'] = str(e)

        return result

    async def check_server_status(self, server: Dict) -> Dict:
        """Get detailed server status"""
        try:
            url = f"http://{server['host']}:{server['port']}/status"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        return await response.json()
        except:
            pass
        return None

    async def verify_all_servers(self):
        """Verify all prefill and decode servers"""
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}SERVER HEALTH CHECKS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

        # Check all servers
        all_servers = []
        server_types = []

        for server in self.config['prefill_servers']:
            all_servers.append(server)
            server_types.append('prefill')

        for server in self.config['decode_servers']:
            all_servers.append(server)
            server_types.append('decode')

        # Run health checks in parallel
        health_checks = [self.check_server_health(server) for server in all_servers]
        status_checks = [self.check_server_status(server) for server in all_servers]

        health_results = await asyncio.gather(*health_checks, return_exceptions=True)
        status_results = await asyncio.gather(*status_checks, return_exceptions=True)

        # Process results
        for i, (server_type, server, health, status) in enumerate(zip(
            server_types, all_servers, health_results, status_results
        )):
            if isinstance(health, Exception):
                health = {'error': str(health), 'healthy': False}

            # Store results
            server_id = f"{server['host']}:{server['port']}"
            if server_type == 'prefill':
                self.results['prefill_servers'][server_id] = {**health, 'status': status}
            else:
                self.results['decode_servers'][server_id] = {**health, 'status': status}

            # Print results
            self._print_server_status(server_type, health, status)

    def _print_server_status(self, server_type: str, health: Dict, status: Dict):
        """Print formatted server status"""
        name = health.get('name', 'Unknown')
        host = health.get('host', 'N/A')
        port = health.get('port', 'N/A')
        model_type = health.get('model_type', 'unknown')

        # Status symbol
        if health.get('healthy') and health.get('loaded'):
            symbol = f"{Colors.OKGREEN}●{Colors.ENDC}"
            status_text = f"{Colors.OKGREEN}ONLINE{Colors.ENDC}"
        elif health.get('healthy'):
            symbol = f"{Colors.WARNING}◐{Colors.ENDC}"
            status_text = f"{Colors.WARNING}LOADING{Colors.ENDC}"
        else:
            symbol = f"{Colors.FAIL}○{Colors.ENDC}"
            status_text = f"{Colors.FAIL}OFFLINE{Colors.ENDC}"

        print(f"{symbol} {Colors.BOLD}{name}{Colors.ENDC} ({server_type.upper()})")
        print(f"   └─ {host}:{port}")
        print(f"   └─ Model: {model_type}")
        print(f"   └─ Status: {status_text}")

        if health.get('error'):
            print(f"   └─ {Colors.FAIL}Error: {health['error']}{Colors.ENDC}")

        if status and isinstance(status, dict):
            backend = status.get('backend', status.get('model', 'Unknown'))
            print(f"   └─ Backend: {backend}")

            if 'memory_allocated_gb' in status:
                mem = status['memory_allocated_gb']
                print(f"   └─ GPU Memory: {mem:.2f} GB")

        print()

    def verify_model_pairing(self):
        """Verify that paired servers have matching models"""
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}MODEL PAIRING VERIFICATION{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

        # Expected pairs
        pairs = [
            {
                'name': 'Qwen-30B Pair',
                'prefill': '169.254.150.105:8000',
                'decode': '169.254.150.102:8001',
                'model': 'qwen'
            },
            {
                'name': 'GPT-OSS-120B Pair',
                'prefill': '169.254.150.106:8000',
                'decode': '169.254.150.101:8001',
                'model': 'gpt-oss'
            }
        ]

        all_pairs_valid = True

        for pair in pairs:
            print(f"{Colors.BOLD}{pair['name']}{Colors.ENDC}")

            # Check prefill server
            prefill_status = self.results['prefill_servers'].get(pair['prefill'])
            decode_status = self.results['decode_servers'].get(pair['decode'])

            prefill_ok = prefill_status and prefill_status.get('healthy') and prefill_status.get('loaded')
            decode_ok = decode_status and decode_status.get('healthy') and decode_status.get('loaded')

            prefill_model = prefill_status.get('model_type') if prefill_status else None
            decode_model = decode_status.get('model_type') if decode_status else None

            models_match = prefill_model == decode_model == pair['model']

            if prefill_ok and decode_ok and models_match:
                print(f"   {Colors.OKGREEN}✓{Colors.ENDC} Pair Status: {Colors.OKGREEN}OPERATIONAL{Colors.ENDC}")
            else:
                print(f"   {Colors.FAIL}✗{Colors.ENDC} Pair Status: {Colors.FAIL}NOT OPERATIONAL{Colors.ENDC}")
                all_pairs_valid = False

            # Prefill server
            if prefill_ok:
                print(f"   {Colors.OKGREEN}✓{Colors.ENDC} Prefill: {pair['prefill']} ({prefill_model})")
            else:
                print(f"   {Colors.FAIL}✗{Colors.ENDC} Prefill: {pair['prefill']} - {prefill_status.get('error', 'Unknown error') if prefill_status else 'No response'}")

            # Decode server
            if decode_ok:
                print(f"   {Colors.OKGREEN}✓{Colors.ENDC} Decode: {pair['decode']} ({decode_model})")
            else:
                print(f"   {Colors.FAIL}✗{Colors.ENDC} Decode: {pair['decode']} - {decode_status.get('error', 'Unknown error') if decode_status else 'No response'}")

            print()

        self.results['orchestration_valid'] = all_pairs_valid

    def check_backend_implementations(self):
        """Check which backends are implemented"""
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}BACKEND IMPLEMENTATION STATUS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

        backends = {
            'HuggingFace Transformers (DGX Prefill)': {
                'file': 'prefill_server_dgx.py',
                'description': 'GPU-optimized prefill with KV cache generation'
            },
            'MLX (Mac Decode)': {
                'file': 'decode_server_mac.py',
                'description': 'Apple Silicon optimized token generation'
            },
            'Ollama (Alternative)': {
                'file': 'decode_server_ollama.py',
                'description': 'Ollama-based inference backend'
            },
            'llama.cpp (PC Only)': {
                'file': '../models/pc_llamacpp_client.py',
                'description': 'llama.cpp client for standalone PC usage'
            }
        }

        for backend_name, info in backends.items():
            file_path = Path(__file__).parent / info['file']
            exists = file_path.exists()

            if exists:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} {Colors.BOLD}{backend_name}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗{Colors.ENDC} {Colors.BOLD}{backend_name}{Colors.ENDC}")

            print(f"   └─ {info['description']}")
            print(f"   └─ File: {info['file']} {'(exists)' if exists else '(missing)'}")
            print()

        # Note about llama.cpp
        print(f"{Colors.WARNING}⚠ NOTE:{Colors.ENDC} llama.cpp is NOT currently used in the disaggregated architecture.")
        print(f"   Current implementation uses:")
        print(f"   - DGX Sparks: HuggingFace Transformers")
        print(f"   - Mac Studios: MLX (Apple Silicon)")
        print()

    def generate_summary(self):
        """Generate overall summary"""
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}CLUSTER STATUS SUMMARY{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

        # Count servers
        total_prefill = len(self.config['prefill_servers'])
        total_decode = len(self.config['decode_servers'])

        healthy_prefill = sum(1 for s in self.results['prefill_servers'].values()
                            if s.get('healthy') and s.get('loaded'))
        healthy_decode = sum(1 for s in self.results['decode_servers'].values()
                           if s.get('healthy') and s.get('loaded'))

        print(f"Prefill Servers: {healthy_prefill}/{total_prefill} operational")
        print(f"Decode Servers: {healthy_decode}/{total_decode} operational")
        print()

        # Overall status
        if healthy_prefill == total_prefill and healthy_decode == total_decode and self.results['orchestration_valid']:
            self.results['overall_status'] = 'OPERATIONAL'
            print(f"Overall Status: {Colors.OKGREEN}{Colors.BOLD}✓ FULLY OPERATIONAL{Colors.ENDC}")
        elif healthy_prefill > 0 and healthy_decode > 0:
            self.results['overall_status'] = 'DEGRADED'
            print(f"Overall Status: {Colors.WARNING}{Colors.BOLD}◐ PARTIALLY OPERATIONAL{Colors.ENDC}")
        else:
            self.results['overall_status'] = 'DOWN'
            print(f"Overall Status: {Colors.FAIL}{Colors.BOLD}✗ NOT OPERATIONAL{Colors.ENDC}")

        print()

        # Recommendations
        if self.results['overall_status'] != 'OPERATIONAL':
            print(f"{Colors.BOLD}Recommendations:{Colors.ENDC}")

            for server_id, status in self.results['prefill_servers'].items():
                if not status.get('healthy') or not status.get('loaded'):
                    print(f"   • Start prefill server at {server_id}")
                    print(f"     Command: python prefill_server_dgx.py --model <model_path>")

            for server_id, status in self.results['decode_servers'].items():
                if not status.get('healthy') or not status.get('loaded'):
                    print(f"   • Start decode server at {server_id}")
                    print(f"     Command: python decode_server_mac.py --model <model_path>")

            print()

    async def run_verification(self):
        """Run complete verification"""
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}{'='*70}")
        print(f"DISTRIBUTED AI GRADER CLUSTER VERIFICATION")
        print(f"{'='*70}{Colors.ENDC}\n")

        if not self.load_config():
            return False

        await self.verify_all_servers()
        self.verify_model_pairing()
        self.check_backend_implementations()
        self.generate_summary()

        # Save results to JSON
        output_file = Path(__file__).parent / "cluster_status.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nDetailed results saved to: {output_file}")

        return self.results['overall_status'] == 'OPERATIONAL'


async def main():
    verifier = ClusterVerifier()
    success = await verifier.run_verification()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
