# Disaggregated Inference Setup

This setup uses **4 machines simultaneously** for maximum performance:

## Architecture

### Code Analysis Pipeline (Qwen)
- **DGX Spark 1** (169.254.150.103:8000) → Prefill phase
- **Mac Studio 2** (169.254.150.102:5002) → Decode phase

### Feedback Generation Pipeline (GPT-OSS)
- **DGX Spark 2** (169.254.150.104:8000) → Prefill phase
- **Mac Studio 1** (169.254.150.101:8003) → Decode phase

## Starting the Servers

### On DGX Spark 1 (169.254.150.103)
```bash
cd servers
chmod +x start_dgx_spark1_qwen_prefill.sh
./start_dgx_spark1_qwen_prefill.sh
```

### On DGX Spark 2 (169.254.150.104)
```bash
cd servers
chmod +x start_dgx_spark2_gptoss_prefill.sh
./start_dgx_spark2_gptoss_prefill.sh
```

### On Mac Studio 1 (169.254.150.101)
```bash
cd servers
chmod +x start_mac1_gptoss_decode.sh
./start_mac1_gptoss_decode.sh
```

### On Mac Studio 2 (169.254.150.102)
```bash
cd servers
chmod +x start_mac2_qwen_decode.sh
./start_mac2_qwen_decode.sh
```

## Testing the Setup

Once all servers are running, test with:

```bash
# Test Qwen pipeline (DGX Spark 1 → Mac Studio 2)
curl -X POST http://169.254.150.103:8000/prefill \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def hello():"}'

# Test GPT-OSS pipeline (DGX Spark 2 → Mac Studio 1)
curl -X POST http://169.254.150.104:8000/prefill \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Provide feedback on this code:"}'
```

## Configuration

The disaggregated setup is configured in `model_config.py`:

```python
CODE_MODEL = "disaggregated:qwen3-coder:30b"      # DGX Spark 1 + Mac Studio 2
FEEDBACK_MODEL = "disaggregated:gpt-oss:120b"     # DGX Spark 2 + Mac Studio 1
```

## How It Works

1. **Prefill Phase** (DGX): Process the prompt and generate KV cache
   - Fast GPU processing for prompt encoding
   - Returns KV cache to decode server

2. **Decode Phase** (Mac): Generate tokens using the KV cache
   - Efficient token generation on Mac Studio
   - Uses MLX for optimized Apple Silicon performance

3. **Parallel Execution**: Both pipelines run simultaneously
   - Code analysis and feedback generation happen in parallel
   - Maximum throughput using all 4 machines

## Performance Benefits

- **2x Throughput**: Two models running in parallel
- **Faster Prefill**: DGX GPUs handle prompt processing
- **Efficient Decode**: Mac Studios optimized for token generation
- **Load Distribution**: Work spread across 4 machines
