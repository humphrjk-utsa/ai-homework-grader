#!/usr/bin/env python3
"""
MLX-based AI client for homework grading
Optimized for Apple Silicon Mac
"""

import time
import streamlit as st
from typing import Optional, Dict, Any
import os

class MLXAIClient:
    """MLX-based AI client optimized for Apple Silicon"""
    
    def __init__(self, model_name: str = None):
        """Initialize MLX AI client with automatic model selection"""
        if model_name is None:
            # Use GPT-OSS-120B as primary for now (Kimi K2 has trust_remote_code issues)
            preferred_models = [
                "lmstudio-community/gpt-oss-120b-MLX-8bit",
                "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit", 
                "mlx-community/gemma-2-27b-it-4bit",
                "mlx-community/Kimi-K2-Instruct-0905-mlx-DQ3_K_M"  # Try Kimi last
            ]
            model_name = self._select_available_model(preferred_models)
        
        print(f"🤖 Initializing MLX client with model: {model_name}")
        """Initialize MLX AI client
        
        Args:
            model_name: HuggingFace model name (MLX compatible)
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.model_loaded_in_memory = False
        self.last_response_time = None
        
        # Don't load model on initialization to avoid blocking UI
        # Model will be loaded on first use
    
    def _select_available_model(self, preferred_models):
        """Select the first available model from the preferred list"""
        import os
        import glob
        
        # Get available MLX models
        hf_cache = os.path.expanduser("~/.cache/huggingface/hub/")
        available_models = []
        
        if os.path.exists(hf_cache):
            model_dirs = glob.glob(os.path.join(hf_cache, "models--*mlx*"))
            model_dirs.extend(glob.glob(os.path.join(hf_cache, "models--*MLX*")))
            model_dirs.extend(glob.glob(os.path.join(hf_cache, "models--lmstudio-community--*")))
            model_dirs.extend(glob.glob(os.path.join(hf_cache, "models--mlx-community--*")))
            
            for model_dir in model_dirs:
                dir_name = os.path.basename(model_dir)
                if dir_name.startswith("models--"):
                    parts = dir_name[8:].split("--")
                    if len(parts) >= 2:
                        model_name = "/".join(parts)
                        available_models.append(model_name)
        
        # Select first preferred model that's available
        for preferred in preferred_models:
            if preferred in available_models:
                print(f"✅ Selected model: {preferred}")
                return preferred
        
        # Fallback to first available model
        if available_models:
            fallback = available_models[0]
            print(f"⚠️ Using fallback model: {fallback}")
            return fallback
        
        # Last resort - default to GPT-OSS-120B
        print(f"❌ No MLX models found, using GPT-OSS-120B default")
        return "lmstudio-community/gpt-oss-120b-MLX-8bit"
    
    def _load_model(self):
        """Load the MLX model and tokenizer"""
        if self.model_loaded_in_memory:
            return  # Already loaded
            
        try:
            from mlx_lm import load, generate
            import os
            
            # Only show loading message if in Streamlit context
            if hasattr(st, 'info'):
                st.info(f"🔄 Loading {self.model_name} with MLX (optimized for Apple Silicon)...")
            else:
                print(f"🔄 Loading {self.model_name} with MLX...")
            
            # Special handling for Kimi models that require trust_remote_code
            if "kimi" in self.model_name.lower():
                # Try to load with trust_remote_code by monkey-patching
                try:
                    import transformers
                    from transformers import AutoConfig, AutoTokenizer
                    
                    # Pre-load config and tokenizer with trust_remote_code=True
                    print("🔧 Pre-loading Kimi model components with trust_remote_code=True...")
                    config = AutoConfig.from_pretrained(self.model_name, trust_remote_code=True)
                    tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
                    
                    # Now try MLX load (it should use the cached components)
                    self.model, self.tokenizer = load(self.model_name)
                    
                except Exception as kimi_error:
                    print(f"⚠️ Kimi-specific loading failed: {kimi_error}")
                    # Fall back to regular load
                    self.model, self.tokenizer = load(self.model_name)
            else:
                # Regular loading for other models
                self.model, self.tokenizer = load(self.model_name)
            self.model_loaded_in_memory = True
            
            if hasattr(st, 'success'):
                st.success(f"✅ {self.model_name} loaded successfully!")
            else:
                print(f"✅ {self.model_name} loaded successfully!")
            
        except Exception as e:
            self.model_loaded_in_memory = False
            error_msg = str(e)
            
            if hasattr(st, 'error'):
                st.error(f"❌ Failed to load MLX model: {error_msg}")
            else:
                print(f"❌ Failed to load MLX model: {error_msg}")
                
            # If Kimi K2 fails, try GPT-OSS-120B fallback
            if "kimi" in self.model_name.lower():
                print("🔄 Kimi K2 failed, falling back to GPT-OSS-120B...")
                self._try_fallback_model()
    
    def _try_fallback_model(self):
        """Try loading GPT-OSS-120B as fallback"""
        try:
            from mlx_lm import load
            fallback_model = "lmstudio-community/gpt-oss-120b-MLX-8bit"
            
            print(f"🔄 Trying fallback: {fallback_model}")
            self.model_name = fallback_model
            self.model, self.tokenizer = load(self.model_name)
            self.model_loaded_in_memory = True
            
            if hasattr(st, 'success'):
                st.success(f"✅ Fallback successful: {self.model_name}")
            else:
                print(f"✅ Fallback successful: {self.model_name}")
                
        except Exception as fallback_error:
            if hasattr(st, 'error'):
                st.error(f"❌ Fallback also failed: {fallback_error}")
            else:
                print(f"❌ Fallback also failed: {fallback_error}")
            self.model_loaded_in_memory = False
    
    def is_available(self) -> bool:
        """Check if MLX AI is available"""
        try:
            import mlx_lm
            return True
        except ImportError:
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 2000, show_progress: bool = False) -> Optional[str]:
        """Generate response using MLX
        
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
            from mlx_lm import generate
            
            start_time = time.time()
            
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("🚀 Generating response with MLX...")
            
            # Generate response
            response_generator = generate(
                model=self.model,
                tokenizer=self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False
            )
            
            # MLX generate returns a generator, collect all tokens
            response_text = ''.join(response_generator)
            
            end_time = time.time()
            self.last_response_time = end_time - start_time
            
            if show_progress:
                progress_bar.progress(1.0)
                status_text.text(f"✅ Response generated in {self.last_response_time:.1f}s")
            
            return response_text
            
        except Exception as e:
            if show_progress:
                st.error(f"❌ MLX generation failed: {e}")
            return None
    
    def preload_model(self) -> bool:
        """Preload model into memory"""
        if not self.model_loaded_in_memory:
            self._load_model()
        return self.model_loaded_in_memory
    
    def check_model_memory_status(self) -> bool:
        """Check if model is loaded in memory (MLX compatibility method)"""
        return self.model_loaded_in_memory
    
    def _check_model_memory_status(self) -> bool:
        """Check if model is loaded in memory (internal method)"""
        return self.model_loaded_in_memory
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_name,
            "loaded": self.model_loaded_in_memory,
            "backend": "MLX (Apple Silicon optimized)",
            "last_response_time": self.last_response_time
        }

class LlamaCppClient:
    """Alternative llama.cpp client"""
    
    def __init__(self, model_path: str = None):
        """Initialize llama.cpp client
        
        Args:
            model_path: Path to GGUF model file
        """
        self.model_path = model_path
        self.model = None
        self.model_loaded_in_memory = False
        self.last_response_time = None
        
        if model_path and os.path.exists(model_path):
            self._load_model()
    
    def _load_model(self):
        """Load llama.cpp model"""
        try:
            from llama_cpp import Llama
            
            st.info(f"🔄 Loading model with llama.cpp...")
            
            # Load model with optimized settings for Mac
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=4096,  # Context window
                n_threads=8,  # Use multiple threads
                n_gpu_layers=-1,  # Use Metal if available
                verbose=False
            )
            
            self.model_loaded_in_memory = True
            st.success("✅ llama.cpp model loaded successfully!")
            
        except ImportError:
            st.error("❌ llama-cpp-python not installed. Run: pip install llama-cpp-python")
        except Exception as e:
            st.error(f"❌ Failed to load llama.cpp model: {e}")
            self.model_loaded_in_memory = False
    
    def is_available(self) -> bool:
        """Check if llama.cpp is available"""
        try:
            import llama_cpp
            return True
        except ImportError:
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 2000, show_progress: bool = False) -> Optional[str]:
        """Generate response using llama.cpp"""
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
                echo=False
            )
            
            end_time = time.time()
            self.last_response_time = end_time - start_time
            
            if show_progress:
                progress_bar.progress(1.0)
                status_text.text(f"✅ Response generated in {self.last_response_time:.1f}s")
            
            return response['choices'][0]['text']
            
        except Exception as e:
            if show_progress:
                st.error(f"❌ llama.cpp generation failed: {e}")
            return None

def get_available_ai_backends():
    """Get list of available AI backends"""
    backends = []
    
    # Check MLX
    mlx_client = MLXAIClient()
    if mlx_client.is_available():
        backends.append({
            "name": "MLX (Apple Silicon Optimized)",
            "type": "mlx",
            "recommended": True,
            "description": "Native Apple Silicon optimization, fastest on Mac"
        })
    
    # Check llama.cpp
    llamacpp_client = LlamaCppClient()
    if llamacpp_client.is_available():
        backends.append({
            "name": "llama.cpp",
            "type": "llamacpp", 
            "recommended": False,
            "description": "Cross-platform, requires GGUF model files"
        })
    
    # Check Ollama (existing)
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            backends.append({
                "name": "Ollama",
                "type": "ollama",
                "recommended": False,
                "description": "Local model server (currently having issues)"
            })
    except:
        pass
    
    return backends

def create_ai_client(backend_type: str = "mlx", **kwargs):
    """Factory function to create AI client"""
    if backend_type == "mlx":
        return MLXAIClient(**kwargs)
    elif backend_type == "llamacpp":
        return LlamaCppClient(**kwargs)
    elif backend_type == "ollama":
        # Import existing Ollama client
        from ai_grader import LocalAIClient
        return LocalAIClient(**kwargs)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")