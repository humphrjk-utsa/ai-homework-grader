# DGX + Mac Qwen3 Coder Disaggregated Inference Setup

## Goal
Offload Qwen3-Coder-30B prefill to DGX Spark cluster, keep decode on Mac M4 Max

## Current Status
- ✅ Mac M4 Max: **Ollama** (simpler than llama.cpp)
- ✅ DGX Spark: llama.cpp source transferred, ready to compile
- ✅ Passwordless SSH: Mac → DGX working
- ✅ Network: 10GbE connection, ~0.6ms latency

## Model
**Qwen3-Coder-30B-A3B-Instruct** (currently using 8-bit MLX version)

Need GGUF format:
- For DGX (llama.cpp): Download from HuggingFace `bartowski/Qwen2.5-Coder-32B-Instruct-GGUF`
- For Mac (Ollama): Use `ollama pull qwen2.5-coder:32b`

## Setup Steps

### 1. Install llama.cpp on DGX
Since DGX has no internet, options:
- **Option A**: Clone llama.cpp on Mac, tar it, scp to DGX, compile there
- **Option B**: Use pre-built binaries if available
- **Option C**: Build on Mac (ARM), copy binary to DGX (also ARM - Grace CPU)

### 2. Get Qwen3 Coder GGUF model
- Download on Mac (has internet)
- Transfer to DGX via scp
- Recommended quantization: Q4_K_M or Q5_K_M (balance speed/quality)

### 3. Start servers

**DGX (Prefill only - llama.cpp):**
```bash
llama-server \
  --model /path/to/qwen2.5-coder-32b.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers 99 \
  --flash-attn \
  --cont-batching \
  --parallel 4
```

**Mac M4 Max (Decode - Ollama):**
```bash
# Pull model
ollama pull qwen2.5-coder:32b

# Ollama runs as service automatically
# API available at http://localhost:11434
```

**Mac M3 Ultra (Feedback - MLX):**
```bash
# No changes - keep existing GPT-OSS-120B MLX server
```

### 4. Build Coordinator
Python script to:
1. Send prompt to DGX for prefill
2. Get KV cache from DGX
3. Send KV cache to Mac for decode
4. Stream tokens from Mac

### 5. Update distributed_config.json
Add DGX endpoint and configure hybrid mode

## Architecture

```
Grading Request
      ↓
Coordinator (Mac M4 Max)
      ↓
   Prompt
      ↓
DGX Spark (Prefill) ←→ 200Gbps ←→ DGX Spark 2
      ↓ (KV cache via 10GbE)
Mac M4 Max (Decode)
      ↓
   Tokens
      ↓
Response
```

## Performance Expectations
- **Current**: Qwen at 100% GPU, bottleneck
- **After**: 
  - DGX handles compute-heavy prefill
  - Mac handles memory-bandwidth decode
  - Should reduce Mac GPU usage significantly
  - Faster overall throughput

## Next Steps
1. Clone llama.cpp on Mac
2. Tar and transfer to DGX
3. Compile on DGX with CUDA support
4. Download Qwen3 Coder GGUF
5. Test basic inference on both
6. Build coordinator
7. Integrate with grading system
