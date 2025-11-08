#!/usr/bin/env python3
"""
Real-time Disaggregated Inference Metrics Dashboard
Shows detailed Ollama-style performance metrics
"""
import streamlit as st
import time
from disaggregated_client import DisaggregatedClient
from model_config import MODEL_SETTINGS

st.set_page_config(page_title="Disaggregated Inference Metrics", layout="wide")

st.title("📊 Disaggregated Inference - Real-Time Metrics")
st.markdown("---")

# Model selection
model_options = [k for k in MODEL_SETTINGS.keys() if k.startswith('disaggregated:')]
selected_model = st.selectbox("Select Model", model_options, index=0)

config = MODEL_SETTINGS[selected_model]

st.info(f"""
**Model**: {selected_model}  
**Prefill Server**: {config['prefill_url']}  
**Decode Server**: {config['decode_url']}  
""")

# Test prompt
prompt = st.text_area("Test Prompt", value="Write a Python function to calculate fibonacci numbers:", height=100)
max_tokens = st.slider("Max Tokens", 50, 500, 200)

if st.button("🚀 Generate & Show Metrics", type="primary"):
    client = DisaggregatedClient(
        prefill_url=config['prefill_url'],
        decode_url=config['decode_url']
    )
    
    with st.spinner("Generating..."):
        start = time.time()
        result = client.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.3
        )
        total_time = time.time() - start
    
    metrics = result.get('metrics', {})
    
    # Display metrics
    st.success(f"✅ Generation complete in {total_time:.3f}s")
    
    st.markdown("---")
    st.subheader("⚡ Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Time", f"{total_time:.3f}s")
        st.metric("Method", result.get('method', 'N/A'))
    
    with col2:
        total = metrics.get('total', {})
        st.metric("Total Tokens", total.get('total_tokens', 0))
        st.metric("Overall Speed", f"{total.get('overall_tokens_per_sec', 0):.1f} tok/s")
    
    with col3:
        st.metric("Prompt Tokens", total.get('prompt_tokens', 0))
        st.metric("Generated Tokens", total.get('generated_tokens', 0))
    
    # Detailed breakdown
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔵 Prefill Phase (DGX)")
        prefill = metrics.get('prefill', {})
        st.metric("Time", f"{prefill.get('time_s', 0):.4f}s")
        st.metric("Prompt Tokens", prefill.get('prompt_tokens', 0))
        st.metric("Speed", f"{prefill.get('tokens_per_sec', 0):.1f} tok/s")
        st.metric("Duration (ns)", f"{prefill.get('duration_ns', 0):,}")
        
        # Percentage
        pct = (prefill.get('time_s', 0) / total_time * 100) if total_time > 0 else 0
        st.progress(pct / 100)
        st.caption(f"{pct:.1f}% of total time")
    
    with col2:
        st.subheader("🟢 Decode Phase (Mac)")
        decode = metrics.get('decode', {})
        st.metric("Time", f"{decode.get('time_s', 0):.4f}s")
        st.metric("Tokens Generated", decode.get('tokens_generated', 0))
        st.metric("Speed", f"{decode.get('tokens_per_sec', 0):.1f} tok/s")
        st.metric("Eval Duration (ns)", f"{decode.get('eval_duration_ns', 0):,}")
        st.metric("Total Duration (ns)", f"{decode.get('total_duration_ns', 0):,}")
        
        # Percentage
        pct = (decode.get('time_s', 0) / total_time * 100) if total_time > 0 else 0
        st.progress(pct / 100)
        st.caption(f"{pct:.1f}% of total time")
    
    # Generated output
    st.markdown("---")
    st.subheader("📝 Generated Output")
    st.code(result.get('response', ''), language='text')
    
    # Raw metrics JSON
    with st.expander("🔍 Raw Metrics (JSON)"):
        st.json(metrics)

st.markdown("---")
st.caption("Disaggregated Inference: DGX Sparks (Prefill) + Mac Studios (Decode)")
