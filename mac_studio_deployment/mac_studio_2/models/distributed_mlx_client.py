#!/usr/bin/env python3
"""
Distributed MLX Client for Two Mac Studios
Runs models across multiple machines via Thunderbolt bridge
"""

import requests
import time
import streamlit as st
from typing import Optional, Dict, Any
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class DistributedMLXClient:
    """Distributed MLX client for two Mac Studios"""
    
    def __init__(self, 
                 qwen_server_url: str = "http://192.168.1.100:5001",  # Mac Studio 1
                 gemma_server_url: str = "http://192.168.1.101:5002"): # Mac Studio 2
        """Initialize distributed MLX client
        
        Args:
            qwen_server_url: URL for Qwen Coder server (Mac Studio 1)
            gemma_server_url: URL for Gemma server (Mac Studio 2)
        """
        self.qwen_server_url = qwen_server_url
        self.gemma_server_url = gemma_server_url
        self.last_response_times = {}
        
    def check_server_status(self, server_url: str, model_name: str) -> bool:
        """Check if a model server is available"""
        try:
            response = requests.get(f"{server_url}/health", timeout=3)
            return response.status_code == 200
        except:
            # Try a simple ping to the generate endpoint
            try:
                response = requests.post(
                    f"{server_url}/generate",
                    json={"prompt": "test", "max_tokens": 1},
                    timeout=5
                )
                return response.status_code == 200
            except:
                return False
    
    def generate_code_analysis(self, prompt: str, max_tokens: int = 2400) -> Optional[str]:
        """Generate code analysis using Qwen on Mac Studio 1"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.qwen_server_url}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.1
                },
                timeout=120  # 2 minute timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                self.last_response_times['qwen'] = time.time() - start_time
                return result.get('response', '')
            else:
                return None
                
        except Exception as e:
            st.error(f"❌ Qwen server error: {e}")
            return None
    
    def generate_feedback(self, prompt: str, max_tokens: int = 3800) -> Optional[str]:
        """Generate feedback using Gemma on Mac Studio 2"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.gemma_server_url}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.3
                },
                timeout=150  # 2.5 minute timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                self.last_response_times['gemma'] = time.time() - start_time
                return result.get('response', '')
            else:
                return None
                
        except Exception as e:
            st.error(f"❌ Gemma server error: {e}")
            return None
    
    async def generate_parallel(self, code_prompt: str, feedback_prompt: str) -> Dict[str, Any]:
        """Generate both responses in parallel using async"""
        
        async def fetch_qwen():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.qwen_server_url}/generate",
                    json={"prompt": code_prompt, "max_tokens": 2400, "temperature": 0.1},
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '')
                    return None
        
        async def fetch_gemma():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.gemma_server_url}/generate",
                    json={"prompt": feedback_prompt, "max_tokens": 3800, "temperature": 0.3},
                    timeout=aiohttp.ClientTimeout(total=150)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '')
                    return None
        
        start_time = time.time()
        
        # Run both requests in parallel
        qwen_task = asyncio.create_task(fetch_qwen())
        gemma_task = asyncio.create_task(fetch_gemma())
        
        qwen_result, gemma_result = await asyncio.gather(qwen_task, gemma_task)
        
        total_time = time.time() - start_time
        
        return {
            'code_analysis': qwen_result,
            'feedback': gemma_result,
            'parallel_time': total_time,
            'qwen_time': self.last_response_times.get('qwen', 0),
            'gemma_time': self.last_response_times.get('gemma', 0)
        }
    
    def generate_parallel_sync(self, code_prompt: str, feedback_prompt: str) -> Dict[str, Any]:
        """Synchronous wrapper for parallel generation"""
        try:
            # Use ThreadPoolExecutor for true parallel execution
            with ThreadPoolExecutor(max_workers=2) as executor:
                start_time = time.time()
                
                # Submit both tasks
                qwen_future = executor.submit(self.generate_code_analysis, code_prompt)
                gemma_future = executor.submit(self.generate_feedback, feedback_prompt)
                
                # Get results
                qwen_result = qwen_future.result(timeout=120)
                gemma_result = gemma_future.result(timeout=150)
                
                total_time = time.time() - start_time
                
                return {
                    'code_analysis': qwen_result,
                    'feedback': gemma_result,
                    'parallel_time': total_time,
                    'qwen_time': self.last_response_times.get('qwen', 0),
                    'gemma_time': self.last_response_times.get('gemma', 0),
                    'parallel_efficiency': (self.last_response_times.get('qwen', 0) + 
                                          self.last_response_times.get('gemma', 0)) / total_time
                }
                
        except Exception as e:
            st.error(f"❌ Parallel generation failed: {e}")
            return {
                'code_analysis': None,
                'feedback': None,
                'parallel_time': 0,
                'error': str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of both Mac Studios"""
        qwen_status = self.check_server_status(self.qwen_server_url, "Qwen")
        gemma_status = self.check_server_status(self.gemma_server_url, "Gemma")
        
        return {
            'qwen_available': qwen_status,
            'gemma_available': gemma_status,
            'distributed_ready': qwen_status and gemma_status,
            'qwen_server': self.qwen_server_url,
            'gemma_server': self.gemma_server_url
        }

def show_distributed_status():
    """Show distributed system status in Streamlit sidebar"""
    
    # Get server URLs from config or environment
    import os
    qwen_url = os.getenv('QWEN_SERVER_URL', 'http://192.168.1.100:5001')
    gemma_url = os.getenv('GEMMA_SERVER_URL', 'http://192.168.1.101:5002')
    
    client = DistributedMLXClient(qwen_url, gemma_url)
    status = client.get_system_status()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🖥️ Distributed MLX System")
    
    if status['qwen_available']:
        st.sidebar.success("✅ Mac Studio 1: Qwen Coder")
    else:
        st.sidebar.error("❌ Mac Studio 1: Offline")
    
    if status['gemma_available']:
        st.sidebar.success("✅ Mac Studio 2: Gemma")
    else:
        st.sidebar.error("❌ Mac Studio 2: Offline")
    
    if status['distributed_ready']:
        st.sidebar.info("⚡ **True Parallel Processing**")
        st.sidebar.success("🌉 Thunderbolt Bridge Active")
    else:
        st.sidebar.warning("⚠️ Distributed system incomplete")
    
    # Show server URLs
    st.sidebar.caption(f"Qwen: {qwen_url}")
    st.sidebar.caption(f"Gemma: {gemma_url}")