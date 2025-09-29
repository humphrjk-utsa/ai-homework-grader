#!/usr/bin/env python3
"""
Unified Model Interface for MLX and Ollama
Handles both model types seamlessly in the UI
"""

import streamlit as st
import requests
import os
from datetime import datetime

class UnifiedModelInterface:
    """Unified interface for both MLX and Ollama models"""
    
    def __init__(self):
        self.detect_available_backends()
        self.setup_preferred_backend()
    
    def detect_available_backends(self):
        """Detect which AI backends are available"""
        self.available_backends = {}
        
        # Check MLX (Apple Silicon optimized)
        try:
            from mlx_ai_client import MLXAIClient
            mlx_client = MLXAIClient()
            if mlx_client.is_available():
                self.available_backends['MLX'] = {
                    'client': mlx_client,
                    'status': 'available',
                    'description': 'Apple Silicon optimized (MLX)',
                    'models': mlx_client.get_available_models() if hasattr(mlx_client, 'get_available_models') else ['gpt-oss-120b']
                }
        except Exception as e:
            self.available_backends['MLX'] = {
                'status': 'unavailable',
                'error': str(e),
                'description': 'Apple Silicon optimized (MLX) - Not available'
            }
        
        # Check Ollama
        try:
            from ai_grader import LocalAIClient
            ollama_client = LocalAIClient()
            if ollama_client.is_available():
                models = ollama_client.get_available_models()
                self.available_backends['Ollama'] = {
                    'client': ollama_client,
                    'status': 'available',
                    'description': 'Ollama (Cross-platform)',
                    'models': [m.get('name', '') for m in models]
                }
            else:
                self.available_backends['Ollama'] = {
                    'status': 'unavailable',
                    'error': 'Ollama not running or no models available',
                    'description': 'Ollama (Cross-platform) - Not available'
                }
        except Exception as e:
            self.available_backends['Ollama'] = {
                'status': 'unavailable',
                'error': str(e),
                'description': 'Ollama (Cross-platform) - Not available'
            }
    
    def setup_preferred_backend(self):
        """Setup the preferred backend based on availability"""
        # Prefer MLX on Apple Silicon, Ollama otherwise
        if 'MLX' in self.available_backends and self.available_backends['MLX']['status'] == 'available':
            self.preferred_backend = 'MLX'
            self.active_client = self.available_backends['MLX']['client']
        elif 'Ollama' in self.available_backends and self.available_backends['Ollama']['status'] == 'available':
            self.preferred_backend = 'Ollama'
            self.active_client = self.available_backends['Ollama']['client']
        else:
            self.preferred_backend = None
            self.active_client = None
    
    def show_model_selection_ui(self):
        """Show model selection interface in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 AI Model Configuration")
        
        # Show available backends
        available_count = sum(1 for backend in self.available_backends.values() if backend['status'] == 'available')
        
        if available_count == 0:
            st.sidebar.error("❌ No AI backends available")
            st.sidebar.markdown("""
            **Setup Required:**
            - **MLX**: Install MLX and download models
            - **Ollama**: Run `ollama serve` and pull models
            """)
            return None
        
        # Backend selection
        available_backends = [name for name, info in self.available_backends.items() if info['status'] == 'available']
        
        if len(available_backends) > 1:
            selected_backend = st.sidebar.selectbox(
                "AI Backend",
                available_backends,
                index=available_backends.index(self.preferred_backend) if self.preferred_backend in available_backends else 0,
                help="Choose between MLX (Apple Silicon optimized) and Ollama (cross-platform)"
            )
        else:
            selected_backend = available_backends[0]
            st.sidebar.info(f"Using: {selected_backend}")
        
        # Update active client if selection changed
        if selected_backend != self.preferred_backend:
            self.preferred_backend = selected_backend
            self.active_client = self.available_backends[selected_backend]['client']
        
        # Show backend-specific info
        backend_info = self.available_backends[selected_backend]
        st.sidebar.caption(backend_info['description'])
        
        # Model selection within backend
        if 'models' in backend_info and backend_info['models']:
            available_models = backend_info['models']
            
            if len(available_models) > 1:
                current_model = getattr(self.active_client, 'model_name', available_models[0])
                selected_model = st.sidebar.selectbox(
                    "Model",
                    available_models,
                    index=available_models.index(current_model) if current_model in available_models else 0
                )
                
                # Update client model if changed
                if hasattr(self.active_client, 'model_name'):
                    self.active_client.model_name = selected_model
            else:
                st.sidebar.info(f"Model: {available_models[0]}")
        
        return self.active_client
    
    def show_unified_status(self):
        """Show unified status for the active backend"""
        if not self.active_client:
            st.error("❌ No AI backend available")
            self.show_setup_instructions()
            return
        
        backend_name = self.preferred_backend
        model_name = getattr(self.active_client, 'model_name', 'Unknown Model')
        
        # Check model status
        is_loaded = self.check_model_status()
        
        # Show status
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if is_loaded:
                st.success(f"🚀 {model_name} ready ({backend_name})")
                st.caption("Fast responses expected")
            else:
                st.warning(f"💤 {model_name} not loaded ({backend_name})")
                if backend_name == 'MLX':
                    st.caption("First request: 30-60 seconds")
                else:
                    st.caption("First request: 2-3 minutes")
        
        with col2:
            if st.button("🔥 Warm Up", key="unified_warm_up"):
                self.warm_up_model()
                st.rerun()
        
        # Show backend-specific optimization tips
        self.show_optimization_tips()
    
    def check_model_status(self):
        """Check if the model is loaded (backend-agnostic)"""
        if not self.active_client:
            return False
        
        try:
            if self.preferred_backend == 'MLX':
                # MLX-specific status check
                return getattr(self.active_client, 'model_loaded_in_memory', False)
            else:
                # Ollama-specific status check
                if hasattr(self.active_client, '_check_model_memory_status'):
                    return self.active_client._check_model_memory_status()
                else:
                    return getattr(self.active_client, 'model_loaded_in_memory', False)
        except Exception:
            return False
    
    def warm_up_model(self):
        """Warm up the active model"""
        if not self.active_client:
            st.error("No active AI client")
            return
        
        try:
            with st.spinner(f"Loading {self.active_client.model_name} ({self.preferred_backend})..."):
                if self.preferred_backend == 'MLX':
                    # MLX-specific warm up
                    if hasattr(self.active_client, 'preload_model'):
                        success = self.active_client.preload_model()
                    else:
                        response = self.active_client.generate_response("System ready", max_tokens=5)
                        success = response is not None
                else:
                    # Ollama-specific warm up
                    if hasattr(self.active_client, 'preload_model'):
                        success = self.active_client.preload_model()
                    else:
                        response = self.active_client.generate_response("System ready", max_tokens=5)
                        success = response is not None
                
                if success:
                    st.success(f"✅ {self.active_client.model_name} loaded and ready!")
                else:
                    st.error("❌ Model loading failed")
        
        except Exception as e:
            st.error(f"Warm up failed: {e}")
    
    def show_optimization_tips(self):
        """Show backend-specific optimization tips"""
        if self.preferred_backend == 'MLX':
            self.show_mlx_tips()
        elif self.preferred_backend == 'Ollama':
            self.show_ollama_tips()
    
    def show_mlx_tips(self):
        """Show MLX-specific optimization tips"""
        with st.expander("🍎 MLX Optimization (Apple Silicon)"):
            st.markdown("""
            **MLX Performance Tips:**
            
            **Memory Management:**
            - MLX automatically manages GPU memory
            - Models stay loaded until system restart
            - Shared memory across applications
            
            **Performance Expectations:**
            - **Load time**: 30-60 seconds (first time)
            - **Response time**: 10-20 seconds (once loaded)
            - **Memory usage**: Optimized for Apple Silicon
            
            **Optimal Setup:**
            ```bash
            # Ensure MLX is properly installed
            pip install mlx-lm
            
            # Download models to local storage
            mlx_lm.download --model gpt-oss-120b
            ```
            
            **Troubleshooting:**
            - Restart if model becomes unresponsive
            - Check available disk space for model storage
            - Monitor Activity Monitor for memory usage
            """)
    
    def show_ollama_tips(self):
        """Show Ollama-specific optimization tips"""
        with st.expander("🔧 Ollama Optimization"):
            st.markdown("""
            **Ollama Performance Tips:**
            
            **Memory Management:**
            - Large models may be unloaded to save RAM
            - Use keep-alive settings to maintain loaded models
            - Monitor system memory usage
            
            **Performance Expectations:**
            - **Load time**: 2-3 minutes (from external drive)
            - **Response time**: 15-30 seconds (once loaded)
            - **Memory usage**: ~70GB for 120B models
            
            **Optimal Setup:**
            ```bash
            # Set keep-alive for longer sessions
            export OLLAMA_KEEP_ALIVE=24h
            
            # Restart Ollama with new settings
            killall ollama
            ollama serve
            ```
            
            **Model Management:**
            ```bash
            # Check running models
            ollama ps
            
            # Pull specific model
            ollama pull gpt-oss:120b
            
            # List available models
            ollama list
            ```
            """)
    
    def show_setup_instructions(self):
        """Show setup instructions for both backends"""
        st.markdown("### 🚀 AI Backend Setup")
        
        tab1, tab2 = st.tabs(["MLX (Apple Silicon)", "Ollama (Cross-platform)"])
        
        with tab1:
            st.markdown("""
            **MLX Setup for Apple Silicon Macs:**
            
            1. **Install MLX:**
            ```bash
            pip install mlx-lm
            ```
            
            2. **Download Models:**
            ```bash
            # Download gpt-oss model
            python -m mlx_lm.download --model microsoft/DialoGPT-medium
            ```
            
            3. **Verify Installation:**
            ```bash
            python -c "import mlx.core as mx; print('MLX available')"
            ```
            
            **Advantages:**
            - Optimized for Apple Silicon
            - Faster inference on M1/M2/M3 chips
            - Lower memory usage
            - Better battery efficiency
            """)
        
        with tab2:
            st.markdown("""
            **Ollama Setup (Any Platform):**
            
            1. **Install Ollama:**
            ```bash
            # macOS
            brew install ollama
            
            # Or download from: https://ollama.ai
            ```
            
            2. **Start Ollama:**
            ```bash
            ollama serve
            ```
            
            3. **Pull Models:**
            ```bash
            # Pull a large model for grading
            ollama pull gpt-oss:120b
            
            # Or smaller alternatives
            ollama pull gemma3:27b
            ollama pull qwen3-coder:30b
            ```
            
            **Advantages:**
            - Cross-platform compatibility
            - Large model selection
            - Easy model management
            - Community support
            """)
    
    def get_active_client(self):
        """Get the currently active AI client"""
        return self.active_client
    
    def get_backend_info(self):
        """Get information about the active backend"""
        if not self.preferred_backend:
            return None
        
        return {
            'backend': self.preferred_backend,
            'model': getattr(self.active_client, 'model_name', 'Unknown'),
            'status': 'available' if self.active_client else 'unavailable',
            'loaded': self.check_model_status()
        }

# Global instance for use across the app
unified_interface = UnifiedModelInterface()

def get_unified_ai_client():
    """Get the unified AI client for use in other modules"""
    return unified_interface.get_active_client()

def show_unified_model_status():
    """Show unified model status in sidebar"""
    client = unified_interface.show_model_selection_ui()
    if client:
        unified_interface.show_unified_status()
    return client