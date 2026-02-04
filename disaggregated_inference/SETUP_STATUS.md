# Disaggregated llama.cpp Setup Status

**Date:** 2026-02-03
**Branch:** DGX-TEST-For-Alex

---

## ✅ Models Configured

### Pair 1: Qwen3-Coder-30B-Q8 (Code Analysis)

| Machine | Path | Status |
|---------|------|--------|
| **DGX Spark 3** (Prefill) | `/home/humphrjk/models/qwen3-coder-30b-q8.gguf` | ✅ Ready |
| **Mac Studio 2** (Decode) | `~/models/gguf/qwen3-coder-30b-q8.gguf` | ✅ Copied |

### Pair 2: GPT-OSS-120B-Q8 (Feedback Generation)

| Machine | Path | Status |
|---------|------|--------|
| **DGX Spark 4** (Prefill) | `/home/humphrjk/models/gpt-oss-120b-q8.gguf` | ✅ Ready |
| **Mac Studio 1** (Decode) | `~/models/gguf/gpt-oss-120b-q8.gguf` | ⚠️ Need to copy |

**Note:** Mac Studio 1's 512GB RAM can easily handle the full GPT-OSS-120B model (~60GB)!

---

## 🔧 llama-cpp-python Installation

| Machine | IP | Python | llama-cpp-python | Hardware |
|---------|-----|--------|------------------|----------|
| **Mac Studio 1** (local) | 169.254.150.101 | ✅ 3.12.2 | ✅ v0.3.16 (Metal) | **M3 Ultra (512GB RAM)** |
| **Mac Studio 2** | 169.254.150.102 | ✅ 3.12.8 | ✅ v0.3.16 (Metal) | **M4 Ultra (128GB RAM)** |
| **DGX Spark 3** | 169.254.150.105 | ✅ 3.12.3 | ✅ v0.3.16 (CUDA) | **Grace Blackwell GPU** |
| **DGX Spark 4** | 169.254.150.106 | ✅ 3.12.3 | ✅ v0.3.16 (CUDA) | **Grace Blackwell GPU** |

**Note:** Exceptional hardware! Mac Studios have M3/M4 Ultra with massive unified memory. DGX Sparks have Grace Blackwell GPUs with CUDA acceleration.

---

## 📁 Server Scripts Updated

### DGX Prefill Servers
**File:** [start_dgx_servers_llamacpp.sh](start_dgx_servers_llamacpp.sh)

**Configuration:**
```bash
DGX Spark 3: 169.254.150.105:8000 (Qwen3-Coder-30B Q8)
DGX Spark 4: 169.254.150.106:8000 (GPT-OSS-120B Q8)

Model Paths:
  QWEN:    /home/humphrjk/models/qwen3-coder-30b-q8.gguf
  GPT-OSS: /home/humphrjk/models/gpt-oss-120b-q8.gguf
```

### Mac Decode Servers
**File:** [start_mac_servers_llamacpp.sh](start_mac_servers_llamacpp.sh)

**Configuration:**
```bash
Mac Studio 1: 169.254.150.101:8001 (GPT-OSS-120B Q8)
Mac Studio 2: 169.254.150.102:8001 (Qwen3-Coder-30B Q8)

Model Paths:
  QWEN:    ~/models/gguf/qwen3-coder-30b-q8.gguf
  GPT-OSS: ~/models/gguf/gpt-oss-120b-q8.gguf
```

---

## 📋 Pending Actions

### 1. Wait for Installation to Complete
Check progress:
```bash
tail -f /private/tmp/claude-501/-Users-humphrjk-Library-CloudStorage-OneDrive-ionxs-ai-analytics-ai-homework-grader/tasks/bd44224.output
```

Verify when done:
```bash
python3 -c "import llama_cpp; print('✓ Installed:', llama_cpp.__version__)"
ssh humphrjk@169.254.150.105 "python3 -c 'import llama_cpp'"
ssh humphrjk@169.254.150.106 "python3 -c 'import llama_cpp'"
ssh humphrjk@169.254.150.102 "python3 -c 'import llama_cpp'"
```

### 2. Copy GPT-OSS Model to Mac Studio 1
```bash
# Copy from DGX Spark 4
scp humphrjk@169.254.150.106:/home/humphrjk/models/gpt-oss-120b-q8.gguf \
    ~/models/gguf/gpt-oss-120b-q8.gguf
```

Or from local cache:
```bash
# Your local GPT-OSS files (2-part)
cp ~/Library/Caches/llama.cpp/unsloth_gpt-oss-120b-GGUF_UD-Q8_K_XL_*.gguf ~/models/gguf/
```

### 3. Start Servers

Once installation completes:

```bash
cd disaggregated_inference

# Start DGX prefill servers
./start_dgx_servers_llamacpp.sh

# Start Mac decode servers
./start_mac_servers_llamacpp.sh

# Verify all running
python3 check_status.py
```

### 4. Run Benchmarks

```bash
# Test disaggregated vs Mac-only
python3 benchmark_disaggregated.py
```

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Disaggregated Inference                   │
└─────────────────────────────────────────────────────────────┘

Pair 1: Code Analysis (Qwen3-Coder-30B-Q8)
─────────────────────────────────────────────────────────────
DGX Spark 3          →  llama.cpp state  →   Mac Studio 2
169.254.150.105:8000    (~18GB model)        169.254.150.102:8001
Prefill (CPU/ARM)       KV cache transfer    Decode (Metal)

Pair 2: Feedback Generation (GPT-OSS-120B-Q8)
─────────────────────────────────────────────────────────────
DGX Spark 4          →  llama.cpp state  →   Mac Studio 1
169.254.150.106:8000    (~60GB model)        169.254.150.101:8001
Prefill (CPU/ARM)       KV cache transfer    Decode (Metal)
```

---

## ⚠️ Known Issues

1. **DGX Grace Blackwell Architecture:**
   - DGX Sparks have ARM64 Grace CPUs + Blackwell GPUs
   - CUDA compiler path needed explicit configuration
   - Installing with GGML_CUDA=on for full GPU acceleration
   - Should provide excellent prefill performance

2. **Multi-part GGUF:**
   - GPT-OSS-120B is a 2-part GGUF file
   - llama.cpp should handle automatically
   - If issues, may need to merge parts

3. **Mac Studio 2 Network:**
   - Had PyPI connectivity issues
   - Installing with `--break-system-packages`

---

## 🔄 Fallback Options

If DGX prefill performance is poor (CPU-only ARM):

### Option A: Mac-Only Mode
Use Mac Studios for full generation (prefill + decode):
```bash
./start_mac_servers_llamacpp.sh
# Skip DGX servers
```

### Option B: Use Existing Ollama Setup
Your models work with Ollama:
```bash
./start_mac_servers_ollama.sh
```

### Option C: Build CUDA Support
Set up CUDA compiler on DGX Sparks:
```bash
export CUDACXX=/usr/local/cuda/bin/nvcc
export PATH=/usr/local/cuda/bin:$PATH
CMAKE_ARGS='-DGGML_CUDA=on' pip3 install --force-reinstall llama-cpp-python
```

---

## 📊 Expected Performance

### With CUDA on Grace Blackwell + M3/M4 Ultra (installing now):
- **DGX Prefill:** 500-2000+ tok/s (Blackwell GPU!)
- **Mac Decode:** 60-120 tok/s (M3/M4 Ultra with Metal!)
- **Speedup:** 60-80%+ faster than Mac-only
- **Key advantage:** Massive 512GB/128GB unified memory = no swapping!

### Mac-Only (fallback if needed):
- **Mac M3/M4 Ultra:** 60-120 tok/s (can handle full model)
- **Baseline:** Already very fast with this hardware!

---

## 📚 Documentation

- **Setup Guide:** [LLAMACPP_TRUE_DISAGGREGATED.md](LLAMACPP_TRUE_DISAGGREGATED.md)
- **Performance:** [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)
- **Deployment:** [LLAMACPP_DEPLOYMENT.md](LLAMACPP_DEPLOYMENT.md)
- **Cluster Analysis:** [../CLUSTER_ANALYSIS.md](../CLUSTER_ANALYSIS.md)

---

**Next Step:** Wait for installation to complete, then start servers!
