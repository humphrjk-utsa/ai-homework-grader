# Disaggregated Inference System

Split inference workload between DGX Sparks (prefill) and Mac Studios (decode) for optimal performance.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DISAGGREGATED INFERENCE                   │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   DGX SPARK 1        │         │   DGX SPARK 2        │
│   192.168.100.1      │         │   192.168.100.2      │
│                      │         │                      │
│   Qwen 3 Coder 30B   │         │   GPT-OSS 120B       │
│   PREFILL SERVER     │         │   PREFILL SERVER     │
│   Port 8000          │         │   Port 8000          │
│                      │         │                      │
│   • Process prompt   │         │   • Process prompt   │
│   • Generate KV      │         │   • Generate KV      │
│   • High throughput  │         │   • High throughput  │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                │
           │ KV Cache Transfer              │
           │ (ConnectX-7 200Gb/s)           │
           ▼                                ▼
┌──────────────────────┐         ┌──────────────────────┐
│   MAC STUDIO 1       │         │   MAC STUDIO 2       │
│   169.254.150.101    │         │   169.254.150.102    │
│                      │         │                      │
│   Qwen 3 Coder 30B   │         │   GPT-OSS 120B       │
│   DECODE SERVER      │         │   DECODE SERVER      │
│   Port 8001          │         │   Port 8001          │
│                      │         │                      │
│   • Receive KV       │         │   • Receive KV       │
│   • Generate tokens  │         │   • Generate tokens  │
│   • Low latency      │         │   • Low latency      │
└──────────────────────┘         └──────────────────────┘
```

## Why Disaggregated?

**DGX Strengths (Prefill):**
- 8x H100 GPUs with NVLink
- Massive parallel processing
- Fast KV cache generation
- ConnectX-7 for data transfer

**Mac Strengths (Decode):**
- Unified memory architecture
- Low latency token generation
- MLX optimization
- Energy efficient

## Quick Start

### 1. Start DGX Prefill Servers
```bash
./disaggregated_inference/start_dgx_servers.sh
```

This starts:
- DGX Spark 1: Qwen 3 Coder 30B @ 192.168.100.1:8000
- DGX Spark 2: GPT-OSS 120B @ 192.168.100.2:8000

### 2. Start Mac Decode Servers
```bash
./disaggregated_inference/start_mac_servers.sh
```

This starts:
- Mac Studio 1: Qwen 3 Coder 30B @ 169.254.150.101:8001
- Mac Studio 2: GPT-OSS 120B @ 169.254.150.102:8001

### 3. Test the System
```bash
python3 disaggregated_inference/test_system.py
```

### 4. Use the Orchestrator
```python
from disaggregated_inference.orchestrator import DisaggregatedInference

config = {
    'prefill_servers': [
        {'host': '192.168.100.1', 'port': 8000, 'model': 'qwen'},
        {'host': '192.168.100.2', 'port': 8000, 'model': 'gpt-oss'}
    ],
    'decode_servers': [
        {'host': '169.254.150.101', 'port': 8001, 'model': 'qwen'},
        {'host': '169.254.150.102', 'port': 8001, 'model': 'gpt-oss'}
    ]
}

orchestrator = DisaggregatedInference(config)

result = await orchestrator.generate(
    prompt="def fibonacci(n):",
    model_type="qwen",
    max_tokens=100
)

print(result['response'])
```

## Files

- `prefill_server_dgx.py` - DGX prefill server (PyTorch/CUDA)
- `decode_server_mac.py` - Mac decode server (MLX)
- `orchestrator.py` - Coordinates prefill→decode pipeline
- `start_dgx_servers.sh` - Start both DGX servers
- `start_mac_servers.sh` - Start both Mac servers
- `stop_all_servers.sh` - Stop all servers
- `test_system.py` - Test the complete system

## API Endpoints

### Prefill Server (DGX)
- `GET /health` - Check server status
- `POST /prefill` - Process prompt and generate KV cache
  ```json
  {
    "prompt": "def fibonacci(n):"
  }
  ```

### Decode Server (Mac)
- `GET /health` - Check server status
- `POST /decode` - Generate tokens from KV cache
  ```json
  {
    "kv_cache": "...",
    "input_ids": [...],
    "max_new_tokens": 100
  }
  ```
- `POST /generate` - Fallback: full generation on Mac
  ```json
  {
    "prompt": "def fibonacci(n):",
    "max_tokens": 100
  }
  ```

## Monitoring

### Check Server Status
```bash
# DGX Spark 1
curl http://192.168.100.1:8000/health

# DGX Spark 2
curl http://192.168.100.2:8000/health

# Mac Studio 1
curl http://169.254.150.101:8001/health

# Mac Studio 2
curl http://169.254.150.102:8001/health
```

### View Logs
```bash
# DGX logs
ssh humphrjk@169.254.150.103 'tail -f ~/logs/prefill_qwen.log'
ssh humphrjk@169.254.150.104 'tail -f ~/logs/prefill_gpt_oss.log'

# Mac logs
tail -f ~/logs/decode_qwen.log
ssh humphrjk@169.254.150.102 'tail -f ~/logs/decode_gpt_oss.log'
```

## Performance Expectations

### Qwen 3 Coder 30B
- Prefill: ~0.5-1s (DGX)
- Decode: ~50-80 tok/s (Mac)
- Total: Better than Mac-only (~30 tok/s)

### GPT-OSS 120B
- Prefill: ~2-3s (DGX)
- Decode: ~20-30 tok/s (Mac)
- Total: Better than Mac-only (~10 tok/s)

## Troubleshooting

### Servers not responding
```bash
# Check if processes are running
ssh humphrjk@169.254.150.103 'ps aux | grep prefill_server'
ps aux | grep decode_server

# Restart servers
./disaggregated_inference/stop_all_servers.sh
./disaggregated_inference/start_dgx_servers.sh
./disaggregated_inference/start_mac_servers.sh
```

### Network issues
```bash
# Test connectivity
ping 192.168.100.1
ping 169.254.150.101

# Check if ports are open
nc -zv 192.168.100.1 8000
nc -zv 169.254.150.101 8001
```

### Model not loaded
Check logs for CUDA/MLX errors and ensure models are in correct paths:
- DGX: `~/models/fp4/qwen3-coder-30b-fp4`
- Mac: `~/models/fp4/qwen3-coder-30b-fp4`

## Fallback Behavior

The orchestrator automatically falls back to Mac-only generation if:
1. DGX prefill server is unavailable
2. Mac decode server is unavailable
3. Prefill request fails
4. Decode request fails

This ensures the system always works, even if disaggregated mode fails.
