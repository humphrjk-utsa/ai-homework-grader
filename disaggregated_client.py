#!/usr/bin/env python3
"""
Disaggregated Inference Client for AI Homework Grader
Updated to use Parallax distributed inference cluster (Mac Studios + DGX Sparks)
"""
import requests
import time
import logging
import json
import os
from typing import Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class DisaggregatedClient:
    """Client for Parallax distributed inference cluster

    This client uses Parallax to distribute inference across:
    - Mac Studio 1 (M3 Ultra 512GB) - Scheduler
    - Mac Studio 2 (M4 Ultra 128GB) - Worker
    - DGX Spark 1 (spark-2935) - GPU prefill
    - DGX Spark 2 (RR191562IP01) - GPU prefill

    Maintains backward compatibility with the old llama.cpp KV cache interface.
    """

    def __init__(self, config_path: str = "cluster_config.json"):
        """Initialize Parallax client with configuration

        Args:
            config_path: Path to Parallax config (defaults to cluster_config.json)
                        Falls back to disaggregated_inference/config_current.json for compatibility
        """
        # Try loading Parallax config first
        self.config = {}
        self.scheduler_url = "http://169.254.150.101:3001"
        self.api_url = f"{self.scheduler_url}/v1/chat/completions"
        self.timeout = 300
        self.last_response_times = {}

        # Try to load config
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                parallax_config = self.config.get('parallax', {})
                self.scheduler_url = parallax_config.get('scheduler_url', self.scheduler_url)
                self.api_url = f"{self.scheduler_url}/v1/chat/completions"
        elif os.path.exists('disaggregated_inference/config_current.json'):
            # Fallback to old config for compatibility
            with open('disaggregated_inference/config_current.json', 'r') as f:
                old_config = json.load(f)
                # Old config doesn't have Parallax settings, use defaults
                logger.info("Using legacy config, defaulting to Parallax scheduler")

        # Verify Parallax is available
        self._verify_connection()

        logger.info(f"✅ Disaggregated client initialized (Parallax)")
        logger.info(f"   Scheduler: {self.scheduler_url}")

    def _verify_connection(self):
        """Verify Parallax scheduler is reachable"""
        try:
            response = requests.get(f"{self.scheduler_url}/", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Parallax scheduler is online")
            else:
                logger.warning(f"⚠️ Parallax scheduler returned {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Could not reach Parallax scheduler: {e}")

    def _get_server_url(self, server: Dict, endpoint: str) -> str:
        """Legacy method for compatibility - now returns Parallax API URL"""
        return self.api_url

    def generate(self, model: str, prompt: str, max_tokens: int = 2000) -> Tuple[str, Dict]:
        """
        Generate text using Parallax distributed inference

        Args:
            model: Model name (e.g., "qwen3-coder:30b" or "gpt-oss:120b")
                   Note: With Parallax, the model is determined by cluster configuration
            prompt: Input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Tuple of (response_text, metrics_dict)
        """
        start_time = time.time()

        # Determine temperature based on model type (for legacy compatibility)
        if 'qwen' in model.lower() or 'coder' in model.lower():
            model_key = 'qwen'
            temperature = 0.1
            system_message = "You are an expert code analyzer for R programming and data analytics. Analyze the student's code and provide structured feedback in JSON format."
        else:
            model_key = 'gpt-oss'
            temperature = 0.3
            system_message = "You are an expert instructor providing feedback on student submissions. Generate constructive, detailed feedback in JSON format."

        logger.info(f"🔄 Using Parallax cluster for {model_key}")
        logger.info(f"   Scheduler: {self.scheduler_url}")

        try:
            # Build messages for OpenAI-compatible API
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]

            payload = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
                "chat_template_kwargs": {"enable_thinking": False}
            }

            logger.info(f"🚀 Sending request to Parallax cluster...")
            request_start = time.time()

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code != 200:
                raise Exception(f"Parallax API failed: {response.status_code} - {response.text}")

            result = response.json()
            total_time = time.time() - start_time
            request_time = time.time() - request_start

            # Extract response content
            generated_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')

            # Extract usage metrics
            usage = result.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)

            # Calculate speeds
            prefill_speed = prompt_tokens / (request_time * 0.3) if request_time > 0 else 0  # Estimate
            decode_speed = completion_tokens / (request_time * 0.7) if request_time > 0 else 0  # Estimate

            logger.info(f"✅ Generation complete: {completion_tokens} tokens in {total_time:.2f}s")
            logger.info(f"   Throughput: {completion_tokens / total_time:.1f} tok/s")

            # Build metrics dict (compatible with old interface)
            metrics = {
                'prefill_time': request_time * 0.3,  # Estimated prefill portion
                'decode_time': request_time * 0.7,   # Estimated decode portion
                'total_time': total_time,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'prefill_speed': prefill_speed,
                'decode_speed': decode_speed,
                'tokens_per_second': completion_tokens / total_time if total_time > 0 else 0,
                'state_size_mb': 0,  # Not applicable for Parallax
                'method': 'parallax_distributed',
                'prefill_server': f"Parallax Cluster ({self.scheduler_url})",
                'decode_server': f"Parallax Cluster ({self.scheduler_url})"
            }

            # Store for diagnostics
            self.last_response_times[model_key] = total_time
            self.last_response_times[f'{model_key}_metrics'] = metrics

            return generated_text, metrics

        except Exception as e:
            logger.error(f"❌ Parallax inference failed: {e}")
            raise

    def generate_parallel(self, code_prompt: str, feedback_prompt: str,
                          code_max_tokens: int = 2400,
                          feedback_max_tokens: int = 3500) -> Dict:
        """Generate both code analysis and feedback in parallel

        This uses ThreadPoolExecutor to run both generations concurrently,
        taking advantage of Parallax's ability to handle multiple requests.

        Args:
            code_prompt: Prompt for code analysis
            feedback_prompt: Prompt for feedback generation
            code_max_tokens: Max tokens for code analysis
            feedback_max_tokens: Max tokens for feedback

        Returns:
            Dict with 'code_analysis', 'feedback', and timing metrics
        """
        logger.info(f"🚀 Starting parallel Parallax generation...")
        logger.info(f"   Scheduler: {self.scheduler_url}")

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                start_time = time.time()

                # Submit both tasks
                logger.info(f"📤 Submitting code analysis task...")
                code_future = executor.submit(
                    self.generate, 'qwen3-coder:30b', code_prompt, code_max_tokens
                )
                logger.info(f"📤 Submitting feedback task...")
                feedback_future = executor.submit(
                    self.generate, 'gpt-oss:120b', feedback_prompt, feedback_max_tokens
                )

                # Get results
                logger.info(f"⏳ Waiting for code analysis result...")
                code_result, code_metrics = code_future.result(timeout=self.timeout)
                logger.info(f"✅ Code analysis received: {len(code_result) if code_result else 0} chars")

                logger.info(f"⏳ Waiting for feedback result...")
                feedback_result, feedback_metrics = feedback_future.result(timeout=self.timeout)
                logger.info(f"✅ Feedback received: {len(feedback_result) if feedback_result else 0} chars")

                total_time = time.time() - start_time

                qwen_time = code_metrics.get('total_time', 0)
                gemma_time = feedback_metrics.get('total_time', 0)
                sequential_time = qwen_time + gemma_time

                return {
                    'code_analysis': code_result,
                    'feedback': feedback_result,
                    'parallel_time': total_time,
                    'qwen_time': qwen_time,
                    'gemma_time': gemma_time,
                    'parallel_efficiency': sequential_time / total_time if total_time > 0 else 0,
                    'qwen_metrics': code_metrics,
                    'gemma_metrics': feedback_metrics,
                    'performance_metrics': {
                        'qwen': code_metrics,
                        'gemma': feedback_metrics,
                        'total_tokens': code_metrics.get('total_tokens', 0) + feedback_metrics.get('total_tokens', 0),
                        'combined_tokens_per_second': (
                            code_metrics.get('completion_tokens', 0) + feedback_metrics.get('completion_tokens', 0)
                        ) / total_time if total_time > 0 else 0
                    }
                }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"❌ Parallel generation failed: {e}")
            logger.error(f"Full traceback:\n{error_details}")

            return {
                'code_analysis': None,
                'feedback': None,
                'parallel_time': 0,
                'error': f"{type(e).__name__}: {str(e)}"
            }

    def check_status(self) -> Dict:
        """Check Parallax cluster status

        Returns:
            Dict with cluster status information
        """
        try:
            response = requests.get(f"{self.scheduler_url}/", timeout=5)
            scheduler_online = response.status_code == 200
        except:
            scheduler_online = False

        return {
            'scheduler_online': scheduler_online,
            'scheduler_url': self.scheduler_url,
            'method': 'parallax_distributed',
            'distributed_ready': scheduler_online
        }

    def get_performance_diagnostics(self) -> Dict:
        """Get detailed performance diagnostics

        Returns:
            Dict with performance metrics from last generation
        """
        qwen_metrics = self.last_response_times.get('qwen_metrics', {})
        gemma_metrics = self.last_response_times.get('gemma_metrics', {})

        return {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'backend': 'parallax_distributed',
            'scheduler_url': self.scheduler_url,
            'qwen_performance': {
                'model': 'Parallax Cluster',
                'server': self.scheduler_url,
                'prompt_tokens': qwen_metrics.get('prompt_tokens', 0),
                'output_tokens': qwen_metrics.get('completion_tokens', 0),
                'total_tokens': qwen_metrics.get('total_tokens', 0),
                'generation_time_seconds': qwen_metrics.get('total_time', 0),
                'tokens_per_second': qwen_metrics.get('tokens_per_second', 0)
            },
            'gemma_performance': {
                'model': 'Parallax Cluster',
                'server': self.scheduler_url,
                'prompt_tokens': gemma_metrics.get('prompt_tokens', 0),
                'output_tokens': gemma_metrics.get('completion_tokens', 0),
                'total_tokens': gemma_metrics.get('total_tokens', 0),
                'generation_time_seconds': gemma_metrics.get('total_time', 0),
                'tokens_per_second': gemma_metrics.get('tokens_per_second', 0)
            },
            'combined_metrics': {
                'total_tokens_processed': qwen_metrics.get('total_tokens', 0) + gemma_metrics.get('total_tokens', 0),
                'total_output_tokens': qwen_metrics.get('completion_tokens', 0) + gemma_metrics.get('completion_tokens', 0)
            }
        }


# Backward compatibility: create aliases
ParallaxDisaggregatedClient = DisaggregatedClient


def test_connection():
    """Test Parallax connection"""
    print("=" * 60)
    print("Testing Parallax Disaggregated Client")
    print("=" * 60)

    try:
        client = DisaggregatedClient()
        status = client.check_status()

        print(f"\nScheduler Status:")
        print(f"  Online: {status['scheduler_online']}")
        print(f"  URL: {status['scheduler_url']}")
        print(f"  Method: {status['method']}")

        if status['scheduler_online']:
            print("\n✅ Parallax cluster is ready!")

            # Test a simple generation
            print("\nTesting generation...")
            result, metrics = client.generate(
                model='qwen3-coder:30b',
                prompt='What is 2 + 2? Answer with just the number.',
                max_tokens=50
            )

            print(f"\nResult: {result[:200]}...")
            print(f"Tokens: {metrics['completion_tokens']}")
            print(f"Time: {metrics['total_time']:.2f}s")
            print(f"Speed: {metrics['tokens_per_second']:.1f} tok/s")

            return True
        else:
            print("\n❌ Parallax cluster is not available")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_connection()
