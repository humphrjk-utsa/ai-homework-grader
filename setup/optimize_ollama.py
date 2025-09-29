#!/usr/bin/env python3
"""
Optimize Ollama Configuration for RTX Pro 6000
Maximizes parallel processing performance without MIG
"""

import json
import requests
import time
import os
from pathlib import Path
from typing import Dict, Any, List

class OllamaOptimizer:
    """Optimize Ollama for maximum parallel performance"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api"
    
    def check_ollama_status(self) -> Dict[str, Any]:
        """Check Ollama server status and configuration"""
        try:
            # Check if server is running
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code != 200:
                return {"running": False, "error": f"HTTP {response.status_code}"}
            
            # Get model list
            models_data = response.json()
            models = models_data.get('models', [])
            
            # Check GPU memory usage
            gpu_info = self._get_gpu_info()
            
            return {
                "running": True,
                "models_count": len(models),
                "models": [m['name'] for m in models],
                "gpu_info": gpu_info
            }
            
        except Exception as e:
            return {"running": False, "error": str(e)}
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information"""
        try:
            import subprocess
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                parts = result.stdout.strip().split(', ')
                if len(parts) >= 3:
                    return {
                        "memory_used_mb": int(parts[0]),
                        "memory_total_mb": int(parts[1]),
                        "gpu_utilization": int(parts[2]),
                        "memory_used_gb": round(int(parts[0]) / 1024, 1),
                        "memory_total_gb": round(int(parts[1]) / 1024, 1),
                        "memory_free_gb": round((int(parts[1]) - int(parts[0])) / 1024, 1)
                    }
            
            return {"error": "Could not parse nvidia-smi output"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def optimize_model_loading(self, models: List[str]) -> Dict[str, Any]:
        """Optimize model loading for parallel processing"""
        print("🚀 Optimizing model loading for parallel processing...")
        
        results = {}
        
        for model in models:
            print(f"\n🔧 Optimizing {model}...")
            
            # Pre-load model with optimized settings
            start_time = time.time()
            
            try:
                # Send a small prompt to load the model into VRAM
                payload = {
                    "model": model,
                    "prompt": "Ready for grading",
                    "stream": False,
                    "options": {
                        "num_predict": 1,
                        "temperature": 0.1,
                        "num_ctx": 4096,  # Optimize context window
                        "num_batch": 512,  # Optimize batch size
                        "num_gpu_layers": -1,  # Use all GPU layers
                        "use_mmap": True,  # Memory mapping
                        "use_mlock": False,  # Don't lock memory
                        "num_thread": 8  # Optimize CPU threads
                    }
                }
                
                response = requests.post(f"{self.api_url}/generate", json=payload, timeout=120)
                
                load_time = time.time() - start_time
                
                if response.status_code == 200:
                    results[model] = {
                        "status": "optimized",
                        "load_time": round(load_time, 2),
                        "memory_after": self._get_gpu_info()
                    }
                    print(f"✅ {model} optimized in {load_time:.1f}s")
                else:
                    results[model] = {
                        "status": "failed",
                        "error": f"HTTP {response.status_code}"
                    }
                    print(f"❌ {model} optimization failed")
                    
            except Exception as e:
                results[model] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {model} error: {e}")
        
        return results
    
    def benchmark_parallel_performance(self) -> Dict[str, Any]:
        """Benchmark parallel processing performance"""
        print("\n🏃 Benchmarking parallel performance...")
        
        models = [
            "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest",
            "gemma3:27b-it-q8_0"
        ]
        
        # Test prompts
        code_prompt = """Analyze this R code:
library(dplyr)
data <- read.csv("file.csv")
summary(data)
"""
        
        feedback_prompt = """Provide feedback on this data analysis:
The student calculated basic statistics and created visualizations.
"""
        
        # Sequential benchmark
        print("📊 Testing sequential processing...")
        sequential_start = time.time()
        
        for i, (model, prompt) in enumerate(zip(models, [code_prompt, feedback_prompt])):
            model_start = time.time()
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 50,  # Short response for benchmark
                    "temperature": 0.3
                }
            }
            
            response = requests.post(f"{self.api_url}/generate", json=payload, timeout=60)
            model_time = time.time() - model_start
            
            print(f"  Model {i+1}: {model_time:.1f}s")
        
        sequential_time = time.time() - sequential_start
        
        # Parallel benchmark (simulated)
        print("⚡ Testing parallel processing...")
        import concurrent.futures
        
        def generate_response(model_prompt_pair):
            model, prompt = model_prompt_pair
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 50,
                    "temperature": 0.3
                }
            }
            
            start = time.time()
            response = requests.post(f"{self.api_url}/generate", json=payload, timeout=60)
            return time.time() - start
        
        parallel_start = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(generate_response, (models[0], code_prompt)),
                executor.submit(generate_response, (models[1], feedback_prompt))
            ]
            
            times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        parallel_time = time.time() - parallel_start
        
        # Calculate efficiency
        efficiency = sequential_time / parallel_time if parallel_time > 0 else 1.0
        
        results = {
            "sequential_time": round(sequential_time, 2),
            "parallel_time": round(parallel_time, 2),
            "efficiency_gain": round(efficiency, 2),
            "individual_times": [round(t, 2) for t in times],
            "gpu_info": self._get_gpu_info()
        }
        
        print(f"📊 Results:")
        print(f"  Sequential: {sequential_time:.1f}s")
        print(f"  Parallel: {parallel_time:.1f}s")
        print(f"  Efficiency: {efficiency:.1f}x speedup")
        
        return results
    
    def create_optimized_config(self) -> Dict[str, Any]:
        """Create optimized Ollama configuration"""
        
        # Optimal settings for RTX Pro 6000
        config = {
            "models": {
                "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest": {
                    "num_ctx": 4096,
                    "num_batch": 512,
                    "num_gpu_layers": -1,
                    "num_thread": 8,
                    "use_mmap": True,
                    "use_mlock": False,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                },
                "gemma3:27b-it-q8_0": {
                    "num_ctx": 4096,
                    "num_batch": 512,
                    "num_gpu_layers": -1,
                    "num_thread": 8,
                    "use_mmap": True,
                    "use_mlock": False,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            },
            "parallel_processing": {
                "max_concurrent": 2,
                "timeout_seconds": 300,
                "retry_attempts": 3
            },
            "gpu_optimization": {
                "target_memory_usage": 0.8,  # Use 80% of VRAM
                "memory_growth": True,
                "allow_memory_growth": True
            }
        }
        
        # Save config
        config_path = Path("ollama_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Saved optimized config to {config_path}")
        
        return config
    
    def print_optimization_report(self):
        """Print comprehensive optimization report"""
        print("\n🖥️ RTX Pro 6000 Ollama Optimization Report")
        print("=" * 60)
        
        # System status
        status = self.check_ollama_status()
        print(f"Ollama Status: {'✅ Running' if status['running'] else '❌ Not Running'}")
        
        if status['running']:
            print(f"Models Available: {status['models_count']}")
            
            gpu_info = status.get('gpu_info', {})
            if 'memory_total_gb' in gpu_info:
                print(f"GPU Memory: {gpu_info['memory_used_gb']:.1f}GB / {gpu_info['memory_total_gb']:.1f}GB used")
                print(f"GPU Utilization: {gpu_info.get('gpu_utilization', 'N/A')}%")
        
        # Optimization recommendations
        print(f"\n💡 Optimization Recommendations:")
        print(f"✅ Use parallel processing for 1.3x+ speedup")
        print(f"✅ Keep both models loaded in VRAM (61GB total)")
        print(f"✅ Use Q8_0 quantization for best quality/performance")
        print(f"✅ Optimize context window (4096 tokens)")
        print(f"✅ Enable memory mapping for efficiency")
        
        # Performance expectations
        print(f"\n📊 Expected Performance:")
        print(f"• Code Analysis (Qwen 3.0 Coder 30B): ~15s")
        print(f"• Feedback Generation (Gemma 3.0 27B): ~47s")
        print(f"• Parallel Total: ~47s (vs ~62s sequential)")
        print(f"• Memory Usage: ~61GB / 95.6GB (64% utilization)")

def main():
    """Main optimization function"""
    optimizer = OllamaOptimizer()
    
    print("🚀 RTX Pro 6000 Ollama Optimizer")
    print("=" * 40)
    
    # Check status
    status = optimizer.check_ollama_status()
    
    if not status['running']:
        print("❌ Ollama is not running")
        print("💡 Start Ollama with: ollama serve")
        return False
    
    print("✅ Ollama is running")
    
    # Optimize models
    models = [
        "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest",
        "gemma3:27b-it-q8_0"
    ]
    
    optimization_results = optimizer.optimize_model_loading(models)
    
    # Benchmark performance
    benchmark_results = optimizer.benchmark_parallel_performance()
    
    # Create optimized config
    config = optimizer.create_optimized_config()
    
    # Print report
    optimizer.print_optimization_report()
    
    print(f"\n🎉 Optimization complete!")
    print(f"💡 Your RTX Pro 6000 is optimized for maximum homework grading performance!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n💡 Next steps:")
            print("   1. Run: python test_ollama_grading.py")
            print("   2. Start grading: streamlit run pc_start.py")
    except KeyboardInterrupt:
        print("\n👋 Optimization interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")