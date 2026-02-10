#!/usr/bin/env python3
"""
vLLM Client for Direct Inference on DGX Sparks
Routes code analysis to Spark 1 (Qwen FP8) and feedback to Spark 2 (GPT-OSS MXFP4)
"""

import requests
import time
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor


class VLLMClient:
    """Client for vLLM inference on 2x DGX Sparks"""

    def __init__(self,
                 qwen_server_url: str = "http://169.254.150.106:8000",
                 gptoss_server_url: str = "http://169.254.150.105:8000",
                 timeout: int = 300):
        """Initialize vLLM client with two server URLs.

        Args:
            qwen_server_url: URL for Spark running Qwen FP8 (code analysis)
            gptoss_server_url: URL for Spark running GPT-OSS MXFP4 (feedback)
            timeout: Request timeout in seconds
        """
        self.qwen_server_url = qwen_server_url
        self.gptoss_server_url = gptoss_server_url
        self.qwen_api_url = f"{qwen_server_url}/v1/chat/completions"
        self.gptoss_api_url = f"{gptoss_server_url}/v1/chat/completions"
        self.timeout = timeout
        self.last_response_times = {}

        # Model names as served by vLLM (must match --served-model-name or model ID)
        self.code_model = "Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8"
        self.feedback_model = "openai/gpt-oss-120b"

    def _check_single_server(self, server_url: str) -> bool:
        """Check if a single vLLM server is available via /v1/models."""
        try:
            response = requests.get(f"{server_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False

    def check_server_status(self) -> bool:
        """Check if BOTH vLLM servers are available."""
        return (self._check_single_server(self.qwen_server_url) and
                self._check_single_server(self.gptoss_server_url))

    def get_available_models(self) -> list:
        """Get list of available models from both vLLM servers."""
        models = []
        for server_url in [self.qwen_server_url, self.gptoss_server_url]:
            try:
                response = requests.get(f"{server_url}/v1/models", timeout=5)
                if response.status_code == 200:
                    models.extend(response.json().get('data', []))
            except:
                pass
        return models

    def _call_vllm(self, server_url: str, model: str, messages: list,
                   max_tokens: int = 2000, temperature: float = 0.1) -> tuple:
        """Make a non-streaming call to a specific vLLM server.

        Args:
            server_url: The vLLM server API URL
            model: Model name (required by vLLM)
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Tuple of (generated_text, metrics_dict) or (None, {}) on failure
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }

            start_time = time.time()

            response = requests.post(
                server_url,
                json=payload,
                timeout=self.timeout
            )

            generation_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

                usage = result.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)

                tokens_per_second = completion_tokens / generation_time if generation_time > 0 else 0

                return content, {
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens,
                    'generation_time': generation_time,
                    'tokens_per_second': tokens_per_second
                }
            else:
                print(f"  vLLM API returned status {response.status_code}: {response.text[:200]}")
                return None, {}

        except requests.exceptions.Timeout:
            print(f"  vLLM API timeout after {self.timeout} seconds")
            return None, {}
        except requests.exceptions.ConnectionError as e:
            print(f"  vLLM connection error: {e}")
            return None, {}
        except Exception as e:
            print(f"  vLLM API error: {e}")
            return None, {}

    def generate_code_analysis(self, prompt: str, max_tokens: int = 2400) -> Optional[str]:
        """Generate code analysis — routes to Spark 1 (Qwen FP8).

        Args:
            prompt: The analysis prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Analysis text or None on failure
        """
        start_time = time.time()

        messages = [
            {"role": "system", "content": "You are an expert code analyzer for R programming and data analytics. Analyze the student's code and provide structured feedback in JSON format."},
            {"role": "user", "content": prompt}
        ]

        result, metrics = self._call_vllm(
            server_url=self.qwen_api_url,
            model=self.code_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.1
        )

        generation_time = time.time() - start_time
        self.last_response_times['qwen'] = generation_time
        self.last_response_times['qwen_metrics'] = metrics

        if result:
            output_tokens = metrics.get('completion_tokens', len(result.split()))
            tokens_per_second = output_tokens / generation_time if generation_time > 0 else 0
            print(f"  [VLLM/CODE] {output_tokens} tokens in {generation_time:.1f}s ({tokens_per_second:.1f} tok/s)")

        return result

    def generate_feedback(self, prompt: str, max_tokens: int = 3500) -> Optional[str]:
        """Generate feedback — routes to Spark 2 (GPT-OSS MXFP4).

        Args:
            prompt: The feedback prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Feedback text or None on failure
        """
        start_time = time.time()

        messages = [
            {"role": "system", "content": "You are an expert instructor providing feedback on student submissions. Generate constructive, detailed feedback in JSON format."},
            {"role": "user", "content": prompt}
        ]

        result, metrics = self._call_vllm(
            server_url=self.gptoss_api_url,
            model=self.feedback_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3
        )

        generation_time = time.time() - start_time
        self.last_response_times['gemma'] = generation_time
        self.last_response_times['gemma_metrics'] = metrics

        if result:
            output_tokens = metrics.get('completion_tokens', len(result.split()))
            tokens_per_second = output_tokens / generation_time if generation_time > 0 else 0
            print(f"  [VLLM/FEEDBACK] {output_tokens} tokens in {generation_time:.1f}s ({tokens_per_second:.1f} tok/s)")

        return result

    def generate_parallel_sync(self, code_prompt: str, feedback_prompt: str) -> Dict[str, Any]:
        """Generate both code analysis and feedback in parallel.

        Args:
            code_prompt: Prompt for code analysis (sent to Spark 1 / Qwen)
            feedback_prompt: Prompt for feedback generation (sent to Spark 2 / GPT-OSS)

        Returns:
            Dict with 'code_analysis', 'feedback', timing metrics
        """
        print(f"  Starting vLLM parallel generation...")
        print(f"   Qwen Server: {self.qwen_server_url}")
        print(f"   GPT-OSS Server: {self.gptoss_server_url}")

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                start_time = time.time()

                code_future = executor.submit(self.generate_code_analysis, code_prompt)
                feedback_future = executor.submit(self.generate_feedback, feedback_prompt)

                code_result = code_future.result(timeout=self.timeout)
                feedback_result = feedback_future.result(timeout=self.timeout)

                total_time = time.time() - start_time

                qwen_metrics = self.last_response_times.get('qwen_metrics', {})
                gemma_metrics = self.last_response_times.get('gemma_metrics', {})

                qwen_time = self.last_response_times.get('qwen', 0)
                gemma_time = self.last_response_times.get('gemma', 0)
                sequential_time = qwen_time + gemma_time

                return {
                    'code_analysis': code_result,
                    'feedback': feedback_result,
                    'parallel_time': total_time,
                    'qwen_time': qwen_time,
                    'gemma_time': gemma_time,
                    'parallel_efficiency': sequential_time / total_time if total_time > 0 else 0,
                    'qwen_metrics': qwen_metrics,
                    'gemma_metrics': gemma_metrics,
                    'performance_metrics': {
                        'qwen': qwen_metrics,
                        'gemma': gemma_metrics,
                        'total_tokens': qwen_metrics.get('total_tokens', 0) + gemma_metrics.get('total_tokens', 0),
                        'combined_tokens_per_second': (
                            qwen_metrics.get('completion_tokens', 0) + gemma_metrics.get('completion_tokens', 0)
                        ) / total_time if total_time > 0 else 0
                    }
                }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"  vLLM parallel generation EXCEPTION: {e}")
            print(f"Full traceback:\n{error_details}")

            return {
                'code_analysis': None,
                'feedback': None,
                'parallel_time': 0,
                'error': f"{type(e).__name__}: {str(e)}"
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of vLLM servers."""
        qwen_available = self._check_single_server(self.qwen_server_url)
        gptoss_available = self._check_single_server(self.gptoss_server_url)
        models = self.get_available_models() if (qwen_available or gptoss_available) else []

        return {
            'qwen_server_available': qwen_available,
            'gptoss_server_available': gptoss_available,
            'distributed_ready': qwen_available and gptoss_available,
            'qwen_server_url': self.qwen_server_url,
            'gptoss_server_url': self.gptoss_server_url,
            'available_models': models,
            'qwen_available': qwen_available,
            'gemma_available': gptoss_available,
        }

    def get_performance_diagnostics(self) -> Dict[str, Any]:
        """Get detailed performance diagnostics."""
        qwen_metrics = self.last_response_times.get('qwen_metrics', {})
        gemma_metrics = self.last_response_times.get('gemma_metrics', {})

        return {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'qwen_performance': {
                'model': 'vLLM (DGX Spark)',
                'server': self.qwen_server_url,
                'prompt_tokens': qwen_metrics.get('prompt_tokens', 0),
                'output_tokens': qwen_metrics.get('completion_tokens', 0),
                'total_tokens': qwen_metrics.get('total_tokens', 0),
                'generation_time_seconds': qwen_metrics.get('generation_time', 0),
                'tokens_per_second': qwen_metrics.get('tokens_per_second', 0),
                'server_url': self.qwen_server_url
            },
            'gemma_performance': {
                'model': 'vLLM (DGX Spark)',
                'server': self.gptoss_server_url,
                'prompt_tokens': gemma_metrics.get('prompt_tokens', 0),
                'output_tokens': gemma_metrics.get('completion_tokens', 0),
                'total_tokens': gemma_metrics.get('total_tokens', 0),
                'generation_time_seconds': gemma_metrics.get('generation_time', 0),
                'tokens_per_second': gemma_metrics.get('tokens_per_second', 0),
                'server_url': self.gptoss_server_url
            },
            'combined_metrics': {
                'total_tokens_processed': qwen_metrics.get('total_tokens', 0) + gemma_metrics.get('total_tokens', 0),
                'total_output_tokens': qwen_metrics.get('completion_tokens', 0) + gemma_metrics.get('completion_tokens', 0),
                'parallel_efficiency': self.last_response_times.get('parallel_efficiency', 0),
                'combined_throughput_tokens_per_second': (
                    qwen_metrics.get('completion_tokens', 0) + gemma_metrics.get('completion_tokens', 0)
                ) / max(qwen_metrics.get('generation_time', 1), gemma_metrics.get('generation_time', 1))
            }
        }


def show_vllm_status():
    """Show vLLM system status in Streamlit sidebar"""
    from engine._compat import st

    client = VLLMClient()
    status = client.get_system_status()

    st.sidebar.markdown("---")
    st.sidebar.subheader("DGX Spark vLLM")

    if status['qwen_server_available']:
        st.sidebar.success(f"Qwen FP8: Online")
        st.sidebar.caption(f"   {status['qwen_server_url']}")
    else:
        st.sidebar.error(f"Qwen FP8: Offline")

    if status['gptoss_server_available']:
        st.sidebar.success(f"GPT-OSS MXFP4: Online")
        st.sidebar.caption(f"   {status['gptoss_server_url']}")
    else:
        st.sidebar.error(f"GPT-OSS MXFP4: Offline")

    if status['distributed_ready']:
        st.sidebar.success("vLLM Inference Ready")
    else:
        st.sidebar.warning("vLLM not fully available")
