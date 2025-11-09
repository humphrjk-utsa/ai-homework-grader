#!/usr/bin/env python3
"""
Disaggregated Inference Client for AI Homework Grader
Calls Flask wrapper servers that use Ollama on DGX (prefill) and Mac (decode)
"""
import requests
import time
import logging
from typing import Dict, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class DisaggregatedClient:
    """Client for disaggregated inference (DGX prefill + Mac decode) via Flask wrappers"""
    
    def __init__(self, config_path: str = "disaggregated_inference/config_current.json"):
        """Initialize client with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.prefill_servers = {s['model']: s for s in self.config['prefill_servers']}
        self.decode_servers = {s['model']: s for s in self.config['decode_servers']}
        
        logger.info(f"Initialized disaggregated client with {len(self.prefill_servers)} prefill and {len(self.decode_servers)} decode servers")
    
    def _get_server_url(self, server: Dict, endpoint: str) -> str:
        """Get server URL, using localhost if it's the local machine"""
        import socket
        host = server['host']
        port = server['port']
        
        # Check if this is a local IP by trying to bind to it
        # If we can't reach it via external IP, use localhost
        try:
            # Get local IPs
            hostname = socket.gethostname()
            local_ips = [socket.gethostbyname(hostname)]
            # Also check common local IPs
            local_ips.extend(['127.0.0.1', 'localhost'])
            
            # If the server host matches a local IP, use localhost
            if host in local_ips or host.startswith('169.254.150.101'):
                host = 'localhost'
        except:
            pass
        
        return f"http://{host}:{port}{endpoint}"
    
    def generate(self, model: str, prompt: str, max_tokens: int = 2000) -> Tuple[str, Dict]:
        """
        Generate text using disaggregated inference
        
        Args:
            model: Model name (e.g., "qwen3-coder:30b" or "gpt-oss:120b")
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (response_text, metrics_dict)
        """
        start_time = time.time()
        
        # Determine model type
        if 'qwen' in model.lower() or 'coder' in model.lower():
            model_key = 'qwen'
        else:
            model_key = 'gpt-oss'
        
        # Get servers
        prefill_server = self.prefill_servers.get(model_key)
        decode_server = self.decode_servers.get(model_key)
        
        if not prefill_server or not decode_server:
            raise ValueError(f"No servers configured for model type: {model_key}")
        
        logger.info(f"Using {model_key}: prefill={prefill_server['host']}:{prefill_server['port']}, decode={decode_server['host']}:{decode_server['port']}")
        
        try:
            # Step 1: Prefill on DGX via Flask wrapper
            prefill_url = self._get_server_url(prefill_server, '/prefill')
            logger.info(f"🚀 Prefill on DGX: {prefill_url}")
            prefill_start = time.time()
            
            response = requests.post(
                prefill_url,
                json={'prompt': prompt},
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Prefill failed: {response.status_code} - {response.text}")
            
            prefill_result = response.json()
            prefill_time = time.time() - prefill_start
            
            # Extract prefill metrics
            prefill_metrics = prefill_result.get('metrics', {})
            prompt_tokens = prefill_metrics.get('prompt_eval_count', 0)
            prefill_tokens_per_sec = prefill_metrics.get('prompt_tokens_per_sec', 0)
            
            logger.info(f"✅ Prefill completed in {prefill_time:.3f}s ({prompt_tokens} tokens, {prefill_tokens_per_sec:.1f} tok/s)")
            
            # Step 2: Decode on Mac via Flask wrapper
            decode_url = self._get_server_url(decode_server, '/decode')
            logger.info(f"🚀 Decode on Mac: {decode_url}")
            decode_start = time.time()
            
            response = requests.post(
                decode_url,
                json={
                    'context': prefill_result.get('context', prompt),
                    'prompt': prompt,
                    'max_new_tokens': max_tokens,
                    'temperature': 0.2
                },
                timeout=180
            )
            
            if response.status_code != 200:
                raise Exception(f"Decode failed: {response.status_code} - {response.text}")
            
            decode_result = response.json()
            decode_time = time.time() - decode_start
            total_time = time.time() - start_time
            
            # Extract decode metrics
            decode_metrics = decode_result.get('metrics', {})
            tokens_generated = decode_metrics.get('eval_count', decode_result.get('tokens_generated', 0))
            decode_tokens_per_sec = decode_metrics.get('tokens_per_sec', decode_result.get('tokens_per_sec', 0))
            
            logger.info(f"✅ Decode completed in {decode_time:.3f}s ({tokens_generated} tokens, {decode_tokens_per_sec:.1f} tok/s)")
            logger.info(f"⏱️ Total time: {total_time:.3f}s")
            
            response_text = decode_result.get('generated_text', '')
            
            metrics = {
                'prefill_time': prefill_time,
                'decode_time': decode_time,
                'total_time': total_time,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': tokens_generated,
                'total_tokens': prompt_tokens + tokens_generated,
                'prefill_speed': prefill_tokens_per_sec,
                'decode_speed': decode_tokens_per_sec,
                'method': 'disaggregated_ollama',
                'prefill_server': f"{prefill_server['host']}:{prefill_server['port']}",
                'decode_server': f"{decode_server['host']}:{decode_server['port']}"
            }
            
            return response_text, metrics
            
        except Exception as e:
            logger.error(f"❌ Disaggregated inference failed: {e}")
            raise

