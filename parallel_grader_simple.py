#!/usr/bin/env python3
"""
Parallel Batch Grading System - Simple Sequential Version
Processes submissions one at a time but uses the best available server
"""

import requests
import json
import logging
from typing import List, Dict
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleParallelGrader:
    """Simple grader that processes submissions sequentially but efficiently"""

    def __init__(self, config_path: str = "disaggregated_inference/config_parallel.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        logger.info(f"✅ Grader initialized with {len(self.config['prefill_servers'])} prefill and {len(self.config['decode_servers'])} decode servers")

    def grade_batch(self, submissions: List[Dict], model: str = 'gpt-oss:120b') -> List[Dict]:
        """Grade submissions sequentially with disaggregated inference"""

        model_type = 'qwen' if 'qwen' in model.lower() else 'gpt-oss'

        # Find servers for this model
        prefill_server = next((s for s in self.config['prefill_servers'] if s['model'] == model_type), None)
        decode_server = next((s for s in self.config['decode_servers'] if s['model'] == model_type), None)

        if not prefill_server or not decode_server:
            raise ValueError(f"No servers found for model {model_type}")

        logger.info(f"🚀 Grading {len(submissions)} submissions")
        logger.info(f"   Prefill: {prefill_server['name']}")
        logger.info(f"   Decode: {decode_server['name']}")

        batch_start = time.time()
        results = []

        for idx, submission in enumerate(submissions, 1):
            student_id = submission.get('student_id', f'student_{idx}')
            logger.info(f"\n[{idx}/{len(submissions)}] Processing {student_id}...")

            result = self._grade_single(submission, prefill_server, decode_server, model)
            results.append(result)

        batch_time = time.time() - batch_start
        successful = sum(1 for r in results if r['success'])

        logger.info(f"\n📊 Batch Complete!")
        logger.info(f"   Total time: {batch_time:.2f}s")
        logger.info(f"   Successful: {successful}/{len(submissions)}")
        logger.info(f"   Avg time: {batch_time/len(submissions):.2f}s per submission")

        return results

    def _grade_single(self, submission: Dict, prefill_server: Dict, decode_server: Dict, model: str) -> Dict:
        """Grade a single submission"""
        student_id = submission.get('student_id', 'unknown')
        prompt = submission.get('prompt', '')
        max_tokens = submission.get('max_tokens', 500)

        start_time = time.time()

        try:
            # Prefill
            prefill_url = f"http://{prefill_server['host']}:{prefill_server['port']}/prefill"
            prefill_response = requests.post(prefill_url, json={'prompt': prompt}, timeout=60)
            prefill_result = prefill_response.json()

            llama_state = prefill_result.get('llama_state')
            n_tokens = prefill_result.get('n_tokens', 0)
            is_compressed = prefill_result.get('compressed', True)

            logger.info(f"  ✅ Prefill: {n_tokens} tokens @ {prefill_result.get('prefill_speed', 0):.1f} tok/s")

            # Decode  
            decode_host = 'localhost' if prefill_server['host'].startswith('169.254.150.101') else decode_server['host']
            decode_url = f"http://{decode_host}:{decode_server['port']}/decode"
            decode_response = requests.post(decode_url, json={
                'prompt': prompt,
                'llama_state': llama_state,
                'n_tokens': n_tokens,
                'compressed': is_compressed,
                'max_new_tokens': max_tokens,
                'temperature': 0.2
            }, timeout=300)
            decode_result = decode_response.json()

            total_time = time.time() - start_time
            logger.info(f"  ✅ Decode: {decode_result.get('tokens_generated', 0)} tokens @ {decode_result.get('tokens_per_sec', 0):.1f} tok/s")
            logger.info(f"  ⏱️  Total: {total_time:.2f}s")

            return {
                'student_id': student_id,
                'success': True,
                'generated_text': decode_result.get('generated_text', ''),
                'total_time': total_time
            }

        except Exception as e:
            logger.error(f"  ❌ Failed: {e}")
            return {
                'student_id': student_id,
                'success': False,
                'error': str(e),
                'total_time': time.time() - start_time
            }


if __name__ == '__main__':
    # Test with 4 submissions
    submissions = [
        {'student_id': 'student_001', 'prompt': 'Grade this factorial code:\n\ndef factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)\n\nProvide feedback.', 'max_tokens': 500},
        {'student_id': 'student_002', 'prompt': 'Grade this fibonacci code:\n\ndef fib(n):\n    a, b = 0, 1\n    for _ in range(n): a, b = b, a+b\n    return a\n\nProvide feedback.', 'max_tokens': 500},
        {'student_id': 'student_003', 'prompt': 'Grade this bubble sort:\n\ndef bubble(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr)-i-1):\n            if arr[j] > arr[j+1]: arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr\n\nProvide feedback.', 'max_tokens': 500},
        {'student_id': 'student_004', 'prompt': 'Grade this binary search:\n\ndef bsearch(arr, x):\n    l, r = 0, len(arr)-1\n    while l <= r:\n        m = (l+r)//2\n        if arr[m] == x: return m\n        elif arr[m] < x: l = m+1\n        else: r = m-1\n    return -1\n\nProvide feedback.', 'max_tokens': 500},
    ]

    grader = SimpleParallelGrader()
    results = grader.grade_batch(submissions)

    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    for r in results:
        if r['success']:
            print(f"{r['student_id']}: {r['total_time']:.2f}s - {len(r['generated_text'])} chars")
        else:
            print(f"{r['student_id']}: FAILED - {r['error']}")
