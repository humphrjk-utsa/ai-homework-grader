# Distributed AI Grader Cluster Analysis

**Branch:** DGX-TEST-For-Alex
**Date:** 2026-02-03
**Status:** ⚠️ PARTIALLY OPERATIONAL (Mac Studios running, DGX Sparks offline)

---

## Executive Summary

Your distributed AI grader system is designed with a **disaggregated inference architecture** where:
- **DGX Sparks** handle **prefill** (parallel KV cache generation on GPU)
- **Mac Studios** handle **decode** (sequential token generation on Apple Silicon)

### Current Status

✅ **Mac Studios (Decode):** Both operational
❌ **DGX Sparks (Prefill):** Not responding (timeout)
⚠️ **System Mode:** Fallback to Mac-only generation

---

## Architecture Overview

### Cluster Configuration

| Pair | Prefill (DGX) | Decode (Mac) | Model | Status |
|------|---------------|--------------|-------|--------|
| **Pair 1** | DGX Spark 3<br>169.254.150.105:8000 | Mac Studio 2<br>169.254.150.102:8001 | **Qwen-30B-Coder** | ⚠️ Decode only |
| **Pair 2** | DGX Spark 4<br>169.254.150.106:8000 | Mac Studio 1<br>169.254.150.101:8001 | **GPT-OSS-120B** | ⚠️ Decode only |

### Backend Implementations

| Backend | Usage | Implementation | Status |
|---------|-------|----------------|--------|
| **HuggingFace Transformers** | DGX Prefill | [prefill_server_dgx.py](disaggregated_inference/prefill_server_dgx.py) | ✅ Code exists |
| **MLX (Apple Metal)** | Mac Decode | [decode_server_mac.py](disaggregated_inference/decode_server_mac.py) | ✅ Operational |
| **Ollama** | Alternative backend | [prefill_server_ollama.py](disaggregated_inference/prefill_server_ollama.py), [decode_server_ollama.py](disaggregated_inference/decode_server_ollama.py) | ✅ Code exists |
| **llama.cpp** | PC standalone only | [models/pc_llamacpp_client.py](models/pc_llamacpp_client.py) | ⚠️ Not integrated |

---

## Critical Finding: llama.cpp NOT Integrated

### You mentioned using llama.cpp, but the current implementation uses:

**DGX Sparks (Prefill):**
```python
# File: disaggregated_inference/prefill_server_dgx.py
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)
```

**Mac Studios (Decode):**
```python
# File: disaggregated_inference/decode_server_mac.py
from mlx_lm import load, generate

model, tokenizer = load(model_path)
response = generate(model, tokenizer, prompt=prompt)
```

### llama.cpp Exists Only For:
- **PC-based standalone client** ([models/pc_llamacpp_client.py](models/pc_llamacpp_client.py))
- Loads GGUF models with `llama_cpp.Llama()`
- NOT used in the disaggregated DGX ↔ Mac architecture

---

## Orchestration Layer

### Main Orchestrator
**File:** [disaggregated_inference/orchestrator.py](disaggregated_inference/orchestrator.py:1-242)

**Workflow:**
1. **Health check** all servers asynchronously
2. **Prefill request** → DGX Spark (generates KV cache)
3. **Decode request** → Mac Studio (uses KV cache, generates tokens)
4. **Fallback** → Mac-only if DGX unavailable

**Key Methods:**
- `update_server_status()` - Async health checks
- `prefill_request()` - Send prompt to DGX
- `decode_request()` - Send KV cache to Mac
- `generate()` - Main two-phase generation
- `fallback_generate()` - Mac-only fallback

---

## Current Issues

### 1. DGX Sparks Not Responding
```
DGX Spark 3 (169.254.150.105:8000) - ❌ Timeout
DGX Spark 4 (169.254.150.106:8000) - ❌ Timeout
```

**Possible Causes:**
- Prefill servers not started
- Network connectivity issues
- Firewall blocking port 8000
- Models not loaded or loading failed

**Diagnosis Steps:**
```bash
# Test SSH connectivity
ssh humphrjk@169.254.150.105
ssh humphrjk@169.254.150.106

# Check if servers are running
ssh humphrjk@169.254.150.105 "ps aux | grep prefill_server"
ssh humphrjk@169.254.150.106 "ps aux | grep prefill_server"

# Check logs
ssh humphrjk@169.254.150.105 "tail -100 ~/prefill_server.log"
```

### 2. llama.cpp Not Installed for Disaggregated Use

The system doesn't use llama.cpp for the DGX ↔ Mac architecture. To integrate it:

**Option A: Convert to llama.cpp-based architecture**
1. Create `prefill_server_llamacpp.py` for DGX
2. Create `decode_server_llamacpp.py` for Mac
3. Implement KV cache serialization/deserialization
4. Install llama.cpp on all machines

**Option B: Use existing Ollama backend**
```bash
cd disaggregated_inference
./start_dgx_servers_ollama.sh
./start_mac_servers_ollama.sh
```

**Option C: Keep current HuggingFace + MLX setup**
- Already implemented and working
- Just need to start DGX servers

---

## Recommended Actions

### Immediate (Fix Current System)

1. **Start DGX Prefill Servers**
```bash
# Deploy to DGX Sparks
cd disaggregated_inference
./start_dgx_servers.sh

# Or manually SSH and start
ssh humphrjk@169.254.150.105
cd ~/ai-homework-grader/disaggregated_inference
python3 prefill_server_dgx.py --model <path-to-qwen-model> --host 0.0.0.0 --port 8000

ssh humphrjk@169.254.150.106
cd ~/ai-homework-grader/disaggregated_inference
python3 prefill_server_dgx.py --model <path-to-gpt-oss-model> --host 0.0.0.0 --port 8000
```

2. **Verify Model Paths**
```bash
# On DGX Spark 3 (Qwen)
ssh humphrjk@169.254.150.105 "ls -la ~/models/*qwen*"

# On DGX Spark 4 (GPT-OSS)
ssh humphrjk@169.254.150.106 "ls -la ~/models/*gpt-oss*"
```

3. **Run Verification**
```bash
cd disaggregated_inference

# Check cluster status
python3 check_status.py

# Or use the new comprehensive verifier
python3 verify_cluster_status.py

# Check llama.cpp installation (if planning to integrate)
./verify_llamacpp_installation.sh
```

### Short-term (Enhance System)

4. **Document Model Locations**
Create `MODEL_PATHS.md` with exact paths on each machine

5. **Add Monitoring**
- Set up health check cron jobs
- Log aggregation from all machines
- Alert on server failures

6. **Test Disaggregated Flow**
```bash
cd disaggregated_inference
python3 -c "
import asyncio
from orchestrator import DisaggregatedInference
import json

async def test():
    with open('config_current.json') as f:
        config = json.load(f)

    orch = DisaggregatedInference(config)
    result = await orch.generate(
        prompt='def fibonacci(n):',
        model_type='qwen',
        max_tokens=50
    )
    print(result)

asyncio.run(test())
"
```

### Long-term (If Needed)

7. **Integrate llama.cpp** (only if required)
- Implement KV cache extraction from llama.cpp
- Test GGUF model compatibility
- Benchmark performance vs current setup

8. **Or Switch to Ollama** (simpler alternative)
- Already implemented
- Easier model management
- Built-in model serving

---

## Model Configuration

### Code Analyzer (Qwen-30B-Coder)
**Pair:** DGX Spark 3 → Mac Studio 2

```python
{
  'model_name': 'mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit',
  'max_tokens': 2400,
  'temperature': 0.1,  # Low temp for precise analysis
  'timeout': 75
}
```

**DGX Model:** Should be HuggingFace compatible Qwen model
**Mac Model:** MLX-optimized Qwen model

### Feedback Generator (GPT-OSS-120B)
**Pair:** DGX Spark 4 → Mac Studio 1

```python
{
  'model_name': 'mlx-community/gemma-3-27b-it-bf16',  # or GPT-OSS
  'max_tokens': 3800,
  'temperature': 0.3,  # Higher temp for creative feedback
  'timeout': 75
}
```

**DGX Model:** Should be HuggingFace compatible GPT-OSS-120B
**Mac Model:** MLX-optimized GPT-OSS or Gemma

---

## Performance Metrics

### Expected Performance

| Phase | Device | Operation | Expected Speed |
|-------|--------|-----------|----------------|
| Prefill | DGX Spark GPU | KV cache generation | 0.1-1s for typical prompts |
| Decode | Mac Studio | Token generation | 30-100 tok/s |

### Current Performance (Mac-only fallback)

```
Mac Studio 1: ✅ Healthy (169.254.150.101:8001)
Mac Studio 2: ✅ Healthy (169.254.150.102:8001)
Mode: Full generation on Mac (prefill + decode)
Speed: 30-80 tok/s (depending on model)
```

---

## Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Ethernet 169.254.150.x                     │
└─────────────────────────────────────────────────────────────┘
         │                │                │                │
    ┌────▼────┐      ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
    │ Mac 1   │      │ Mac 2   │     │ DGX 3   │     │ DGX 4   │
    │ .101    │      │ .102    │     │ .105    │     │ .106    │
    │ GPT-OSS │      │ Qwen    │     │ Qwen    │     │ GPT-OSS │
    │ DECODE  │      │ DECODE  │     │ PREFILL │     │ PREFILL │
    │ :8001   │      │ :8001   │     │ :8000   │     │ :8000   │
    │ ✅      │      │ ✅      │     │ ❌      │     │ ❌      │
    └─────────┘      └─────────┘     └─────────┘     └─────────┘
         ▲                ▲                ▲                ▲
         │                │                │                │
         └────────────────┴────────────────┴────────────────┘
                      Orchestrator
              (orchestrator.py or disaggregated_client.py)
```

---

## Files and Scripts

### Core Implementation
- [orchestrator.py](disaggregated_inference/orchestrator.py) - Main orchestration logic
- [prefill_server_dgx.py](disaggregated_inference/prefill_server_dgx.py) - DGX prefill server
- [decode_server_mac.py](disaggregated_inference/decode_server_mac.py) - Mac decode server
- [config_current.json](disaggregated_inference/config_current.json) - Server configuration

### Deployment
- [start_dgx_servers.sh](disaggregated_inference/start_dgx_servers.sh) - Start DGX servers
- [start_mac_servers.sh](disaggregated_inference/start_mac_servers.sh) - Start Mac servers
- [deploy_to_machines.sh](disaggregated_inference/deploy_to_machines.sh) - Deploy code
- [stop_all_servers.sh](disaggregated_inference/stop_all_servers.sh) - Stop all servers

### Monitoring
- [check_status.py](disaggregated_inference/check_status.py) - Quick status check (works now)
- [verify_cluster_status.py](disaggregated_inference/verify_cluster_status.py) - Comprehensive verification (new, requires aiohttp)
- [verify_llamacpp_installation.sh](disaggregated_inference/verify_llamacpp_installation.sh) - llama.cpp check (new)

### Alternative Backends
- [prefill_server_ollama.py](disaggregated_inference/prefill_server_ollama.py) - Ollama prefill
- [decode_server_ollama.py](disaggregated_inference/decode_server_ollama.py) - Ollama decode
- [start_dgx_servers_ollama.sh](disaggregated_inference/start_dgx_servers_ollama.sh) - Start Ollama DGX
- [start_mac_servers_ollama.sh](disaggregated_inference/start_mac_servers_ollama.sh) - Start Ollama Mac

---

## Next Steps

### Priority 1: Get DGX Sparks Running
1. SSH into DGX Spark 3 and 4
2. Verify models are downloaded
3. Start prefill servers
4. Test orchestration flow

### Priority 2: Clarify llama.cpp Requirements
**Questions for you:**
1. Do you NEED llama.cpp, or is HuggingFace + MLX acceptable?
2. If llama.cpp is required, which machines should use it?
3. Are the models already in GGUF format, or are they HuggingFace checkpoints?

### Priority 3: Document Model Paths
Create a clear mapping of:
- Which models are on which machines
- Exact file paths
- Model formats (GGUF, safetensors, etc.)

---

## Contact Points

**Current working components:**
- Mac Studio 1: 169.254.150.101:8001 ✅
- Mac Studio 2: 169.254.150.102:8001 ✅

**Need attention:**
- DGX Spark 3: 169.254.150.105:8000 ❌
- DGX Spark 4: 169.254.150.106:8000 ❌

**Verification commands:**
```bash
# Quick status
cd disaggregated_inference && python3 check_status.py

# Detailed llama.cpp check
cd disaggregated_inference && ./verify_llamacpp_installation.sh

# Test Mac decode directly
curl http://169.254.150.101:8001/health
curl http://169.254.150.102:8001/health
```

---

**Generated:** 2026-02-03
**Branch:** DGX-TEST-For-Alex
**System Status:** ⚠️ Partially Operational (Mac decode only, DGX prefill offline)
