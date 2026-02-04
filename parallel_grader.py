#!/usr/bin/env python3
"""
Parallel Batch Grading System
Processes multiple student notebooks concurrently using all available DGX and Mac resources
"""

import asyncio
import aiohttp
import json
import logging
from typing import List, Dict, Tuple
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ParallelGrader:
    """Coordinates parallel grading across multiple DGX prefill and Mac decode servers"""

    def __init__(self, config_path: str = "disaggregated_inference/config_parallel.json"):
        """Initialize with configuration for all servers"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Separate servers by type and model
        self.prefill_servers = {
            'qwen': [],
            'gpt-oss': []
        }
        self.decode_servers = {
            'qwen': [],
            'gpt-oss': []
        }

        # Organize servers by model type
        for server in self.config['prefill_servers']:
            model_type = server['model']
            self.prefill_servers[model_type].append(server)

        for server in self.config['decode_servers']:
            model_type = server['model']
            self.decode_servers[model_type].append(server)

        logger.info(f"✅ Parallel Grader initialized")
        logger.info(f"   Prefill capacity: qwen={len(self.prefill_servers['qwen'])}, gpt-oss={len(self.prefill_servers['gpt-oss'])}")
        logger.info(f"   Decode capacity: qwen={len(self.decode_servers['qwen'])}, gpt-oss={len(self.decode_servers['gpt-oss'])}")

    def _get_server_url(self, server: Dict, endpoint: str) -> str:
        """Get server URL, using localhost if it's the local machine"""
        import socket
        host = server['host']
        port = server['port']

        # Check if this is a local IP
        try:
            hostname = socket.gethostname()
            local_ips = [socket.gethostbyname(hostname), '127.0.0.1', 'localhost']
            if host in local_ips or host.startswith('169.254.150.101'):
                host = 'localhost'
        except:
            pass

        return f"http://{host}:{port}{endpoint}"

    async def _process_single_submission(
        self,
        session: aiohttp.ClientSession,
        submission: Dict,
        prefill_server: Dict,
        decode_server: Dict,
        model: str
    ) -> Dict:
        """Process a single student submission through prefill and decode"""

        student_id = submission.get('student_id', 'unknown')
        prompt = submission.get('prompt', '')
        max_tokens = submission.get('max_tokens', 2000)

        start_time = time.time()

        try:
            # Step 1: Prefill on DGX
            prefill_url = self._get_server_url(prefill_server, '/prefill')
            logger.info(f"📝 [{student_id}] Starting prefill on {prefill_server['name']}")

            prefill_start = time.time()
            async with session.post(
                prefill_url,
                json={'prompt': prompt, 'return_state': True},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                prefill_result = await response.json()

            prefill_time = time.time() - prefill_start

            llama_state = prefill_result.get('llama_state')
            n_tokens = prefill_result.get('n_tokens', 0)
            is_compressed = prefill_result.get('compressed', True)
            prefill_speed = prefill_result.get('prefill_speed', 0)

            logger.info(f"✅ [{student_id}] Prefill complete: {n_tokens} tokens @ {prefill_speed:.1f} tok/s ({prefill_time:.2f}s)")

            # Step 2: Decode on Mac
            decode_url = self._get_server_url(decode_server, '/decode')
            logger.info(f"🚀 [{student_id}] Starting decode on {decode_server['name']}")

            decode_start = time.time()
            async with session.post(
                decode_url,
                json={
                    'prompt': prompt,
                    'llama_state': llama_state,
                    'n_tokens': n_tokens,
                    'compressed': is_compressed,
                    'max_new_tokens': max_tokens,
                    'temperature': 0.2
                },
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                decode_result = await response.json()

            decode_time = time.time() - decode_start
            total_time = time.time() - start_time

            generated_text = decode_result.get('generated_text', '')
            tokens_generated = decode_result.get('tokens_generated', 0)
            decode_speed = decode_result.get('tokens_per_sec', 0)

            logger.info(f"✅ [{student_id}] Decode complete: {tokens_generated} tokens @ {decode_speed:.1f} tok/s ({decode_time:.2f}s)")
            logger.info(f"⏱️  [{student_id}] Total time: {total_time:.2f}s")

            return {
                'student_id': student_id,
                'success': True,
                'generated_text': generated_text,
                'metrics': {
                    'prefill_time': prefill_time,
                    'decode_time': decode_time,
                    'total_time': total_time,
                    'prompt_tokens': n_tokens,
                    'completion_tokens': tokens_generated,
                    'prefill_speed': prefill_speed,
                    'decode_speed': decode_speed,
                    'prefill_server': prefill_server['name'],
                    'decode_server': decode_server['name']
                }
            }

        except Exception as e:
            logger.error(f"❌ [{student_id}] Failed: {e}")
            return {
                'student_id': student_id,
                'success': False,
                'error': str(e),
                'metrics': {
                    'total_time': time.time() - start_time
                }
            }

    async def grade_batch_async(
        self,
        submissions: List[Dict],
        model: str = 'gpt-oss:120b',
        max_concurrent: int = 4
    ) -> List[Dict]:
        """
        Grade multiple submissions in parallel

        Args:
            submissions: List of dicts with 'student_id', 'prompt', 'max_tokens'
            model: Model to use ('gpt-oss:120b' or 'qwen3-coder:30b')
            max_concurrent: Maximum concurrent requests (default: 4 for 2 DGX + 2 Mac)

        Returns:
            List of results with generated text and metrics
        """

        # Determine model type
        model_type = 'qwen' if 'qwen' in model.lower() else 'gpt-oss'

        # Get available servers
        prefill_pool = self.prefill_servers[model_type]
        decode_pool = self.decode_servers[model_type]

        if not prefill_pool or not decode_pool:
            raise ValueError(f"No servers available for model type: {model_type}")

        logger.info(f"🚀 Starting batch grading")
        logger.info(f"   Total submissions: {len(submissions)}")
        logger.info(f"   Model: {model}")
        logger.info(f"   Concurrent workers: {max_concurrent}")
        logger.info(f"   Prefill servers: {len(prefill_pool)}")
        logger.info(f"   Decode servers: {len(decode_pool)}")

        batch_start = time.time()

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(idx: int, submission: Dict):
            """Process submission with concurrency control"""
            async with semaphore:
                # Round-robin server selection
                prefill_server = prefill_pool[idx % len(prefill_pool)]
                decode_server = decode_pool[idx % len(decode_pool)]

                return await self._process_single_submission(
                    session,
                    submission,
                    prefill_server,
                    decode_server,
                    model
                )

        # Process all submissions concurrently (up to max_concurrent at a time)
        async with aiohttp.ClientSession() as session:
            tasks = [
                process_with_semaphore(idx, submission)
                for idx, submission in enumerate(submissions)
            ]
            results = await asyncio.gather(*tasks)

        batch_time = time.time() - batch_start

        # Calculate statistics
        successful = sum(1 for r in results if r['success'])
        total_tokens = sum(r['metrics'].get('completion_tokens', 0) for r in results if r['success'])
        avg_time = sum(r['metrics']['total_time'] for r in results if r['success']) / max(successful, 1)
        throughput = len(submissions) / batch_time

        logger.info(f"")
        logger.info(f"📊 Batch Grading Complete!")
        logger.info(f"   Total time: {batch_time:.2f}s")
        logger.info(f"   Successful: {successful}/{len(submissions)}")
        logger.info(f"   Total tokens generated: {total_tokens}")
        logger.info(f"   Average time per submission: {avg_time:.2f}s")
        logger.info(f"   Throughput: {throughput:.2f} submissions/sec")
        logger.info(f"   Speedup vs sequential: {(len(submissions) * avg_time / batch_time):.2f}x")

        return results

    def grade_batch(
        self,
        submissions: List[Dict],
        model: str = 'gpt-oss:120b',
        max_concurrent: int = 4
    ) -> List[Dict]:
        """
        Synchronous wrapper for grade_batch_async

        Args:
            submissions: List of dicts with 'student_id', 'prompt', 'max_tokens'
            model: Model to use
            max_concurrent: Maximum concurrent requests

        Returns:
            List of results
        """
        return asyncio.run(self.grade_batch_async(submissions, model, max_concurrent))


def main():
    """Example usage"""

    # Create test submissions
    test_submissions = [
        {
            'student_id': 'student_001',
            'prompt': '''Grade this Python code:

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

Provide detailed feedback on correctness, efficiency, and code quality.''',
            'max_tokens': 500
        },
        {
            'student_id': 'student_002',
            'prompt': '''Grade this Python code:

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

Provide detailed feedback on correctness, efficiency, and code quality.''',
            'max_tokens': 500
        },
        {
            'student_id': 'student_003',
            'prompt': '''Grade this Python code:

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

Provide detailed feedback on correctness, efficiency, and code quality.''',
            'max_tokens': 500
        },
        {
            'student_id': 'student_004',
            'prompt': '''Grade this Python code:

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

Provide detailed feedback on correctness, efficiency, and code quality.''',
            'max_tokens': 500
        }
    ]

    # Grade in parallel
    grader = ParallelGrader()
    results = grader.grade_batch(test_submissions, model='gpt-oss:120b', max_concurrent=4)

    # Print results
    print("\n" + "="*80)
    print("GRADING RESULTS")
    print("="*80 + "\n")

    for result in results:
        if result['success']:
            print(f"Student: {result['student_id']}")
            print(f"Time: {result['metrics']['total_time']:.2f}s")
            print(f"Tokens: {result['metrics']['completion_tokens']}")
            print(f"Feedback preview: {result['generated_text'][:200]}...")
            print("-" * 80)
        else:
            print(f"Student: {result['student_id']} - FAILED: {result['error']}")
            print("-" * 80)


if __name__ == '__main__':
    main()
