# Disaggregated Inference - Quick Start

Get your disaggregated inference system running in 3 steps.

## What is This?

Split AI inference between DGX Sparks (prefill) and Mac Studios (decode):
- **DGX**: Fast parallel prompt processing → KV cache
- **Mac**: Efficient sequential token generation
- **Result**: Better performance than either alone

## Prerequisites

✅ Static IPs configured (see `setup_static_ips.sh`)
✅ Models distributed to all machines
✅ Dependencies installed (PyTorch on DGX, MLX on Mac)

## 3-Step Startup

### 1️⃣ Start DGX Prefill Servers
```bash
./disaggregated_inference/start_dgx_servers.sh
```

Wait for: `✅ DGX prefill servers started!`

### 2️⃣ Start Mac Decode Servers
```bash
./disaggregated_inference/start_mac_servers.sh
```

Wait for: `✅ Mac decode servers started!`

### 3️⃣ Test the System
```bash
python3 disaggregated_inference/check_status.py
```

Should show: `✅ All systems operational`

## Quick Test

```bash
python3 disaggregated_inference/test_system.py
```

This will:
- Test Qwen 3 Coder 30B generation
- Test GPT-OSS 120B generation
- Show performance metrics

## Usage Example

```python
from disaggregated_inference.orchestrator import DisaggregatedInference
import asyncio

config = {
    'prefill_servers': [
        {'host': '192.168.100.1', 'port': 8000, 'model': 'qwen'},
    ],
    'decode_servers': [
        {'host': '169.254.150.101', 'port': 8001, 'model': 'qwen'},
    ]
}

orchestrator = DisaggregatedInference(config)

result = await orchestrator.generate(
    prompt="def fibonacci(n):",
    model_type="qwen",
    max_tokens=100
)

print(result['response'])
print(f"Speed: {result['tokens_per_sec']:.1f} tok/s")
```

## Monitoring

### Check Status
```bash
python3 disaggregated_inference/check_status.py
```

### View Logs
```bash
./disaggregated_inference/monitor_logs.sh
```

### Stop Everything
```bash
./disaggregated_inference/stop_all_servers.sh
```

## Troubleshooting

### Servers not responding?
```bash
# Check if running
ps aux | grep server

# Restart
./disaggregated_inference/stop_all_servers.sh
./disaggregated_inference/start_dgx_servers.sh
./disaggregated_inference/start_mac_servers.sh
```

### Network issues?
```bash
# Test connectivity
ping 192.168.100.1
curl http://192.168.100.1:8000/health
```

### Model not loading?
```bash
# Check model exists
ssh humphrjk@169.254.150.103 'ls ~/models/fp4/qwen3-coder-30b-fp4/'

# Check logs
ssh humphrjk@169.254.150.103 'tail -50 ~/logs/prefill_qwen.log'
```

## Architecture

```
Prompt → DGX Prefill → KV Cache → Mac Decode → Tokens
         (Fast)        (200Gb/s)   (Efficient)
```

## Files

- `prefill_server_dgx.py` - DGX server (PyTorch)
- `decode_server_mac.py` - Mac server (MLX)
- `orchestrator.py` - Coordinates everything
- `start_dgx_servers.sh` - Start DGX servers
- `start_mac_servers.sh` - Start Mac servers
- `stop_all_servers.sh` - Stop all servers
- `check_status.py` - Check system health
- `test_system.py` - Run tests
- `monitor_logs.sh` - View all logs

## Next Steps

1. ✅ Get system running (you're here!)
2. 📊 Run benchmarks: `python3 benchmarks/compare_disaggregated.py`
3. 🔧 Integrate with grading system
4. 📈 Monitor performance over time

## Support

See `DEPLOYMENT.md` for detailed deployment guide.
See `README.md` for architecture details.
