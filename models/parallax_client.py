#!/usr/bin/env python3
"""
Parallax Client for Distributed Inference
Uses Parallax cluster (Mac Studios + DGX Sparks) for distributed LLM inference
"""

import requests
import time
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class ParallaxClient:
    """Client for Parallax distributed inference cluster"""

    def __init__(self,
                 scheduler_url: str = "http://169.254.150.101:3001",
                 timeout: int = 300):
        """Initialize Parallax client

        Args:
            scheduler_url: URL for Parallax scheduler (Mac 1)
            timeout: Request timeout in seconds
        """
        self.scheduler_url = scheduler_url
        self.api_url = f"{scheduler_url}/v1/chat/completions"
        self.timeout = timeout
        self.last_response_times = {}

        # Default model configuration
        self.code_model = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
        self.feedback_model = "openai/gpt-oss"

    def check_server_status(self) -> bool:
        """Check if Parallax scheduler is available"""
        try:
            response = requests.get(f"{self.scheduler_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_available_models(self) -> list:
        """Get list of available models from Parallax"""
        try:
            response = requests.get(f"{self.scheduler_url}/v1/models", timeout=5)
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except:
            return []

    def _call_parallax(self, messages: list, max_tokens: int = 2000,
                       temperature: float = 0.1,
                       enable_thinking: bool = False) -> Optional[str]:
        """Make a call to Parallax API

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            enable_thinking: Enable reasoning mode for Qwen3 models

        Returns:
            Generated text or None on failure
        """
        try:
            payload = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
                "chat_template_kwargs": {"enable_thinking": enable_thinking}
            }

            start_time = time.time()

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )

            generation_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

                # Extract usage metrics if available
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
                print(f"❌ Parallax API returned status {response.status_code}: {response.text}")
                return None, {}

        except requests.exceptions.Timeout:
            print(f"⏰ Parallax API timeout after {self.timeout} seconds")
            return None, {}
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Parallax connection error: {e}")
            return None, {}
        except Exception as e:
            print(f"❌ Parallax API error: {e}")
            return None, {}

    def generate_code_analysis(self, prompt: str, max_tokens: int = 2400) -> Optional[str]:
        """Generate code analysis using Parallax cluster

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

        result, metrics = self._call_parallax(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.1,
            enable_thinking=False  # Disable reasoning for faster response
        )

        generation_time = time.time() - start_time
        self.last_response_times['qwen'] = generation_time
        self.last_response_times['qwen_metrics'] = metrics

        if result:
            output_tokens = metrics.get('completion_tokens', len(result.split()))
            tokens_per_second = output_tokens / generation_time if generation_time > 0 else 0
            print(f"🔧 [PARALLAX/CODE] {output_tokens} tokens in {generation_time:.1f}s ({tokens_per_second:.1f} tok/s)")

        return result

    def generate_feedback(self, prompt: str, max_tokens: int = 3500) -> Optional[str]:
        """Generate feedback using Parallax cluster

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

        result, metrics = self._call_parallax(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
            enable_thinking=False
        )

        generation_time = time.time() - start_time
        self.last_response_times['gemma'] = generation_time
        self.last_response_times['gemma_metrics'] = metrics

        if result:
            output_tokens = metrics.get('completion_tokens', len(result.split()))
            tokens_per_second = output_tokens / generation_time if generation_time > 0 else 0
            print(f"📝 [PARALLAX/FEEDBACK] {output_tokens} tokens in {generation_time:.1f}s ({tokens_per_second:.1f} tok/s)")

        return result

    def generate_parallel_sync(self, code_prompt: str, feedback_prompt: str) -> Dict[str, Any]:
        """Generate both code analysis and feedback in parallel

        Args:
            code_prompt: Prompt for code analysis
            feedback_prompt: Prompt for feedback generation

        Returns:
            Dict with 'code_analysis', 'feedback', timing metrics
        """
        print(f"🚀 Starting Parallax parallel generation...")
        print(f"   Scheduler: {self.scheduler_url}")

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                start_time = time.time()

                # Submit both tasks
                print(f"📤 Submitting code analysis task...")
                code_future = executor.submit(self.generate_code_analysis, code_prompt)
                print(f"📤 Submitting feedback task...")
                feedback_future = executor.submit(self.generate_feedback, feedback_prompt)

                # Get results
                print(f"⏳ Waiting for code analysis result...")
                code_result = code_future.result(timeout=self.timeout)
                print(f"✅ Code analysis received: {len(code_result) if code_result else 0} chars")

                print(f"⏳ Waiting for feedback result...")
                feedback_result = feedback_future.result(timeout=self.timeout)
                print(f"✅ Feedback received: {len(feedback_result) if feedback_result else 0} chars")

                total_time = time.time() - start_time

                # Get performance metrics
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
            print(f"❌ Parallax parallel generation EXCEPTION: {e}")
            print(f"Full traceback:\n{error_details}")

            return {
                'code_analysis': None,
                'feedback': None,
                'parallel_time': 0,
                'error': f"{type(e).__name__}: {str(e)}"
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of Parallax cluster"""
        scheduler_available = self.check_server_status()
        models = self.get_available_models() if scheduler_available else []

        return {
            'scheduler_available': scheduler_available,
            'distributed_ready': scheduler_available,
            'scheduler_url': self.scheduler_url,
            'available_models': models,
            'qwen_available': scheduler_available,  # For compatibility
            'gemma_available': scheduler_available,  # For compatibility
        }

    def get_performance_diagnostics(self) -> Dict[str, Any]:
        """Get detailed performance diagnostics"""
        qwen_metrics = self.last_response_times.get('qwen_metrics', {})
        gemma_metrics = self.last_response_times.get('gemma_metrics', {})

        return {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'qwen_performance': {
                'model': 'Parallax Cluster',
                'server': 'Parallax Scheduler',
                'prompt_tokens': qwen_metrics.get('prompt_tokens', 0),
                'output_tokens': qwen_metrics.get('completion_tokens', 0),
                'total_tokens': qwen_metrics.get('total_tokens', 0),
                'generation_time_seconds': qwen_metrics.get('generation_time', 0),
                'tokens_per_second': qwen_metrics.get('tokens_per_second', 0),
                'server_url': self.scheduler_url
            },
            'gemma_performance': {
                'model': 'Parallax Cluster',
                'server': 'Parallax Scheduler',
                'prompt_tokens': gemma_metrics.get('prompt_tokens', 0),
                'output_tokens': gemma_metrics.get('completion_tokens', 0),
                'total_tokens': gemma_metrics.get('total_tokens', 0),
                'generation_time_seconds': gemma_metrics.get('generation_time', 0),
                'tokens_per_second': gemma_metrics.get('tokens_per_second', 0),
                'server_url': self.scheduler_url
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


def show_parallax_status():
    """Show Parallax system status in Streamlit sidebar"""
    import streamlit as st

    client = ParallaxClient()
    status = client.get_system_status()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Parallax Cluster")

    if status['scheduler_available']:
        st.sidebar.success("✅ Scheduler: Online")
        st.sidebar.caption(f"   URL: {status['scheduler_url']}")

        models = status.get('available_models', [])
        if models:
            st.sidebar.info(f"📦 Models: {len(models)} loaded")
            for model in models[:3]:  # Show first 3
                st.sidebar.caption(f"   • {model.get('id', 'Unknown')}")
    else:
        st.sidebar.error("❌ Scheduler: Offline")
        st.sidebar.caption(f"   URL: {status['scheduler_url']}")

    if status['distributed_ready']:
        st.sidebar.success("⚡ Distributed Inference Ready")
    else:
        st.sidebar.warning("⚠️ Cluster not available")
