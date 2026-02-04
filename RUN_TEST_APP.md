# Inference Test App - Quick Start Guide

This standalone test app allows external users to compare Mac-only vs Disaggregated inference performance.

## Prerequisites

All inference servers must be running:
- DGX Spark 3 (Qwen prefill): `169.254.150.105:8080`
- DGX Spark 4 (GPT-OSS prefill): `169.254.150.106:8080`
- Mac Studio 1 (GPT-OSS decode): `169.254.150.101:8081`
- Mac Studio 2 (Qwen decode): `169.254.150.102:8081`

## Running the Test App

### 1. Start the app

```bash
cd /Users/humphrjk/Library/CloudStorage/OneDrive-ionxs.ai/analytics/ai-homework-grader
streamlit run test_inference_app.py --server.port 8501
```

### 2. Open in browser

The app will automatically open at: `http://localhost:8501`

Or access from another machine: `http://169.254.150.101:8501` (replace with your IP)

### 3. Share with external users

To allow external users to access:

```bash
# Run with external access
streamlit run test_inference_app.py --server.port 8501 --server.address 0.0.0.0
```

Then share: `http://YOUR_IP:8501`

## Features

### 1. Compare Performance

Test the same prompt with both modes:
- **Mac-only**: All processing on Mac (prefill + decode locally)
- **Disaggregated**: DGX prefill → Mac decode

### 2. Sample Prompts

Choose from preset prompts:
- R tidyverse code analysis
- Python pandas code analysis
- Student feedback generation
- Quick test prompts

Or enter custom prompts.

### 3. Performance Metrics

**Disaggregated mode shows:**
- Total time, prefill time, decode time
- Prefill speed (tok/s), decode speed (tok/s)
- State size (MB)
- Server info

**Mac-only mode shows:**
- Total time
- Generation speed (tok/s)
- Server used

### 4. Health Monitoring

Click "Check Server Health" to verify all servers are online.

## Note: Mac-only Mode Setup

The current Mac decode servers are configured for disaggregated inference only. For true Mac-only standalone testing, you have two options:

### Option A: Use Ollama (if running)

If Ollama is running on the Macs on port 11434, the app can use it for standalone mode.

### Option B: Add /generate endpoint to decode servers

The decode servers need a `/generate` endpoint that does full inference (not just decode):

```python
@app.route('/generate', methods=['POST'])
def generate():
    """Full generation (prefill + decode) on Mac"""
    data = request.json
    prompt = data.get('prompt', '')
    max_tokens = data.get('max_new_tokens', 500)

    # Use llama-cpp-python for full generation
    response = model(prompt, max_tokens=max_tokens)

    return jsonify({
        'generated_text': response['choices'][0]['text'],
        'tokens_generated': response['usage']['completion_tokens'],
        'speed': ...
    })
```

## Expected Performance

### Small Prompts (<100 tokens)

- **Mac-only**: ~3-5 seconds
- **Disaggregated**: ~3-5 seconds
- **Winner**: Similar

### Large Prompts (2000+ tokens)

- **Mac-only**: ~30 seconds (slow prefill on Mac)
- **Disaggregated**: ~15 seconds (fast prefill on DGX)
- **Winner**: Disaggregated (2x faster)

### Typical Grading Workload (~4000 tokens input)

- **Mac-only**: ~40-50 seconds
- **Disaggregated**: ~20-25 seconds
- **Winner**: Disaggregated (2x faster)

## Troubleshooting

### "Server offline" errors

Check that all servers are running:

```bash
# DGX servers
curl http://169.254.150.105:8080/health
curl http://169.254.150.106:8080/health

# Mac servers
curl http://169.254.150.101:8081/health
curl http://169.254.150.102:8081/health
```

Restart if needed (see [DEPLOYMENT_READY.md](disaggregated_inference/DEPLOYMENT_READY.md)).

### "Mac-only mode not working"

The decode servers currently only support disaggregated mode. Either:
1. Use Ollama for Mac-only testing (if available)
2. Add `/generate` endpoint to decode servers
3. Focus testing on disaggregated mode (recommended)

### Connection timeouts

- Increase timeout in code if dealing with very large outputs
- Check network connectivity between machines
- Verify firewall rules allow connections on ports 8080/8081

## Demo Script for External Users

1. **Open the app**: Navigate to the URL
2. **Check health**: Click "Check Server Health" to verify all systems online
3. **Choose mode**: Select "Mac-only" or "Disaggregated"
4. **Select model**: Qwen (code) or GPT-OSS (feedback)
5. **Pick a prompt**: Use a sample or write custom
6. **Generate**: Click "🚀 Generate"
7. **Compare**: Try the same prompt with both modes to see the difference!

## Production Use

This test app is for demonstration and benchmarking. For production grading, use the main Streamlit app (`app.py`) which includes:
- Assignment management
- Student submission handling
- Validation and scoring
- Report generation
- Database integration

The disaggregated inference is automatically used in the main app when configured.
