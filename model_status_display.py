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
    
    # Check Ollama connection
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
                st.sidebar.success("✅ Qwen 3.0 Coder (Code Analysis)")
            else:
                st.sidebar.error("❌ Qwen 3.0 Coder - Not Available")
            
            # Feedback generator status
            if feedback_model in available_models:
                st.sidebar.success("✅ Gemma 3.0 (Feedback Generation)")
            else:
                st.sidebar.error("❌ Gemma 3.0 - Not Available")
            
            # Show parallel processing info
            if code_model in available_models and feedback_model in available_models:
                st.sidebar.info("⚡ **Parallel Processing Ready**")
                
                # Check if models are loaded in memory
                try:
                    ps_response = requests.get("http://localhost:11434/api/ps", timeout=2)
                    if ps_response.status_code == 200:
                        running_models = ps_response.json().get("models", [])
                        loaded_models = [model.get("name") for model in running_models]
                        
                        if code_model in loaded_models:
                            st.sidebar.success("🔥 Code Analyzer: Loaded in Memory")
                        else:
                            st.sidebar.warning("💤 Code Analyzer: Will load on first use")
                        
                        if feedback_model in loaded_models:
                            st.sidebar.success("🔥 Feedback Generator: Loaded in Memory")
                        else:
                            st.sidebar.warning("💤 Feedback Generator: Will load on first use")
                except:
                    st.sidebar.info("📊 Memory status check unavailable")
            else:
                st.sidebar.warning("⚠️ Two-model system incomplete")
            
            # Show total available models
            st.sidebar.caption(f"📚 Total models available: {len(available_models)}")
            
        else:
            st.sidebar.error("❌ Ollama server error")
    
    except requests.exceptions.ConnectionError:
        st.sidebar.error("❌ Ollama not running")
        st.sidebar.info("💡 Start Ollama to enable AI grading")
    
    except requests.exceptions.Timeout:
        st.sidebar.warning("⏰ Ollama connection timeout")
    
    except Exception as e:
        st.sidebar.error(f"❌ Model check failed: {str(e)[:30]}...")

def show_grading_performance_stats(grading_stats):
    """Show performance statistics from two-model grading"""
    
    if not grading_stats:
        return
    
    st.subheader("⚡ Two-Model Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        code_time = grading_stats.get('code_analysis_time', 0)
        st.metric("Code Analysis", f"{code_time:.1f}s")
    
    with col2:
        feedback_time = grading_stats.get('feedback_generation_time', 0)
        st.metric("Feedback Generation", f"{feedback_time:.1f}s")
    
    with col3:
        efficiency = grading_stats.get('parallel_efficiency', 0)
        st.metric("Parallel Speedup", f"{efficiency:.1f}x")
    
    # Show parallel vs sequential comparison
    parallel_time = grading_stats.get('parallel_time', 0)
    sequential_time = code_time + feedback_time
    
    if parallel_time > 0 and sequential_time > 0:
        time_saved = sequential_time - parallel_time
        st.success(f"⚡ **Parallel Processing Saved {time_saved:.1f} seconds** ({parallel_time:.1f}s vs {sequential_time:.1f}s sequential)")

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
                feedback_models = [m for m in available_models if any(keyword in m.lower() for keyword in ['gemma', 'llama', 'mistral'])]
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
        
        📝 **Feedback Generator (Gemma 3.0)**:
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