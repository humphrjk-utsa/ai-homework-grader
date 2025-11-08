#!/usr/bin/env python3
"""
Disaggregated Inference Client for AI Homework Grader
Uses Ollama on both DGX (prefill) and Mac (decode) with KV cache passing
"""
import requests
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DisaggregatedClient:
    """Client for disaggregated inference (DGX prefill + Mac decode) using Ollama"""
    
    def __init__(self, prefill_url: str, decode_url: str, model_name: str):
        self.prefill_url = prefill_url
        self.decode_url = decode_url
        self.model_name = model_name
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> Dict:
        """
        Generate text using disaggregated inference with Ollama
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dict with 'response', 'prefill_time', 'decode_time', 'total_time', 'metrics'
        """
        start_time = time.time()
        
        try:
            # Step 1: Prefill on DGX (Ollama)
            logger.info(f"🚀 Prefill on DGX: {self.prefill_url} ({self.model_name})")
            prefill_start = time.time()
            
            response = requests.post(
                f"{self.prefill_url}/api/generate",
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'num_predict': 1  # Just prefill, minimal generation
                    }
                },
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Prefill failed: {response.status_code}")
            
            prefill_result = response.json()
            prefill_time = time.time() - prefill_start
            
            # Extract prefill metrics
            prompt_eval_count = prefill_result.get('prompt_eval_count', 0)
            prompt_eval_duration = prefill_result.get('prompt_eval_duration', 0)
            
            logger.info(f"✅ Prefill completed in {prefill_time:.3f}s ({prompt_eval_count} tokens)")
            
            # Step 2: Decode on Mac (Ollama with context)
            logger.info(f"🚀 Decode on Mac: {self.decode_url}")
            decode_start = time.time()
            
            response = requests.post(
                f"{self.decode_url}/api/generate",
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'context': prefill_result.get('context', []),  # Pass KV cache from prefill
                    'stream': False,
                    'options': {
                        'num_predict': max_tokens,
                        'temperature': temperature
                    }
                },
                timeout=180
            )
            
            if response.status_code != 200:
                raise Exception(f"Decode failed: {response.status_code}")
            
            decode_result = response.json()
            decode_time = time.time() - decode_start
            total_time = time.time() - start_time
            
            # Extract decode metrics
            eval_count = decode_result.get('eval_count', 0)
            eval_duration = decode_result.get('eval_duration', 0)
            tokens_per_sec = (eval_count / (eval_duration / 1e9)) if eval_duration > 0 else 0
            
            logger.info(f"✅ Decode completed in {decode_time:.3f}s ({eval_count} tokens, {tokens_per_sec:.1f} tok/s)")
            logger.info(f"⏱️ Total time: {total_time:.3f}s")
            
            return {
                'response': decode_result.get('response', ''),
                'prefill_time': prefill_time,
                'decode_time': decode_time,
                'total_time': total_time,
                'tokens_per_sec': tokens_per_sec,
                'method': 'disaggregated_ollama',
                'metrics': {
                    'prefill': {
                        'time_s': prefill_time,
                        'prompt_tokens': prompt_eval_count,
                        'tokens_per_sec': (prompt_eval_count / (prompt_eval_duration / 1e9)) if prompt_eval_duration > 0 else 0,
                        'duration_ns': prompt_eval_duration
                    },
                    'decode': {
                        'time_s': decode_time,
                        'tokens_generated': eval_count,
                        'tokens_per_sec': tokens_per_sec,
                        'eval_duration_ns': eval_duration,
                        'total_duration_ns': decode_result.get('total_duration', 0)
                    },
                    'total': {
                        'time_s': total_time,
                        'prompt_tokens': prompt_eval_count,
                        'generated_tokens': eval_count,
                        'total_tokens': prompt_eval_count + eval_count,
                        'overall_tokens_per_sec': (prompt_eval_count + eval_count) / total_time if total_time > 0 else 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Disaggregated inference failed: {e}")
            raise


def create_disaggregated_client(model_name: str, model_config: Dict) -> Optional[DisaggregatedClient]:
    """
    Create a disaggregated client if the model is configured for it
    
    Args:
        model_name: Name of the model (e.g., "disaggregated:qwen3-coder:30b")
        model_config: Configuration dict from model_config.py
        
    Returns:
        DisaggregatedClient if model supports it, None otherwise
    """
    if not model_name.startswith('disaggregated:'):
        return None
    
    prefill_url = model_config.get('prefill_url')
    decode_url = model_config.get('decode_url')
    ollama_model_name = model_config.get('model_name')
    
    if not prefill_url or not decode_url or not ollama_model_name:
        logger.warning(f"Model {model_name} missing prefill_url, decode_url, or model_name")
        return None
    
    logger.info(f"✅ Creating disaggregated client for {model_name}")
    logger.info(f"   Prefill: {prefill_url} ({ollama_model_name})")
    logger.info(f"   Decode: {decode_url} ({ollama_model_name})")
    
    return DisaggregatedClient(prefill_url, decode_url, ollama_model_name)
