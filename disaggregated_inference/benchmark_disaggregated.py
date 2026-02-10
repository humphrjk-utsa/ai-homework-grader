#!/usr/bin/env python3
"""
Benchmark: Mac-only vs Disaggregated Inference
Compare performance of different inference strategies
"""

import asyncio
import time
import json
import requests
from typing import Dict, List
import statistics
from orchestrator import DisaggregatedInference

class DisaggregatedBenchmark:
    """Benchmark disaggregated vs Mac-only inference"""

    def __init__(self, config_path: str = "config_current.json"):
        with open(config_path) as f:
            self.config = json.load(f)

        self.orchestrator = DisaggregatedInference(self.config)
        self.results = {
            'mac_only': [],
            'disaggregated': [],
            'dgx_prefill_only': []
        }

    async def benchmark_mac_only(self, prompt: str, model_type: str, max_tokens: int = 100) -> Dict:
        """Benchmark Mac-only generation (full prefill + decode on Mac)"""
        print(f"\n🖥️  Benchmarking Mac-only generation...")

        # Get Mac decode server for this model type
        decode_server = None
        for server in self.config['decode_servers']:
            if server['model'] == model_type:
                decode_server = server
                break

        if not decode_server:
            return {'error': 'No decode server found for model type'}

        start_time = time.time()

        try:
            url = f"http://{decode_server['host']}:{decode_server['port']}/generate"
            response = requests.post(
                url,
                json={
                    'prompt': prompt,
                    'max_tokens': max_tokens,
                    'temperature': 0.7
                },
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                total_time = time.time() - start_time

                result = {
                    'method': 'mac_only',
                    'model_type': model_type,
                    'server': f"{decode_server['host']}:{decode_server['port']}",
                    'total_time': total_time,
                    'generation_time': data.get('generation_time', total_time),
                    'response_length': len(data.get('response', '')),
                    'tokens_generated': data.get('metrics', {}).get('completion_tokens', 0),
                    'tokens_per_sec': data.get('metrics', {}).get('tokens_per_sec', 0)
                }

                print(f"   ✓ Total time: {total_time:.3f}s")
                print(f"   ✓ Speed: {result['tokens_per_sec']:.1f} tok/s")

                return result
            else:
                return {'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'error': str(e)}

    async def benchmark_dgx_prefill_only(self, prompt: str, model_type: str) -> Dict:
        """Benchmark DGX prefill speed only (KV cache generation)"""
        print(f"\n🎮 Benchmarking DGX prefill speed...")

        # Get DGX prefill server for this model type
        prefill_server = None
        for server in self.config['prefill_servers']:
            if server['model'] == model_type:
                prefill_server = server
                break

        if not prefill_server:
            return {'error': 'No prefill server found for model type'}

        start_time = time.time()

        try:
            url = f"http://{prefill_server['host']}:{prefill_server['port']}/prefill"
            response = requests.post(
                url,
                json={'prompt': prompt},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                total_time = time.time() - start_time

                result = {
                    'method': 'dgx_prefill_only',
                    'model_type': model_type,
                    'server': f"{prefill_server['host']}:{prefill_server['port']}",
                    'prefill_time': data.get('prefill_time', total_time),
                    'prompt_tokens': data.get('prompt_tokens', 0),
                    'kv_cache_size_mb': data.get('kv_cache_size_mb', 0),
                    'prefill_speed': data.get('prompt_tokens', 0) / data.get('prefill_time', 1) if data.get('prefill_time', 0) > 0 else 0
                }

                print(f"   ✓ Prefill time: {result['prefill_time']:.3f}s")
                print(f"   ✓ Prefill speed: {result['prefill_speed']:.1f} tok/s")
                print(f"   ✓ KV cache: {result['kv_cache_size_mb']:.1f} MB")

                return result
            else:
                return {'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'error': str(e)}

    async def benchmark_disaggregated(self, prompt: str, model_type: str, max_tokens: int = 100) -> Dict:
        """Benchmark full disaggregated inference (DGX prefill → Mac decode)"""
        print(f"\n⚡ Benchmarking disaggregated inference...")

        result = await self.orchestrator.generate(
            prompt=prompt,
            model_type=model_type,
            max_tokens=max_tokens
        )

        if 'error' not in result:
            print(f"   ✓ Total time: {result.get('total_time', 0):.3f}s")
            print(f"   ✓ Prefill time: {result.get('prefill_time', 0):.3f}s")
            print(f"   ✓ Decode time: {result.get('decode_time', 0):.3f}s")
            print(f"   ✓ Speed: {result.get('tokens_per_sec', 0):.1f} tok/s")

        return result

    async def run_comparison(self, prompt: str, model_type: str = 'qwen', max_tokens: int = 100, iterations: int = 3):
        """Run complete comparison benchmark"""
        print("="*80)
        print("DISAGGREGATED vs MAC-ONLY BENCHMARK")
        print("="*80)
        print(f"\nPrompt: {prompt[:100]}...")
        print(f"Model: {model_type}")
        print(f"Max tokens: {max_tokens}")
        print(f"Iterations: {iterations}")
        print()

        # Run multiple iterations for statistical significance
        for i in range(iterations):
            print(f"\n{'='*80}")
            print(f"ITERATION {i+1}/{iterations}")
            print(f"{'='*80}")

            # Benchmark DGX prefill speed
            dgx_result = await self.benchmark_dgx_prefill_only(prompt, model_type)
            if 'error' not in dgx_result:
                self.results['dgx_prefill_only'].append(dgx_result)

            # Benchmark Mac-only generation
            mac_result = await self.benchmark_mac_only(prompt, model_type, max_tokens)
            if 'error' not in mac_result:
                self.results['mac_only'].append(mac_result)

            # Benchmark disaggregated generation
            disagg_result = await self.benchmark_disaggregated(prompt, model_type, max_tokens)
            if 'error' not in disagg_result:
                self.results['disaggregated'].append(disagg_result)

            # Small delay between iterations
            await asyncio.sleep(2)

        # Generate comparison report
        self.generate_report()

    def generate_report(self):
        """Generate detailed comparison report"""
        print("\n" + "="*80)
        print("BENCHMARK RESULTS")
        print("="*80)

        # DGX Prefill Performance
        if self.results['dgx_prefill_only']:
            print("\n🎮 DGX PREFILL PERFORMANCE (GPU)")
            print("-" * 80)

            prefill_times = [r['prefill_time'] for r in self.results['dgx_prefill_only']]
            prefill_speeds = [r['prefill_speed'] for r in self.results['dgx_prefill_only']]

            print(f"Average prefill time:  {statistics.mean(prefill_times):.3f}s ± {statistics.stdev(prefill_times) if len(prefill_times) > 1 else 0:.3f}s")
            print(f"Average prefill speed: {statistics.mean(prefill_speeds):.1f} tok/s")
            print(f"Min prefill time:      {min(prefill_times):.3f}s")
            print(f"Max prefill time:      {max(prefill_times):.3f}s")

        # Mac-only Performance
        if self.results['mac_only']:
            print("\n🖥️  MAC-ONLY PERFORMANCE (Full generation on Mac)")
            print("-" * 80)

            mac_times = [r['total_time'] for r in self.results['mac_only']]
            mac_speeds = [r['tokens_per_sec'] for r in self.results['mac_only'] if r['tokens_per_sec'] > 0]

            print(f"Average total time:    {statistics.mean(mac_times):.3f}s ± {statistics.stdev(mac_times) if len(mac_times) > 1 else 0:.3f}s")
            if mac_speeds:
                print(f"Average speed:         {statistics.mean(mac_speeds):.1f} tok/s")
            print(f"Min total time:        {min(mac_times):.3f}s")
            print(f"Max total time:        {max(mac_times):.3f}s")

        # Disaggregated Performance
        if self.results['disaggregated']:
            print("\n⚡ DISAGGREGATED PERFORMANCE (DGX prefill → Mac decode)")
            print("-" * 80)

            disagg_times = [r['total_time'] for r in self.results['disaggregated']]
            disagg_prefill = [r['prefill_time'] for r in self.results['disaggregated'] if 'prefill_time' in r]
            disagg_decode = [r['decode_time'] for r in self.results['disaggregated'] if 'decode_time' in r]
            disagg_speeds = [r['tokens_per_sec'] for r in self.results['disaggregated'] if r.get('tokens_per_sec', 0) > 0]

            print(f"Average total time:    {statistics.mean(disagg_times):.3f}s ± {statistics.stdev(disagg_times) if len(disagg_times) > 1 else 0:.3f}s")
            if disagg_prefill:
                print(f"Average prefill time:  {statistics.mean(disagg_prefill):.3f}s")
            if disagg_decode:
                print(f"Average decode time:   {statistics.mean(disagg_decode):.3f}s")
            if disagg_speeds:
                print(f"Average speed:         {statistics.mean(disagg_speeds):.1f} tok/s")

        # Comparison
        if self.results['mac_only'] and self.results['disaggregated']:
            print("\n📊 COMPARISON")
            print("="*80)

            mac_avg = statistics.mean([r['total_time'] for r in self.results['mac_only']])
            disagg_avg = statistics.mean([r['total_time'] for r in self.results['disaggregated']])

            if disagg_avg < mac_avg:
                speedup = (mac_avg - disagg_avg) / mac_avg * 100
                print(f"✅ Disaggregated is FASTER by {speedup:.1f}%")
                print(f"   Time saved: {mac_avg - disagg_avg:.3f}s per request")
            else:
                slowdown = (disagg_avg - mac_avg) / mac_avg * 100
                print(f"⚠️  Mac-only is FASTER by {slowdown:.1f}%")
                print(f"   Disaggregated overhead: {disagg_avg - mac_avg:.3f}s")

            print(f"\nMac-only avg:        {mac_avg:.3f}s")
            print(f"Disaggregated avg:   {disagg_avg:.3f}s")

            # Analyze where time is spent
            if disagg_prefill and disagg_decode:
                avg_prefill = statistics.mean(disagg_prefill)
                avg_decode = statistics.mean(disagg_decode)
                network_overhead = disagg_avg - (avg_prefill + avg_decode)

                print(f"\nTime breakdown (disaggregated):")
                print(f"  Prefill (DGX):     {avg_prefill:.3f}s ({avg_prefill/disagg_avg*100:.1f}%)")
                print(f"  Decode (Mac):      {avg_decode:.3f}s ({avg_decode/disagg_avg*100:.1f}%)")
                print(f"  Network overhead:  {network_overhead:.3f}s ({network_overhead/disagg_avg*100:.1f}%)")

        # Save results to JSON
        with open('benchmark_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print("\n" + "="*80)
        print("Results saved to: benchmark_results.json")
        print("="*80 + "\n")


async def main():
    """Run benchmark suite"""
    benchmark = DisaggregatedBenchmark()

    # Test prompts
    test_cases = [
        {
            'name': 'Short code completion',
            'prompt': 'def fibonacci(n):',
            'model_type': 'qwen',
            'max_tokens': 50
        },
        {
            'name': 'Medium code completion',
            'prompt': '''Write a Python function to implement a binary search tree with insert, search, and delete operations. Include proper documentation.

def binary_search_tree():''',
            'model_type': 'qwen',
            'max_tokens': 150
        },
        {
            'name': 'Long explanation',
            'prompt': 'Explain the concept of recursion in programming with examples:',
            'model_type': 'gpt-oss',
            'max_tokens': 200
        }
    ]

    # Run benchmarks
    for test_case in test_cases:
        print("\n" + "="*80)
        print(f"TEST CASE: {test_case['name']}")
        print("="*80)

        await benchmark.run_comparison(
            prompt=test_case['prompt'],
            model_type=test_case['model_type'],
            max_tokens=test_case['max_tokens'],
            iterations=3
        )


if __name__ == '__main__':
    asyncio.run(main())
