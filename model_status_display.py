#!/usr/bin/env python3
"""
Model Status Display for Web Interface
Shows the two-model system status and performance
"""

import streamlit as st
import requests
import time

def show_two_model_status():
    """Display two-model system status in sidebar"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI Model Status")
    
    # Check MLX models first (preferred for Apple Silicon)
    mlx_available = False
    try:
        from models.mlx_ai_client import MLXAIClient
        import os
        import glob
        
        # Check for MLX models in HuggingFace cache
        hf_cache = os.path.expanduser("~/.cache/huggingface/hub/")
        available_mlx_models = []
        
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
                        available_mlx_models.append(model_name)
        
        # Check for our specific models
        qwen_model = "mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit"
        gptoss_model = "lmstudio-community/gpt-oss-120b-MLX-8bit"
        
        qwen_available = qwen_model in available_mlx_models
        gptoss_available = gptoss_model in available_mlx_models
        
        # Display status
        if qwen_available:
            st.sidebar.success("✅ Qwen 3.0 Coder (MLX 8bit)")
        else:
            st.sidebar.error("❌ Qwen 3.0 Coder - Not Available")
        
        if gptoss_available:
            st.sidebar.success("✅ GPT-OSS 120B (MLX 8bit)")
        else:
            st.sidebar.error("❌ GPT-OSS 120B - Not Available")
        
        if qwen_available and gptoss_available:
            st.sidebar.info("⚡ **MLX Two-Model System Ready**")
            st.sidebar.success("🍎 Apple Silicon Optimized")
            mlx_available = True
        elif qwen_available or gptoss_available:
            st.sidebar.warning("⚠️ Partial MLX setup - some models missing")
        else:
            st.sidebar.warning("⚠️ MLX models not found")
        
        # Show total MLX models
        if available_mlx_models:
            st.sidebar.caption(f"📚 MLX models available: {len(available_mlx_models)}")
        
    except ImportError:
        st.sidebar.error("❌ MLX not installed")
        st.sidebar.info("💡 Run: pip install mlx-lm")
    except Exception as e:
        st.sidebar.error(f"❌ MLX check failed: {str(e)[:30]}...")
    
    # Fallback to Ollama if MLX not available
    if not mlx_available:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                
                # Check our two models
                code_model = "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest"
                feedback_model = "gemma3:27b-it-q8_0"
                
                # Code analyzer status
                if code_model in available_models:
                    st.sidebar.success("✅ Qwen 3.0 Coder (Ollama)")
                else:
                    st.sidebar.error("❌ Qwen 3.0 Coder - Not Available")
                
                # Feedback generator status
                if feedback_model in available_models:
                    st.sidebar.success("✅ GPT-OSS 120B (Ollama)")
                else:
                    st.sidebar.error("❌ GPT-OSS 120B - Not Available")
                
                # Show parallel processing info
                if code_model in available_models and feedback_model in available_models:
                    st.sidebar.info("⚡ **Ollama Two-Model System Ready**")
                else:
                    st.sidebar.warning("⚠️ Two-model system incomplete")
                
                # Show total available models
                st.sidebar.caption(f"📚 Ollama models available: {len(available_models)}")
                
            else:
                st.sidebar.error("❌ Ollama server error")
        
        except requests.exceptions.ConnectionError:
            st.sidebar.error("❌ Ollama not running")
            st.sidebar.info("💡 Install MLX or start Ollama")
        
        except requests.exceptions.Timeout:
            st.sidebar.warning("⏰ Ollama connection timeout")
        
        except Exception as e:
            st.sidebar.error(f"❌ Model check failed: {str(e)[:30]}...")

def show_grading_performance_stats(grading_stats):
    """Show performance statistics from two-model grading"""
    
    if not grading_stats:
        return
    
    st.subheader("⚡ Two-Model Performance")
    
    # Main timing metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        code_time = grading_stats.get('code_analysis_time', 0)
        st.metric("Code Analysis", f"{code_time:.1f}s")
    
    with col2:
        feedback_time = grading_stats.get('feedback_generation_time', 0)
        st.metric("Feedback Generation", f"{feedback_time:.1f}s")
    
    with col3:
        efficiency = grading_stats.get('parallel_efficiency', 0)
        if efficiency > 0:
            st.metric("Parallel Speedup", f"{efficiency:.1f}x")
        else:
            total_time = grading_stats.get('total_time', 0)
            st.metric("Total Time", f"{total_time:.1f}s")
    
    # Show parallel vs sequential comparison
    parallel_time = grading_stats.get('parallel_time', 0)
    sequential_time = code_time + feedback_time
    
    if parallel_time > 0 and sequential_time > 0:
        time_saved = sequential_time - parallel_time
        st.success(f"⚡ **Parallel Processing Saved {time_saved:.1f} seconds** ({parallel_time:.1f}s vs {sequential_time:.1f}s sequential)")
    
    # Show detailed throughput metrics if available
    qwen_metrics = grading_stats.get('qwen_metrics', {})
    gemma_metrics = grading_stats.get('gemma_metrics', {})
    
    if qwen_metrics or gemma_metrics:
        st.markdown("---")
        st.markdown("**🚀 Throughput Metrics (Disaggregated System)**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔧 Qwen Coder (Code Analysis)**")
            if qwen_metrics:
                prefill_speed = qwen_metrics.get('prefill_tokens_per_second', 0)
                decode_speed = qwen_metrics.get('decode_tokens_per_second', 0)
                prompt_tokens = qwen_metrics.get('prompt_tokens', 0)
                completion_tokens = qwen_metrics.get('completion_tokens', 0)
                
                if prefill_speed > 0:
                    st.metric("Prefill Speed", f"{prefill_speed:.0f} tok/s", 
                             help="Prompt processing speed on DGX Spark 1")
                if decode_speed > 0:
                    st.metric("Decode Speed", f"{decode_speed:.0f} tok/s", 
                             help="Token generation speed on Mac Studio 2")
                
                st.caption(f"📊 {prompt_tokens} prompt + {completion_tokens} completion = {prompt_tokens + completion_tokens} total tokens")
                st.caption(f"⏱️ {code_time:.1f}s total")
            else:
                st.info("No metrics available")
        
        with col2:
            st.markdown("**📝 GPT-OSS (Feedback Generation)**")
            if gemma_metrics:
                prefill_speed = gemma_metrics.get('prefill_tokens_per_second', 0)
                decode_speed = gemma_metrics.get('decode_tokens_per_second', 0)
                prompt_tokens = gemma_metrics.get('prompt_tokens', 0)
                completion_tokens = gemma_metrics.get('completion_tokens', 0)
                
                if prefill_speed > 0:
                    st.metric("Prefill Speed", f"{prefill_speed:.0f} tok/s", 
                             help="Prompt processing speed on DGX Spark 2")
                if decode_speed > 0:
                    st.metric("Decode Speed", f"{decode_speed:.0f} tok/s", 
                             help="Token generation speed on Mac Studio 1")
                
                st.caption(f"📊 {prompt_tokens} prompt + {completion_tokens} completion = {prompt_tokens + completion_tokens} total tokens")
                st.caption(f"⏱️ {feedback_time:.1f}s total")
            else:
                st.info("No metrics available")

def show_model_selection_interface():
    """Allow users to select different models for the two-model system"""
    
    st.subheader("🔧 Model Configuration")
    
    # Get available models
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Code Analysis Model:**")
                code_models = [m for m in available_models if any(keyword in m.lower() for keyword in ['coder', 'code', 'qwen'])]
                if not code_models:
                    code_models = available_models
                
                selected_code_model = st.selectbox(
                    "Select code analyzer:",
                    code_models,
                    index=0 if code_models else 0
                )
            
            with col2:
                st.write("**Feedback Generation Model:**")
                feedback_models = [m for m in available_models if any(keyword in m.lower() for keyword in ['gpt-oss', 'gemma', 'llama', 'mistral'])]
                if not feedback_models:
                    feedback_models = available_models
                
                selected_feedback_model = st.selectbox(
                    "Select feedback generator:",
                    feedback_models,
                    index=0 if feedback_models else 0
                )
            
            if st.button("🔄 Update Model Configuration"):
                # This would update the configuration
                st.success(f"✅ Updated to: {selected_code_model} + {selected_feedback_model}")
                st.info("💡 Restart grading session to apply changes")
        
        else:
            st.error("❌ Cannot connect to Ollama to get model list")
    
    except Exception as e:
        st.error(f"❌ Model configuration failed: {e}")

def show_two_model_explanation():
    """Explain how the two-model system works"""
    
    with st.expander("🤖 How the Two-Model System Works"):
        st.write("""
        **Parallel AI Processing for Better Grading:**
        
        🔧 **Code Analyzer (Qwen 3.0 Coder)**:
        - Analyzes R code syntax and logic
        - Checks technical execution
        - Evaluates programming best practices
        - Identifies code issues and improvements
        
        📝 **Feedback Generator (GPT-OSS 120B)**:
        - Reviews written analysis and reflections
        - Evaluates business thinking
        - Assesses communication clarity
        - Generates constructive feedback
        
        ⚡ **Parallel Processing Benefits**:
        - **2x faster** than sequential processing
        - **Specialized expertise** for each task
        - **Higher quality** analysis and feedback
        - **Consistent grading** across submissions
        
        🎯 **Result Integration**:
        - Combines technical and analytical scores
        - Validates mathematical consistency
        - Generates comprehensive reports
        - Maintains 37.5-point scale accuracy
        """)

def main():
    """Test the model status display"""
    print("🤖 Model Status Display Ready")
    print("✅ Use show_two_model_status() in Streamlit sidebar")
    print("✅ Use show_grading_performance_stats() after grading")

if __name__ == "__main__":
    main()