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
        
        # Initialize server manager for auto-restart
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from server_manager import ServerManager
            self.server_manager = ServerManager()
            self.auto_restart_enabled = True
        except Exception as e:
            print(f"⚠️ Server manager not available: {e}")
            self.server_manager = None
            self.auto_restart_enabled = False
        
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
    
    def auto_restart_server(self, server_name: str) -> bool:
        """Auto-restart a server if it's down"""
        if not self.auto_restart_enabled or not self.server_manager:
            return False
        
        print(f"🔄 Auto-restarting {server_name}...")
        try:
            success = self.server_manager.auto_restart_if_needed(server_name)
            if success:
                print(f"✅ {server_name} restarted successfully")
            else:
                print(f"❌ Failed to restart {server_name}")
            return success
        except Exception as e:
            print(f"❌ Auto-restart failed: {e}")
            return False
    
    def generate_code_analysis(self, prompt: str, max_tokens: int = 1800, retry_count: int = 0) -> Optional[str]:
        """Generate code analysis using Qwen on Mac Studio 1"""
        try:
            start_time = time.time()
            prompt_tokens = len(prompt.split())  # Rough token count
            
            response = requests.post(
                f"{self.qwen_server_url}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.1
                },
                timeout=180  # 3 minute timeout (increased for 8-bit model)
            )
            
            if response.status_code == 200:
                result = response.json()
                generation_time = time.time() - start_time
                self.last_response_times['qwen'] = generation_time
                
                # Calculate performance metrics
                response_text = result.get('response', '')
                output_tokens = len(response_text.split())
                tokens_per_second = output_tokens / generation_time if generation_time > 0 else 0
                
                # Store performance metrics
                self.last_response_times['qwen_metrics'] = {
                    'prompt_tokens': prompt_tokens,
                    'output_tokens': output_tokens,
                    'total_tokens': prompt_tokens + output_tokens,
                    'generation_time': generation_time,
                    'tokens_per_second': tokens_per_second,
                    'prompt_eval_time': generation_time * 0.1,  # Estimate 10% for prompt processing
                    'model': 'Qwen-30B-Coder'
                }
                
                print(f"🔧 [QWEN] {output_tokens} tokens in {generation_time:.1f}s ({tokens_per_second:.1f} tok/s)")
                
                return response_text
            else:
                print(f"❌ Qwen server returned status {response.status_code}")
                # Try auto-restart if enabled and this is first attempt
                if retry_count == 0 and self.auto_restart_enabled:
                    print("🔄 Attempting to auto-restart Qwen server...")
                    if self.auto_restart_server('qwen'):
                        time.sleep(5)  # Wait for server to start
                        return self.generate_code_analysis(prompt, max_tokens, retry_count=1)
                return None
                
        except requests.exceptions.Timeout:
            print(f"⏰ Qwen server timeout after 180 seconds")
            st.error(f"⏰ Qwen server timeout - request took too long")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Qwen server connection error: {e}")
            # Try auto-restart if enabled and this is first attempt
            if retry_count == 0 and self.auto_restart_enabled:
                print("🔄 Attempting to auto-restart Qwen server...")
                if self.auto_restart_server('qwen'):
                    time.sleep(5)  # Wait for server to start
                    return self.generate_code_analysis(prompt, max_tokens, retry_count=1)
            st.error(f"❌ Qwen server connection error: {e}")
            return None
        except Exception as e:
            print(f"❌ Qwen server error: {e}")
            st.error(f"❌ Qwen server error: {e}")
            return None
    
    def generate_feedback(self, prompt: str, max_tokens: int = 3000, retry_count: int = 0) -> Optional[str]:
        """Generate feedback using Gemma on Mac Studio 1"""
        try:
            start_time = time.time()
            prompt_tokens = len(prompt.split())  # Rough token count
            
            response = requests.post(
                f"{self.gemma_server_url}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.3
                },
                timeout=200  # 3.3 minute timeout (increased for larger prompts)
            )
            
            if response.status_code == 200:
                result = response.json()
                generation_time = time.time() - start_time
                self.last_response_times['gemma'] = generation_time
                
                # Calculate performance metrics
                response_text = result.get('response', '')
                print(f"🔍 DEBUG: Gemma response keys: {result.keys()}")
                print(f"🔍 DEBUG: Response text length: {len(response_text)}")
                print(f"🔍 DEBUG: Response preview: {response_text[:200] if response_text else 'EMPTY!'}")
                
                output_tokens = len(response_text.split()) if response_text else 0
                tokens_per_second = output_tokens / generation_time if generation_time > 0 else 0
                
                # Store performance metrics
                self.last_response_times['gemma_metrics'] = {
                    'prompt_tokens': prompt_tokens,
                    'output_tokens': output_tokens,
                    'total_tokens': prompt_tokens + output_tokens,
                    'generation_time': generation_time,
                    'tokens_per_second': tokens_per_second,
                    'prompt_eval_time': generation_time * 0.15,  # Estimate 15% for prompt processing
                    'model': 'Gemma-3-27B'
                }
                
                print(f"📝 [GEMMA] {output_tokens} tokens in {generation_time:.1f}s ({tokens_per_second:.1f} tok/s)")
                print(f"   Response preview: {response_text[:100]}...")
                
                return response_text
            else:
                print(f"❌ Gemma server returned status {response.status_code}")
                # Try auto-restart if enabled and this is first attempt
                if retry_count == 0 and self.auto_restart_enabled:
                    print("🔄 Attempting to auto-restart Gemma server...")
                    if self.auto_restart_server('gemma'):
                        time.sleep(5)  # Wait for server to start
                        return self.generate_feedback(prompt, max_tokens, retry_count=1)
                return None
                
        except requests.exceptions.Timeout:
            print(f"⏰ Gemma server timeout after 200 seconds")
            st.error(f"⏰ Gemma server timeout - request took too long")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Gemma server connection error: {e}")
            # Try auto-restart if enabled and this is first attempt
            if retry_count == 0 and self.auto_restart_enabled:
                print("🔄 Attempting to auto-restart Gemma server...")
                if self.auto_restart_server('gemma'):
                    time.sleep(5)  # Wait for server to start
                    return self.generate_feedback(prompt, max_tokens, retry_count=1)
            st.error(f"❌ Gemma server connection error: {e}")
            return None
        except Exception as e:
            print(f"❌ Gemma server error: {e}")
            import traceback
            print(traceback.format_exc())
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
            print(f"🚀 Starting parallel generation...")
            print(f"   Qwen server: {self.qwen_server_url}")
            print(f"   Gemma server: {self.gemma_server_url}")
            
            # Use ThreadPoolExecutor for true parallel execution
            with ThreadPoolExecutor(max_workers=2) as executor:
                start_time = time.time()
                
                # Submit both tasks
                print(f"📤 Submitting Qwen task (code analysis)...")
                qwen_future = executor.submit(self.generate_code_analysis, code_prompt)
                print(f"📤 Submitting Gemma task (feedback)...")
                gemma_future = executor.submit(self.generate_feedback, feedback_prompt)
                
                # Get results with increased timeout
                print(f"⏳ Waiting for Qwen result...")
                try:
                    qwen_result = qwen_future.result(timeout=180)  # Increased from 120 to 180
                    print(f"✅ Qwen result received: {len(qwen_result) if qwen_result else 0} chars")
                    
                    # If Qwen failed, try to restart it
                    if not qwen_result and self.auto_restart_enabled:
                        print("⚠️ Qwen returned None, attempting auto-restart...")
                        if self.auto_restart_server('qwen'):
                            print("🔄 Retrying Qwen after restart...")
                            qwen_result = self.generate_code_analysis(code_prompt)
                except TimeoutError:
                    print("⏰ Qwen timed out after 180 seconds")
                    if self.auto_restart_enabled:
                        print("🔄 Attempting to restart Qwen after timeout...")
                        if self.auto_restart_server('qwen'):
                            print("🔄 Retrying Qwen after restart...")
                            qwen_result = self.generate_code_analysis(code_prompt)
                        else:
                            qwen_result = None
                    else:
                        qwen_result = None
                
                print(f"⏳ Waiting for Gemma result...")
                try:
                    gemma_result = gemma_future.result(timeout=200)  # Increased from 150 to 200
                    print(f"✅ Gemma result received: {len(gemma_result) if gemma_result else 0} chars")
                    
                    # If Gemma failed, try to restart it
                    if not gemma_result and self.auto_restart_enabled:
                        print("⚠️ Gemma returned None, attempting auto-restart...")
                        if self.auto_restart_server('gemma'):
                            print("🔄 Retrying Gemma after restart...")
                            gemma_result = self.generate_feedback(feedback_prompt)
                except TimeoutError:
                    print("⏰ Gemma timed out after 200 seconds")
                    if self.auto_restart_enabled:
                        print("🔄 Attempting to restart Gemma after timeout...")
                        if self.auto_restart_server('gemma'):
                            print("🔄 Retrying Gemma after restart...")
                            gemma_result = self.generate_feedback(feedback_prompt)
                        else:
                            gemma_result = None
                    else:
                        gemma_result = None
                
                total_time = time.time() - start_time
                
                # Get performance metrics
                qwen_metrics = self.last_response_times.get('qwen_metrics', {})
                gemma_metrics = self.last_response_times.get('gemma_metrics', {})
                
                return {
                    'code_analysis': qwen_result,
                    'feedback': gemma_result,
                    'parallel_time': total_time,
                    'qwen_time': self.last_response_times.get('qwen', 0),
                    'gemma_time': self.last_response_times.get('gemma', 0),
                    'parallel_efficiency': (self.last_response_times.get('qwen', 0) + 
                                          self.last_response_times.get('gemma', 0)) / total_time,
                    'performance_metrics': {
                        'qwen': qwen_metrics,
                        'gemma': gemma_metrics,
                        'total_tokens': qwen_metrics.get('total_tokens', 0) + gemma_metrics.get('total_tokens', 0),
                        'combined_tokens_per_second': (
                            qwen_metrics.get('output_tokens', 0) + gemma_metrics.get('output_tokens', 0)
                        ) / total_time if total_time > 0 else 0
                    }
                }
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Parallel generation failed: {e}")
            print(f"Full traceback:\n{error_details}")
            st.error(f"❌ Parallel generation failed: {e}")
            return {
                'code_analysis': None,
                'feedback': None,
                'parallel_time': 0,
                'error': f"{str(e)}\n{error_details}"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of both Mac Studios with model information"""
        qwen_status = self.check_server_status(self.qwen_server_url, "Qwen")
        gemma_status = self.check_server_status(self.gemma_server_url, "Gemma")
        
        # Get model information from servers
        qwen_info = {}
        gemma_info = {}
        
        if qwen_status:
            try:
                import requests
                response = requests.get(f"{self.qwen_server_url}/status", timeout=3)
                if response.status_code == 200:
                    qwen_info = response.json()
            except:
                pass
        
        if gemma_status:
            try:
                import requests
                response = requests.get(f"{self.gemma_server_url}/status", timeout=3)
                if response.status_code == 200:
                    gemma_info = response.json()
            except:
                pass
        
        return {
            'qwen_available': qwen_status,
            'gemma_available': gemma_status,
            'distributed_ready': qwen_status and gemma_status,
            'qwen_server': self.qwen_server_url,
            'gemma_server': self.gemma_server_url,
            'qwen_info': qwen_info,
            'gemma_info': gemma_info
        }
    
    def get_performance_diagnostics(self) -> Dict[str, Any]:
        """Get detailed performance diagnostics for both models"""
        qwen_metrics = self.last_response_times.get('qwen_metrics', {})
        gemma_metrics = self.last_response_times.get('gemma_metrics', {})
        
        diagnostics = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'qwen_performance': {
                'model': qwen_metrics.get('model', 'Qwen-30B-Coder'),
                'server': 'Mac Studio 2',
                'prompt_tokens': qwen_metrics.get('prompt_tokens', 0),
                'output_tokens': qwen_metrics.get('output_tokens', 0),
                'total_tokens': qwen_metrics.get('total_tokens', 0),
                'generation_time_seconds': qwen_metrics.get('generation_time', 0),
                'tokens_per_second': qwen_metrics.get('tokens_per_second', 0),
                'prompt_eval_time_seconds': qwen_metrics.get('prompt_eval_time', 0),
                'server_url': self.qwen_server_url
            },
            'gemma_performance': {
                'model': gemma_metrics.get('model', 'GPT-OSS-120B'),
                'server': 'Mac Studio 1',
                'prompt_tokens': gemma_metrics.get('prompt_tokens', 0),
                'output_tokens': gemma_metrics.get('output_tokens', 0),
                'total_tokens': gemma_metrics.get('total_tokens', 0),
                'generation_time_seconds': gemma_metrics.get('generation_time', 0),
                'tokens_per_second': gemma_metrics.get('tokens_per_second', 0),
                'prompt_eval_time_seconds': gemma_metrics.get('prompt_eval_time', 0),
                'server_url': self.gemma_server_url
            },
            'combined_metrics': {
                'total_tokens_processed': qwen_metrics.get('total_tokens', 0) + gemma_metrics.get('total_tokens', 0),
                'total_output_tokens': qwen_metrics.get('output_tokens', 0) + gemma_metrics.get('output_tokens', 0),
                'parallel_efficiency': self.last_response_times.get('parallel_efficiency', 0),
                'combined_throughput_tokens_per_second': (
                    qwen_metrics.get('output_tokens', 0) + gemma_metrics.get('output_tokens', 0)
                ) / max(qwen_metrics.get('generation_time', 1), gemma_metrics.get('generation_time', 1))
            }
        }
        
        return diagnostics

def show_distributed_status():
    """Show distributed system status in Streamlit sidebar with dynamic model names"""
    
    # Get server URLs from config file or environment
    import os
    import json
    import requests
    
    # Try to read from distributed_config.json first
    try:
        with open('distributed_config.json', 'r') as f:
            config = json.load(f)
        qwen_url = config['urls']['qwen_server']
        gemma_url = config['urls']['gemma_server']
    except:
        # Fallback to environment variables or defaults
        qwen_url = os.getenv('QWEN_SERVER_URL', 'http://10.55.0.1:5001')
        gemma_url = os.getenv('GEMMA_SERVER_URL', 'http://10.55.0.2:5002')
    
    client = DistributedMLXClient(qwen_url, gemma_url)
    status = client.get_system_status()
    
    # Get actual model information from servers
    def get_server_info(url):
        try:
            response = requests.get(f"{url}/status", timeout=3)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}
    
    qwen_info = get_server_info(qwen_url)
    gemma_info = get_server_info(gemma_url)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🖥️ Distributed MLX System")
    
    # Dynamic labels based on actual server configuration
    if status['qwen_available']:
        qwen_model = qwen_info.get('model', 'Qwen-30B-Coder')
        qwen_purpose = qwen_info.get('purpose', 'Code Analysis')
        qwen_studio = qwen_info.get('mac_studio', 2)
        st.sidebar.success(f"✅ Mac Studio {qwen_studio}: {qwen_model}")
        st.sidebar.caption(f"   Purpose: {qwen_purpose}")
    else:
        st.sidebar.error("❌ Qwen Server: Offline")
    
    if status['gemma_available']:
        gemma_model = gemma_info.get('model', 'GPT-OSS-120B')
        gemma_purpose = gemma_info.get('purpose', 'Feedback Generation')
        gemma_studio = gemma_info.get('mac_studio', 1)
        st.sidebar.success(f"✅ Mac Studio {gemma_studio}: {gemma_model}")
        st.sidebar.caption(f"   Purpose: {gemma_purpose}")
    else:
        st.sidebar.error("❌ Feedback Server: Offline")
    
    if status['distributed_ready']:
        st.sidebar.info("⚡ **True Parallel Processing**")
        st.sidebar.success("🌉 Thunderbolt Bridge Active")
    else:
        st.sidebar.warning("⚠️ Distributed system incomplete")
    
    # Show server URLs with dynamic information
    st.sidebar.markdown("**Server Details:**")
    if qwen_info:
        qwen_model_short = qwen_info.get('model', 'Unknown').replace('-MLX-8bit', '').replace('gpt-oss-', 'GPT-OSS-')
        st.sidebar.caption(f"Code Analysis: {qwen_url}")
        st.sidebar.caption(f"Model: {qwen_model_short}")
    else:
        st.sidebar.caption(f"Code Analysis: {qwen_url} (offline)")
    
    if gemma_info:
        gemma_model_short = gemma_info.get('model', 'Unknown').replace('-MLX-8bit', '').replace('gpt-oss-', 'GPT-OSS-')
        st.sidebar.caption(f"Feedback Gen: {gemma_url}")
        st.sidebar.caption(f"Model: {gemma_model_short}")
    else:
        st.sidebar.caption(f"Feedback Gen: {gemma_url} (offline)")
    
    # Show server URLs
    st.sidebar.caption(f"Qwen: {qwen_url}")
    st.sidebar.caption(f"Gemma: {gemma_url}")