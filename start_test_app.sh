#!/bin/bash
# Quick start script for Inference Test App

echo "======================================================================"
echo "  AI Homework Grader - Inference Performance Test App"
echo "======================================================================"
echo ""
echo "This app allows you to compare:"
echo "  - Mac-only (standalone) inference"
echo "  - Disaggregated (DGX + Mac) inference"
echo ""
echo "Starting Streamlit app..."
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Start streamlit with external access
streamlit run test_inference_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --browser.gatherUsageStats false

# Note: To run locally only (no external access), use:
# streamlit run test_inference_app.py --server.port 8501
