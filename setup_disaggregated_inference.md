# Disaggregated Inference Setup Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DISAGGREGATED INFERENCE                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  DGX Spark 1 │◄───────►│  DGX Spark 2 │                 │
│  │ (Prefill)    │ ConnectX│ (Prefill)    │                 │
│  │ 192.168.100.1│   -7    │192.168.100.2 │                 │
│  └──────┬───────┘         └──────┬───────┘                 │
│         │                         │                          │
│         │    10GbE Ethernet       │                          │
│         │   169.254.150.x         │                          │
│         │                         │                          │
│  ┌──────▼───────┐         ┌──────▼───────┐                 │
│  │ Mac Studio 1 │◄───────►│ Mac Studio 2 │                 │
│  │  (Decode)    │Thunderbt│  (Decode)    │                 │
│  │169.254.150.  │  Bridge │169.254.150.  │                 │
│  │     101      │         │     102      │                 │
│  └──────────────┘         └──────────────┘                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Network Configuration

### DGX Sparks
- **DGX Spark 1:**
  - Ethernet: 169.254.150.103
  - ConnectX-7: 192.168.100.1 (RDMA)
  - Models: ~/models/fp4/

- **DGX Spark 2:**
  - Ethernet: 169.254.150.104
  - ConnectX-7: 192.168.100.2 (RDMA)
  - Models: ~/models/fp4/

### Mac Studios
- **Mac Studio 1:**
  - Ethernet: 169.254.150.101
  - 10GbE: 10.176.26.7
  - Models: ~/models/fp4/

- **Mac Studio 2:**
  - Ethernet: 169.254.150.102
  - 10GbE: 10.176.142.167
  - Models: ~/models/fp4/

## Models Available

Both model pairs on all machines:
1. **Qwen 3 Coder 30B FP4** (17GB) - Code analysis
2. **GPT-OSS 120B FP4** (63GB) - Feedback generation

## Implementation Options

### Option 1: vLLM Disaggregated Serving (Recommended)

**DGX Sparks (Prefill):**
```bash
# Install vLLM with CUDA support
pip install vllm

# Start prefill server on DGX Spark 1
vllm serve ~/models/fp4/qwen3-coder-30b-fp4 \
  --host 192.168.100.1 \
  --port 8000 \
  --tensor-parallel-size 2 \
  --pipeline-parallel-size 2 \
  --enable-prefix-caching \
  --disable-log-requests

# Start prefill server on DGX Spark 2
vllm serve ~/models/fp4/gpt-oss-120b-fp4 \
  --host 192.168.100.2 \
  --port 8000 \
  --tensor-parallel-size 2 \
  --pipeline-parallel-size 2 \
  --enable-prefix-caching
```

**Mac Studios (Decode):**
```bash
# Install MLX-LM
pip install mlx-lm

# Start decode server on Mac Studio 1
python -m mlx_lm.server \
  --model ~/models/fp4/qwen3-coder-30b-fp4 \
  --host 169.254.150.101 \
  --port 8001

# Start decode server on Mac Studio 2
python -m mlx_lm.server \
  --model ~/models/fp4/gpt-oss-120b-fp4 \
  --host 169.254.150.102 \
  --port 8001
```

### Option 2: TensorRT-LLM (NVIDIA Optimized)

**DGX Sparks:**
```bash
# Build TensorRT-LLM engine
trtllm-build \
  --checkpoint_dir ~/models/fp4/qwen3-coder-30b-fp4 \
  --output_dir /tmp/qwen_engine \
  --gemm_plugin float16 \
  --max_batch_size 32

# Run inference server
mpirun -n 2 --allow-run-as-root \
  python tensorrt_llm/examples/run.py \
  --engine_dir /tmp/qwen_engine \
  --tokenizer_dir ~/models/fp4/qwen3-coder-30b-fp4
```

### Option 3: Custom Disaggregated Pipeline

I can create a custom Python implementation that:
1. Sends prompts to DGX for prefill
2. Transfers KV cache to Mac
3. Mac generates tokens using cached prefill
4. Returns results

## Performance Expectations

### Prefill (DGX Sparks)
- **Throughput:** ~10,000 tokens/sec (both GPUs)
- **Latency:** ~50ms for 1000 tokens
- **Batch size:** 32-64 prompts

### Decode (Mac Studios)
- **Throughput:** ~100 tokens/sec per model
- **Latency:** ~10ms per token
- **Memory:** Efficient with FP4 quantization

### Overall
- **Speedup:** 3-5x vs Mac-only inference
- **Efficiency:** DGX handles compute-heavy prefill, Mac handles sequential decode
- **Scalability:** Can add more Macs for decode capacity

## Next Steps

1. **Choose implementation:** vLLM (easiest), TensorRT-LLM (fastest), or Custom
2. **Install dependencies** on all machines
3. **Start servers** on DGX and Mac
4. **Test connectivity** and KV cache transfer
5. **Benchmark performance** with real workloads
6. **Integrate with grading system**

## Testing Commands

```bash
# Test DGX prefill server
curl http://192.168.100.1:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def hello():", "max_tokens": 10}'

# Test Mac decode server
curl http://169.254.150.101:8001/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def hello():", "max_tokens": 50}'
```

## Which option would you like to implement?
