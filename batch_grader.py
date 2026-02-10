#!/usr/bin/env python3
"""
Simple Batch Grader with Round-Robin Server Selection
Processes student submissions sequentially using disaggregated inference
"""

from disaggregated_client import DisaggregatedClient
import time
import logging
from typing import List, Dict
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchGrader:
    """Simple batch grader using disaggregated inference"""

    def __init__(self):
        self.client = DisaggregatedClient()
        logger.info("✅ Batch Grader initialized")

    def grade_batch(
        self,
        submissions: List[Dict],
        model: str = 'gpt-oss:120b',
        max_tokens: int = 2000
    ) -> List[Dict]:
        """
        Grade a batch of student submissions sequentially

        Args:
            submissions: List of dicts with 'student_id' and 'prompt'
            model: Model to use for grading
            max_tokens: Max tokens to generate per submission

        Returns:
            List of results with feedback and metrics
        """

        logger.info(f"🚀 Starting batch grading")
        logger.info(f"   Total submissions: {len(submissions)}")
        logger.info(f"   Model: {model}")
        logger.info(f"   Max tokens: {max_tokens}")
        logger.info("")

        batch_start = time.time()
        results = []

        for idx, submission in enumerate(submissions, 1):
            student_id = submission.get('student_id', f'student_{idx}')
            prompt = submission.get('prompt', '')

            logger.info(f"[{idx}/{len(submissions)}] 📝 Grading {student_id}...")

            try:
                start_time = time.time()

                # Use disaggregated inference
                feedback, metrics = self.client.generate(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens
                )

                total_time = time.time() - start_time

                # Log results
                logger.info(f"  ✅ Complete in {total_time:.1f}s")
                logger.info(f"     Prefill: {metrics.get('prefill_time', 0):.2f}s @ {metrics.get('prefill_speed', 0):.1f} tok/s")
                logger.info(f"     Decode:  {metrics.get('decode_time', 0):.2f}s @ {metrics.get('decode_speed', 0):.1f} tok/s")
                logger.info(f"     Tokens:  {metrics.get('completion_tokens', 0)} generated")
                logger.info("")

                results.append({
                    'student_id': student_id,
                    'success': True,
                    'feedback': feedback,
                    'metrics': metrics,
                    'total_time': total_time
                })

            except Exception as e:
                logger.error(f"  ❌ Failed: {e}")
                logger.info("")
                results.append({
                    'student_id': student_id,
                    'success': False,
                    'error': str(e),
                    'total_time': time.time() - start_time
                })

        # Summary statistics
        batch_time = time.time() - batch_start
        successful = sum(1 for r in results if r['success'])
        total_tokens = sum(
            r.get('metrics', {}).get('completion_tokens', 0)
            for r in results if r['success']
        )
        avg_time = batch_time / len(submissions) if submissions else 0

        logger.info("=" * 80)
        logger.info("📊 BATCH GRADING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total time:        {batch_time:.1f}s")
        logger.info(f"Successful:        {successful}/{len(submissions)}")
        logger.info(f"Total tokens:      {total_tokens:,}")
        logger.info(f"Avg time/student:  {avg_time:.1f}s")
        logger.info(f"Throughput:        {len(submissions)/batch_time*3600:.1f} students/hour")
        logger.info("=" * 80)

        return results

    def save_results(self, results: List[Dict], output_file: str):
        """Save grading results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"💾 Results saved to {output_file}")


def main():
    """Test with sample submissions"""

    # Sample student submissions
    test_submissions = [
        {
            'student_id': 'student_001',
            'prompt': '''Grade the following Python code for a factorial function:

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)
```

Requirements:
1. Correctly calculates factorial
2. Handles edge case (n=0)
3. Code quality and efficiency

Provide detailed feedback and a grade out of 10.'''
        },
        {
            'student_id': 'student_002',
            'prompt': '''Grade the following Python code for a Fibonacci function:

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

Requirements:
1. Correctly calculates Fibonacci numbers
2. Efficient implementation
3. Code quality

Provide detailed feedback and a grade out of 10.'''
        },
    ]

    # Create grader and process submissions
    grader = BatchGrader()
    results = grader.grade_batch(
        submissions=test_submissions,
        model='gpt-oss:120b',
        max_tokens=500
    )

    # Display results
    print("\n" + "=" * 80)
    print("GRADING RESULTS")
    print("=" * 80 + "\n")

    for result in results:
        if result['success']:
            print(f"Student: {result['student_id']}")
            print(f"Time: {result['total_time']:.1f}s")
            print(f"Feedback preview:")
            print(result['feedback'][:300] + "...")
            print("-" * 80)
        else:
            print(f"Student: {result['student_id']} - FAILED")
            print(f"Error: {result['error']}")
            print("-" * 80)

    # Save results
    grader.save_results(results, 'batch_grading_results.json')


if __name__ == '__main__':
    main()
