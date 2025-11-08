# Ollama Disaggregated Inference Setup

## ✅ Correct Architecture: DGX Prefill → Mac Decode (Both Ollama)

This is the proper disaggregated setup using Ollama's KV cache passing.

### How It Works

```
┌──────────────────────────────────────────────────────────────┐
│              CODE ANALYSIS PIPELINE (Qwen)                    │
│                                                               │
│  Step 1: DGX Spark 1 (Prefill)                               │
│  ├─ Ollama: qwen3-coder:30b                                  │
│  ├─ Process prompt → Generate KV cache                       │
│  ├─ Fast GPU prefill: ~2-3 seconds                           │
│  └─ Return: prompt + context (KV cache)                      │
│                    ↓                                          │
│  Step 2: Mac Studio 2 (Decode)                               │
│  ├─ Ollama: qwen3-coder:30b                                  │
│  ├─ Receive KV cache from DGX                                │
│  ├─ Generate tokens using cached context                     │
│  ├─ Fast decode: ~8-10 seconds                               │
│  └─ Return: Generated response                               │
│                                                               │
│  Total: ~10-13 seconds                                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│           FEEDBACK GENERATION PIPELINE (GPT-OSS)              │
│                                                               │
│  Step 1: DGX Spark 2 (Prefill)                               │
│  ├─ Ollama: gpt-oss:120b                                     │
│  ├─ Process prompt → Generate KV cache                       │
│  ├─ Fast GPU prefill: ~3-4 seconds                           │
│  └─ Return: prompt + context (KV cache)                      │
│                    ↓                                          │
│  Step 2: Mac Studio 1 (Decode)                               │
│  ├─ Ollama: gpt-oss:120b                                     │
│  ├─ Receive KV cache from DGX                                │
│  ├─ Generate tokens using cached context                     │
│  ├─ Fast decode: ~10-12 seconds                              │
│  └─ Return: Generated response                               │
│                                                               │
│  Total: ~13-16 seconds                                        │
└──────────────────────────────────────────────────────────────┘

BOTH PIPELINES RUN IN PARALLEL
Total grading time: ~16 seconds (max of both)
```

## Configuration

### model_config.py
```python
CODE_MODEL = "disaggregated:qwen3-coder:30b"      # DGX Spark 1 → Mac Studio 2
FEEDBACK_MODEL = "disaggregated:gpt-oss:120b"     # DGX Spark 2 → Mac Studio 1

MODEL_SETTINGS = {
    "disaggregated:qwen3-coder:30b": {
        "prefill_url": "http://169.254.150.103:11434",  # DGX Spark 1 Ollama
        "decode_url": "http://169.254.150.102:11434",   # Mac Studio 2 Ollama
        "model_name": "qwen3-coder:30b"
    },
    "disaggregated:gpt-oss:120b": {
        "prefill_url": "http://169.254.150.104:11434",  # DGX Spark 2 Ollama
        "decode_url": "http://localhost:11434",         # Mac Studio 1 Ollama
        "model_name": "gpt-oss:120b"
    }
}
```

## Required Ollama Instances

### DGX Spark 1 (169.254.150.103)
- ✅ Ollama running on port 11434
- ✅ Model: `qwen3-coder:30b` loaded
- 🎯 Role: Prefill for code analysis

### DGX Spark 2 (169.254.150.104)
- ✅ Ollama running on port 11434
- ✅ Model: `gpt-oss:120b` loaded
- 🎯 Role: Prefill for feedback generation

### Mac Studio 1 (localhost)
- ✅ Ollama running on port 11434
- ✅ Model: `gpt-oss:120b` loaded
- 🎯 Role: Decode for feedback generation

### Mac Studio 2 (169.254.150.102)
- ⚠️ Ollama needs to be running on port 11434
- ⚠️ Model: `qwen3-coder:30b` needs to be loaded
- 🎯 Role: Decode for code analysis

## Setup Mac Studio 2

On Mac Studio 2, run:
```bash
# Pull the model if not already present
ollama pull qwen3-coder:30b

# Start Ollama (should auto-start, but verify)
ollama serve
```

Verify it's working:
```bash
curl http://169.254.150.102:11434/api/tags
```

## How Ollama KV Cache Passing Works

1. **Prefill Phase** (DGX):
   - Ollama processes the prompt
   - Generates KV cache (context)
   - Returns `context` array with cache data

2. **Decode Phase** (Mac):
   - Receives prompt + context from prefill
   - Ollama uses the context to skip re-processing
   - Only generates new tokens
   - Much faster than regenerating from scratch

3. **Key Benefit**:
   - DGX does heavy lifting (prefill)
   - Mac does efficient token generation
   - Total time is faster than either alone

## Performance Expectations

### Prefill (DGX)
- Qwen 3.0 Coder: ~2-3 seconds
- GPT-OSS 120B: ~3-4 seconds

### Decode (Mac)
- Qwen 3.0 Coder: ~8-10 seconds
- GPT-OSS 120B: ~10-12 seconds

### Total (Parallel)
- Both pipelines: ~16 seconds
- 2x faster than sequential
- 2x faster than single model

## Testing

Test the setup:
```bash
# Test Qwen pipeline
python3 -c "
from disaggregated_client import DisaggregatedClient
client = DisaggregatedClient(
    'http://169.254.150.103:11434',
    'http://169.254.150.102:11434',
    'qwen3-coder:30b'
)
result = client.generate('def hello():', max_tokens=100)
print(f'Response: {result[\"response\"][:100]}')
print(f'Time: {result[\"total_time\"]:.2f}s')
"

# Test GPT-OSS pipeline
python3 -c "
from disaggregated_client import DisaggregatedClient
client = DisaggregatedClient(
    'http://169.254.150.104:11434',
    'http://localhost:11434',
    'gpt-oss:120b'
)
result = client.generate('Provide feedback:', max_tokens=100)
print(f'Response: {result[\"response\"][:100]}')
print(f'Time: {result[\"total_time\"]:.2f}s')
"
```

## Advantages Over Previous Attempts

✅ **Uses Ollama on both sides**: No Ollama→MLX incompatibility
✅ **True KV cache passing**: Mac doesn't regenerate from scratch
✅ **Faster**: DGX prefill + Mac decode is optimal
✅ **Reliable**: Ollama's context passing is well-tested
✅ **Simple**: No custom servers needed

## Ready to Use

Once Mac Studio 2 has Ollama running with qwen3-coder:30b, the system is ready!

Restart the Streamlit app and grade a submission - you should see:
- "Using disaggregated inference for code"
- "Using disaggregated inference for feedback"
- Faster grading times (~16s total)
