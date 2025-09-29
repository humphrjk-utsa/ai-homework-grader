#!/usr/bin/env python3
"""
PC-based llama.cpp AI client for homework grading
Optimized for Windows/Linux systems using llama.cpp
"""

import time
import streamlit as st
from typing import Optional, Dict, Any, List
import os
import glob
import json
from pathlib import Path

class PCLlamaCppClient:
    """PC-based llama.cpp AI client optimized for Windows/Linux"""
    
    def __init__(self, model_path: str = None, model_name: str = None):
        """Initialize PC llama.cpp client with automatic model selection
        
        Args:
            model_path: Direct path to GGUF model file
            model_name: Model name for automatic selection
        """
        self.model = None
        self.model_loaded_in_memory = False
        self.last_response_time = None
        
        if model_path and os.path.exists(model_path):
            self.model_path = model_path
            self.model_name = os.path.basename(model_path)
        elif model_name:
            self.model_path = self._find_model_by_name(model_name)
            self.model_name = model_name
        else:
            # Auto-select best available model
            self.model_path = self._select_best_available_model()
            self.model_name = os.path.basename(self.model_path) if self.model_path else "unknown"
        
        print(f"🤖 Initializing PC llama.cpp client with model: {self.model_name}")
        print(f"📁 Model path: {self.model_path}")
        
        # Don't load model on initialization to avoid blocking UI
        # Model will be loaded on first use
    
    def _get_common_model_directories(self) -> List[str]:
        """Get common directories where GGUF models might be stored"""
        directories = []
        
        # Common model directories
        home = Path.home()
        
        # LM Studio models
        lm_studio_paths = [
            home / ".cache" / "lm-studio" / "models",
            home / "AppData" / "Roaming" / "LMStudio" / "models",  # Windows
            home / ".local" / "share" / "LMStudio" / "models"      # Linux
        ]
        
        # Ollama models (GGUF format)
        ollama_paths = [
            home / ".ollama" / "models",
            home / "AppData" / "Local" / "Ollama" / "models"       # Windows
        ]
        
        # HuggingFace cache
        hf_paths = [
            home / ".cache" / "huggingface" / "hub",
            home / ".cache" / "huggingface" / "transformers"
        ]
        
        # Custom model directories
        custom_paths = [
            Path("./models"),
            Path("../models"),
            home / "models",
            home / "Documents" / "models"
        ]
        
        all_paths = lm_studio_paths + ollama_paths + hf_paths + custom_paths
        
        # Return existing directories
        for path in all_paths:
            if path.exists() and path.is_dir():
                directories.append(str(path))
        
        return directories
    
    def _find_gguf_models(self) -> List[Dict[str, Any]]:
        """Find all available GGUF models"""
        models = []
        directories = self._get_common_model_directories()
        
        for directory in directories:
            # Search for GGUF files recursively
            gguf_files = glob.glob(os.path.join(directory, "**", "*.gguf"), recursive=True)
            
            for gguf_file in gguf_files:
                file_size = os.path.getsize(gguf_file)
                file_size_gb = file_size / (1024**3)
                
                models.append({
                    "path": gguf_file,
                    "name": os.path.basename(gguf_file),
                    "directory": directory,
                    "size_gb": file_size_gb,
                    "size_bytes": file_size
                })
        
        # Sort by size (larger models often better quality)
        models.sort(key=lambda x: x["size_gb"], reverse=True)
        return models
    
    def _select_best_available_model(self) -> Optional[str]:
        """Select the best available GGUF model (prioritizing FP16/BF16)"""
        models = self._find_gguf_models()
        
        if not models:
            print("❌ No GGUF models found in common directories")
            return None
        
        # First, filter out quantized models and prefer floating point
        fp_models = self._filter_floating_point_models(models)
        
        if fp_models:
            print(f"✅ Found {len(fp_models)} floating point models")
            models_to_search = fp_models
        else:
            print("⚠️ No floating point models found, falling back to quantized")
            models_to_search = models
        
        # Preferred model patterns (in order of preference)
        preferred_patterns = [
            "llama-3.1-70b",
            "llama-3.1-8b", 
            "llama-3-70b",
            "llama-3-8b",
            "qwen2.5-coder",
            "qwen",
            "gemma-2-27b",
            "gemma-2-9b",
            "mistral",
            "phi-3"
        ]
        
        # Try to find preferred models
        for pattern in preferred_patterns:
            for model in models_to_search:
                if pattern.lower() in model["name"].lower():
                    model_type = self._get_model_precision_type(model["name"])
                    print(f"✅ Selected preferred model: {model['name']} ({model['size_gb']:.1f}GB, {model_type})")
                    return model["path"]
        
        # Fallback to largest available model (prefer FP16/BF16)
        if models_to_search:
            best_model = models_to_search[0]
            model_type = self._get_model_precision_type(best_model["name"])
            print(f"⚠️ Using largest available model: {best_model['name']} ({best_model['size_gb']:.1f}GB, {model_type})")
            return best_model["path"]
        
        return None
    
    def _filter_floating_point_models(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter models to prefer floating point over quantized versions"""
        from pc_config import get_pc_config
        config = get_pc_config()
        avoid_patterns = config.get("avoid_quantized_patterns", [])
        
        # Separate floating point and quantized models
        fp_models = []
        quantized_models = []
        
        for model in models:
            name_lower = model["name"].lower()
            
            # Check if model is quantized
            is_quantized = any(pattern in name_lower for pattern in avoid_patterns)
            
            # Check for floating point indicators
            is_fp = any(fp_type in name_lower for fp_type in ["fp16", "bf16", "f16", "float16", "bfloat16"])
            
            if is_fp and not is_quantized:
                fp_models.append(model)
            elif not is_quantized and not any(q_pattern in name_lower for q_pattern in ["q4", "q5", "q6", "q8", "int4", "int8"]):
                # Assume unspecified precision is floating point if no quantization indicators
                fp_models.append(model)
            else:
                quantized_models.append(model)
        
        # Sort floating point models by size (larger first)
        fp_models.sort(key=lambda x: x["size_gb"], reverse=True)
        
        return fp_models
    
    def _get_model_precision_type(self, model_name: str) -> str:
        """Determine the precision type of a model"""
        name_lower = model_name.lower()
        
        if "fp16" in name_lower or "f16" in name_lower or "float16" in name_lower:
            return "FP16"
        elif "bf16" in name_lower or "bfloat16" in name_lower:
            return "BF16"
        elif any(q in name_lower for q in ["q4_k_m", "q4_k_s"]):
            return "Q4_K"
        elif any(q in name_lower for q in ["q5_k_m", "q5_k_s"]):
            return "Q5_K"
        elif "q8_0" in name_lower:
            return "Q8_0"
        elif any(q in name_lower for q in ["q4", "int4", "4bit"]):
            return "Q4"
        elif any(q in name_lower for q in ["q8", "int8", "8bit"]):
            return "Q8"
        else:
            return "FP32 (assumed)"
    
    def _find_model_by_name(self, model_name: str) -> Optional[str]:
        """Find a model by partial name match"""
        models = self._find_gguf_models()
        
        for model in models:
            if model_name.lower() in model["name"].lower():
                print(f"✅ Found model by name: {model['name']}")
                return model["path"]
        
        print(f"❌ Model '{model_name}' not found")
        return None
    
    def _load_model(self):
        """Load the llama.cpp model"""
        if self.model_loaded_in_memory:
            return  # Already loaded
        
        if not self.model_path or not os.path.exists(self.model_path):
            print(f"❌ Model file not found: {self.model_path}")
            return
            
        try:
            from llama_cpp import Llama
            
            # Show loading message
            if hasattr(st, 'info'):
                st.info(f"🔄 Loading {self.model_name} with llama.cpp...")
            else:
                print(f"🔄 Loading {self.model_name} with llama.cpp...")
            
            # Determine optimal settings based on system
            n_gpu_layers = self._get_optimal_gpu_layers()
            n_threads = self._get_optimal_threads()
            
            # Load model with optimized settings
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=4096,  # Context window
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=False,
                use_mmap=True,  # Memory mapping for efficiency
                use_mlock=False,  # Don't lock memory (can cause issues)
                n_batch=512,  # Batch size for processing
                f16_kv=True,  # Use half precision for key/value cache
            )
            
            self.model_loaded_in_memory = True
            
            if hasattr(st, 'success'):
                st.success(f"✅ {self.model_name} loaded successfully!")
            else:
                print(f"✅ {self.model_name} loaded successfully!")
            
        except ImportError:
            error_msg = "llama-cpp-python not installed. Install with: pip install llama-cpp-python"
            if hasattr(st, 'error'):
                st.error(f"❌ {error_msg}")
            else:
                print(f"❌ {error_msg}")
            self.model_loaded_in_memory = False
            
        except Exception as e:
            self.model_loaded_in_memory = False
            error_msg = str(e)
            
            if hasattr(st, 'error'):
                st.error(f"❌ Failed to load llama.cpp model: {error_msg}")
            else:
                print(f"❌ Failed to load llama.cpp model: {error_msg}")
    
    def _get_optimal_gpu_layers(self) -> int:
        """Determine optimal number of GPU layers"""
        try:
            # Try to detect GPU
            import subprocess
            
            # Check for NVIDIA GPU
            try:
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("🎮 NVIDIA GPU detected, using GPU acceleration")
                    return -1  # Use all layers on GPU
            except:
                pass
            
            # Check for AMD GPU (ROCm)
            try:
                result = subprocess.run(['rocm-smi'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("🎮 AMD GPU detected, using GPU acceleration")
                    return -1  # Use all layers on GPU
            except:
                pass
            
            # Fallback to CPU
            print("💻 Using CPU inference")
            return 0
            
        except Exception:
            return 0  # CPU fallback
    
    def _get_optimal_threads(self) -> int:
        """Determine optimal number of threads"""
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            # Use 75% of available cores, but at least 4
            optimal_threads = max(4, int(cpu_count * 0.75))
            print(f"🧵 Using {optimal_threads} threads (detected {cpu_count} cores)")
            return optimal_threads
        except:
            return 8  # Safe default
    
    def is_available(self) -> bool:
        """Check if llama.cpp is available"""
        try:
            import llama_cpp
            return True
        except ImportError:
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 2000, show_progress: bool = False) -> Optional[str]:
        """Generate response using llama.cpp
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            show_progress: Show progress indicator
            
        Returns:
            Generated response or None if failed
        """
        if not self.model_loaded_in_memory:
            if show_progress:
                st.warning("Model not loaded, attempting to load...")
            self._load_model()
            
        if not self.model_loaded_in_memory:
            return None
        
        try:
            start_time = time.time()
            
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("🚀 Generating response with llama.cpp...")
            
            # Generate response
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=0.3,
                top_p=0.9,
                echo=False,
                stop=["</s>", "<|im_end|>", "<|endoftext|>"]  # Common stop tokens
            )
            
            end_time = time.time()
            self.last_response_time = end_time - start_time
            
            if show_progress:
                progress_bar.progress(1.0)
                status_text.text(f"✅ Response generated in {self.last_response_time:.1f}s")
            
            return response['choices'][0]['text'].strip()
            
        except Exception as e:
            if show_progress:
                st.error(f"❌ llama.cpp generation failed: {e}")
            return None
    
    def preload_model(self) -> bool:
        """Preload model into memory"""
        if not self.model_loaded_in_memory:
            self._load_model()
        return self.model_loaded_in_memory
    
    def check_model_memory_status(self) -> bool:
        """Check if model is loaded in memory"""
        return self.model_loaded_in_memory
    
    def _check_model_memory_status(self) -> bool:
        """Check if model is loaded in memory (internal method)"""
        return self.model_loaded_in_memory
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_name,
            "path": self.model_path,
            "loaded": self.model_loaded_in_memory,
            "backend": "llama.cpp (PC optimized)",
            "last_response_time": self.last_response_time
        }
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available GGUF models with precision information"""
        models = self._find_gguf_models()
        
        # Add precision type information
        for model in models:
            model["precision_type"] = self._get_model_precision_type(model["name"])
            model["is_floating_point"] = model["precision_type"] in ["FP16", "BF16", "FP32 (assumed)"]
        
        return models

def get_available_ai_backends():
    """Get list of available AI backends for PC"""
    backends = []
    
    # Check llama.cpp
    pc_client = PCLlamaCppClient()
    if pc_client.is_available():
        available_models = pc_client.list_available_models()
        backends.append({
            "name": "llama.cpp (PC Optimized)",
            "type": "pc_llamacpp",
            "recommended": True,
            "description": f"Cross-platform inference, {len(available_models)} GGUF models found",
            "models_count": len(available_models)
        })
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            backends.append({
                "name": "Ollama",
                "type": "ollama",
                "recommended": False,
                "description": "Local model server"
            })
    except:
        pass
    
    return backends

def create_ai_client(backend_type: str = "pc_llamacpp", **kwargs):
    """Factory function to create AI client"""
    if backend_type == "pc_llamacpp":
        return PCLlamaCppClient(**kwargs)
    elif backend_type == "ollama":
        # Import existing Ollama client
        from ai_grader import LocalAIClient
        return LocalAIClient(**kwargs)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")