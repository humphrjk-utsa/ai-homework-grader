#!/usr/bin/env python3
"""
Disaggregated Inference Client for AI Homework Grader
Uses llama.cpp C API for KV cache state transfer (DGX prefill + Mac decode)
"""
import requests
import time
import logging
from typing import Dict, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class DisaggregatedClient:
    """Client for disaggregated inference using llama.cpp C API state transfer"""

    def __init__(self, config_path: str = "disaggregated_inference/config_current.json"):
        """Initialize client with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.prefill_servers = {s['model']: s for s in self.config['prefill_servers']}
        self.decode_servers = {s['model']: s for s in self.config['decode_servers']}

        logger.info(f"✅ Disaggregated client initialized (llama.cpp C API)")
        logger.info(f"   Prefill servers: {len(self.prefill_servers)} (DGX)")
        logger.info(f"   Decode servers: {len(self.decode_servers)} (Mac)")
    
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
        Generate text using disaggregated inference with llama.cpp C API

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

        logger.info(f"🔄 Using {model_key} pipeline:")
        logger.info(f"   Prefill: {prefill_server['name']} ({prefill_server['host']}:{prefill_server['port']})")
        logger.info(f"   Decode:  {decode_server['name']} ({decode_server['host']}:{decode_server['port']})")

        try:
            # Step 1: Prefill on DGX (generate KV cache)
            prefill_url = self._get_server_url(prefill_server, '/prefill')
            logger.info(f"🚀 Step 1: Prefill on {prefill_server['name']}")
            prefill_start = time.time()

            response = requests.post(
                prefill_url,
                json={
                    'prompt': prompt,
                    'return_state': True  # Request KV cache state
                },
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"Prefill failed: {response.status_code} - {response.text}")

            prefill_result = response.json()
            prefill_time = time.time() - prefill_start

            # Extract KV cache state and metrics
            llama_state = prefill_result.get('llama_state')
            n_tokens = prefill_result.get('n_tokens', 0)
            state_size_mb = prefill_result.get('state_size_mb', 0)
            is_compressed = prefill_result.get('compressed', True)  # Get compression flag

            # Get speed from server or calculate it
            prefill_speed = prefill_result.get('speed', 0)
            if prefill_speed == 0 and n_tokens > 0 and prefill_time > 0:
                prefill_speed = n_tokens / prefill_time

            if not llama_state:
                raise Exception("Prefill did not return llama_state")

            logger.info(f"✅ Prefill complete: {n_tokens} tokens @ {prefill_speed:.1f} tok/s")
            logger.info(f"   State size: {state_size_mb:.1f} MB {'(compressed)' if is_compressed else '(uncompressed)'}")

            # Step 2: Decode on Mac (load KV cache, generate tokens)
            decode_url = self._get_server_url(decode_server, '/decode')
            logger.info(f"🚀 Step 2: Decode on {decode_server['name']}")
            decode_start = time.time()

            response = requests.post(
                decode_url,
                json={
                    'prompt': prompt,  # Original prompt for context
                    'llama_state': llama_state,  # KV cache from prefill
                    'n_tokens': n_tokens,  # Token count from prefill
                    'compressed': is_compressed,  # Compression flag
                    'max_new_tokens': max_tokens,
                    'temperature': 0.2
                },
                timeout=300
            )

            if response.status_code != 200:
                raise Exception(f"Decode failed: {response.status_code} - {response.text}")

            decode_result = response.json()
            decode_time = time.time() - decode_start
            total_time = time.time() - start_time

            # Extract decode metrics
            tokens_generated = decode_result.get('tokens_generated', 0)
            generated_text = decode_result.get('generated_text', '')

            # Get speed from server or calculate it
            decode_speed = decode_result.get('speed', decode_result.get('tokens_per_sec', 0))
            if decode_speed == 0 and tokens_generated > 0 and decode_time > 0:
                decode_speed = tokens_generated / decode_time

            logger.info(f"✅ Decode complete: {tokens_generated} tokens @ {decode_speed:.1f} tok/s")
            logger.info(f"⏱️ Total time: {total_time:.2f}s (prefill: {prefill_time:.2f}s, decode: {decode_time:.2f}s)")

            # Build metrics
            metrics = {
                'prefill_time': prefill_time,
                'decode_time': decode_time,
                'total_time': total_time,
                'prompt_tokens': n_tokens,
                'completion_tokens': tokens_generated,
                'total_tokens': n_tokens + tokens_generated,
                'prefill_speed': prefill_speed,
                'decode_speed': decode_speed,
                'state_size_mb': state_size_mb,
                'method': 'disaggregated_llamacpp',
                'prefill_server': f"{prefill_server['name']} ({prefill_server['host']}:{prefill_server['port']})",
                'decode_server': f"{decode_server['name']} ({decode_server['host']}:{decode_server['port']})"
            }

            return generated_text, metrics

        except Exception as e:
            logger.error(f"❌ Disaggregated inference failed: {e}")
            raise

