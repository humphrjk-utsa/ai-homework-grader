# Disaggregated Inference Setup - Complete

## ✅ Configuration Complete

Your system is now configured to use **all 4 machines simultaneously** with prefill/decode disaggregated inference:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CODE ANALYSIS PIPELINE                    │
│                                                              │
│  DGX Spark 1 (Prefill)  →  Mac Studio 2 (Decode)           │
│  169.254.150.103:8000      169.254.150.102:5002             │
│  Qwen 3.0 Coder 30B        Qwen 3.0 Coder 30B              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 FEEDBACK GENERATION PIPELINE                 │
│                                                              │
│  DGX Spark 2 (Prefill)  →  Mac Studio 1 (Decode)           │
│  169.254.150.104:8000      169.254.150.101:8003             │
│  GPT-OSS 120B              GPT-OSS 120B                     │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Files Created/Modified

### Configuration Files
- ✅ `model_config.py` - Updated with disaggregated model configs
- ✅ `business_analytics_grader_v2.py` - Added `generate_with_ollama()` method
- ✅ `disaggregated_client.py` - Handles prefill/decode coordination

### Server Files
- ✅ `servers/qwen_prefill_server_dgx.py` - DGX Spark 1 prefill server
- ✅ `servers/gpt_oss_prefill_server_dgx.py` - DGX Spark 2 prefill server
- ✅ `servers/qwen_server.py` - Mac Studio 2 decode server (updated)
- ✅ `servers/gpt_oss_server_working.py` - Mac Studio 1 decode server (updated)

### Startup Scripts
- ✅ `servers/start_dgx_spark1_qwen_prefill.sh`
- ✅ `servers/start_dgx_spark2_gptoss_prefill.sh`
- ✅ `servers/start_mac2_qwen_decode.sh`
- ✅ `servers/start_mac1_gptoss_decode.sh`

### Documentation & Testing
- ✅ `servers/README_DISAGGREGATED_SETUP.md` - Setup instructions
- ✅ `servers/test_disaggregated_setup.py` - Test script

## 🚀 Starting the System

### Step 1: Start Prefill Servers on DGX Machines

**On DGX Spark 1 (169.254.150.103):**
```bash
cd servers
./start_dgx_spark1_qwen_prefill.sh
```

**On DGX Spark 2 (169.254.150.104):**
```bash
cd servers
./start_dgx_spark2_gptoss_prefill.sh
```

### Step 2: Start Decode Servers on Mac Studios

**On Mac Studio 2 (169.254.150.102):**
```bash
cd servers
./start_mac2_qwen_decode.sh
```

**On Mac Studio 1 (169.254.150.101):**
```bash
cd servers
./start_mac1_gptoss_decode.sh
```

### Step 3: Test the Setup

```bash
python3 servers/test_disaggregated_setup.py
```

## 🔧 How It Works

### Prefill Phase (DGX)
1. Receives the prompt
2. Uses Ollama to process prompt and generate KV cache
3. Returns prompt + context to decode server
4. **Fast GPU processing** for prompt encoding

### Decode Phase (Mac Studio)
1. Receives prompt + context from prefill
2. Uses MLX to generate tokens
3. Returns generated text
4. **Efficient Apple Silicon** token generation

### Parallel Execution
- Both pipelines run **simultaneously**
- Code analysis (Qwen) and feedback (GPT-OSS) happen in parallel
- Maximum throughput using all 4 machines

## 📊 Model Configuration

In `model_config.py`:

```python
# Two-model system configuration
CODE_MODEL = "disaggregated:qwen3-coder:30b"      # DGX Spark 1 + Mac Studio 2
FEEDBACK_MODEL = "disaggregated:gpt-oss:120b"     # DGX Spark 2 + Mac Studio 1

MODEL_SETTINGS = {
    "disaggregated:qwen3-coder:30b": {
        "temperature": 0.3,
        "max_tokens": 2000,
        "description": "Disaggregated Qwen - DGX Spark 1 (prefill) + Mac Studio 2 (decode)",
        "prefill_url": "http://169.254.150.103:8000/prefill",  # DGX Spark 1
        "decode_url": "http://169.254.150.102:5002/decode"     # Mac Studio 2
    },
    "disaggregated:gpt-oss:120b": {
        "temperature": 0.3,
        "max_tokens": 2500,
        "description": "Disaggregated GPT-OSS - DGX Spark 2 (prefill) + Mac Studio 1 (decode)",
        "prefill_url": "http://169.254.150.104:8000/prefill",  # DGX Spark 2
        "decode_url": "http://169.254.150.101:8003/decode"     # Mac Studio 1
    }
}
```

## 🎯 Usage in Grading System

The grader automatically uses disaggregated inference when models are configured:

```python
from model_config import CODE_MODEL, FEEDBACK_MODEL

grader = BusinessAnalyticsGraderV2(
    code_model=CODE_MODEL,      # Uses DGX Spark 1 + Mac Studio 2
    feedback_model=FEEDBACK_MODEL,  # Uses DGX Spark 2 + Mac Studio 1
    rubric_path=rubric_path,
    solution_path=solution_path
)

# Grading automatically uses both pipelines in parallel
result = grader.grade_submission(...)
```

## 🔍 Monitoring

Check server status:
```bash
# Check all health endpoints
curl http://169.254.150.103:8000/health  # DGX Spark 1
curl http://169.254.150.104:8000/health  # DGX Spark 2
curl http://169.254.150.102:5002/health  # Mac Studio 2
curl http://169.254.150.101:5001/health  # Mac Studio 1

# Check detailed status
curl http://169.254.150.103:8000/status
curl http://169.254.150.104:8000/status
curl http://169.254.150.102:5002/status
curl http://169.254.150.101:5001/status
```

## 🎉 Performance Benefits

1. **2x Throughput**: Two models running in parallel
2. **Faster Prefill**: DGX GPUs handle prompt processing efficiently
3. **Efficient Decode**: Mac Studios optimized for token generation with MLX
4. **Load Distribution**: Work spread across 4 machines
5. **Scalability**: Each pipeline can be scaled independently

## 📝 Next Steps

1. Start all 4 servers (see Step 1 & 2 above)
2. Run the test script to verify setup
3. Use the grading system normally - it will automatically use disaggregated inference
4. Monitor performance and adjust token limits if needed

## 🐛 Troubleshooting

**If a server fails to start:**
- Check that the model is loaded in Ollama (for DGX servers)
- Check that MLX models are available (for Mac servers)
- Verify network connectivity between machines
- Check firewall rules allow the specified ports

**If prefill/decode fails:**
- Verify both servers in the pipeline are running
- Check network latency between DGX and Mac
- Review server logs for errors
- Test with the test script to isolate issues

## 🔗 Related Files

- Main grader: `business_analytics_grader_v2.py`
- Model config: `model_config.py`
- Client: `disaggregated_client.py`
- Web interface: `connect_web_interface.py`
