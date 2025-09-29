import streamlit as st
import requests
from datetime import datetime, timedelta

class ModelStatusIndicator:
    """Shows model memory status and provides controls"""
    
    @staticmethod
    def show_model_status(ai_client):
        """Display model status in sidebar or main area"""
        
        # Check current status (handle different client types)
        if hasattr(ai_client, '_check_model_memory_status'):
            is_loaded = ai_client._check_model_memory_status()
            model_name = ai_client.model_name
        else:
            # MLX or other client
            is_loaded = getattr(ai_client, 'model_loaded_in_memory', False)
            model_name = getattr(ai_client, 'model_name', 'Unknown Model')
        
        # Update the client's status
        ai_client.model_loaded_in_memory = is_loaded
        
        # Show status indicator
        if is_loaded:
            st.success(f"🚀 {model_name} ready")
            st.caption("Fast responses (~15-30s)")
        else:
            st.warning(f"💤 {model_name} not loaded")
            st.caption("First request: 2-3 minutes")
        
        # Show controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Check Status", key="refresh_model_status"):
                # Force refresh by clearing session state
                if hasattr(st, 'session_state'):
                    session_key = f"model_loaded_{model_name}"
                    if session_key in st.session_state:
                        del st.session_state[session_key]
                st.rerun()
        
        with col2:
            if st.button("🔥 Warm Up", key="warm_up_model"):
                ModelStatusIndicator.warm_up_model(ai_client)
                st.rerun()
        
        # Show additional info for large models
        if "120b" in model_name.lower():
            ModelStatusIndicator.show_model_persistence_info()
            
        # Show Mac-specific optimization tips
        ModelStatusIndicator.show_mac_optimization_tips()
    
    @staticmethod
    def warm_up_model(ai_client):
        """Send a small request to load the model into memory"""
        try:
            with st.spinner("Loading gpt-oss:120b from external drive (1.5GB/s)..."):
                # Use the aggressive preload function
                success = ai_client.preload_model()
                if success:
                    st.success("✅ Model loaded and ready! (~70GB in memory)")
                    # Update session state
                    if hasattr(st, 'session_state'):
                        session_key = f"model_loaded_{ai_client.model_name}"
                        st.session_state[session_key] = True
                else:
                    # Fallback to regular method
                    warm_up_prompt = "System ready"
                    response = ai_client.generate_response(warm_up_prompt, show_progress=True)
                    if response:
                        st.success("✅ Model warmed up and ready!")
                    else:
                        st.error("Model loading failed - check Ollama connection")
        except Exception as e:
            st.error(f"Failed to warm up model: {e}")
    
    @staticmethod
    def show_model_persistence_info():
        """Show information about model persistence"""
        st.info("""
        **Model Memory Behavior:**
        - Large models (120B) may be unloaded automatically to save RAM
        - Model loads on first request (~2-3 minutes)
        - Subsequent requests are fast while model stays loaded
        - Use "Warm Up Model" before grading sessions
        """)
        
        # Show Ollama configuration tips
        with st.expander("🔧 Improve Model Persistence"):
            st.markdown("""
            **To keep models loaded longer:**
            
            1. **Increase Ollama timeout** (if supported):
            ```bash
            export OLLAMA_KEEP_ALIVE=30m
            ollama serve
            ```
            
            2. **Use model during grading sessions**:
            - Grade assignments in batches
            - Don't take long breaks between requests
            
            3. **Monitor system memory**:
            - 120B model needs ~70GB RAM
            - Close other memory-intensive applications
            
            4. **Consider smaller models for development**:
            - Use smaller model for testing
            - Switch to 120B for production grading
            """)
    
    @staticmethod
    def show_mac_optimization_tips():
        """Show Mac Ultra M3 specific optimization tips"""
        with st.expander("🍎 Mac Ultra M3 Optimization"):
            st.markdown("""
            **Your Mac Ultra M3 with 512GB RAM is perfect for this!**
            
            **Recommended Setup for Fast External Drive:**
            ```bash
            # Set permanent keep-alive and optimize for fast storage
            echo 'export OLLAMA_KEEP_ALIVE=24h' >> ~/.zshrc
            echo 'export OLLAMA_MAX_LOADED_MODELS=2' >> ~/.zshrc
            echo 'export OLLAMA_NUM_PARALLEL=1' >> ~/.zshrc
            source ~/.zshrc
            
            # Restart Ollama with optimized settings
            killall ollama
            ollama serve
            ```
            
            **Performance Expectations:**
            - **Model size**: ~70GB (only 14% of your 512GB RAM)
            - **Load time**: 45-60 seconds (with 1.5GB/s external drive)
            - **Response time**: 15-30 seconds (once loaded)
            - **Persistence**: Should stay loaded for 24 hours
            
            **Memory Usage:**
            - 120B model: ~70GB
            - System + apps: ~50GB
            - **Available**: ~390GB remaining
            
            **Optimal Workflow:**
            1. Load model once per day
            2. Grade all assignments in that session
            3. Model stays fast for entire grading session
            """)
            
            if st.button("📋 Copy Setup Commands"):
                setup_commands = """export OLLAMA_KEEP_ALIVE=24h
killall ollama
ollama serve"""
                st.code(setup_commands, language="bash")
                st.success("Commands ready to copy!")
    
    @staticmethod
    def show_model_info():
        """Show detailed model information"""
        try:
            response = requests.get("http://localhost:11434/api/ps", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                if models:
                    st.subheader("🤖 Active Models")
                    for model in models:
                        name = model.get("name", "Unknown")
                        size = model.get("size", 0)
                        size_gb = size / (1024**3) if size > 0 else 0
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**{name}**")
                        with col2:
                            st.write(f"{size_gb:.1f} GB")
                        with col3:
                            st.write("🟢 Active")
                else:
                    st.info("No models currently loaded in memory")
            else:
                st.error("Could not connect to Ollama")
        except Exception as e:
            st.error(f"Error checking model status: {e}")
    
    @staticmethod
    def estimate_response_time(ai_client, num_requests=1):
        """Estimate response time for upcoming requests"""
        if ai_client.model_loaded_in_memory:
            # Model in memory - fast responses
            base_time = 15  # seconds per request
            total_time = num_requests * base_time
        else:
            # Model not in memory - first request slow, then fast
            first_request_time = 120  # 2 minutes for first request
            subsequent_time = 15 * (num_requests - 1) if num_requests > 1 else 0
            total_time = first_request_time + subsequent_time
        
        # Format time nicely
        if total_time < 60:
            return f"{total_time:.0f} seconds"
        elif total_time < 3600:
            minutes = total_time / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = total_time / 3600
            return f"{hours:.1f} hours"
    
    @staticmethod
    def show_performance_tips():
        """Show tips for optimal performance"""
        st.subheader("⚡ Performance Tips")
        
        st.markdown("""
        **To keep the model in memory:**
        - Keep Ollama running in the background
        - Don't restart your computer unnecessarily
        - Avoid running other large AI models simultaneously
        
        **For faster grading:**
        - Grade assignments in batches
        - Use the "Warm Up Model" button before large grading sessions
        - Consider grading during off-peak hours
        
        **Memory usage:**
        - gpt-oss:120b uses ~70GB RAM when loaded
        - Model stays loaded until system restart or manual unload
        - Multiple tabs/sessions share the same loaded model
        """)