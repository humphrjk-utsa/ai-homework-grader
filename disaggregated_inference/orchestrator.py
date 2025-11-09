#!/usr/bin/env python3
"""
Disaggregated Inference Orchestrator
Coordinates prefill (DGX) and decode (Mac) for optimal performance
"""
import requests
import time
import logging
from typing import Dict, List, Optional
import asyncio
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DisaggregatedInference:
    """Orchestrates prefill on DGX and decode on Mac"""
    
    def __init__(self, config: Dict):
        """
        Initialize with server configuration
        config = {
            'prefill_servers': [
                {'host': '192.168.100.1', 'port': 8000, 'model': 'qwen'},
                {'host': '192.168.100.2', 'port': 8000, 'model': 'gpt-oss'}
            ],
            'decode_servers': [
                {'host': '169.254.150.101', 'port': 8001, 'model': 'qwen'},
                {'host': '169.254.150.102', 'port': 8001, 'model': 'gpt-oss'}
            ]
        }
        """
        self.prefill_servers = config['prefill_servers']
        self.decode_servers = config['decode_servers']
        self.server_status = {}
    
    async def check_server_health(self, server: Dict) -> bool:
        """Check if a server is healthy"""
        try:
            url = f"http://{server['host']}:{server['port']}/health"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('loaded', False)
            return False
        except Exception as e:
            logger.warning(f"Health check failed for {server['host']}:{server['port']}: {e}")
            return False
    
    async def update_server_status(self):
        """Update status of all servers"""
        tasks = []
        for server in self.prefill_servers + self.decode_servers:
            tasks.append(self.check_server_health(server))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, server in enumerate(self.prefill_servers + self.decode_servers):
            server_id = f"{server['host']}:{server['port']}"
            self.server_status[server_id] = results[i] if not isinstance(results[i], Exception) else False
    
    def get_best_server(self, servers: List[Dict], model_type: str) -> Optional[Dict]:
        """Get the best available server for a model type"""
        for server in servers:
            if server['model'] == model_type:
                server_id = f"{server['host']}:{server['port']}"
                if self.server_status.get(server_id, False):
                    return server
        return None
    
    async def prefill_request(self, server: Dict, prompt: str) -> Optional[Dict]:
        """Send prefill request to DGX"""
        try:
            url = f"http://{server['host']}:{server['port']}/prefill"
            data = {'prompt': prompt}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Prefill failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Prefill request failed: {e}")
            return None
    
    async def decode_request(self, server: Dict, prefill_result: Dict, max_tokens: int = 100) -> Optional[Dict]:
        """Send decode request to Mac"""
        try:
            url = f"http://{server['host']}:{server['port']}/decode"
            data = {
                'kv_cache': prefill_result.get('kv_cache'),
                'input_ids': prefill_result.get('input_ids'),
                'max_new_tokens': max_tokens,
                'prompt': prefill_result.get('original_prompt', '')  # Fallback for MLX
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=60) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Decode failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Decode request failed: {e}")
            return None
    
    async def generate(self, prompt: str, model_type: str = 'qwen', max_tokens: int = 100) -> Dict:
        """
        Generate text using disaggregated inference
        
        Args:
            prompt: Input text
            model_type: 'qwen' or 'gpt-oss'
            max_tokens: Maximum tokens to generate
            
        Returns:
            {
                'response': 'generated text',
                'prefill_time': 0.123,
                'decode_time': 1.234,
                'total_time': 1.357,
                'method': 'disaggregated' or 'fallback'
            }
        """
        start_time = time.time()
        
        # Update server status
        await self.update_server_status()
        
        # Get best servers
        prefill_server = self.get_best_server(self.prefill_servers, model_type)
        decode_server = self.get_best_server(self.decode_servers, model_type)
        
        if not prefill_server or not decode_server:
            logger.warning("Servers not available, trying fallback...")
            return await self.fallback_generate(prompt, model_type, max_tokens)
        
        logger.info(f"Using prefill: {prefill_server['host']} decode: {decode_server['host']}")
        
        # Step 1: Prefill on DGX
        prefill_result = await self.prefill_request(prefill_server, prompt)
        if not prefill_result:
            logger.warning("Prefill failed, trying fallback...")
            return await self.fallback_generate(prompt, model_type, max_tokens)
        
        # Step 2: Decode on Mac
        prefill_result['original_prompt'] = prompt  # For MLX fallback
        decode_result = await self.decode_request(decode_server, prefill_result, max_tokens)
        if not decode_result:
            logger.warning("Decode failed, trying fallback...")
            return await self.fallback_generate(prompt, model_type, max_tokens)
        
        total_time = time.time() - start_time
        
        return {
            'response': decode_result.get('generated_text', ''),
            'prefill_time': prefill_result.get('prefill_time', 0),
            'decode_time': decode_result.get('decode_time', 0),
            'total_time': total_time,
            'method': 'disaggregated',
            'prefill_server': f"{prefill_server['host']}:{prefill_server['port']}",
            'decode_server': f"{decode_server['host']}:{decode_server['port']}",
            'tokens_per_sec': decode_result.get('tokens_per_sec', 0)
        }
    
    async def fallback_generate(self, prompt: str, model_type: str, max_tokens: int) -> Dict:
        """Fallback to Mac-only generation if disaggregated fails"""
        decode_server = self.get_best_server(self.decode_servers, model_type)
        
        if not decode_server:
            return {
                'error': 'No servers available',
                'method': 'failed'
            }
        
        try:
            url = f"http://{decode_server['host']}:{decode_server['port']}/generate"
            data = {
                'prompt': prompt,
                'max_tokens': max_tokens
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=60) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'response': result.get('response', ''),
                            'total_time': result.get('generation_time', 0),
                            'method': 'mac_fallback',
                            'server': f"{decode_server['host']}:{decode_server['port']}"
                        }
        except Exception as e:
            logger.error(f"Fallback generation failed: {e}")
        
        return {
            'error': 'All generation methods failed',
            'method': 'failed'
        }


# Example usage
async def main():
    config = {
        'prefill_servers': [
            {'host': '169.254.150.103', 'port': 8000, 'model': 'qwen'},
            {'host': '169.254.150.104', 'port': 8000, 'model': 'gpt-oss'}
        ],
        'decode_servers': [
            {'host': '169.254.150.101', 'port': 8001, 'model': 'qwen'},
            {'host': '169.254.150.102', 'port': 8001, 'model': 'gpt-oss'}
        ]
    }
    
    orchestrator = DisaggregatedInference(config)
    
    # Test generation
    result = await orchestrator.generate(
        prompt="def fibonacci(n):",
        model_type="qwen",
        max_tokens=50
    )
    
    print("\n" + "="*60)
    print("Generation Result:")
    print("="*60)
    print(f"Response: {result.get('response', 'N/A')}")
    print(f"Method: {result.get('method', 'N/A')}")
    print(f"Total time: {result.get('total_time', 0):.3f}s")
    if 'tokens_per_sec' in result:
        print(f"Speed: {result['tokens_per_sec']:.1f} tok/s")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
