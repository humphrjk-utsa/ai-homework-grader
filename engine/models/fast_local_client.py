#!/usr/bin/env python3
"""
High-speed unencrypted client for local Thunderbolt connections
Optimized for Mac Studio to Mac Studio communication
"""

import socket
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional

class FastLocalClient:
    """High-speed unencrypted client for local model servers"""
    
    def __init__(self, qwen_host="10.55.0.2", qwen_port=5002, 
                 gpt_host="10.55.0.1", gpt_port=5001):
        self.qwen_host = qwen_host
        self.qwen_port = qwen_port
        self.gpt_host = gpt_host
        self.gpt_port = gpt_port
        
        # Optimize socket settings for high-speed local connections
        self.socket_options = [
            (socket.SOL_SOCKET, socket.SO_SNDBUF, 2097152),  # 2MB send buffer
            (socket.SOL_SOCKET, socket.SO_RCVBUF, 2097152),  # 2MB receive buffer
            (socket.SOL_TCP, socket.TCP_NODELAY, 1),         # Disable Nagle algorithm
            (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1),     # Reuse addresses
        ]
    
    def _create_optimized_socket(self):
        """Create socket optimized for high-speed local transfers"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Apply optimizations
        for level, option, value in self.socket_options:
            try:
                sock.setsockopt(level, option, value)
            except OSError:
                pass  # Some options might not be available
        
        return sock
    
    def _send_request(self, host: str, port: int, data: dict) -> Optional[dict]:
        """Send request using optimized socket"""
        try:
            sock = self._create_optimized_socket()
            sock.settimeout(120)  # 2 minute timeout
            
            # Connect
            sock.connect((host, port))
            
            # Prepare HTTP request
            json_data = json.dumps(data)
            request = f"""POST /generate HTTP/1.1\r
Host: {host}:{port}\r
Content-Type: application/json\r
Content-Length: {len(json_data)}\r
Connection: close\r
\r
{json_data}"""
            
            # Send request
            sock.sendall(request.encode())
            
            # Receive response
            response_data = b""
            while True:
                chunk = sock.recv(65536)  # 64KB chunks
                if not chunk:
                    break
                response_data += chunk
            
            sock.close()
            
            # Parse HTTP response
            if b'\r\n\r\n' in response_data:
                headers, body = response_data.split(b'\r\n\r\n', 1)
                try:
                    return json.loads(body.decode())
                except json.JSONDecodeError:
                    return None
            
            return None
            
        except Exception as e:
            print(f"❌ Socket request failed: {e}")
            return None
    
    def generate_qwen(self, prompt: str, max_tokens: int = 800) -> Optional[str]:
        """Generate with Qwen using optimized connection"""
        start_time = time.time()
        
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.1
        }
        
        print(f"🔄 Qwen request (optimized socket)...")
        result = self._send_request(self.qwen_host, self.qwen_port, data)
        
        if result:
            duration = time.time() - start_time
            print(f"✅ Qwen completed in {duration:.1f}s")
            return result.get('response', '')
        
        return None
    
    def generate_gpt(self, prompt: str, max_tokens: int = 1200) -> Optional[str]:
        """Generate with GPT-OSS using optimized connection"""
        start_time = time.time()
        
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        print(f"🔄 GPT-OSS request (optimized socket)...")
        result = self._send_request(self.gpt_host, self.gpt_port, data)
        
        if result:
            duration = time.time() - start_time
            print(f"✅ GPT-OSS completed in {duration:.1f}s")
            return result.get('response', '')
        
        return None
    
    def generate_parallel_fast(self, code_prompt: str, feedback_prompt: str) -> Dict[str, Any]:
        """Generate both responses in parallel using optimized sockets"""
        
        print("⚡ Starting optimized parallel generation...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            qwen_future = executor.submit(self.generate_qwen, code_prompt, 800)
            gpt_future = executor.submit(self.generate_gpt, feedback_prompt, 1200)
            
            qwen_result = qwen_future.result(timeout=120)
            gpt_result = gpt_future.result(timeout=150)
        
        total_time = time.time() - start_time
        
        return {
            'code_analysis': qwen_result,
            'feedback': gpt_result,
            'parallel_time': total_time,
            'success': qwen_result is not None and gpt_result is not None,
            'method': 'optimized_sockets'
        }

# Test the fast client
if __name__ == "__main__":
    print("🧪 Testing Fast Local Client")
    print("=" * 30)
    
    client = FastLocalClient()
    
    result = client.generate_parallel_fast(
        "def analyze_data(): # Complete this R function for data analysis",
        "Provide constructive feedback on the student's R programming approach"
    )
    
    if result['success']:
        print(f"\n✅ Fast parallel generation completed!")
        print(f"   Total time: {result['parallel_time']:.1f}s")
        print(f"   Method: {result['method']}")
        print(f"   Code analysis: {result['code_analysis'][:100] if result['code_analysis'] else 'None'}...")
        print(f"   Feedback: {result['feedback'][:100] if result['feedback'] else 'None'}...")
    else:
        print("❌ Fast generation failed")