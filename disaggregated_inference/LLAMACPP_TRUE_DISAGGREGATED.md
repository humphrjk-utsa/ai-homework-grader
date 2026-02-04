# True Disaggregated llama.cpp: DGX Prefill → Mac Decode

## ✅ You're Right! Same Backend = Compatible KV Cache

Since you're using **llama.cpp on BOTH** DGX and Mac with the **same GGUF models**, the KV cache format IS compatible!

```
DGX Spark (llama.cpp + Qwen.gguf)  →  llama.cpp state  →  Mac Studio (llama.cpp + Qwen.gguf)
                                     ✅ COMPATIBLE!
```

**The confusion was:** I was initially describing mixing PyTorch (Transformers) ↔ llama.cpp, which won't work.

**Your approach:** llama.cpp everywhere = TRUE disaggregated inference! 🎯

---

## Architecture

### Pair 1: Qwen-30B-Coder
```
┌─────────────────────────────────┐
│ DGX Spark 3 (169.254.150.105)  │
│ llama.cpp Prefill Server        │
│ Qwen-30B-Coder Q4_K_M.gguf     │
│ GPU: NVIDIA (CUDA)              │
└────────────┬────────────────────┘
             │ llama.cpp state
             │ (~250MB)
             ▼
┌─────────────────────────────────┐
│ Mac Studio 2 (169.254.150.102) │
│ llama.cpp Decode Server         │
│ Qwen-30B-Coder Q4_K_M.gguf     │
│ GPU: Metal (Apple Silicon)      │
└─────────────────────────────────┘
```

### Pair 2: Llama-70B-Instruct
```
┌─────────────────────────────────┐
│ DGX Spark 4 (169.254.150.106)  │
│ llama.cpp Prefill Server        │
│ Llama-70B-Instruct Q4_K_M.gguf │
│ GPU: NVIDIA (CUDA)              │
└────────────┬────────────────────┘
             │ llama.cpp state
             │ (~450MB)
             ▼
┌─────────────────────────────────┐
│ Mac Studio 1 (169.254.150.101) │
│ llama.cpp Decode Server         │
│ Llama-70B-Instruct Q4_K_M.gguf │
│ GPU: Metal (Apple Silicon)      │
└─────────────────────────────────┘
```

---

## Key Difference: llama.cpp State Transfer

**What gets transferred:**
- llama.cpp internal state (includes KV cache)
- Token positions
- Context state
- All attention cache data

**Format:** llama.cpp's native state serialization (same format on both sides!)

**Size:**
- Qwen-32B: ~200-300MB
- Llama-70B: ~400-500MB

---

## Setup Steps

### Step 1: Install llama.cpp on ALL Machines

```bash
cd disaggregated_inference
./install_llamacpp.sh
```

**This installs:**
- DGX Sparks: llama-cpp-python with CUDA support
- Mac Studios: llama-cpp-python with Metal support

### Step 2: Download SAME GGUF Models for Each Pair

**CRITICAL:** Both DGX and Mac in each pair MUST have the EXACT SAME model file!

```bash
# Download models locally first
./download_gguf_models.sh

# Models will be in: ~/models/gguf/
# - qwen2.5-coder-32b-instruct-q4_k_m.gguf
# - llama-3.1-70b-instruct-q4_k_m.gguf
```

### Step 3: Distribute Models to Machines

**Pair 1: Qwen-30B (DGX Spark 3 + Mac Studio 2)**

```bash
# Copy to DGX Spark 3
scp ~/models/gguf/qwen2.5-coder-32b-instruct-q4_k_m.gguf \
    humphrjk@169.254.150.105:~/models/gguf/

# Copy to Mac Studio 2
scp ~/models/gguf/qwen2.5-coder-32b-instruct-q4_k_m.gguf \
    humphrjk@169.254.150.102:~/models/gguf/
```

**Pair 2: Llama-70B (DGX Spark 4 + Mac Studio 1)**

```bash
# Copy to DGX Spark 4
scp ~/models/gguf/llama-3.1-70b-instruct-q4_k_m.gguf \
    humphrjk@169.254.150.106:~/models/gguf/

# Copy to Mac Studio 1
scp ~/models/gguf/llama-3.1-70b-instruct-q4_k_m.gguf \
    humphrjk@169.254.150.101:~/models/gguf/
```

### Step 4: Verify Models Match

**IMPORTANT:** Verify the models are identical (same hash):

```bash
# Check DGX Spark 3
ssh humphrjk@169.254.150.105 "md5sum ~/models/gguf/qwen*.gguf"

# Check Mac Studio 2
ssh humphrjk@169.254.150.102 "md5 ~/models/gguf/qwen*.gguf"

# Hashes MUST match!
```

### Step 5: Start llama.cpp Servers

```bash
cd disaggregated_inference

# Start DGX prefill servers (llama.cpp)
./start_dgx_servers_llamacpp.sh

# Start Mac decode servers (llama.cpp)
./start_mac_servers_llamacpp.sh

# Verify
python3 check_status.py
```

---

## How State Transfer Works

### Phase 1: Prefill on DGX (GPU Parallel Processing)

```python
# DGX Spark prefill_server_llamacpp.py

# 1. Load model
model = Llama(model_path, n_gpu_layers=-1)  # All on GPU

# 2. Process prompt (prefill)
tokens = model.tokenize(prompt)
model.eval(tokens)  # Populate KV cache

# 3. Extract llama.cpp state
state_bytes = model.save_state()  # Serialize internal state

# 4. Send to Mac
response = {
    'llama_state': base64.encode(state_bytes),
    'prefill_time': 0.234,  # Very fast on GPU!
    'prompt': original_prompt
}
```

**DGX Prefill Speed:** 500-2000 tok/s (NVIDIA GPU parallel processing)

### Phase 2: Decode on Mac (Sequential Token Generation)

```python
# Mac Studio decode_server_llamacpp.py

# 1. Receive state from DGX
state_bytes = base64.decode(request['llama_state'])

# 2. Load model (same GGUF file!)
model = Llama(model_path, n_gpu_layers=1)  # Metal acceleration

# 3. Restore llama.cpp state
model.load_state(state_bytes)  # Inject KV cache!

# 4. Continue generation (decode only)
response = model.generate(
    [],  # No prompt needed - state has it!
    max_tokens=100
)
```

**Mac Decode Speed:** 30-80 tok/s (Apple Silicon optimized for sequential)

---

## Expected Performance

### Example: Grading Assignment

**Input:** 500 token prompt (student code + rubric)
**Output:** 200 tokens (feedback)

**Mac-only (full generation):**
```
Prefill:  500 tokens @ 60 tok/s   = 8.3s
Decode:   200 tokens @ 40 tok/s   = 5.0s
Total:    13.3s
```

**Disaggregated (DGX → Mac):**
```
Prefill:  500 tokens @ 1200 tok/s = 0.42s (DGX CUDA)
Network:  State transfer (~250MB)  = 0.15s
Decode:   200 tokens @ 45 tok/s   = 4.44s (Mac Metal)
Total:    5.01s
```

**Speedup:** 62% faster! ✅

**Key benefit:** DGX GPU does prefill 20x faster than Mac!

---

## Network Transfer Optimization

### State Size by Model

| Model | State Size | 1Gbps Transfer | 10Gbps Transfer |
|-------|------------|----------------|-----------------|
| Qwen-32B Q4 | ~250MB | 2.0s | 0.2s |
| Llama-70B Q4 | ~450MB | 3.6s | 0.36s |

**Your Ethernet:** 169.254.150.x network
**Expected:** ~1Gbps = 0.2-0.4s transfer time

**Optimization:**
- Use dedicated network interface for DGX ↔ Mac
- Consider 10GbE if available
- Compress state (optional)

---

## Configuration File Update

Create `config_llamacpp.json`:

```json
{
  "comment": "llama.cpp disaggregated inference - same models on both sides",
  "prefill_servers": [
    {
      "host": "169.254.150.105",
      "port": 8000,
      "model": "qwen",
      "name": "DGX Spark 3 (llama.cpp)",
      "backend": "llamacpp",
      "model_file": "qwen2.5-coder-32b-instruct-q4_k_m.gguf"
    },
    {
      "host": "169.254.150.106",
      "port": 8000,
      "model": "gpt-oss",
      "name": "DGX Spark 4 (llama.cpp)",
      "backend": "llamacpp",
      "model_file": "llama-3.1-70b-instruct-q4_k_m.gguf"
    }
  ],
  "decode_servers": [
    {
      "host": "169.254.150.102",
      "port": 8001,
      "model": "qwen",
      "name": "Mac Studio 2 (llama.cpp)",
      "backend": "llamacpp",
      "model_file": "qwen2.5-coder-32b-instruct-q4_k_m.gguf"
    },
    {
      "host": "169.254.150.101",
      "port": 8001,
      "model": "gpt-oss",
      "name": "Mac Studio 1 (llama.cpp)",
      "backend": "llamacpp",
      "model_file": "llama-3.1-70b-instruct-q4_k_m.gguf"
    }
  ],
  "note": "CRITICAL: Each pair must have IDENTICAL GGUF model files!"
}
```

---

## Testing

### Test Individual Servers

**DGX Prefill:**
```bash
curl -X POST http://169.254.150.105:8000/prefill \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def fibonacci(n):"}'
```

**Mac Decode:**
```bash
curl -X POST http://169.254.150.102:8001/decode \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def fibonacci(n):",
    "llama_state": "<base64_state_from_dgx>",
    "max_new_tokens": 50
  }'
```

### Test End-to-End

```bash
python3 test_llamacpp_disaggregated.py
```

### Run Benchmarks

```bash
python3 benchmark_disaggregated.py
```

---

## Advantages of This Approach

✅ **Same backend everywhere** - No format conversion needed
✅ **True KV cache transfer** - llama.cpp state is fully compatible
✅ **GGUF models** - Easy to download and deploy
✅ **Maximum GPU utilization** - DGX for parallel, Mac for sequential
✅ **Proven performance** - llama.cpp is highly optimized

---

## Troubleshooting

### "State loading failed"

**Check:**
1. Are models IDENTICAL on both machines? (check md5sum)
2. Are llama.cpp versions the same? (`python3 -c "import llama_cpp; print(llama_cpp.__version__)"`)
3. Is the model loaded with same context size? (n_ctx must match)

**Fix:**
```bash
# Ensure same llama-cpp-python version
pip install llama-cpp-python==0.2.82  # Use specific version

# Verify models match
ssh humphrjk@169.254.150.105 "md5sum ~/models/gguf/*.gguf"
ssh humphrjk@169.254.150.102 "md5sum ~/models/gguf/*.gguf"
```

### "State too large" or transfer timeout

**Solution:** Increase network timeout or compress state

```python
# In prefill_server_llamacpp.py
import zlib
compressed = zlib.compress(state_bytes, level=1)  # Fast compression
```

### "Model mismatch error"

Both machines must load the model with SAME parameters:
- Same n_ctx (context window)
- Same model file
- Same llama.cpp version

---

## Performance Monitoring

```python
# Monitor disaggregated performance
result = await orchestrator.generate(prompt="...", model_type="qwen")

print(f"Prefill time: {result['prefill_time']:.3f}s (DGX)")
print(f"Network time: {result['network_time']:.3f}s")
print(f"Decode time: {result['decode_time']:.3f}s (Mac)")
print(f"Total time: {result['total_time']:.3f}s")

speedup = (mac_only_time - total_time) / mac_only_time * 100
print(f"Speedup: {speedup:.1f}% faster than Mac-only")
```

---

## Next Steps

1. ✅ Install llama.cpp on all machines
2. ✅ Download GGUF models
3. ✅ Distribute IDENTICAL models to each pair
4. ✅ Start servers
5. ✅ Run benchmarks
6. ✅ Measure actual speedup!

**Start here:**
```bash
cd disaggregated_inference
./install_llamacpp.sh
./download_gguf_models.sh
# ... distribute models ...
./start_dgx_servers_llamacpp.sh
./start_mac_servers_llamacpp.sh
python3 benchmark_disaggregated.py
```

This will give you TRUE disaggregated inference with llama.cpp on both sides! 🚀
